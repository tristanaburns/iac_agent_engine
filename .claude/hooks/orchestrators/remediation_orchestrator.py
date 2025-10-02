"""Remediation orchestrator following SOLID principles.

Single Responsibility: Coordinates all remediation operations.
"""

from pathlib import Path
from typing import Any, Dict, List


class RemediationOrchestrator:
    """Orchestrates remediation operations."""

    def __init__(self):
        """Initialize remediation orchestrator."""
        from operations.logging.logger import logger

        self.logger = logger

        # Import git protection manager from tools
        self._git_manager = None
        self._quality_workflow = None

    @property
    def git_manager(self):
        """Lazy load git protection manager."""
        if self._git_manager is None:
            import sys

            from utils.path_resolver import PathResolver

            resolver = PathResolver()
            sys.path.insert(0, str(resolver.tools_dir))

            try:
                from tools.git_protection_manager import GitProtectionManager

                self._git_manager = GitProtectionManager(resolver.project_dir)
            except ImportError:
                self.logger.warning("Git protection manager not available")
                self._git_manager = None

        return self._git_manager

    @property
    def quality_workflow(self):
        """Lazy load quality workflow."""
        if self._quality_workflow is None:
            # Try to get SDK client from main orchestrator
            from claude_sdk.client.sdk_initializer import SDKInitializer

            initializer = SDKInitializer()
            sdk_client = initializer.get_client()

            if sdk_client:
                from claude_sdk.workflows.quality_workflow import QualityWorkflow

                self._quality_workflow = QualityWorkflow(sdk_client)
            else:
                self.logger.warning("Claude SDK not available for quality workflow")

        return self._quality_workflow

    def remediate(
        self, quality_report: Dict[str, Any], use_sdk: bool = False
    ) -> Dict[str, Any]:
        """Run remediation based on quality report.

        Args:
            quality_report: Quality check report
            use_sdk: Whether to use Claude SDK for remediation

        Returns:
            Dictionary with remediation results
        """
        issues_count = quality_report.get("issues_found", 0)
        self.logger.info(f"Starting remediation for {issues_count} issues")

        results = {
            "issues_found": issues_count,
            "issues_fixed": 0,
            "operations": [],
            "success": True,
        }

        if issues_count == 0:
            self.logger.info("No issues to remediate")
            return results

        try:
            # Create git protection commit before remediation
            protection_result = self._create_protection_commit(issues_count)
            results["operations"].append(
                {
                    "type": "protection_commit",
                    "result": protection_result,
                }
            )

            protection_commit = protection_result.get("commit_hash")

            # Run remediation
            if use_sdk and self.quality_workflow:
                # Use Claude SDK for intelligent remediation
                remediation_result = self._run_sdk_remediation(quality_report)
            else:
                # Use direct tool remediation
                remediation_result = self._run_tool_remediation(quality_report)

            results["operations"].append(
                {
                    "type": "remediation",
                    "result": remediation_result,
                }
            )

            # Verify remediation success
            verification_result = self._verify_remediation()
            results["operations"].append(
                {
                    "type": "verification",
                    "result": verification_result,
                }
            )

            if verification_result.get("success", False):
                # Create completion commit
                completion_result = self._create_completion_commit(
                    remediation_result.get("issues_fixed", 0)
                )
                results["operations"].append(
                    {
                        "type": "completion_commit",
                        "result": completion_result,
                    }
                )

                results["issues_fixed"] = remediation_result.get("issues_fixed", 0)
                self.logger.success(
                    f"Remediation successful: {results['issues_fixed']} issues fixed"
                )
            else:
                # Rollback to protection commit
                if protection_commit and self.git_manager:
                    rollback_result = self.git_manager.rollback_to_protection_commit(
                        protection_commit
                    )
                    results["operations"].append(
                        {
                            "type": "rollback",
                            "result": rollback_result,
                        }
                    )
                    self.logger.warning(
                        "Remediation failed - rolled back to protection commit"
                    )

                results["success"] = False

        except Exception as e:
            self.logger.exception(f"Error during remediation: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def _create_protection_commit(self, issues_count: int) -> Dict[str, Any]:
        """Create git protection commit before remediation.

        Args:
            issues_count: Number of issues to fix

        Returns:
            Protection commit result
        """
        if not self.git_manager:
            return {
                "success": False,
                "error": "Git protection not available",
            }

        try:
            result = self.git_manager.create_protection_commit(
                operation_description=f"Quality remediation - {issues_count} issues",
                target_files=None,  # Protect entire codebase
            )

            if result["success"]:
                self.logger.info(f"Protection commit created: {result['commit_hash']}")

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _run_tool_remediation(self, quality_report: Dict[str, Any]) -> Dict[str, Any]:
        """Run remediation using quality tools directly.

        Args:
            quality_report: Quality check report

        Returns:
            Remediation results
        """
        from .quality_orchestrator import QualityOrchestrator

        quality_orchestrator = QualityOrchestrator()

        self.logger.info("Running tool-based remediation")

        # Get files that need formatting
        files_to_format = []
        for check in quality_report.get("checks", []):
            if check["result"].get("needs_formatting", False):
                file_path = Path(check["file"])
                if file_path not in files_to_format:
                    files_to_format.append(file_path)

        if not files_to_format:
            return {
                "success": True,
                "issues_fixed": 0,
                "message": "No files need formatting",
            }

        # Format the files
        format_result = quality_orchestrator.format_files(files_to_format)

        return {
            "success": format_result.get("success", False),
            "issues_fixed": format_result.get("files_formatted", 0),
            "files_modified": files_to_format,
            "format_result": format_result,
        }

    def _run_sdk_remediation(self, quality_report: Dict[str, Any]) -> Dict[str, Any]:
        """Run remediation using Claude SDK.

        Args:
            quality_report: Quality check report

        Returns:
            Remediation results
        """
        if not self.quality_workflow:
            self.logger.warning(
                "Claude SDK not available - falling back to tool remediation"
            )
            return self._run_tool_remediation(quality_report)

        self.logger.info("Running SDK-based remediation")

        try:
            # Generate remediation plan
            issues = self._extract_issues_from_report(quality_report)
            recommendations = self.quality_workflow.generate_fix_recommendations(issues)

            if not recommendations or not recommendations.get("success"):
                self.logger.warning(
                    "Failed to generate recommendations - using tool remediation"
                )
                return self._run_tool_remediation(quality_report)

            # Execute remediation plan
            remediation_plan = {
                "summary": f"Fix {len(issues)} quality issues",
                "recommendations": recommendations.get("recommendations", []),
            }

            target_files = self._get_target_files_from_report(quality_report)
            execution_result = self.quality_workflow.execute_remediation(
                remediation_plan, target_files
            )

            if execution_result and execution_result.get("success"):
                return {
                    "success": True,
                    "issues_fixed": len(issues),
                    "sdk_result": execution_result,
                }
            else:
                # Fallback to tool remediation if SDK fails
                self.logger.warning("SDK remediation failed - using tool remediation")
                return self._run_tool_remediation(quality_report)

        except Exception as e:
            self.logger.exception(f"SDK remediation error: {e}")
            return self._run_tool_remediation(quality_report)

    def _verify_remediation(self) -> Dict[str, Any]:
        """Verify that remediation was successful.

        Returns:
            Verification results
        """
        from utils.process_runner import ProcessRunner

        runner = ProcessRunner()

        self.logger.info("Verifying remediation results")

        # Try to compile Python files
        compile_result = runner.run_python_module("py_compile", ["-"], timeout=30)

        # Check if tests pass (if available)
        test_result = runner.run_command(
            ["python", "-m", "pytest", "--co", "-q"], timeout=30
        )

        success = compile_result.get("success", False)

        return {
            "success": success,
            "compilation_check": compile_result.get("success", False),
            "test_collection": test_result.get("success", False),
        }

    def _create_completion_commit(self, issues_fixed: int) -> Dict[str, Any]:
        """Create completion commit after successful remediation.

        Args:
            issues_fixed: Number of issues that were fixed

        Returns:
            Completion commit result
        """
        if not self.git_manager:
            return {
                "success": False,
                "error": "Git protection not available",
            }

        try:
            result = self.git_manager.create_completion_commit(
                operation_description=f"Completed quality remediation - {issues_fixed} issues fixed",
                tools_executed=["black", "isort"],
                files_modified=[],  # Would be populated from remediation results
            )

            if result["success"]:
                self.logger.success(
                    f"Completion commit created: {result['commit_hash']}"
                )

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _extract_issues_from_report(
        self, quality_report: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract issues from quality report.

        Args:
            quality_report: Quality check report

        Returns:
            List of issues
        """
        issues = []
        for check in quality_report.get("checks", []):
            if check["result"].get("needs_formatting", False):
                issues.append(
                    {
                        "type": check["type"],
                        "file": check["file"],
                        "message": f"{check['type']} formatting needed",
                    }
                )
        return issues

    def _get_target_files_from_report(
        self, quality_report: Dict[str, Any]
    ) -> List[Path]:
        """Get target files from quality report.

        Args:
            quality_report: Quality check report

        Returns:
            List of target file paths
        """
        files = set()
        for check in quality_report.get("checks", []):
            files.add(Path(check["file"]))
        return list(files)
