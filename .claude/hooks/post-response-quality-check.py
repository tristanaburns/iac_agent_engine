#!/usr/bin/env python3
"""
Claude Code Stop Hook - Post-Response Quality Check.

Runs automatic code quality checks after each Claude response.
"""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add tools directory to Python path for unicode_manager import
sys.path.insert(0, str(Path(__file__).parent / "tools"))

try:
    from tools.unicode_manager import UnicodeManager

    unicode_manager_class: Optional[type] = UnicodeManager
except ImportError:
    unicode_manager_class = None


def log_message(message, level="INFO", project_dir=None):
    """Log a message with timestamp to both console and log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{level}] {message}"

    # Also write to log file
    if project_dir is None:
        project_dir = Path.cwd()
    log_file = (
        Path(project_dir) / ".claude" / "hooks" / "quality-checks" / "hooks-trigger.log"
    )
    log_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception:
        pass  # Silent fail if can't write log

    return formatted_msg


def _find_recently_modified_python_files(project_dir, minutes=5):
    """Find Python files that have been modified recently."""
    current_time = time.time()
    cutoff_time = current_time - (minutes * 60)  # Convert minutes to seconds

    python_files = []
    for pattern in ["**/*.py"]:
        for file_path in Path(project_dir).glob(pattern):
            try:
                if file_path.stat().st_mtime > cutoff_time:
                    python_files.append(file_path)
            except (OSError, FileNotFoundError):
                continue

    return python_files


def _run_black_check(python_files, project_dir):
    """Run Black formatter check on the provided files."""
    check_cmd = ["python", "-m", "black", "--check", "--diff"] + [
        str(f) for f in python_files
    ]
    return subprocess.run(
        check_cmd, capture_output=True, text=True, cwd=project_dir, timeout=60
    )


def _process_black_check_result(check_result, python_files):
    """Process the result of Black check command and return summary."""
    file_count = len(python_files)

    if check_result.returncode == 0:
        summary = (
            f"All {file_count} recently modified Python files are "
            f"already formatted correctly"
        )
        files_formatted = []
    else:
        summary = f"Found {file_count} recently modified files that need formatting"
        files_formatted = check_result.stdout.split("\n") if check_result.stdout else []

    return summary, files_formatted


def run_black_formatter(project_dir):
    """Run Black formatter on Python files."""
    results = {
        "formatter": "black",
        "status": "success",
        "files_formatted": [],
        "errors": [],
        "summary": "",
    }

    try:
        # Find recently modified Python files
        python_files = _find_recently_modified_python_files(project_dir)

        # Guard clause: No files to process
        if not python_files:
            results["summary"] = "No recently modified Python files found"
            return results

        # Run Black check and process results
        check_result = _run_black_check(python_files, project_dir)
        summary, files_formatted = _process_black_check_result(
            check_result, python_files
        )

        results["summary"] = summary
        results["files_formatted"] = files_formatted

    except subprocess.TimeoutExpired:
        results["status"] = "timeout"
        results["errors"].append("Black formatter timed out")
        results["summary"] = "Formatter operation timed out"
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
        results["summary"] = f"Error running formatter: {str(e)}"

    return results


def _run_validation_command(
    command: list, file_path: str, project_dir: str, timeout: int = 10
) -> tuple:
    """Generic subprocess execution with consistent error handling for validation commands.

    Args:
        command: Command list to execute
        file_path: File path being validated
        project_dir: Project directory for execution context
        timeout: Command timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr, exception)
    """
    log_message(
        f"DEBUG: Executing validation command: {' '.join(command)}",
        "DEBUG",
        project_dir,
    )

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=project_dir,
            timeout=timeout,
        )
        log_message(
            f"DEBUG: Command completed with returncode: {result.returncode}",
            "DEBUG",
            project_dir,
        )
        return result.returncode, result.stdout, result.stderr, None
    except subprocess.TimeoutExpired as e:
        log_message(
            f"ERROR: Command timed out after {timeout}s: {' '.join(command)}",
            "ERROR",
            project_dir,
        )
        return -1, "", f"Command timed out after {timeout}s", e
    except Exception as e:
        log_message(
            f"ERROR: Command execution failed: {' '.join(command)} - {str(e)}",
            "ERROR",
            project_dir,
        )
        return -1, "", str(e), e


def _validate_compilation(file_path: Path, project_dir: str) -> dict:
    """Validate Python file compilation using py_compile.

    Args:
        file_path: Path to the Python file to validate
        project_dir: Project directory for execution context

    Returns:
        Dictionary with compilation validation results
    """
    log_message(
        f"DEBUG: Starting compilation validation for: {file_path}", "DEBUG", project_dir
    )

    command = ["python", "-m", "py_compile", str(file_path)]
    returncode, stdout, stderr, exception = _run_validation_command(
        command, str(file_path), project_dir
    )

    if returncode == 0:
        log_message(
            f"DEBUG: Compilation validation successful for: {file_path}",
            "DEBUG",
            project_dir,
        )
        return {"status": "success", "error": None}
    else:
        log_message(
            f"ERROR: Compilation validation failed for: {file_path} - {stderr}",
            "ERROR",
            project_dir,
        )
        return {"status": "failed", "error": stderr}


def _validate_linting(file_path: Path, project_dir: str) -> dict:
    """Validate Python file linting using flake8.

    Args:
        file_path: Path to the Python file to validate
        project_dir: Project directory for execution context

    Returns:
        Dictionary with linting validation results
    """
    log_message(
        f"DEBUG: Starting linting validation for: {file_path}", "DEBUG", project_dir
    )

    command = ["python", "-m", "flake8", "--max-line-length=88", str(file_path)]
    returncode, stdout, stderr, exception = _run_validation_command(
        command, str(file_path), project_dir
    )

    if returncode == 0:
        log_message(
            f"DEBUG: Linting validation successful for: {file_path}",
            "DEBUG",
            project_dir,
        )
        return {"status": "success", "output": None}
    else:
        log_message(
            f"WARNING: Linting issues found for: {file_path}", "WARNING", project_dir
        )
        return {"status": "issues_found", "output": stdout if stdout else None}


def _validate_type_checking(file_path: Path, project_dir: str) -> dict:
    """Validate Python file type checking using mypy.

    Args:
        file_path: Path to the Python file to validate
        project_dir: Project directory for execution context

    Returns:
        Dictionary with type checking validation results
    """
    log_message(
        f"DEBUG: Starting type checking validation for: {file_path}",
        "DEBUG",
        project_dir,
    )

    command = ["python", "-m", "mypy", "--ignore-missing-imports", str(file_path)]
    returncode, stdout, stderr, exception = _run_validation_command(
        command, str(file_path), project_dir
    )

    if returncode == 0:
        log_message(
            f"DEBUG: Type checking validation successful for: {file_path}",
            "DEBUG",
            project_dir,
        )
        return {"status": "success", "output": None}
    else:
        log_message(
            f"WARNING: Type checking issues found for: {file_path}",
            "WARNING",
            project_dir,
        )
        return {"status": "issues_found", "output": stdout if stdout else None}


def _validate_and_format_code(file_path: Path, project_dir: str) -> dict:
    """Validate and auto-format Python file using Black.

    Args:
        file_path: Path to the Python file to validate and format
        project_dir: Project directory for execution context

    Returns:
        Dictionary with formatting validation results
    """
    log_message(
        f"DEBUG: Starting format validation for: {file_path}", "DEBUG", project_dir
    )

    # First check if formatting is needed
    check_command = [
        "python",
        "-m",
        "black",
        "--check",
        "--line-length=88",
        str(file_path),
    ]
    returncode, stdout, stderr, exception = _run_validation_command(
        check_command, str(file_path), project_dir
    )

    if returncode == 0:
        log_message(
            f"DEBUG: File already properly formatted: {file_path}", "DEBUG", project_dir
        )
        return {"status": "success"}
    else:
        # Auto-format the file
        log_message(f"INFO: Auto-formatting file: {file_path}", "INFO", project_dir)
        format_command = ["python", "-m", "black", "--line-length=88", str(file_path)]
        format_returncode, format_stdout, format_stderr, format_exception = (
            _run_validation_command(format_command, str(file_path), project_dir)
        )

        if format_returncode == 0:
            log_message(
                f"INFO: File auto-formatted successfully: {file_path}",
                "INFO",
                project_dir,
            )
            return {
                "status": "auto_formatted",
                "message": "File was automatically formatted",
            }
        else:
            log_message(
                f"ERROR: Auto-formatting failed for: {file_path} - {format_stderr}",
                "ERROR",
                project_dir,
            )
            return {"status": "error", "error": format_stderr}


def run_post_cleanup_validation(file_path: Path, project_dir: str) -> dict:
    """Run validation checks on a file after unicode cleanup.

    Performs: lint, typecheck, format, and compile checks using extracted helper functions.

    Args:
        file_path: Path to the file to validate
        project_dir: Project directory

    Returns:
        Dictionary with validation results
    """
    log_message(
        f"DEBUG: Starting post-cleanup validation for: {file_path}",
        "DEBUG",
        project_dir,
    )

    # Initialize results structure
    results: Dict[str, Any] = {
        "file": str(file_path),
        "lint": {"status": "skipped"},
        "typecheck": {"status": "skipped"},
        "format": {"status": "skipped"},
        "compile": {"status": "skipped"},
        "success": True,
    }

    # Skip non-Python files
    if file_path.suffix != ".py":
        log_message(
            f"DEBUG: Skipping non-Python file: {file_path}", "DEBUG", project_dir
        )
        return results

    log_message(
        f"DEBUG: Processing Python file validation: {file_path}", "DEBUG", project_dir
    )

    # 1. Compilation validation
    results["compile"] = _validate_compilation(file_path, project_dir)
    if results["compile"]["status"] == "failed":
        results["success"] = False

    # 2. Linting validation
    results["lint"] = _validate_linting(file_path, project_dir)

    # 3. Type checking validation
    results["typecheck"] = _validate_type_checking(file_path, project_dir)

    # 4. Formatting validation with auto-format
    results["format"] = _validate_and_format_code(file_path, project_dir)

    log_message(
        f"DEBUG: Validation completed for: {file_path} - Success: {results['success']}",
        "DEBUG",
        project_dir,
    )
    return results


def _find_recently_modified_files(project_dir, time_window_minutes=5):
    """Find Python files modified within the specified time window.

    Args:
        project_dir: Project directory to search
        time_window_minutes: Time window in minutes for "recent" files

    Returns:
        List of Path objects for recently modified Python files
    """
    log_message(
        f"DEBUG: Searching for files modified in last {time_window_minutes} minutes",
        "DEBUG",
        project_dir,
    )

    current_time = time.time()
    cutoff_time = current_time - (time_window_minutes * 60)
    recent_files = []

    for pattern in ["**/*.py"]:
        log_message(
            f"DEBUG: Scanning pattern {pattern} in {project_dir}", "DEBUG", project_dir
        )
        for file_path in Path(project_dir).glob(pattern):
            try:
                if file_path.stat().st_mtime > cutoff_time:
                    recent_files.append(file_path)
                    log_message(
                        f"DEBUG: Found recent file: {file_path}", "DEBUG", project_dir
                    )
            except (OSError, FileNotFoundError) as e:
                log_message(
                    f"DEBUG: Skipping inaccessible file {file_path}: {e}",
                    "DEBUG",
                    project_dir,
                )
                continue

    log_message(
        f"DEBUG: Found {len(recent_files)} recently modified Python files",
        "DEBUG",
        project_dir,
    )
    return recent_files


def _process_unicode_in_files(recent_files, project_dir):
    """Process unicode cleanup in the provided files with comprehensive logging.

    Args:
        recent_files: List of Path objects to process
        project_dir: Project directory for logging context

    Returns:
        Dictionary with processing results
    """
    log_message(
        f"DEBUG: Starting unicode processing on {len(recent_files)} files",
        "DEBUG",
        project_dir,
    )

    processing_results = {
        "files_cleaned": 0,
        "unicode_replaced": 0,
        "errors": [],
        "cleaned_files": [],
    }

    try:
        unicode_manager = unicode_manager_class(mode="delete")
        log_message(
            "DEBUG: Unicode manager initialized in delete mode", "DEBUG", project_dir
        )

        for file_path in recent_files:
            log_message(f"DEBUG: Processing file: {file_path}", "DEBUG", project_dir)
            try:
                result = unicode_manager.process_file(file_path)

                if result["processed"] and result["modified"]:
                    processing_results["files_cleaned"] += 1
                    processing_results["cleaned_files"].append(Path(file_path))
                    log_message(
                        f"DEBUG: File cleaned: {file_path}", "DEBUG", project_dir
                    )

                    # Handle both delete and replace modes
                    if "unicode_deleted" in result:
                        unicode_count = result["unicode_deleted"]
                        processing_results["unicode_replaced"] += unicode_count
                        log_message(
                            f"DEBUG: Deleted {unicode_count} unicode chars from "
                            f"{file_path}",
                            "DEBUG",
                            project_dir,
                        )
                    elif "unicode_replaced" in result:
                        unicode_count = result["unicode_replaced"]
                        processing_results["unicode_replaced"] += unicode_count
                        log_message(
                            f"DEBUG: Replaced {unicode_count} unicode chars in "
                            f"{file_path}",
                            "DEBUG",
                            project_dir,
                        )

                elif result["error"] and "excluded" not in result["error"]:
                    error_msg = f"{file_path}: {result['error']}"
                    processing_results["errors"].append(error_msg)
                    log_message(
                        f"DEBUG: Processing error: {error_msg}", "DEBUG", project_dir
                    )
                else:
                    log_message(
                        f"DEBUG: File skipped or no changes: {file_path}",
                        "DEBUG",
                        project_dir,
                    )

            except Exception as e:
                error_msg = f"{file_path}: {str(e)}"
                processing_results["errors"].append(error_msg)
                log_message(
                    f"DEBUG: Exception processing {file_path}: {e}",
                    "DEBUG",
                    project_dir,
                )

        log_message(
            f"DEBUG: Unicode processing complete. "
            f"Cleaned {processing_results['files_cleaned']} files",
            "DEBUG",
            project_dir,
        )

    except Exception as e:
        error_msg = f"Unicode manager initialization failed: {str(e)}"
        processing_results["errors"].append(error_msg)
        log_message(
            f"DEBUG: Critical error in unicode processing: {e}", "DEBUG", project_dir
        )

    return processing_results


def _validate_cleaned_files(cleaned_files, project_dir):
    """Validate files after unicode cleanup with comprehensive logging.

    Args:
        cleaned_files: List of Path objects that were cleaned
        project_dir: Project directory for logging context

    Returns:
        List of validation results for each file
    """
    log_message(
        f"DEBUG: Starting validation of {len(cleaned_files)} cleaned files",
        "DEBUG",
        project_dir,
    )

    validation_results = []

    if not cleaned_files:
        log_message("DEBUG: No cleaned files to validate", "DEBUG", project_dir)
        return validation_results

    for cleaned_file in cleaned_files:
        log_message(f"DEBUG: Validating file: {cleaned_file}", "DEBUG", project_dir)

        try:
            # First run Black formatter to handle any formatting issues
            log_message(
                f"DEBUG: Running Black formatter on {cleaned_file}",
                "DEBUG",
                project_dir,
            )
            black_result = subprocess.run(
                ["python", "-m", "black", "--line-length=88", str(cleaned_file)],
                capture_output=True,
                text=True,
                cwd=project_dir,
                timeout=10,
            )

            if black_result.returncode == 0:
                log_message(
                    f"DEBUG: Black formatting successful for {cleaned_file}",
                    "DEBUG",
                    project_dir,
                )
            else:
                log_message(
                    f"DEBUG: Black formatting issues for {cleaned_file}: {black_result.stderr}",
                    "DEBUG",
                    project_dir,
                )

            # Then run comprehensive validation
            log_message(
                f"DEBUG: Running post-cleanup validation on {cleaned_file}",
                "DEBUG",
                project_dir,
            )
            validation = run_post_cleanup_validation(cleaned_file, project_dir)
            validation_results.append(validation)

            # Log detailed validation results
            if not validation["success"]:
                log_message(
                    f"WARNING: Validation issues found in {cleaned_file}",
                    "WARNING",
                    project_dir,
                )

                if validation["compile"]["status"] == "failed":
                    compile_error = validation["compile"]["error"]
                    log_message(
                        f"ERROR: Compilation error in {cleaned_file}: {compile_error}",
                        "ERROR",
                        project_dir,
                    )

                if validation["lint"]["status"] == "issues_found":
                    lint_output = validation["lint"].get("output", "No details")
                    log_message(
                        f"DEBUG: Lint issues in {cleaned_file}: {lint_output}",
                        "DEBUG",
                        project_dir,
                    )

                if validation["typecheck"]["status"] == "issues_found":
                    type_output = validation["typecheck"].get("output", "No details")
                    log_message(
                        f"DEBUG: Type check issues in {cleaned_file}: {type_output}",
                        "DEBUG",
                        project_dir,
                    )

            else:
                log_message(
                    f"DEBUG: {cleaned_file} validated successfully after unicode cleanup",
                    "DEBUG",
                    project_dir,
                )

        except Exception as e:
            log_message(
                f"ERROR: Exception during validation of {cleaned_file}: {e}",
                "ERROR",
                project_dir,
            )
            # Create error validation result
            error_validation = {
                "file": str(cleaned_file),
                "success": False,
                "validation_error": str(e),
            }
            validation_results.append(error_validation)

    log_message(
        f"DEBUG: Validation complete for {len(cleaned_files)} files",
        "DEBUG",
        project_dir,
    )
    return validation_results


def _format_cleanup_results(results, recent_files, project_dir):
    """Format cleanup results with comprehensive logging."""
    log_message(
        f"DEBUG: Starting result formatting for {results['files_cleaned']} cleaned files",
        "DEBUG",
        project_dir,
    )

    if results["files_cleaned"] > 0:
        log_message(
            f"DEBUG: Formatting success summary for {results['files_cleaned']} files",
            "DEBUG",
            project_dir,
        )

        # Determine validation status
        validation_passed = all(v["success"] for v in results.get("validation", []))
        validation_status = (
            "(all validated)" if validation_passed else "(with validation issues)"
        )

        log_message(
            f"DEBUG: Validation status: {validation_status}", "DEBUG", project_dir
        )

        # Format success summary
        results["summary"] = (
            f"Deleted {results['unicode_replaced']} unicode characters from "
            f"{results['files_cleaned']} files {validation_status}"
        )
    else:
        log_message(
            "DEBUG: No files were cleaned, formatting no-changes summary",
            "DEBUG",
            project_dir,
        )
        results["summary"] = (
            f"No unicode characters found in {len(recent_files)} recently modified files"
        )

    log_message(
        f"DEBUG: Result formatting complete: {results['summary']}", "DEBUG", project_dir
    )
    return results


def run_unicode_cleanup(project_dir):
    """Run unicode cleanup on recently modified files with comprehensive logging."""
    log_message("DEBUG: Starting unicode cleanup process", "DEBUG", project_dir)

    results = {
        "status": "success",
        "files_cleaned": 0,
        "unicode_replaced": 0,
        "errors": [],
        "summary": "",
    }

    try:
        if unicode_manager_class is None:
            log_message(
                "DEBUG: UnicodeManager not available, skipping cleanup",
                "DEBUG",
                project_dir,
            )
            results["status"] = "skipped"
            results["summary"] = "UnicodeManager not available"
            return results

        # Use extracted file discovery function
        recent_files = _find_recently_modified_files(project_dir)

        if not recent_files:
            log_message("DEBUG: No recently modified files found", "DEBUG", project_dir)
            results["summary"] = "No recently modified Python files found"
            return results

        # Process unicode cleanup using extracted function
        processing_results = _process_unicode_in_files(recent_files, project_dir)

        # Update main results with processing outcomes
        results["files_cleaned"] = processing_results["files_cleaned"]
        results["unicode_replaced"] = processing_results["unicode_replaced"]
        results["errors"].extend(processing_results["errors"])
        cleaned_files = processing_results["cleaned_files"]

        # Run validation on cleaned files using extracted function
        validation_results = _validate_cleaned_files(cleaned_files, project_dir)
        results["validation"] = validation_results

        # Format results using extracted function
        results = _format_cleanup_results(results, recent_files, project_dir)

    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
        results["summary"] = f"Error running unicode cleanup: {str(e)}"

    return results


def write_results_file(project_dir, formatting_results, unicode_results, hook_context):
    """Write quality check results to JSON file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    response_id = hook_context.get("response_id", "unknown")[:8]

    filename = f"post-response-quality-{timestamp}-{response_id}.json"
    # Use project directory for quality-checks results
    results_dir = Path(project_dir) / ".claude" / "hooks" / "quality-checks"
    results_dir.mkdir(parents=True, exist_ok=True)

    output_file = results_dir / filename

    output_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "response_id": response_id,
        "hook_type": "Stop",
        "project_directory": str(project_dir),
        "quality_checks": {
            "formatting": formatting_results,
            "unicode_cleanup": unicode_results,
        },
        "hook_info": {
            "hook_type": "Stop",
            "hook_script": str(Path(__file__).absolute()),
            "execution_time": datetime.datetime.now().isoformat(),
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return output_file


def trigger_quality_remediation(results_file, hook_context, project_dir):
    """Trigger the quality remediation workflow if needed."""
    try:
        # Import and run the quality remediation trigger
        trigger_script = Path(__file__).parent / "quality-remediation-trigger.py"

        if trigger_script.exists():
            print(
                log_message(
                    "Checking if quality remediation is needed...", "INFO", project_dir
                )
            )

            # Prepare input data for the trigger script
            trigger_input = {
                "session_id": hook_context.get("response_id", "unknown"),
                "cwd": str(project_dir),
                "reason": "post-response-check",
                "results_file": str(results_file),
            }

            result = subprocess.run(
                ["python", str(trigger_script)],
                input=json.dumps(trigger_input),
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        print(
                            log_message(
                                f"Remediation: {line.strip()}", "INFO", project_dir
                            )
                        )

            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    if line.strip():
                        print(
                            log_message(
                                f"Remediation Error: {line.strip()}",
                                "WARN",
                                project_dir,
                            )
                        )

    except Exception as e:
        print(log_message(f"Error triggering remediation: {e}", "ERROR", project_dir))


def main() -> int:
    """Execute main hook."""
    try:
        # Determine project directory first
        project_dir = Path.cwd()
        if "CLAUDE_PROJECT_DIR" in os.environ:
            project_dir = Path(os.environ["CLAUDE_PROJECT_DIR"])

        # Log that the hook was triggered immediately
        log_message(
            "==== POST-RESPONSE-QUALITY-CHECK HOOK TRIGGERED ====", "HOOK", project_dir
        )

        # Read hook input from stdin
        input_data = {}
        if not sys.stdin.isatty():
            try:
                input_text = sys.stdin.read().strip()
                if input_text:
                    input_data = json.loads(input_text)
                    log_message(
                        f"Received input: {json.dumps(input_data)[:100]}...",
                        "DEBUG",
                        project_dir,
                    )
            except json.JSONDecodeError as e:
                print(log_message(f"Invalid JSON input: {e}", "ERROR", project_dir))
                return 1

        # Get response context
        response_id = input_data.get("response_id", "standalone")
        hook_type = input_data.get("hook_type", "Stop")

        print(
            log_message(
                f"{hook_type} hook triggered - Response: {response_id[:8]}",
                "INFO",
                project_dir,
            )
        )
        log_message(
            f"Hook Type: {hook_type}, Response ID: {response_id}", "INFO", project_dir
        )

        print(
            log_message(
                f"Running post-response quality check on: {project_dir}",
                "INFO",
                project_dir,
            )
        )

        # Run quality checks
        formatting_results = run_black_formatter(project_dir)

        # Run unicode cleanup after formatting
        unicode_results = run_unicode_cleanup(project_dir)

        # Write results to file
        results_file = write_results_file(
            project_dir, formatting_results, unicode_results, input_data
        )
        print(
            log_message(
                f"Quality check complete - Results saved to: {results_file}",
                "INFO",
                project_dir,
            )
        )
        print(
            log_message(
                f"Formatting Status: {formatting_results['status']}",
                "INFO",
                project_dir,
            )
        )
        print(
            log_message(
                f"Formatting Summary: {formatting_results['summary']}",
                "INFO",
                project_dir,
            )
        )
        print(
            log_message(
                f"Unicode Cleanup Status: {unicode_results['status']}",
                "INFO",
                project_dir,
            )
        )
        print(
            log_message(
                f"Unicode Cleanup Summary: {unicode_results['summary']}",
                "INFO",
                project_dir,
            )
        )

        # Trigger remediation workflow if needed
        trigger_quality_remediation(results_file, input_data, project_dir)

        return 0

    except Exception as e:
        print(log_message(f"Hook execution failed: {e}", "ERROR", project_dir))
        return 1


if __name__ == "__main__":
    sys.exit(main())
