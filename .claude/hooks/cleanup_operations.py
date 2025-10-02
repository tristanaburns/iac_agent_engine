"""Cleanup operations - unicode cleanup and file processing."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, cast

from process_runner import ProcessRunner


class CleanupOperations:
    """Handles all cleanup operations in one place."""

    def __init__(self):
        """Initialize cleanup operations."""
        self.session_file = Path(".claude/hooks/unicode_session.json")
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.modified_files: Set[str] = set()

    def clean_unicode_in_file(self, file_path: Path) -> Dict[str, Any]:
        """Clean unicode issues in a single file.

        Args:
            file_path: Path to file to clean

        Returns:
            Dictionary with results
        """
        if not file_path.exists() or not file_path.is_file():
            return {"processed": False, "error": "File not found"}

        # Skip binary files and excluded directories
        if not self._should_process_file(file_path):
            return {"processed": False, "reason": "Skipped"}

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Replace problematic unicode characters
            replacements = {
                "\u2013": "-",  # En dash
                "\u2014": "--",  # Em dash
                "\u2018": "'",  # Left single quote
                "\u2019": "'",  # Right single quote
                "\u201c": '"',  # Left double quote
                "\u201d": '"',  # Right double quote
                "\u2026": "...",  # Ellipsis
                "\u00a0": " ",  # Non-breaking space
            }

            unicode_replaced = 0
            for unicode_char, replacement in replacements.items():
                if unicode_char in content:
                    content = content.replace(unicode_char, replacement)
                    unicode_replaced += content.count(
                        replacement
                    ) - original_content.count(replacement)

            # Write back if changed
            modified = content != original_content
            if modified:
                file_path.write_text(content, encoding="utf-8")
                self._track_file(file_path)

            return {
                "processed": True,
                "modified": modified,
                "unicode_replaced": unicode_replaced,
                "file_path": str(file_path),
            }

        except Exception as e:
            return {"processed": False, "error": str(e)}

    def clean_unicode_in_directory(
        self, directory: Path, recursive: bool = True
    ) -> Dict[str, Any]:
        """Clean unicode issues in all files in directory.

        Args:
            directory: Directory to process
            recursive: Whether to process subdirectories

        Returns:
            Dictionary with results
        """
        if not self._validate_directory(directory):
            return self._create_error_result("Directory not found")

        stats = self._initialize_directory_stats()
        files = self._get_files_to_process(directory, recursive)

        self._process_files_for_unicode_cleanup(files, stats)

        return stats

    def _validate_directory(self, directory: Path) -> bool:
        """Validate that directory exists and is a directory.

        Args:
            directory: Directory path to validate

        Returns:
            True if directory is valid, False otherwise
        """
        return directory.exists() and directory.is_dir()

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error result dictionary.

        Args:
            error_message: Error message to include

        Returns:
            Error result dictionary
        """
        return {
            "files_processed": 0,
            "files_modified": 0,
            "error": error_message,
        }

    def _initialize_directory_stats(self) -> Dict[str, Any]:
        """Initialize statistics dictionary for directory processing.

        Returns:
            Initialized stats dictionary
        """
        return {
            "files_processed": 0,
            "files_modified": 0,
            "unicode_replaced": 0,
            "errors": [],
        }

    def _get_files_to_process(self, directory: Path, recursive: bool) -> List[Path]:
        """Get list of files to process from directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of file paths to process
        """
        if recursive:
            return [f for f in directory.rglob("*") if f.is_file()]
        else:
            return [f for f in directory.glob("*") if f.is_file()]

    def _process_files_for_unicode_cleanup(
        self, files: List[Path], stats: Dict[str, Any]
    ) -> None:
        """Process each file for unicode cleanup and update stats.

        Args:
            files: List of files to process
            stats: Statistics dictionary to update
        """
        for file_path in files:
            result = self.clean_unicode_in_file(file_path)
            self._update_stats_from_result(file_path, result, stats)

    def _update_stats_from_result(
        self, file_path: Path, result: Dict[str, Any], stats: Dict[str, Any]
    ) -> None:
        """Update statistics based on file processing result.

        Args:
            file_path: Path of the processed file
            result: Result from processing the file
            stats: Statistics dictionary to update
        """
        if result.get("processed"):
            stats["files_processed"] += 1
            if result.get("modified"):
                stats["files_modified"] += 1
                stats["unicode_replaced"] += cast(
                    int, result.get("unicode_replaced", 0)
                )
        elif result.get("error"):
            stats["errors"].append(f"{file_path}: {result['error']}")

    def clean_session_files(self) -> Dict[str, Any]:
        """Clean all files tracked in current session.

        Returns:
            Dictionary with results
        """
        session_files = self._get_session_files()
        if not session_files:
            return {"files_processed": 0, "files_modified": 0}

        stats: Dict[str, Any] = {
            "files_processed": 0,
            "files_modified": 0,
            "unicode_replaced": 0,
        }

        for file_path in session_files:
            result = self.clean_unicode_in_file(file_path)
            if result.get("processed"):
                stats["files_processed"] += 1
                if result.get("modified"):
                    stats["files_modified"] += 1
                    stats["unicode_replaced"] += cast(
                        int, result.get("unicode_replaced", 0)
                    )

        return stats

    def run_git_cleanup(self, project_path: Path) -> Dict[str, Any]:
        """Run git cleanup operations.

        Args:
            project_path: Path to git repository

        Returns:
            Dictionary with results
        """
        runner = ProcessRunner(working_dir=project_path)

        operations = []

        # Git status
        result = runner.run_command(["git", "status", "--porcelain"])
        if result["success"]:
            operations.append({"operation": "git_status", "success": True})
        else:
            operations.append(
                {
                    "operation": "git_status",
                    "success": False,
                    "error": result.get("error"),
                }
            )

        # Git add (if there are changes)
        if result["success"] and result["stdout"].strip():
            add_result = runner.run_command(["git", "add", "."])
            operations.append(
                {
                    "operation": "git_add",
                    "success": add_result["success"],
                    "error": (
                        add_result.get("error") if not add_result["success"] else None
                    ),
                }
            )

        return {"operations": operations}

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Skip excluded directories
        excluded_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            "dist",
            "build",
            ".mypy_cache",
            "backups",
            ".tox",
            "site-packages",
            "logs",
        }

        for part in file_path.parts:
            if part in excluded_dirs:
                return False

        # Only process text files
        text_extensions = {".py", ".md", ".txt", ".yml", ".yaml", ".json", ".js", ".ts"}
        return file_path.suffix in text_extensions

    def _track_file(self, file_path: Path) -> None:
        """Track file in session."""
        self.modified_files.add(str(file_path.absolute()))
        self._save_session()

    def _save_session(self) -> None:
        """Save session data."""
        try:
            data = {
                "modified_files": list(self.modified_files),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.session_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Fail silently

    def _get_session_files(self) -> List[Path]:
        """Get files from current session."""
        try:
            if self.session_file.exists():
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    return [
                        Path(f)
                        for f in data.get("modified_files", [])
                        if Path(f).exists()
                    ]
        except Exception:
            pass
        return []
