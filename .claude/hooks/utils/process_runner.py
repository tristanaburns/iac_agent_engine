"""Process execution utilities following SOLID principles.

Single Responsibility: Only handles subprocess execution.
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProcessRunner:
    """Runs external processes with consistent error handling."""

    def __init__(self, working_dir: Optional[Path] = None, timeout: int = 60):
        """Initialize with working directory and default timeout."""
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.default_timeout = timeout

    def _initialize_result_dict(self, command: List[str]) -> Dict[str, Any]:
        """Initialize result dictionary with default values.

        Args:
            command: Command and arguments as list

        Returns:
            Dictionary with initialized default values
        """
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "error": None,
            "command": " ".join(command),
        }

    def _execute_subprocess(
        self, command: List[str], timeout: int, capture_output: bool, check: bool
    ) -> subprocess.CompletedProcess:
        """Execute subprocess with given parameters.

        Args:
            command: Command and arguments as list
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero exit code

        Returns:
            CompletedProcess instance

        Raises:
            subprocess.TimeoutExpired: If command times out
            subprocess.CalledProcessError: If command fails and check=True
            FileNotFoundError: If command not found
        """
        return subprocess.run(
            command,
            cwd=self.working_dir,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=check,
        )

    def _handle_timeout_exception(
        self, result: Dict[str, Any], e: subprocess.TimeoutExpired, timeout: int
    ) -> None:
        """Handle subprocess timeout exceptions.

        Args:
            result: Result dictionary to update
            e: TimeoutExpired exception
            timeout: Timeout value that was exceeded
        """
        result["error"] = f"Command timed out after {timeout} seconds"
        if hasattr(e, "stdout") and e.stdout:
            result["stdout"] = e.stdout.decode("utf-8", errors="ignore")
        if hasattr(e, "stderr") and e.stderr:
            result["stderr"] = e.stderr.decode("utf-8", errors="ignore")

    def _handle_process_exception(
        self, result: Dict[str, Any], e: subprocess.CalledProcessError
    ) -> None:
        """Handle subprocess CalledProcessError exceptions.

        Args:
            result: Result dictionary to update
            e: CalledProcessError exception
        """
        result["error"] = f"Command failed with exit code {e.returncode}"
        result["returncode"] = e.returncode
        if hasattr(e, "stdout") and e.stdout:
            result["stdout"] = e.stdout
        if hasattr(e, "stderr") and e.stderr:
            result["stderr"] = e.stderr

    def _handle_generic_exceptions(
        self, result: Dict[str, Any], e: Exception, command: List[str]
    ) -> None:
        """Handle generic exceptions (FileNotFoundError and others).

        Args:
            result: Result dictionary to update
            e: Exception that occurred
            command: Command that was attempted
        """
        if isinstance(e, FileNotFoundError):
            result["error"] = f"Command not found: {command[0]}"
        else:
            result["error"] = f"Unexpected error: {str(e)}"

    def run_command(
        self,
        command: List[str],
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = False,
    ) -> Dict[str, Any]:
        """Run a command and return structured result.

        Args:
            command: Command and arguments as list
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero exit code

        Returns:
            Dictionary with keys:
                - success: Boolean indicating success
                - returncode: Process return code
                - stdout: Captured stdout (if capture_output=True)
                - stderr: Captured stderr (if capture_output=True)
                - error: Error message if failed
        """
        # Use default timeout if none provided
        effective_timeout = timeout if timeout is not None else self.default_timeout

        # Initialize result dictionary with default values
        result = self._initialize_result_dict(command)

        try:
            # Execute the subprocess
            process = self._execute_subprocess(
                command, effective_timeout, capture_output, check
            )

            # Update result with successful execution data
            result["success"] = process.returncode == 0
            result["returncode"] = process.returncode
            if capture_output:
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr

        except subprocess.TimeoutExpired as e:
            self._handle_timeout_exception(result, e, effective_timeout)

        except subprocess.CalledProcessError as e:
            self._handle_process_exception(result, e)

        except (FileNotFoundError, Exception) as e:
            self._handle_generic_exceptions(result, e, command)

        return result

    def run_python_module(
        self,
        module: str,
        args: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run a Python module with arguments."""
        command = ["python", "-m", module]
        if args:
            command.extend(args)
        return self.run_command(command, timeout=timeout)

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", command],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_with_retry(
        self,
        command: List[str],
        max_retries: int = 3,
        retry_delay: int = 1,
    ) -> Dict[str, Any]:
        """Run command with retry logic."""
        import time

        for attempt in range(max_retries):
            result = self.run_command(command)
            if result["success"]:
                return result

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        return result
