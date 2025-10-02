#!/usr/bin/env python3
"""
Git Protection Manager Module.

============================

Provides git-based protection for automated code quality operations.
Creates safety commits before and after quality tool execution to ensure
complete traceability and rollback capability.

Author: System
Version: 1.0.0
"""


import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class GitProtectionManager:
    """
    Manages git-based protection for automated code quality operations.

    Creates protective commits before and after quality tool execution,
    ensuring complete traceability and rollback capability.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        protected_branches: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize Git Protection Manager.

        Args:
            project_root: Path to git repository root
            protected_branches: List of protected branch names (e.g., ['main', 'master', 'production'])
        """
        self.project_root = project_root or Path.cwd()
        self.protected_branches = protected_branches or ["main", "master", "production"]
        self.stats = {"protection_commits": 0, "completion_commits": 0, "errors": 0}
        self.logger = logging.getLogger(__name__)

    def _run_git_command(
        self, cmd: List[str], timeout: int = 30, log_command: bool = True
    ) -> Tuple[bool, str, str]:
        """
        Run a git command and return success status, stdout, stderr.

        Args:
            cmd: Git command to run
            timeout: Command timeout in seconds
            log_command: Whether to log the command execution

        Returns:
            Tuple of (success, stdout, stderr)
        """
        if log_command:
            self.logger.debug(
                f"[GIT-PROTECTION] Executing git command: {' '.join(cmd)}"
            )
            print(f"[DEBUG] Git command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )

            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if log_command:
                self.logger.debug(
                    f"[GIT-PROTECTION] Command result: success={success}, stdout={stdout[:100]}..., stderr={stderr[:100]}..."
                )
                print(f"[DEBUG] Command result: success={success}")
                if stderr:
                    print(f"[DEBUG] Command stderr: {stderr}")

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Git command timed out after {timeout} seconds"
            self.logger.error(f"[GIT-PROTECTION] {error_msg}")
            print(f"[DEBUG] {error_msg}")
            return False, "", error_msg
        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"[GIT-PROTECTION] Git command failed with exception: {error_msg}"
            )
            print(f"[DEBUG] Git command exception: {error_msg}")
            return False, "", error_msg

    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        success, _, _ = self._run_git_command(
            ["git", "rev-parse", "--is-inside-work-tree"], log_command=False
        )
        return success

    def _validate_repository_state(self) -> Tuple[bool, List[str]]:
        """
        Comprehensive repository state validation before any git operations.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        print("[DEBUG] Starting comprehensive repository state validation")
        errors = []

        # Check if we're in a git repository
        if not self._is_git_repository():
            errors.append("Not in a git repository or not in working tree")
            return False, errors

        # Validate HEAD state
        self._check_head_state(errors)

        # Validate current branch
        self._check_protected_branch(errors)

        # Validate repository conflicts and status
        self._check_merge_conflicts_and_status(errors)

        print(f"[DEBUG] Repository validation completed. Errors: {len(errors)}")
        for error in errors:
            print(f"[DEBUG] Validation error: {error}")

        return len(errors) == 0, errors

    def _check_head_state(self, errors: List[str]) -> None:
        """
        Check for detached HEAD state.

        Args:
            errors: List to append errors to
        """
        success, branch_output, stderr = self._run_git_command(
            ["git", "symbolic-ref", "HEAD"], log_command=False
        )
        if not success:
            print(f"[DEBUG] Checking if in detached HEAD state: {stderr}")
            # Check if we're in detached HEAD
            success_head, head_output, _ = self._run_git_command(
                ["git", "rev-parse", "--verify", "HEAD"], log_command=False
            )
            if success_head:
                errors.append(
                    "Repository is in detached HEAD state - unsafe for automated commits"
                )

    def _check_protected_branch(self, errors: List[str]) -> None:
        """
        Check if current branch is protected.

        Args:
            errors: List to append errors to
        """
        current_branch = self._get_current_branch()
        if current_branch and current_branch in self.protected_branches:
            errors.append(
                f"Current branch '{current_branch}' is protected - automated commits not allowed"
            )

    def _check_merge_conflicts_and_status(self, errors: List[str]) -> None:
        """
        Check for merge conflicts and log repository status.

        Args:
            errors: List to append errors to
        """
        success, status_output, stderr = self._run_git_command(
            ["git", "status", "--porcelain"], log_command=False
        )
        if success and status_output:
            # Check for merge conflicts
            for line in status_output.split("\n"):
                if (
                    line.startswith("UU ")
                    or line.startswith("AA ")
                    or line.startswith("DD ")
                ):
                    errors.append("Repository has unresolved merge conflicts")
                    break

            # Log what changes exist
            print(
                f"[DEBUG] Repository has changes: {len(status_output.split())} lines in git status"
            )

    def _has_staged_changes(self) -> bool:
        """Check if there are staged changes in git using porcelain status."""
        success, stdout, _ = self._run_git_command(
            ["git", "status", "--porcelain"], log_command=False
        )
        if not success:
            return False

        # Check for staged changes (lines starting with M, A, D, R, C in first column)
        for line in stdout.split("\n"):
            if line and len(line) >= 2 and line[0] in "MADRC":
                return True
        return False

    def _has_unstaged_changes(self) -> bool:
        """Check if there are unstaged changes in git using porcelain status."""
        success, stdout, _ = self._run_git_command(
            ["git", "status", "--porcelain"], log_command=False
        )
        if not success:
            return False

        # Check for unstaged changes (lines with second column M, D, or untracked ??)
        for line in stdout.split("\n"):
            if line and (line.startswith("??") or (len(line) >= 2 and line[1] in "MD")):
                return True
        return False

    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        success, stdout, _ = self._run_git_command(["git", "branch", "--show-current"])
        return stdout if success else None

    def _get_staged_files_info(self) -> Dict[str, List[str]]:
        """
        Get detailed information about staged files for validation.

        Returns:
            Dictionary with lists of files by change type
        """
        print("[DEBUG] Getting staged files information for validation")
        staged_info = self._initialize_staged_info_dict()

        success, stdout, _ = self._run_git_command(
            ["git", "status", "--porcelain"], log_command=False
        )
        if not success or not stdout:
            return staged_info

        self._parse_status_lines(stdout, staged_info)

        total_files = sum(len(files) for files in staged_info.values())
        print(f"[DEBUG] Found {total_files} staged files across all categories")
        return staged_info

    def _initialize_staged_info_dict(self) -> Dict[str, List[str]]:
        """
        Initialize staged files information dictionary.

        Returns:
            Empty staged info dictionary structure
        """
        return {
            "added": [],
            "modified": [],
            "deleted": [],
            "renamed": [],
            "copied": [],
        }

    def _parse_status_lines(
        self, stdout: str, staged_info: Dict[str, List[str]]
    ) -> None:
        """
        Parse git status output lines and populate staged info.

        Args:
            stdout: Git status output
            staged_info: Dictionary to populate with file information
        """
        for line in stdout.split("\n"):
            if not line or len(line) < 3:
                continue

            status_code = line[0]
            file_path = line[3:].strip()

            if status_code == "A":
                staged_info["added"].append(file_path)
            elif status_code == "M":
                staged_info["modified"].append(file_path)
            elif status_code == "D":
                staged_info["deleted"].append(file_path)
            elif status_code == "R":
                staged_info["renamed"].append(file_path)
            elif status_code == "C":
                staged_info["copied"].append(file_path)

    def _validate_staged_content(self) -> Tuple[bool, List[str]]:
        """
        Validate the content that's about to be staged for safety.

        Returns:
            Tuple of (is_safe, warning_messages)
        """
        print("[DEBUG] Validating staged content for safety")
        warnings: list[str] = []
        staged_info = self._get_staged_files_info()

        total_staged = sum(len(files) for files in staged_info.values())
        if total_staged == 0:
            print("[DEBUG] No staged content to validate")
            return True, []

        # Get all staged files
        all_staged_files = self._collect_all_staged_files(staged_info)

        # Check for file safety issues
        self._check_file_safety(all_staged_files, warnings)

        print(f"[DEBUG] Staged content validation completed. Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"[DEBUG] Staging warning: {warning}")

        # For now, we'll allow staging with warnings (not errors)
        return True, warnings

    def _collect_all_staged_files(self, staged_info: Dict[str, List[str]]) -> List[str]:
        """
        Collect all staged files into a single list.

        Args:
            staged_info: Dictionary of staged files by type

        Returns:
            List of all staged file paths
        """
        all_staged_files = []
        for file_list in staged_info.values():
            all_staged_files.extend(file_list)
        return all_staged_files

    def _check_file_safety(
        self, all_staged_files: List[str], warnings: List[str]
    ) -> None:
        """
        Check staged files for safety issues.

        Args:
            all_staged_files: List of all staged file paths
            warnings: List to append warnings to
        """
        suspicious_extensions = [".exe", ".dll", ".so", ".dylib", ".bin"]
        large_file_threshold = 10 * 1024 * 1024  # 10MB

        for file_path in all_staged_files:
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in suspicious_extensions:
                warnings.append(f"Suspicious binary file staged: {file_path}")

            # Check file size if it exists
            self._check_file_size(file_path, large_file_threshold, warnings)

    def _check_file_size(
        self, file_path: str, threshold: int, warnings: List[str]
    ) -> None:
        """
        Check if file size exceeds threshold.

        Args:
            file_path: Path to file to check
            threshold: Size threshold in bytes
            warnings: List to append warnings to
        """
        full_path = self.project_root / file_path
        if full_path.exists() and full_path.is_file():
            try:
                file_size = full_path.stat().st_size
                if file_size > threshold:
                    warnings.append(
                        f"Large file staged ({file_size} bytes): {file_path}"
                    )
            except OSError:
                pass  # Skip if we can't read file info

    def _get_git_status_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of current git status."""
        print("[DEBUG] Generating comprehensive git status summary")
        summary: Dict[str, Any] = {
            "branch": self._get_current_branch(),
            "has_staged_changes": self._has_staged_changes(),
            "has_unstaged_changes": self._has_unstaged_changes(),
            "modified_files": [],
            "untracked_files": [],
            "staged_files_info": {},
            "repository_state_valid": False,
            "validation_errors": [],
        }

        # Get repository state validation
        is_valid, errors = self._validate_repository_state()
        summary["repository_state_valid"] = is_valid
        summary["validation_errors"] = errors

        # Get staged files information
        summary["staged_files_info"] = self._get_staged_files_info()

        # Get modified files using porcelain status
        success, stdout, _ = self._run_git_command(
            ["git", "status", "--porcelain"], log_command=False
        )
        if success and stdout:
            modified_files = []
            untracked_files = []
            for line in stdout.split("\n"):
                if not line:
                    continue
                if line.startswith("??"):
                    untracked_files.append(line[3:].strip())
                elif len(line) >= 3:
                    modified_files.append(line[3:].strip())
            summary["modified_files"] = modified_files
            summary["untracked_files"] = untracked_files

        print("[DEBUG] Git status summary completed")
        return summary

    def _safe_stage_all_changes(self) -> Tuple[bool, List[str]]:
        """
        Safely stage all changes with comprehensive validation.

        Returns:
            Tuple of (success, error_messages)
        """
        print("[DEBUG] Starting safe staging of all changes")
        errors = []

        # First, validate repository state
        is_valid, validation_errors = self._validate_repository_state()
        if not is_valid:
            errors.extend(validation_errors)
            return False, errors

        # Check what needs to be staged
        if not self._check_staging_requirements(errors):
            return False, errors

        # Perform incremental staging
        if not self._perform_incremental_staging(errors):
            return False, errors

        # Validate staged content
        if not self._validate_staging_result(errors):
            return False, errors

        print("[DEBUG] Safe staging completed successfully")
        return True, []

    def _check_staging_requirements(self, errors: List[str]) -> bool:
        """
        Check if there are changes that need to be staged.

        Args:
            errors: List to append errors to

        Returns:
            True if staging should proceed, False otherwise
        """
        success, status_output, stderr = self._run_git_command(
            ["git", "status", "--porcelain"]
        )
        if not success:
            errors.append(f"Failed to get repository status: {stderr}")
            return False

        if not status_output.strip():
            print("[DEBUG] No changes to stage")
            return True  # No changes, but not an error

        print(
            f"[DEBUG] Repository has changes to stage: {len(status_output.split())} status lines"
        )
        return True

    def _perform_incremental_staging(self, errors: List[str]) -> bool:
        """
        Perform incremental staging of changes for safety.

        Args:
            errors: List to append errors to

        Returns:
            True if staging succeeded, False otherwise
        """
        try:
            # Stage tracked file modifications first
            success, stdout, stderr = self._run_git_command(["git", "add", "-u"])
            if not success:
                errors.append(f"Failed to stage tracked file updates: {stderr}")
                return False

            # Stage new files (but not deletions yet)
            success, stdout, stderr = self._run_git_command(["git", "add", "."])
            if not success and "warning:" not in stderr.lower():
                # Only treat as error if it's not just a warning (like CRLF)
                errors.append(f"Failed to stage new files: {stderr}")
                return False

            return True

        except Exception as e:
            errors.append(f"Exception during staging: {str(e)}")
            return False

    def _validate_staging_result(self, errors: List[str]) -> bool:
        """
        Validate what was actually staged for safety.

        Args:
            errors: List to append errors to

        Returns:
            True if staged content is safe, False otherwise
        """
        is_safe, warnings = self._validate_staged_content()
        if not is_safe:
            errors.append("Staged content failed safety validation")
            return False

        if warnings:
            print("[DEBUG] Staging completed with warnings:")
            for warning in warnings:
                print(f"[DEBUG] Warning: {warning}")

        return True

    def _validate_protection_commit_state(self, result: Dict[str, Any]) -> bool:
        """
        Validate repository state for protection commit.

        Args:
            result: Result dictionary to update with status and errors

        Returns:
            True if repository state is valid, False otherwise
        """
        print("[DEBUG] Getting git status before protection commit")
        result["git_status_before"] = self._get_git_status_summary()
        result["repository_state_valid"] = result["git_status_before"][
            "repository_state_valid"
        ]

        if not result["repository_state_valid"]:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.extend(result["git_status_before"]["validation_errors"])
            print("[DEBUG] Repository state validation failed")
            return False
        return True

    def _validate_staging_state(self, result: Dict[str, Any]) -> bool:
        """
        Validate staging state for protection commit.

        Args:
            result: Result dictionary to update with status and errors

        Returns:
            True if staging is successful, False otherwise
        """
        print("[DEBUG] Attempting to safely stage all changes")
        staging_success, staging_errors = self._safe_stage_all_changes()
        result["staged_safely"] = staging_success

        if not staging_success:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.extend(staging_errors)
            print("[DEBUG] Safe staging failed")
            return False

        # Check if there's anything to commit after staging
        if not self._has_staged_changes():
            print("[DEBUG] No changes staged for protection commit")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append("No changes to commit for protection")
            result["success"] = True  # Not an error, just nothing to protect
            return False
        return True

    def _create_commit_message(
        self, operation_description: str, target_files: Optional[List[str]] = None
    ) -> str:
        """
        Create comprehensive protection commit message.

        Args:
            operation_description: Description of the operation
            target_files: Optional list of target files

        Returns:
            Complete commit message string
        """
        print("[DEBUG] Creating protection commit message")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        staged_info = self._get_staged_files_info()
        total_staged = sum(len(files) for files in staged_info.values())

        commit_message_lines = [
            f"feat: pre-automation protection commit - {operation_description}",
            "",
            f"Automated quality tools are about to execute: {operation_description}",
            f"Protection commit created at: {timestamp}",
            f"Total staged files: {total_staged}",
            "",
        ]

        # Add staged files summary
        if total_staged > 0:
            commit_message_lines.append("Staged changes summary:")
            for change_type, files in staged_info.items():
                if files:
                    commit_message_lines.append(
                        f"  - {change_type}: {len(files)} files"
                    )
            commit_message_lines.append("")

        if target_files:
            commit_message_lines.append("Target files for processing:")
            commit_message_lines.extend(
                [f"  - {file}" for file in target_files[:10]]
            )  # Limit to 10 files
            if len(target_files) > 10:
                commit_message_lines.append("  - ...")
            commit_message_lines.append("")

        commit_message_lines.extend(
            [
                "This commit preserves the codebase state before automated modifications.",
                "Repository state was validated before staging.",
                "All changes were staged safely without --force flags.",
                "If automation fails, use: git reset --hard HEAD~1",
                "",
                "[AI] Generated with Claude Code - Pre-Automation Protection",
                "",
                "Co-Authored-By: Claude <noreply@anthropic.com>",
            ]
        )

        return "\n".join(commit_message_lines)

    def _execute_commit(self, commit_message: str, result: Dict[str, Any]) -> bool:
        """
        Execute the git commit operation.

        Args:
            commit_message: The commit message to use
            result: Result dictionary to update with status and errors

        Returns:
            True if commit succeeds, False otherwise
        """
        print("[DEBUG] Creating protection commit")
        cmd = ["git", "commit", "-m", commit_message]

        success, stdout, stderr = self._run_git_command(cmd)
        if not success:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(f"Failed to create protection commit: {stderr}")
            print(f"[DEBUG] Protection commit failed: {stderr}")
            return False
        return True

    def _finalize_commit_result(
        self, commit_message: str, result: Dict[str, Any]
    ) -> None:
        """
        Finalize the commit result with hash and success status.

        Args:
            commit_message: The commit message that was used
            result: Result dictionary to update with final status
        """
        # Get and validate the commit hash
        success, commit_hash, _ = self._run_git_command(
            ["git", "rev-parse", "HEAD"], log_command=False
        )
        if success:
            result["commit_hash"] = commit_hash
            print(f"[DEBUG] Protection commit created with hash: {commit_hash[:8]}...")
        else:
            print("[DEBUG] Warning: Could not retrieve commit hash")

        result["success"] = True
        result["commit_message"] = commit_message
        self.stats["protection_commits"] += 1
        print("[DEBUG] Protection commit completed successfully")

    def create_protection_commit(
        self, operation_description: str, target_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a protection commit before running quality tools with comprehensive safety.

        Args:
            operation_description: Description of the operation about to be performed
            target_files: Optional list of specific files to be processed

        Returns:
            Dictionary with commit information and status
        """
        print(f"[DEBUG] Starting protection commit for: {operation_description}")
        result: Dict[str, Any] = {
            "success": False,
            "commit_hash": None,
            "commit_message": None,
            "timestamp": datetime.now().isoformat(),
            "git_status_before": None,
            "repository_state_valid": False,
            "staged_safely": False,
            "errors": [],
        }

        try:
            # Validate repository state
            if not self._validate_protection_commit_state(result):
                return result

            # Validate staging state
            if not self._validate_staging_state(result):
                return result

            # Create commit message
            commit_message = self._create_commit_message(
                operation_description, target_files
            )

            # Execute the commit
            if not self._execute_commit(commit_message, result):
                return result

            # Finalize the result
            self._finalize_commit_result(commit_message, result)

        except Exception as e:
            error_msg = f"Unexpected error creating protection commit: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(error_msg)
            self.stats["errors"] += 1

        return result

    def _validate_repository_for_completion(self, result: Dict[str, Any]) -> bool:
        """
        Validate git repository for completion commit.

        Args:
            result: Result dictionary to update with errors

        Returns:
            True if validation passed, False otherwise
        """
        print("[DEBUG] Starting repository validation for completion commit")

        if not self._is_git_repository():
            print("[DEBUG] Repository validation failed: Not in a git repository")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append("Not in a git repository")
            return False

        print("[DEBUG] Repository validation passed: Valid git repository")
        return True

    def _stage_completion_changes(self, result: Dict[str, Any]) -> bool:
        """
        Safely stage all changes made by automation with comprehensive validation.

        Args:
            result: Result dictionary to update with errors

        Returns:
            True if staging succeeded or no changes, False on error
        """
        print("[DEBUG] Starting to safely stage automation changes")

        # Use the same safe staging mechanism as protection commits
        staging_success, staging_errors = self._safe_stage_all_changes()

        if not staging_success:
            print("[DEBUG] Safe staging failed for completion commit")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.extend(staging_errors)
            return False

        # Check if automation made any changes
        if not self._has_staged_changes():
            print("[DEBUG] No changes made by automation to commit")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append("No changes made by automation to commit")
            result["success"] = True  # Not an error, just no changes
            return False

        print("[DEBUG] Automation changes staged safely for completion commit")
        return True

    def _build_completion_message_header(self, operation_description: str) -> List[str]:
        """
        Build the header portion of completion commit message.

        Args:
            operation_description: Description of completed operation

        Returns:
            List of header message lines
        """
        print(
            f"[DEBUG] Building completion message header for: {operation_description}"
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_lines = [
            f"fix: post-automation completion commit - {operation_description}",
            "",
            f"Automated quality tools have completed: {operation_description}",
            f"Completion commit created at: {timestamp}",
            "",
        ]

        print(f"[DEBUG] Created header with {len(header_lines)} lines")
        return header_lines

    def _add_completion_message_sections(
        self,
        lines: List[str],
        tools_executed: List[str],
        files_modified: List[str],
        execution_summary: Optional[Dict[str, Any]],
    ) -> None:
        """
        Add conditional sections to completion commit message.

        Args:
            lines: Message lines to append to
            tools_executed: List of tools that were executed
            files_modified: List of files that were modified
            execution_summary: Optional summary of accomplishments
        """
        print(
            f"[DEBUG] Adding message sections: tools={len(tools_executed)}, files={len(files_modified)}, summary={execution_summary is not None}"
        )

        if tools_executed:
            print(f"[DEBUG] Adding tools section with {len(tools_executed)} tools")
            lines.extend(
                ["Tools executed:", *[f"  - {tool}" for tool in tools_executed], ""]
            )

        if files_modified:
            print(f"[DEBUG] Adding files section with {len(files_modified)} files")
            lines.append("Files modified:")
            lines.extend(
                [f"  - {file}" for file in files_modified[:15]]
            )  # Limit to 15 files
            if len(files_modified) > 15:
                lines.append("  - ...")
            lines.append("")

        if execution_summary:
            print(
                f"[DEBUG] Adding execution summary with {len(execution_summary)} items"
            )
            lines.extend(
                [
                    "Execution summary:",
                    *[
                        f"  - {key}: {value}"
                        for key, value in execution_summary.items()
                    ],
                    "",
                ]
            )

        # Add footer
        lines.extend(
            [
                "This commit contains all changes made by automated quality tools.",
                "All modifications were performed by external tools (black, ruff, mypy, etc.)",
                "",
                "[AI] Generated with Claude Code - Post-Automation Results",
                "",
                "Co-Authored-By: Claude <noreply@anthropic.com>",
            ]
        )

        print(f"[DEBUG] Completed message sections, total lines: {len(lines)}")

    def _execute_completion_commit_with_hash(
        self, commit_message: str, result: Dict[str, Any]
    ) -> bool:
        """
        Execute completion commit and retrieve commit hash.

        Args:
            commit_message: Complete commit message
            result: Result dictionary to update

        Returns:
            True if commit succeeded, False otherwise
        """
        print("[DEBUG] Executing completion commit")

        # Create the commit
        cmd = ["git", "commit", "-m", commit_message]
        success, stdout, stderr = self._run_git_command(cmd)

        if not success:
            print(f"[DEBUG] Completion commit failed: {stderr}")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(f"Failed to create completion commit: {stderr}")
            return False

        print("[DEBUG] Completion commit created successfully, retrieving hash")

        # Get the commit hash
        success, commit_hash, _ = self._run_git_command(["git", "rev-parse", "HEAD"])
        if success:
            result["commit_hash"] = commit_hash
            print(f"[DEBUG] Retrieved commit hash: {commit_hash[:8]}...")
        else:
            print("[DEBUG] Warning: Could not retrieve commit hash")

        result["success"] = True
        result["commit_message"] = commit_message
        self.stats["completion_commits"] += 1

        print("[DEBUG] Completion commit process completed successfully")
        return True

    def create_completion_commit(
        self,
        operation_description: str,
        tools_executed: List[str],
        files_modified: List[str],
        execution_summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a completion commit after quality tools have finished.

        Args:
            operation_description: Description of the completed operation
            tools_executed: List of tools that were executed
            files_modified: List of files that were modified
            execution_summary: Optional summary of what was accomplished

        Returns:
            Dictionary with commit information and status
        """
        print(f"[DEBUG] Starting completion commit for: {operation_description}")

        result: Dict[str, Any] = {
            "success": False,
            "commit_hash": None,
            "commit_message": None,
            "timestamp": datetime.now().isoformat(),
            "git_status_after": None,
            "errors": [],
        }

        try:
            # Validate repository
            if not self._validate_repository_for_completion(result):
                print("[DEBUG] Repository validation failed, returning early")
                return result

            # Get git status after automation
            print("[DEBUG] Collecting git status after automation")
            result["git_status_after"] = self._get_git_status_summary()

            # Stage changes with fallback handling
            if not self._stage_completion_changes(result):
                print("[DEBUG] Staging failed or no changes, returning")
                return result

            # Build commit message
            print("[DEBUG] Building completion commit message")
            commit_message_lines = self._build_completion_message_header(
                operation_description
            )
            self._add_completion_message_sections(
                commit_message_lines, tools_executed, files_modified, execution_summary
            )
            commit_message = "\n".join(commit_message_lines)

            # Execute commit with hash retrieval
            if not self._execute_completion_commit_with_hash(commit_message, result):
                print("[DEBUG] Commit execution failed")
                return result

            print("[DEBUG] Completion commit workflow completed successfully")

        except Exception as e:
            print(f"[DEBUG] Unexpected error in completion commit: {str(e)}")
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(f"Unexpected error creating completion commit: {str(e)}")
            self.stats["errors"] += 1

        return result

    def _validate_rollback_safety(
        self, protection_commit_hash: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that rollback operation is safe before executing.

        Args:
            protection_commit_hash: Hash of the protection commit to rollback to

        Returns:
            Tuple of (is_safe, error_messages)
        """
        print(
            f"[DEBUG] Validating rollback safety for commit: {protection_commit_hash[:8]}..."
        )
        errors = []

        # Validate repository state first
        is_valid, repo_errors = self._validate_repository_state()
        if not is_valid:
            errors.extend(repo_errors)

        # Verify the commit hash exists and is accessible
        success, stdout, stderr = self._run_git_command(
            ["git", "rev-parse", "--verify", protection_commit_hash], log_command=False
        )
        if not success:
            errors.append(
                f"Protection commit hash {protection_commit_hash} does not exist or is invalid"
            )

        # Check if the commit is reachable from current HEAD
        success, stdout, stderr = self._run_git_command(
            ["git", "merge-base", "--is-ancestor", protection_commit_hash, "HEAD"],
            log_command=False,
        )
        if not success:
            # This might be OK if the protection commit is ahead, let's check
            success2, stdout2, stderr2 = self._run_git_command(
                ["git", "merge-base", "--is-ancestor", "HEAD", protection_commit_hash],
                log_command=False,
            )
            if not success2:
                errors.append(
                    f"Protection commit {protection_commit_hash} is not related to current HEAD"
                )

        # Check for uncommitted work that would be lost
        if self._has_unstaged_changes() or self._has_staged_changes():
            errors.append(
                "Rollback would lose uncommitted work - commit or stash changes first"
            )

        print(f"[DEBUG] Rollback safety validation completed. Errors: {len(errors)}")
        return len(errors) == 0, errors

    def rollback_to_protection_commit(
        self, protection_commit_hash: str, force: bool = False
    ) -> Dict[str, Any]:
        """
        Safely rollback to a specific protection commit if automation failed.

        Args:
            protection_commit_hash: Hash of the protection commit to rollback to
            force: Whether to force rollback even with safety warnings (use with caution)

        Returns:
            Dictionary with rollback status and information
        """
        print(
            f"[DEBUG] Starting safe rollback to protection commit: {protection_commit_hash[:8]}..."
        )
        result = self._initialize_rollback_result()

        try:
            # Store current commit hash
            self._store_current_commit_hash(result)

            # Validate rollback safety
            if not self._validate_rollback_operation(
                protection_commit_hash, force, result
            ):
                return result

            # Execute the rollback
            if not self._execute_rollback(protection_commit_hash, result):
                return result

            # Verify rollback success
            self._verify_rollback_success(protection_commit_hash, result)

        except Exception as e:
            self._handle_rollback_exception(e, result)

        return result

    def _initialize_rollback_result(self) -> Dict[str, Any]:
        """
        Initialize rollback result dictionary.

        Returns:
            Initialized result dictionary
        """
        return {
            "success": False,
            "rollback_completed": False,
            "rollback_validated": False,
            "commit_hash_before_rollback": None,
            "errors": [],
        }

    def _store_current_commit_hash(self, result: Dict[str, Any]) -> None:
        """
        Store current commit hash before rollback.

        Args:
            result: Result dictionary to update
        """
        success, current_hash, _ = self._run_git_command(
            ["git", "rev-parse", "HEAD"], log_command=False
        )
        if success:
            result["commit_hash_before_rollback"] = current_hash

    def _validate_rollback_operation(
        self, protection_commit_hash: str, force: bool, result: Dict[str, Any]
    ) -> bool:
        """
        Validate rollback operation safety.

        Args:
            protection_commit_hash: Target commit hash
            force: Whether to force rollback
            result: Result dictionary to update

        Returns:
            True if rollback should proceed, False otherwise
        """
        is_safe, safety_errors = self._validate_rollback_safety(protection_commit_hash)
        result["rollback_validated"] = is_safe

        if not is_safe and not force:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(
                    "Rollback safety validation failed - use force=True to override"
                )
                errors.extend(safety_errors)
            print("[DEBUG] Rollback safety validation failed")
            return False

        if not is_safe and force:
            print("[DEBUG] WARNING: Forcing rollback despite safety concerns")
            for error in safety_errors:
                print(f"[DEBUG] Safety warning (forced): {error}")

        return True

    def _execute_rollback(
        self, protection_commit_hash: str, result: Dict[str, Any]
    ) -> bool:
        """
        Execute the actual rollback operation.

        Args:
            protection_commit_hash: Target commit hash
            result: Result dictionary to update

        Returns:
            True if rollback succeeded, False otherwise
        """
        print(f"[DEBUG] Executing rollback to {protection_commit_hash}")
        cmd = ["git", "reset", "--hard", protection_commit_hash]
        success, stdout, stderr = self._run_git_command(cmd)

        if not success:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append(f"Failed to rollback: {stderr}")
            print(f"[DEBUG] Rollback command failed: {stderr}")
            return False

        return True

    def _verify_rollback_success(
        self, protection_commit_hash: str, result: Dict[str, Any]
    ) -> None:
        """
        Verify that rollback was successful.

        Args:
            protection_commit_hash: Expected commit hash after rollback
            result: Result dictionary to update
        """
        success, new_hash, _ = self._run_git_command(
            ["git", "rev-parse", "HEAD"], log_command=False
        )
        if success and new_hash == protection_commit_hash:
            result["success"] = True
            result["rollback_completed"] = True
            print(f"[DEBUG] Rollback completed successfully to {new_hash[:8]}...")
        else:
            errors = result.get("errors", [])
            if isinstance(errors, list):
                errors.append("Rollback appeared to succeed but verification failed")

    def _handle_rollback_exception(self, e: Exception, result: Dict[str, Any]) -> None:
        """
        Handle exceptions during rollback operation.

        Args:
            e: Exception that occurred
            result: Result dictionary to update
        """
        error_msg = f"Unexpected error during rollback: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        errors = result.get("errors", [])
        if isinstance(errors, list):
            errors.append(error_msg)

    def get_protection_workflow_status(self) -> Dict[str, Any]:
        """Get current status of git protection workflow."""
        return {
            "is_git_repo": self._is_git_repository(),
            "current_branch": self._get_current_branch(),
            "has_staged_changes": self._has_staged_changes(),
            "has_unstaged_changes": self._has_unstaged_changes(),
            "git_status": self._get_git_status_summary(),
            "stats": self.stats.copy(),
        }


def main() -> None:
    """Demonstrate example usage of GitProtectionManager."""
    manager = GitProtectionManager()

    # Example: Create protection commit before quality tools
    protection_result = manager.create_protection_commit(
        operation_description="Python code quality improvements",
        target_files=["src/module.py", "tests/test_module.py"],
    )

    print("Protection commit:", protection_result["success"])
    if protection_result["commit_hash"]:
        print("Commit hash:", protection_result["commit_hash"])

    # Simulate quality tools execution here...

    # Example: Create completion commit after quality tools
    completion_result = manager.create_completion_commit(
        operation_description="Python code quality improvements",
        tools_executed=["black", "ruff", "mypy"],
        files_modified=["src/module.py"],
        execution_summary={"issues_fixed": 5, "files_formatted": 1},
    )

    print("Completion commit:", completion_result["success"])
    if completion_result["commit_hash"]:
        print("Commit hash:", completion_result["commit_hash"])


if __name__ == "__main__":
    main()
