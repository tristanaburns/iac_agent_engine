"""Cleanup orchestrator following SOLID principles.

Single Responsibility: Coordinates all cleanup operations.

This module implements robust dependency injection for unicode cleaning operations
with comprehensive fallback mechanisms and validation.
"""

import re
import sys
import unicodedata
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union


class UnicodeManagerProtocol(Protocol):
    """Protocol defining the expected interface for unicode managers."""

    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean unicode characters from a file.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results including 'cleaned' boolean
        """
        ...


class BaseUnicodeCleaner(ABC):
    """Abstract base class for unicode cleaning implementations."""

    def __init__(self, name: str) -> None:
        """Initialize unicode cleaner.

        Args:
            name: Name identifier for this cleaner
        """
        self.name = name

    @abstractmethod
    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean unicode characters from a file.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results
        """
        pass

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed.

        Args:
            file_path: Path to check

        Returns:
            True if file should be processed
        """
        text_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".go",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".md",
            ".txt",
            ".rst",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".xml",
            ".toml",
        }

        if file_path.suffix.lower() not in text_extensions:
            return False

        skip_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".mypy_cache",
            ".pytest_cache",
            "backups",
        }

        for parent in file_path.parents:
            if parent.name in skip_dirs:
                return False

        return True


class PrimaryUnicodeManager(BaseUnicodeCleaner):
    """Wrapper for the existing UnicodeManager from tools."""

    def __init__(self, unicode_manager: Any) -> None:
        """Initialize with existing unicode manager.

        Args:
            unicode_manager: The original UnicodeManager instance
        """
        super().__init__("PrimaryUnicodeManager")
        self.unicode_manager = unicode_manager

    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean file using the original UnicodeManager.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results
        """
        try:
            # Convert to Path object
            path = Path(file_path) if isinstance(file_path, str) else file_path

            # Use the existing process_file method
            result = self.unicode_manager.process_file(path)

            # Adapt the result to match expected interface
            return {
                "cleaned": result.get("modified", False),
                "unicode_replaced": result.get("unicode_replaced", 0),
                "unicode_deleted": result.get("unicode_deleted", 0),
                "error": result.get("error"),
                "cleaner": self.name,
            }
        except Exception as e:
            return {
                "cleaned": False,
                "error": f"Primary unicode manager failed: {str(e)}",
                "cleaner": self.name,
            }


class BuiltinUnicodeCleaner(BaseUnicodeCleaner):
    """Fallback unicode cleaner using Python built-in methods."""

    def __init__(self) -> None:
        """Initialize builtin unicode cleaner."""
        super().__init__("BuiltinUnicodeCleaner")

    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean file using Python built-in unicode methods.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results
        """
        try:
            path = Path(file_path) if isinstance(file_path, str) else file_path

            if not self._should_process_file(path):
                return {
                    "cleaned": False,
                    "error": "File excluded from processing",
                    "cleaner": self.name,
                }

            # Read file content
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Normalize unicode using built-in methods
            normalized_content = unicodedata.normalize("NFKD", original_content)

            # Remove non-ASCII characters
            cleaned_content = "".join(
                char for char in normalized_content if ord(char) < 128
            )

            changes_made = cleaned_content != original_content

            if changes_made:
                # Write cleaned content back
                with open(path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

            return {
                "cleaned": changes_made,
                "unicode_replaced": len(original_content) - len(cleaned_content),
                "error": None,
                "cleaner": self.name,
            }

        except Exception as e:
            return {
                "cleaned": False,
                "error": f"Builtin unicode cleaner failed: {str(e)}",
                "cleaner": self.name,
            }


class RegexUnicodeCleaner(BaseUnicodeCleaner):
    """Regex-based fallback unicode cleaner."""

    def __init__(self) -> None:
        """Initialize regex unicode cleaner."""
        super().__init__("RegexUnicodeCleaner")

        # Common unicode patterns to clean
        self.unicode_patterns = [
            (r"[\u2013\u2014]", "-"),  # Em/En dashes
            (r"[\u2018\u2019]", "'"),  # Smart quotes
            (r"[\u201C\u201D]", '"'),  # Smart double quotes
            (r"[\u2026]", "..."),  # Ellipsis
            (r"[\u00A0]", " "),  # Non-breaking space
            (r"[\u2192]", "->"),  # Right arrow
            (r"[\u2190]", "<-"),  # Left arrow
            (r"[\u2022]", "*"),  # Bullet point
        ]

    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean file using regex patterns.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results
        """
        try:
            path = Path(file_path) if isinstance(file_path, str) else file_path

            if not self._should_process_file(path):
                return {
                    "cleaned": False,
                    "error": "File excluded from processing",
                    "cleaner": self.name,
                }

            # Read file content
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original_content = content
            replacements_made = 0

            # Apply regex patterns
            for pattern, replacement in self.unicode_patterns:
                matches = len(re.findall(pattern, content))
                content = re.sub(pattern, replacement, content)
                replacements_made += matches

            # Remove any remaining non-ASCII characters
            cleaned_content = re.sub(r"[^\x00-\x7F]", "", content)
            additional_removals = len(content) - len(cleaned_content)

            changes_made = cleaned_content != original_content

            if changes_made:
                # Write cleaned content back
                with open(path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

            return {
                "cleaned": changes_made,
                "unicode_replaced": replacements_made + additional_removals,
                "error": None,
                "cleaner": self.name,
            }

        except Exception as e:
            return {
                "cleaned": False,
                "error": f"Regex unicode cleaner failed: {str(e)}",
                "cleaner": self.name,
            }


class BasicAsciiCleaner(BaseUnicodeCleaner):
    """Last resort ASCII-only cleaner."""

    def __init__(self) -> None:
        """Initialize basic ASCII cleaner."""
        super().__init__("BasicAsciiCleaner")

    def clean_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Clean file by removing all non-ASCII characters.

        Args:
            file_path: Path to the file to clean

        Returns:
            Dictionary with cleaning results
        """
        try:
            path = Path(file_path) if isinstance(file_path, str) else file_path

            if not self._should_process_file(path):
                return {
                    "cleaned": False,
                    "error": "File excluded from processing",
                    "cleaner": self.name,
                }

            # Read file content
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Keep only ASCII characters
            cleaned_content = "".join(
                char for char in original_content if ord(char) < 128
            )

            changes_made = cleaned_content != original_content

            if changes_made:
                # Write cleaned content back
                with open(path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

            return {
                "cleaned": changes_made,
                "unicode_replaced": len(original_content) - len(cleaned_content),
                "error": None,
                "cleaner": self.name,
            }

        except Exception as e:
            return {
                "cleaned": False,
                "error": f"Basic ASCII cleaner failed: {str(e)}",
                "cleaner": self.name,
            }


class UnicodeManagerFactory:
    """Factory for creating and validating unicode managers with fallbacks."""

    def __init__(self, logger: Any) -> None:
        """Initialize unicode manager factory.

        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger
        self._validated_manager: Optional[UnicodeManagerProtocol] = None

    def create_unicode_manager(self) -> UnicodeManagerProtocol:
        """Create and validate a unicode manager with fallbacks.

        Returns:
            A validated unicode manager

        Raises:
            RuntimeError: If all fallback mechanisms fail
        """
        if self._validated_manager is not None:
            return self._validated_manager

        self.logger.info("Creating unicode manager with dependency injection")

        # Try primary implementation first
        primary_manager = self._try_primary_unicode_manager()
        if primary_manager and self._validate_unicode_manager(primary_manager):
            self.logger.info("Primary UnicodeManager loaded and validated successfully")
            self._validated_manager = primary_manager
            return primary_manager

        # Try fallback implementations
        fallback_classes = [
            BuiltinUnicodeCleaner,
            RegexUnicodeCleaner,
            BasicAsciiCleaner,
        ]

        for fallback_class in fallback_classes:
            try:
                self.logger.info(f"Attempting fallback: {fallback_class.__name__}")
                fallback_manager = fallback_class()  # type: ignore[abstract]

                if self._validate_unicode_manager(fallback_manager):
                    self.logger.warning(
                        f"Using fallback unicode cleaner: {fallback_class.__name__}"
                    )
                    self._validated_manager = fallback_manager
                    return fallback_manager
                else:
                    self.logger.error(
                        f"Fallback validation failed: {fallback_class.__name__}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Fallback creation failed {fallback_class.__name__}: {e}"
                )
                continue

        # All fallbacks failed - this is a critical error
        error_msg = (
            "CRITICAL: All unicode cleaning mechanisms failed - file corruption risk"
        )
        self.logger.critical(error_msg)
        raise RuntimeError(error_msg)

    def _try_primary_unicode_manager(self) -> Optional[PrimaryUnicodeManager]:
        """Try to load the primary UnicodeManager from tools.

        Returns:
            PrimaryUnicodeManager if successful, None otherwise
        """
        try:
            from utils.path_resolver import PathResolver

            resolver = PathResolver()
            sys.path.insert(0, str(resolver.tools_dir))

            self.logger.debug(f"Attempting to import from: {resolver.tools_dir}")

            from tools.unicode_manager import UnicodeManager

            unicode_manager = UnicodeManager()
            self.logger.debug("Primary UnicodeManager imported successfully")

            return PrimaryUnicodeManager(unicode_manager)

        except ImportError as e:
            self.logger.warning(f"Primary UnicodeManager import failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Primary UnicodeManager creation failed: {e}")
            return None

    def _validate_unicode_manager(self, manager: UnicodeManagerProtocol) -> bool:
        """Validate that a unicode manager actually works.

        Args:
            manager: Unicode manager to validate

        Returns:
            True if manager is functional
        """
        try:
            self.logger.debug(
                f"Validating unicode manager: {getattr(manager, 'name', 'unknown')}"
            )

            # Test with sample unicode content
            test_content = "Hello \u2192 World \u2713"

            # Create temporary test file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(test_content)
                test_file = Path(f.name)

            try:
                # Test the clean_file method
                result = manager.clean_file(test_file)

                # Validate result structure
                required_keys = {"cleaned", "error", "cleaner"}
                if not all(key in result for key in required_keys):
                    self.logger.error(f"Invalid result structure: {result}")
                    return False

                # Check if operation was successful
                if result.get("error"):
                    self.logger.error(f"Manager validation error: {result['error']}")
                    return False

                self.logger.debug(f"Manager validation successful: {result}")
                return True

            finally:
                # Clean up test file
                try:
                    test_file.unlink()
                except Exception:
                    pass

        except Exception as e:
            self.logger.error(f"Unicode manager validation failed: {e}")
            return False


class CleanupOrchestrator:
    """Orchestrates cleanup operations with robust unicode dependency management."""

    def __init__(self) -> None:
        """Initialize cleanup orchestrator."""
        from operations.logging.logger import logger

        self.logger = logger
        self.unicode_factory = UnicodeManagerFactory(self.logger)
        self._unicode_manager: Optional[UnicodeManagerProtocol] = None

    def get_unicode_manager(self) -> UnicodeManagerProtocol:
        """Get validated unicode manager with dependency injection.

        Returns:
            Validated unicode manager

        Raises:
            RuntimeError: If all unicode cleaning mechanisms fail
        """
        if self._unicode_manager is None:
            try:
                self.logger.debug(
                    "Initializing unicode manager with dependency injection"
                )
                self._unicode_manager = self.unicode_factory.create_unicode_manager()
                self.logger.info("Unicode manager initialized successfully")
            except RuntimeError as e:
                self.logger.critical(f"Unicode manager initialization failed: {e}")
                raise
            except Exception as e:
                self.logger.critical(
                    f"Unexpected error in unicode manager initialization: {e}"
                )
                raise RuntimeError(f"Unicode manager initialization failed: {e}")

        return self._unicode_manager

    def cleanup_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Clean up specific files with robust unicode management.

        Args:
            file_paths: List of files to clean

        Returns:
            Dictionary with cleanup results
        """
        self.logger.info(f"Running cleanup on {len(file_paths)} files")
        results = self._initialize_cleanup_results()

        try:
            unicode_manager = self._setup_unicode_manager(results)
            self._process_all_files(file_paths, unicode_manager, results)
            self._log_cleanup_completion(results)

        except RuntimeError as e:
            self._handle_critical_unicode_failure(results, e)
        except Exception as e:
            self._handle_unexpected_error(results, e)

        return results

    def _initialize_cleanup_results(self) -> Dict[str, Any]:
        """Initialize the results dictionary for cleanup operations.

        Returns:
            Initialized results dictionary
        """
        return {
            "files_cleaned": 0,
            "files_skipped": 0,
            "cleanups": [],
            "success": True,
            "unicode_manager_info": None,
        }

    def _setup_unicode_manager(self, results: Dict[str, Any]) -> UnicodeManagerProtocol:
        """Setup unicode manager and update results with manager info.

        Args:
            results: Results dictionary to update

        Returns:
            Unicode manager instance
        """
        unicode_manager = self.get_unicode_manager()
        results["unicode_manager_info"] = getattr(unicode_manager, "name", "unknown")

        self.logger.info(f"Using unicode manager: {results['unicode_manager_info']}")

        return unicode_manager

    def _process_all_files(
        self,
        file_paths: List[Path],
        unicode_manager: UnicodeManagerProtocol,
        results: Dict[str, Any],
    ) -> None:
        """Process all files in the list with the unicode manager.

        Args:
            file_paths: List of files to process
            unicode_manager: Unicode manager to use for cleaning
            results: Results dictionary to update
        """
        for file_path in file_paths:
            try:
                self._process_single_file(file_path, unicode_manager, results)
            except Exception as e:
                self._handle_file_processing_error(file_path, results, e)

    def _process_single_file(
        self,
        file_path: Path,
        unicode_manager: UnicodeManagerProtocol,
        results: Dict[str, Any],
    ) -> None:
        """Process a single file for cleanup.

        Args:
            file_path: Path to the file to process
            unicode_manager: Unicode manager to use for cleaning
            results: Results dictionary to update
        """
        if self._should_cleanup_file(file_path):
            self._perform_file_cleanup(file_path, unicode_manager, results)
        else:
            self._skip_file_cleanup(file_path, results)

    def _perform_file_cleanup(
        self,
        file_path: Path,
        unicode_manager: UnicodeManagerProtocol,
        results: Dict[str, Any],
    ) -> None:
        """Perform cleanup on a file and update results.

        Args:
            file_path: Path to the file to clean
            unicode_manager: Unicode manager to use for cleaning
            results: Results dictionary to update
        """
        self.logger.debug(f"Processing file: {file_path}")
        cleanup_result = unicode_manager.clean_file(file_path)

        self._add_cleanup_result(file_path, cleanup_result, results)
        self._update_cleanup_counters(file_path, cleanup_result, results)

    def _skip_file_cleanup(self, file_path: Path, results: Dict[str, Any]) -> None:
        """Skip cleanup for a file and update counters.

        Args:
            file_path: Path to the file being skipped
            results: Results dictionary to update
        """
        self._increment_skipped_count(results)
        self.logger.debug(f"Skipping cleanup for {file_path}")

    def _add_cleanup_result(
        self, file_path: Path, cleanup_result: Dict[str, Any], results: Dict[str, Any]
    ) -> None:
        """Add cleanup result to the results list.

        Args:
            file_path: Path to the file that was processed
            cleanup_result: Result from the cleanup operation
            results: Results dictionary to update
        """
        cleanup_list = results["cleanups"]
        assert isinstance(cleanup_list, list)
        cleanup_list.append(
            {
                "file": str(file_path),
                "result": cleanup_result,
            }
        )

    def _update_cleanup_counters(
        self, file_path: Path, cleanup_result: Dict[str, Any], results: Dict[str, Any]
    ) -> None:
        """Update cleanup counters based on cleanup result.

        Args:
            file_path: Path to the file that was processed
            cleanup_result: Result from the cleanup operation
            results: Results dictionary to update
        """
        if cleanup_result.get("cleaned", False):
            self._increment_cleaned_count(results)
            self.logger.debug(f"Cleaned file: {file_path}")
        else:
            self._increment_skipped_count(results)
            if cleanup_result.get("error"):
                self.logger.warning(
                    f"File cleanup failed for {file_path}: {cleanup_result['error']}"
                )

    def _increment_cleaned_count(self, results: Dict[str, Any]) -> None:
        """Increment the cleaned files counter.

        Args:
            results: Results dictionary to update
        """
        files_cleaned = results["files_cleaned"]
        assert isinstance(files_cleaned, int)
        results["files_cleaned"] = files_cleaned + 1

    def _increment_skipped_count(self, results: Dict[str, Any]) -> None:
        """Increment the skipped files counter.

        Args:
            results: Results dictionary to update
        """
        files_skipped = results["files_skipped"]
        assert isinstance(files_skipped, int)
        results["files_skipped"] = files_skipped + 1

    def _handle_file_processing_error(
        self, file_path: Path, results: Dict[str, Any], error: Exception
    ) -> None:
        """Handle errors that occur during file processing.

        Args:
            file_path: Path to the file that caused the error
            results: Results dictionary to update
            error: The exception that occurred
        """
        self.logger.error(f"Error processing individual file {file_path}: {error}")

        error_result = {
            "cleaned": False,
            "error": f"Processing error: {str(error)}",
            "cleaner": "error",
        }

        self._add_cleanup_result(file_path, error_result, results)
        self._increment_skipped_count(results)

    def _log_cleanup_completion(self, results: Dict[str, Any]) -> None:
        """Log the completion of cleanup operations.

        Args:
            results: Results dictionary with completion stats
        """
        self.logger.info(
            f"Cleanup complete: {results['files_cleaned']} cleaned, "
            f"{results['files_skipped']} skipped using {results['unicode_manager_info']}"
        )

    def _handle_critical_unicode_failure(
        self, results: Dict[str, Any], error: RuntimeError
    ) -> None:
        """Handle critical unicode manager failures.

        Args:
            results: Results dictionary to update
            error: The runtime error that occurred
        """
        self.logger.critical(f"CRITICAL: Unicode cleanup failed - {error}")
        results["success"] = False
        results["error"] = f"Critical unicode manager failure: {str(error)}"
        results["critical_failure"] = True

    def _handle_unexpected_error(
        self, results: Dict[str, Any], error: Exception
    ) -> None:
        """Handle unexpected errors during cleanup.

        Args:
            results: Results dictionary to update
            error: The unexpected exception that occurred
        """
        self.logger.exception(f"Unexpected error during cleanup: {error}")
        results["success"] = False
        results["error"] = str(error)

    def final_cleanup(self) -> Dict[str, Any]:
        """Perform final cleanup at session end with dependency validation.

        Returns:
            Dictionary with cleanup results
        """
        self.logger.info("Running final cleanup")

        results = {
            "cleanup_type": "final",
            "operations": [],
            "success": True,
            "dependency_status": None,
        }

        try:
            # Validate unicode manager status
            try:
                unicode_manager = self.get_unicode_manager()
                results["dependency_status"] = {
                    "unicode_manager": getattr(unicode_manager, "name", "unknown"),
                    "status": "available",
                }
                self.logger.info(
                    f"Unicode dependency status: {results['dependency_status']}"
                )
            except Exception as e:
                results["dependency_status"] = {
                    "unicode_manager": "failed",
                    "status": "unavailable",
                    "error": str(e),
                }
                self.logger.error(f"Unicode dependency check failed: {e}")

            # Clean temporary files
            temp_cleanup = self._cleanup_temp_files()
            operations_list = results["operations"]
            assert isinstance(operations_list, list)
            operations_list.append(
                {
                    "type": "temp_files",
                    "result": temp_cleanup,
                }
            )

            # Clean backup files older than retention period
            backup_cleanup = self._cleanup_old_backups()
            operations_list = results["operations"]
            assert isinstance(operations_list, list)
            operations_list.append(
                {
                    "type": "old_backups",
                    "result": backup_cleanup,
                }
            )

            self.logger.info("Final cleanup completed successfully")

        except Exception as e:
            self.logger.exception(f"Error during final cleanup: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def _should_cleanup_file(self, file_path: Path) -> bool:
        """Check if file should be cleaned.

        Args:
            file_path: Path to check

        Returns:
            True if file should be cleaned
        """
        # Skip non-text files
        text_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".go",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".md",
            ".txt",
            ".rst",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".xml",
            ".toml",
        }

        if file_path.suffix.lower() not in text_extensions:
            return False

        # Skip files in certain directories
        skip_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".mypy_cache",
            ".pytest_cache",
        }

        for parent in file_path.parents:
            if parent.name in skip_dirs:
                return False

        return True

    def _cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files.

        Returns:
            Cleanup results
        """
        from utils.path_resolver import PathResolver

        resolver = PathResolver()

        temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.swp"]
        files_deleted = 0

        try:
            for pattern in temp_patterns:
                temp_files = list(resolver.project_dir.glob(f"**/{pattern}"))
                for temp_file in temp_files:
                    try:
                        temp_file.unlink()
                        files_deleted += 1
                        self.logger.debug(f"Deleted temp file: {temp_file}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete {temp_file}: {e}")

            return {
                "success": True,
                "files_deleted": files_deleted,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "files_deleted": files_deleted,
            }

    def _cleanup_old_backups(self, days: int = 7) -> Dict[str, Any]:
        """Clean up old backup files.

        Args:
            days: Delete backups older than this many days

        Returns:
            Cleanup results
        """
        from datetime import datetime, timedelta

        from utils.path_resolver import PathResolver

        resolver = PathResolver()
        backups_dir = resolver.backups_dir

        if not backups_dir.exists():
            return {
                "success": True,
                "files_deleted": 0,
                "message": "No backups directory",
            }

        cutoff_time = datetime.now() - timedelta(days=days)
        files_deleted = 0

        try:
            for backup_file in backups_dir.rglob("*"):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            backup_file.unlink()
                            files_deleted += 1
                            self.logger.debug(f"Deleted old backup: {backup_file}")
                        except Exception as e:
                            self.logger.warning(f"Could not delete {backup_file}: {e}")

            return {
                "success": True,
                "files_deleted": files_deleted,
                "cutoff_days": days,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "files_deleted": files_deleted,
            }
