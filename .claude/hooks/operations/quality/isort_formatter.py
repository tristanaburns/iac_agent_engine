"""isort import formatter operations following SOLID principles.

Single Responsibility: Only handles isort import formatting.
"""

from pathlib import Path
from typing import Any, Dict


class IsortFormatter:
    """Handles isort import sorting operations."""

    def __init__(self, profile: str = "black"):
        """Initialize with isort configuration."""
        self.profile = profile
        self.command_name = "isort"

    def format_imports(
        self,
        target_path: Path,
        check_only: bool = False,
    ) -> Dict[str, Any]:
        """Run isort import formatter on files.

        Args:
            target_path: Path to format (file or directory)
            check_only: Only check, don't modify files

        Returns:
            Dictionary with formatting results
        """
        from utils.process_runner import ProcessRunner

        runner = ProcessRunner(
            working_dir=target_path.parent if target_path.is_file() else target_path
        )

        # Build and execute command
        command = self._build_command(target_path, check_only)
        result = runner.run_command(command, timeout=60)

        # Parse results based on mode
        if check_only:
            formatted_files, needs_formatting = self._parse_check_results(result)
        else:
            formatted_files = self._parse_format_results(result)
            needs_formatting = False

        # Handle errors
        errors = self._handle_errors(result, check_only)

        return {
            "formatter": "isort",
            "status": "success" if result["success"] or check_only else "failed",
            "files_formatted": formatted_files,
            "needs_formatting": needs_formatting,
            "errors": errors,
            "command": result["command"],
            "profile": self.profile,
        }

    def _build_command(self, target_path: Path, check_only: bool) -> list[str]:
        """Build isort command with appropriate flags.

        Args:
            target_path: Path to process
            check_only: Whether to only check formatting

        Returns:
            Command list ready for execution
        """
        command = ["python", "-m", "isort", "--profile", self.profile]

        if check_only:
            command.extend(["--check-only", "--diff"])

        command.append(str(target_path))
        return command

    def _parse_check_results(self, result: Dict[str, Any]) -> tuple[list[str], bool]:
        """Parse isort check mode results.

        Args:
            result: Command execution result

        Returns:
            Tuple of (formatted_files, needs_formatting)
        """
        needs_formatting = not result["success"]
        formatted_files = self._extract_files_from_diff(result.get("stdout", ""))
        return formatted_files, needs_formatting

    def _extract_files_from_diff(self, stdout: str) -> list[str]:
        """Extract file paths from diff output.

        Args:
            stdout: Command output containing diff

        Returns:
            List of file paths that need formatting
        """
        formatted_files = []

        if stdout:
            for line in stdout.split("\n"):
                if self._is_diff_header_line(line):
                    file_path = line[4:].strip()
                    if file_path and file_path not in formatted_files:
                        formatted_files.append(file_path)

        return formatted_files

    def _is_diff_header_line(self, line: str) -> bool:
        """Check if line is a diff header line.

        Args:
            line: Line from diff output

        Returns:
            True if line starts with --- or +++
        """
        return line.startswith("---") or line.startswith("+++")

    def _parse_format_results(self, result: Dict[str, Any]) -> list[str]:
        """Parse isort format mode results.

        Args:
            result: Command execution result

        Returns:
            List of files that were formatted
        """
        formatted_files = []

        if result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "Fixing" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".py"):
                            formatted_files.append(part)

        return formatted_files

    def _handle_errors(self, result: Dict[str, Any], check_only: bool) -> list[str]:
        """Handle and format error messages.

        Args:
            result: Command execution result
            check_only: Whether this was a check-only operation

        Returns:
            List of error messages
        """
        errors = []

        if not result["success"] and not check_only:
            errors.append(result.get("error", "isort formatting failed"))
            if result["stderr"]:
                errors.extend(result["stderr"].split("\n"))

        return errors
