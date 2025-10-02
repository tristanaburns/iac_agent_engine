"""Main orchestrator following SOLID principles.

Single Responsibility: Coordinates all hook operations through sub-orchestrators.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class MainOrchestrator:
    """Main orchestrator that coordinates all hook operations."""

    def __init__(self):
        """Initialize main orchestrator with sub-orchestrators."""
        try:
            from operations.logging.logger import logger
        except (ImportError, ValueError):
            # Fallback if relative import fails
            import sys
            from pathlib import Path

            hooks_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(hooks_dir))
            from operations.logging.logger import logger

        self.logger = logger

        # Initialize path resolver
        try:
            from utils.path_resolver import PathResolver
        except (ImportError, ValueError):
            import sys
            from pathlib import Path

            hooks_dir = Path(__file__).parent.parent
            if str(hooks_dir) not in sys.path:
                sys.path.insert(0, str(hooks_dir))
            from utils.path_resolver import PathResolver

        self.path_resolver = PathResolver()

        # Initialize sub-orchestrators (lazy loading)
        self._quality_orchestrator = None
        self._cleanup_orchestrator = None
        self._remediation_orchestrator = None
        self._sdk_client = None

    @property
    def quality_orchestrator(self):
        """Lazy load quality orchestrator."""
        if self._quality_orchestrator is None:
            from .quality_orchestrator import QualityOrchestrator

            self._quality_orchestrator = QualityOrchestrator()
        return self._quality_orchestrator

    @property
    def cleanup_orchestrator(self):
        """Lazy load cleanup orchestrator."""
        if self._cleanup_orchestrator is None:
            from .cleanup_orchestrator import CleanupOrchestrator

            self._cleanup_orchestrator = CleanupOrchestrator()
        return self._cleanup_orchestrator

    @property
    def remediation_orchestrator(self):
        """Lazy load remediation orchestrator."""
        if self._remediation_orchestrator is None:
            from .remediation_orchestrator import RemediationOrchestrator

            self._remediation_orchestrator = RemediationOrchestrator()
        return self._remediation_orchestrator

    @property
    def sdk_client(self):
        """Lazy load Claude SDK client."""
        if self._sdk_client is None:
            try:
                from claude_sdk.client.sdk_initializer import SDKInitializer
            except (ImportError, ValueError):
                import sys
                from pathlib import Path

                hooks_dir = Path(__file__).parent.parent
                if str(hooks_dir) not in sys.path:
                    sys.path.insert(0, str(hooks_dir))
                from claude_sdk.client.sdk_initializer import SDKInitializer

            initializer = SDKInitializer()
            self._sdk_client = initializer.initialize()
        return self._sdk_client

    def handle_post_tool_use(
        self,
        tool_name: str,
        tool_result: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Handle PostToolUse hook event.

        Args:
            tool_name: Name of the tool that was used
            tool_result: Result from the tool
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Handling PostToolUse for tool: {tool_name}")

        results: Dict[str, Any] = {
            "hook": "PostToolUse",
            "tool": tool_name,
            "operations": [],
        }

        try:
            # Check if this is a file editing tool
            file_edit_tools = ["Edit", "MultiEdit", "Write", "edit_file"]
            if tool_name in file_edit_tools:
                # Extract file paths from tool result
                file_paths = self._extract_file_paths(tool_result, context)

                if file_paths:
                    # Run Unicode cleanup on edited files
                    cleanup_result = self.cleanup_orchestrator.cleanup_files(file_paths)
                    results["operations"].append(
                        {
                            "type": "unicode_cleanup",
                            "result": cleanup_result,
                        }
                    )

                    # Run quality check on edited files
                    quality_result = self.quality_orchestrator.check_files(file_paths)
                    results["operations"].append(
                        {
                            "type": "quality_check",
                            "result": quality_result,
                        }
                    )

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in PostToolUse handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_subagent_stop(
        self, agent_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle SubagentStop hook event.

        Args:
            agent_name: Name of the sub-agent that stopped
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Handling SubagentStop for agent: {agent_name or 'unknown'}")

        results: Dict[str, Any] = {
            "hook": "SubagentStop",
            "agent": agent_name,
            "operations": [],
        }

        try:
            # Run quality check on entire project
            quality_result = self.quality_orchestrator.check_project()
            results["operations"].append(
                {
                    "type": "project_quality_check",
                    "result": quality_result,
                }
            )

            # Check if remediation is needed
            if quality_result.get("issues_found", 0) > 0:
                # Trigger remediation if issues found
                remediation_result = self.remediation_orchestrator.remediate(
                    quality_report=quality_result
                )
                results["operations"].append(
                    {
                        "type": "remediation",
                        "result": remediation_result,
                    }
                )

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in SubagentStop handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_stop(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Stop hook event (session end).

        Args:
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info("Handling Stop hook (session end)")

        results: Dict[str, Any] = {
            "hook": "Stop",
            "operations": [],
        }

        try:
            # Run final quality check
            quality_result = self.quality_orchestrator.check_project(final_check=True)
            results["operations"].append(
                {
                    "type": "final_quality_check",
                    "result": quality_result,
                }
            )

            # Run final cleanup
            cleanup_result = self.cleanup_orchestrator.final_cleanup()
            results["operations"].append(
                {
                    "type": "final_cleanup",
                    "result": cleanup_result,
                }
            )

            # Generate session summary
            summary = self._generate_session_summary(results["operations"])
            results["summary"] = summary

            # Log session summary
            self.logger.section("Session Summary")
            self.logger.dict_log(summary)

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in Stop handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        finally:
            # Cleanup resources
            self._cleanup_resources()

        return results

    def _extract_paths_from_context(
        self, context: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """Extract file paths from context dictionary.

        Args:
            context: Additional context dictionary

        Returns:
            List of file paths from context
        """
        file_paths = []

        if context and "file_paths" in context:
            paths = context["file_paths"]
            if isinstance(paths, list):
                file_paths.extend([Path(p) for p in paths])
            elif isinstance(paths, str):
                file_paths.append(Path(paths))

        return file_paths

    def _extract_paths_from_tool_result(self, tool_result: str) -> List[Path]:
        """Extract file paths from tool result using regex parsing.

        Args:
            tool_result: Tool execution result

        Returns:
            List of file paths found in tool result
        """
        import re

        file_paths = []

        # Look for file paths in the result
        path_pattern = r"(?:File |path:|modified:|created:)\s*([^\s]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))"
        matches = re.findall(path_pattern, tool_result, re.IGNORECASE)

        for match in matches:
            validated_path = self._validate_file_path(match)
            if validated_path:
                file_paths.append(validated_path)

        return file_paths

    def _validate_file_path(self, path_str: str) -> Optional[Path]:
        """Validate and return a file path if it exists.

        Args:
            path_str: String representation of file path

        Returns:
            Path object if valid and exists, None otherwise
        """
        try:
            path = Path(path_str)
            if path.exists():
                return path
        except Exception:
            pass
        return None

    def _extract_file_paths(
        self, tool_result: Optional[str], context: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """Extract file paths from tool result.

        Args:
            tool_result: Tool execution result
            context: Additional context

        Returns:
            List of file paths that were edited
        """
        # Try to extract from context first
        file_paths = self._extract_paths_from_context(context)

        # Try to parse from tool result if no paths from context
        if tool_result and not file_paths:
            file_paths = self._extract_paths_from_tool_result(tool_result)

        return file_paths

    def _generate_session_summary(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of session operations.

        Args:
            operations: List of operations performed

        Returns:
            Summary dictionary
        """
        summary = {
            "total_operations": len(operations),
            "successful_operations": 0,
            "failed_operations": 0,
            "quality_issues_found": 0,
            "quality_issues_fixed": 0,
            "files_cleaned": 0,
            "files_checked": 0,
        }

        for op in operations:
            result = op.get("result", {})
            if result.get("success", False):
                summary["successful_operations"] += 1
            else:
                summary["failed_operations"] += 1

            # Aggregate specific metrics
            if op["type"] in [
                "quality_check",
                "project_quality_check",
                "final_quality_check",
            ]:
                summary["quality_issues_found"] += result.get("issues_found", 0)
                summary["files_checked"] += result.get("files_checked", 0)

            if op["type"] == "remediation":
                summary["quality_issues_fixed"] += result.get("issues_fixed", 0)

            if op["type"] in ["unicode_cleanup", "final_cleanup"]:
                summary["files_cleaned"] += result.get("files_cleaned", 0)

        return summary

    def _cleanup_resources(self):
        """Cleanup resources at session end."""
        try:
            # Shutdown SDK client if initialized
            if self._sdk_client:
                from claude_sdk.client.sdk_initializer import SDKInitializer

                initializer = SDKInitializer()
                initializer.client = self._sdk_client
                initializer.shutdown()
                self._sdk_client = None

            self.logger.debug("Resources cleaned up successfully")

        except Exception as e:
            self.logger.warning(f"Error during resource cleanup: {e}")
