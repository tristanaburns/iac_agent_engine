#!/usr/bin/env python3
"""
Claude Code SessionEnd Hook - Auto Code Quality Check
Runs automatic code formatting and outputs results to file.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


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
        # Find Python files in the project
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(Path(project_dir).glob(pattern))

        if not python_files:
            results["summary"] = "No Python files found to format"
            return results

        # Run Black with --check first to see what would be changed
        check_cmd = ["python", "-m", "black", "--check", "--diff", str(project_dir)]
        check_result = subprocess.run(
            check_cmd, capture_output=True, text=True, cwd=project_dir, timeout=60
        )

        if check_result.returncode == 0:
            results["summary"] = (
                f"All {len(python_files)} Python files are already formatted correctly"
            )
        else:
            # Files need formatting - run Black to format them
            format_cmd = ["python", "-m", "black", str(project_dir)]
            format_result = subprocess.run(
                format_cmd, capture_output=True, text=True, cwd=project_dir, timeout=120
            )

            if format_result.returncode == 0:
                # Parse output to see what was formatted
                output_lines = format_result.stderr.split("\n")
                formatted_files = [
                    line.strip()
                    for line in output_lines
                    if line.strip().endswith(".py")
                ]
                results["files_formatted"] = formatted_files
                results["summary"] = f"Formatted {len(formatted_files)} Python files"
            else:
                results["status"] = "error"
                results["errors"].append(
                    f"Black formatting failed: {format_result.stderr}"
                )
                results["summary"] = "Black formatting encountered errors"

    except subprocess.TimeoutExpired:
        results["status"] = "error"
        results["errors"].append("Black formatting timed out")
        results["summary"] = "Formatting timed out"
    except FileNotFoundError:
        results["status"] = "error"
        results["errors"].append(
            "Black formatter not found - please install: pip install black"
        )
        results["summary"] = "Black formatter not available"
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(f"Unexpected error: {str(e)}")
        results["summary"] = f"Formatting failed: {str(e)}"

    return results


def write_results_file(project_dir, session_data, quality_results):
    """Write quality check results to file."""
    results_dir = Path(project_dir) / ".claude" / "hooks" / "quality-checks"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = session_data.get("session_id", "unknown")[:8]
    results_file = results_dir / f"session-end-quality-{timestamp}-{session_id}.json"

    output_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_data.get("session_id"),
        "session_end_reason": session_data.get("reason", "unknown"),
        "project_directory": project_dir,
        "quality_checks": {"formatting": quality_results},
        "hook_info": {
            "hook_type": "SessionEnd",
            "hook_script": __file__,
            "execution_time": datetime.datetime.now().isoformat(),
        },
    }

    try:
        with open(results_file, "w") as f:
            json.dump(output_data, f, indent=2)

        return str(results_file)
    except Exception as e:
        # Fallback to stdout if file write fails
        print(log_message(f"Failed to write results file: {e}", "ERROR", project_dir))
        return None


def trigger_quality_remediation(project_dir, results_file, session_data):
    """Trigger quality remediation workflow if issues are found."""
    if not results_file:
        return

    try:
        # Call the quality remediation trigger script
        trigger_script = (
            Path(project_dir) / ".claude" / "hooks" / "quality-remediation-trigger.py"
        )

        if trigger_script.exists():
            print(
                log_message(
                    "Checking if quality remediation is needed...", "INFO", project_dir
                )
            )

            # Prepare input data for the trigger script
            trigger_input = {
                "session_id": session_data.get("session_id", "unknown"),
                "cwd": project_dir,
                "reason": session_data.get("reason", "unknown"),
            }

            # Run the trigger script with proper JSON input
            trigger_cmd = ["python", str(trigger_script)]
            trigger_result = subprocess.run(
                trigger_cmd,
                input=json.dumps(trigger_input),
                capture_output=True,
                text=True,
                cwd=project_dir,
                timeout=60,  # Increased timeout for remediation planning
            )

            if trigger_result.returncode == 0:
                # Parse and display the trigger output
                output_lines = trigger_result.stdout.strip().split("\n")
                for line in output_lines[-3:]:  # Show last 3 lines of output
                    if line.strip() and "[INFO]" in line:
                        print(
                            log_message(
                                f"Remediation: {line.split('] ', 1)[-1]}",
                                "INFO",
                                project_dir,
                            )
                        )
            else:
                error_msg = trigger_result.stderr.strip()
                if error_msg:
                    print(
                        log_message(
                            f"Remediation trigger failed: {error_msg}",
                            "WARNING",
                            project_dir,
                        )
                    )
        else:
            print(
                log_message(
                    "Quality remediation trigger script not found", "INFO", project_dir
                )
            )

    except subprocess.TimeoutExpired:
        print(
            log_message("Quality remediation trigger timed out", "WARNING", project_dir)
        )
    except Exception as e:
        print(
            log_message(
                f"Failed to trigger quality remediation: {e}", "WARNING", project_dir
            )
        )


def main():
    """Main hook execution."""
    # Extract session information first to get project_dir
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
        project_dir = input_data.get("cwd", os.getcwd())
    except json.JSONDecodeError as e:
        project_dir = os.getcwd()
        print(
            log_message(f"Invalid JSON input: {e}", "ERROR", project_dir),
            file=sys.stderr,
        )
        sys.exit(1)

    # Log that the hook was triggered
    log_message(
        "==== SESSION-END-QUALITY-CHECK HOOK TRIGGERED ====", "HOOK", project_dir
    )
    log_message(
        f"Received input: {json.dumps(input_data)[:100]}...", "DEBUG", project_dir
    )

    # Extract session information
    session_id = input_data.get("session_id", "unknown")
    reason = input_data.get("reason", "unknown")

    print(
        log_message(
            f"SessionEnd hook triggered - Session: {session_id[:8]}, Reason: {reason}",
            "INFO",
            project_dir,
        )
    )
    log_message(
        f"Session ID: {session_id}, Reason: {reason}, Dir: {project_dir}",
        "INFO",
        project_dir,
    )
    print(
        log_message(
            f"Running auto-formatting check on: {project_dir}", "INFO", project_dir
        )
    )

    # Run Black formatter
    formatting_results = run_black_formatter(project_dir)

    # Write results to file
    results_file = write_results_file(project_dir, input_data, formatting_results)

    # Output summary
    if results_file:
        print(
            log_message(
                f"Quality check complete - Results saved to: {results_file}",
                "INFO",
                project_dir,
            )
        )

    print(
        log_message(
            f"Formatting Status: {formatting_results['status']}", "INFO", project_dir
        )
    )
    print(log_message(f"Summary: {formatting_results['summary']}", "INFO", project_dir))

    if formatting_results["errors"]:
        for error in formatting_results["errors"]:
            print(log_message(f"Error: {error}", "ERROR", project_dir))

    # Trigger quality remediation workflow if needed
    trigger_quality_remediation(project_dir, results_file, input_data)

    # Exit successfully (SessionEnd hooks cannot block)
    sys.exit(0)


if __name__ == "__main__":
    main()
