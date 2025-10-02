"""Black formatter operations following SOLID principles.

Single Responsibility: Only handles Black formatting.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class BlackFormatter:
    """Handles Black code formatting operations."""

    def __init__(self, line_length: int = 88):
        """Initialize with Black configuration."""
        self.line_length = line_length
        self.command_name = "black"

    def format_files(
        self,
        target_path: Path,
        file_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run Black formatter on files.

        Args:
            target_path: Path to format (file or directory)
            file_patterns: Optional file patterns to include

        Returns:
            Dictionary with formatting results
        """
        runner = self._create_process_runner(target_path)
        command = self._build_format_command(target_path, file_patterns)
        result = runner.run_command(command, timeout=120)

        formatted_files, errors = self._parse_format_results(result)

        return self._create_format_result_dict(result, formatted_files, errors, command)

    def _create_process_runner(self, target_path: Path):
        """Create process runner with appropriate working directory.

        Args:
            target_path: Target path for formatting

        Returns:
            ProcessRunner instance
        """
        from utils.process_runner import ProcessRunner

        working_dir = target_path.parent if target_path.is_file() else target_path
        return ProcessRunner(working_dir=working_dir)

    def _build_format_command(
        self, target_path: Path, file_patterns: Optional[List[str]]
    ) -> List[str]:
        """Build the Black formatting command.

        Args:
            target_path: Path to format
            file_patterns: Optional file patterns to include

        Returns:
            Command list for Black formatter
        """
        command = [
            "python",
            "-m",
            "black",
            "--line-length",
            str(self.line_length),
        ]

        # Add file patterns if specified
        if file_patterns:
            self._add_file_patterns_to_command(command, file_patterns)

        # Add target
        command.append(str(target_path))
        return command

    def _add_file_patterns_to_command(
        self, command: List[str], file_patterns: List[str]
    ) -> None:
        """Add file patterns to the command.

        Args:
            command: Command list to modify
            file_patterns: File patterns to add
        """
        for pattern in file_patterns:
            command.extend(["--include", pattern])

    def _parse_format_results(
        self, result: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """Parse formatting results from Black output.

        Args:
            result: Result from process execution

        Returns:
            Tuple of (formatted_files, errors)
        """
        if result["success"]:
            return self._extract_formatted_files(result), []
        else:
            return [], self._extract_error_messages(result)

    def _extract_formatted_files(self, result: Dict[str, Any]) -> List[str]:
        """Extract list of formatted files from stdout.

        Args:
            result: Result from process execution

        Returns:
            List of formatted file paths
        """
        formatted_files = []
        if result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "reformatted" in line.lower():
                    # Extract file path from output
                    parts = line.split()
                    if parts:
                        formatted_files.append(parts[0])
        return formatted_files

    def _extract_error_messages(self, result: Dict[str, Any]) -> List[str]:
        """Extract error messages from failed execution.

        Args:
            result: Result from process execution

        Returns:
            List of error messages
        """
        errors = [result.get("error", "Black formatting failed")]
        if result["stderr"]:
            errors.extend(result["stderr"].split("\n"))
        return errors

    def _create_format_result_dict(
        self,
        result: Dict[str, Any],
        formatted_files: List[str],
        errors: List[str],
        command: List[str],
    ) -> Dict[str, Any]:
        """Create the final result dictionary.

        Args:
            result: Process execution result
            formatted_files: List of formatted files
            errors: List of error messages
            command: Command that was executed

        Returns:
            Complete result dictionary
        """
        return {
            "formatter": "black",
            "status": "success" if result["success"] else "failed",
            "files_formatted": formatted_files,
            "errors": errors,
            "command": result["command"],
            "line_length": self.line_length,
        }

    def check_only(self, target_path: Path) -> Dict[str, Any]:
        """Check if files would be reformatted without modifying them.

        Args:
            target_path: Path to check

        Returns:
            Dictionary with check results
        """
        from utils.process_runner import ProcessRunner

        runner = ProcessRunner(
            working_dir=target_path.parent if target_path.is_file() else target_path
        )

        command = [
            "python",
            "-m",
            "black",
            "--check",
            "--line-length",
            str(self.line_length),
            str(target_path),
        ]

        result = runner.run_command(command)

        files_need_formatting = []
        if not result["success"] and result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "would be reformatted" in line.lower():
                    parts = line.split()
                    if parts:
                        files_need_formatting.append(parts[0])

        return {
            "formatter": "black",
            "needs_formatting": len(files_need_formatting) > 0,
            "files": files_need_formatting,
            "line_length": self.line_length,
        }

    def format_string(self, code: str) -> str:
        """Format a string of Python code.

        Args:
            code: Python code string to format

        Returns:
            Formatted code string
        """
        try:
            import black

            return black.format_str(code, mode=black.Mode(line_length=self.line_length))
        except ImportError:
            # If Black not available as library, use subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)

            try:
                result = self.format_files(temp_path)
                if result["status"] == "success":
                    return temp_path.read_text(encoding="utf-8")
                return code
            finally:
                temp_path.unlink()
