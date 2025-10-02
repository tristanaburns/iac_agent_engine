"""Orchestrator - direct coordination of all operations."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from cleanup_operations import CleanupOperations
from operations.logging.logger import logger
from path_resolver import PathResolver
from process_runner import ProcessRunner
from quality_operations import QualityOperations


class Orchestrator:
    """Direct orchestrator for all operations."""

    def __init__(self):
        """Initialize with direct dependencies."""
        self.path_resolver = PathResolver()
        self.quality_ops = QualityOperations()
        self.cleanup_ops = CleanupOperations()
        self.process_runner = ProcessRunner()
        logger.info("Orchestrator initialized")

    def handle_post_tool_use(
        self,
        tool_name: str,
        tool_result: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Handle file edits - run cleanup and quality checks."""
        logger.info(f"Handling PostToolUse for: {tool_name}")

        results: Dict[str, Any] = {"tool": tool_name, "operations": [], "success": True}

        try:
            # Only process file editing tools
            if tool_name in ["Edit", "MultiEdit", "Write", "edit_file"]:
                file_paths = self._extract_file_paths(tool_result, context)

                if file_paths:
                    # Run unicode cleanup
                    for file_path in file_paths:
                        cleanup_result = self.cleanup_ops.clean_unicode_in_file(
                            file_path
                        )
                        if cleanup_result.get("modified"):
                            logger.info(f"Unicode cleaned: {file_path.name}")

                    # Run quality check
                    quality_result = self.quality_ops.check_quality(
                        file_paths[0].parent
                    )
                    if quality_result.get("needs_formatting"):
                        format_result = self.quality_ops.format_python_files(
                            file_paths[0].parent
                        )
                        results["operations"].append(
                            {"type": "format", "result": format_result}
                        )

        except Exception as e:
            logger.error(f"PostToolUse error: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_subagent_stop(
        self, agent_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle subagent stop - run project-wide quality check."""
        logger.info(f"Handling SubagentStop for: {agent_name or 'unknown'}")

        results: Dict[str, Any] = {
            "agent": agent_name,
            "operations": [],
            "success": True,
        }

        try:
            # Run quality check on current directory
            project_dir = self.path_resolver.project_dir
            quality_result = self.quality_ops.check_quality(project_dir)

            if quality_result.get("needs_formatting"):
                logger.info("Running quality formatting on project")
                format_result = self.quality_ops.format_python_files(project_dir)
                results["operations"].append(
                    {"type": "project_format", "result": format_result}
                )

        except Exception as e:
            logger.error(f"SubagentStop error: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_stop(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle session stop - final cleanup and summary."""
        logger.info("Handling session stop")

        results: Dict[str, Any] = {"operations": [], "success": True}

        try:
            # Final unicode cleanup of session files
            cleanup_result = self.cleanup_ops.clean_session_files()
            if cleanup_result["files_modified"] > 0:
                logger.info(
                    f"Final cleanup: {cleanup_result['files_modified']} files cleaned"
                )

            # Final quality check
            project_dir = self.path_resolver.project_dir
            quality_result = self.quality_ops.check_quality(project_dir)

            if quality_result.get("needs_formatting"):
                format_result = self.quality_ops.format_python_files(project_dir)
                results["operations"].append(
                    {"type": "final_format", "result": format_result}
                )

            # Git cleanup
            git_result = self.cleanup_ops.run_git_cleanup(project_dir)
            results["operations"].append({"type": "git_cleanup", "result": git_result})

            logger.info("Session completed successfully")

        except Exception as e:
            logger.error(f"Stop error: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def _extract_file_paths(
        self, tool_result: Optional[str], context: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """Extract file paths from tool result or context."""
        file_paths = []

        # Check context first
        context_paths = self._extract_paths_from_context(context)
        file_paths.extend(context_paths)

        # Parse from tool result if no context paths found
        if tool_result and not file_paths:
            result_paths = self._extract_paths_from_tool_result(tool_result)
            file_paths.extend(result_paths)

        return file_paths

    def _extract_paths_from_context(
        self, context: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """Extract file paths from context dictionary.

        Args:
            context: Context dictionary that may contain file paths

        Returns:
            List of valid Path objects from context
        """
        file_paths: list[Path] = []

        if not context or "file_paths" not in context:
            return file_paths

        paths = context["file_paths"]
        if isinstance(paths, list):
            file_paths.extend([Path(p) for p in paths if Path(p).exists()])
        elif isinstance(paths, str) and Path(paths).exists():
            file_paths.append(Path(paths))

        return file_paths

    def _extract_paths_from_tool_result(self, tool_result: str) -> List[Path]:
        """Extract file paths from tool result using regex.

        Args:
            tool_result: Tool execution result text

        Returns:
            List of valid Path objects found in tool result
        """
        file_paths = []

        pattern = (
            r"(?:File |path:|modified:|created:)\s*"
            r"([^\s]+\.(?:py|js|ts|md|txt|json|yaml|yml))"
        )
        matches = re.findall(pattern, tool_result, re.IGNORECASE)

        for match in matches:
            path = Path(match)
            if path.exists():
                file_paths.append(path)

        return file_paths
