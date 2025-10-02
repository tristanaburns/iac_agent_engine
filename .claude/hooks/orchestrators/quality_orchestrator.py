"""Quality orchestrator following SOLID principles.

Single Responsibility: Coordinates all quality check operations.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from operations.logging.logger import Logger
    from operations.quality.black_formatter import BlackFormatter
    from operations.quality.isort_formatter import IsortFormatter


class QualityOrchestrator:
    """Orchestrates quality check operations."""

    def __init__(self) -> None:
        """Initialize quality orchestrator."""
        from operations.logging.logger import logger

        self.logger: "Logger" = logger
        self.logger.debug(
            "Initializing QualityOrchestrator with type validation enabled"
        )

        # Initialize quality checkers (lazy loading) with proper type annotations
        self._black_formatter: Optional["BlackFormatter"] = None
        self._isort_formatter: Optional["IsortFormatter"] = None

        self.logger.debug(
            "Type validation: Instance variables initialized with proper type annotations"
        )

    @property
    def black_formatter(self) -> "BlackFormatter":
        """Lazy load Black formatter."""
        if self._black_formatter is None:
            self.logger.debug(
                "Type validation: Loading BlackFormatter instance for lazy loading"
            )
            from operations.quality.black_formatter import BlackFormatter

            self._black_formatter = BlackFormatter()
            self.logger.debug(
                "Type validation: BlackFormatter instance loaded successfully"
            )
        return self._black_formatter

    @property
    def isort_formatter(self) -> "IsortFormatter":
        """Lazy load isort formatter."""
        if self._isort_formatter is None:
            self.logger.debug(
                "Type validation: Loading IsortFormatter instance for lazy loading"
            )
            from operations.quality.isort_formatter import IsortFormatter

            self._isort_formatter = IsortFormatter()
            self.logger.debug(
                "Type validation: IsortFormatter instance loaded successfully"
            )
        return self._isort_formatter

    def check_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Run quality checks on specific files.

        Args:
            file_paths: List of files to check

        Returns:
            Dictionary with check results
        """
        self.logger.info(f"Running quality checks on {len(file_paths)} files")
        self.logger.debug(
            f"Type validation: Processing {len(file_paths)} files with types: {[type(fp).__name__ for fp in file_paths]}"
        )

        results: Dict[str, Any] = {
            "files_checked": len(file_paths),
            "issues_found": 0,
            "checks": [],
            "success": True,
        }

        try:
            # Run Black check
            for file_path in file_paths:
                self.logger.debug(
                    f"Type validation: Processing file {file_path} with suffix {file_path.suffix}"
                )
                if file_path.suffix == ".py":
                    black_result = self.black_formatter.check_only(file_path)
                    results["checks"].append(
                        {
                            "type": "black",
                            "file": str(file_path),
                            "result": black_result,
                        }
                    )
                    if black_result.get("needs_formatting", False):
                        results["issues_found"] += 1

                    # Run isort check
                    isort_result = self.isort_formatter.format_imports(
                        file_path, check_only=True
                    )
                    results["checks"].append(
                        {
                            "type": "isort",
                            "file": str(file_path),
                            "result": isort_result,
                        }
                    )
                    if isort_result.get("needs_formatting", False):
                        results["issues_found"] += 1

            self.logger.info(
                f"Quality check complete: {results['issues_found']} issues found"
            )

        except Exception as e:
            self.logger.exception(f"Error during quality check: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def check_project(self, final_check: bool = False) -> Dict[str, Any]:
        """Run quality checks on entire project.

        Args:
            final_check: Whether this is a final check at session end

        Returns:
            Dictionary with check results
        """
        from utils.path_resolver import PathResolver

        resolver = PathResolver()

        check_type = "final" if final_check else "project"
        self.logger.info(f"Running {check_type} quality check")

        results: Dict[str, Any] = {
            "check_type": check_type,
            "issues_found": 0,
            "files_checked": 0,
            "checks": [],
            "success": True,
        }

        try:
            # Get all Python files in project
            python_files = resolver.get_python_files()
            results["files_checked"] = len(python_files)

            # Run checks on all files
            if python_files:
                file_results = self.check_files(python_files)
                results["issues_found"] = file_results.get("issues_found", 0)
                results["checks"] = file_results.get("checks", [])

            self.logger.info(
                f"{check_type.capitalize()} check complete: "
                f"{results['files_checked']} files, {results['issues_found']} issues"
            )

        except Exception as e:
            self.logger.exception(f"Error during {check_type} check: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def format_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Format files using quality tools.

        Args:
            file_paths: List of files to format

        Returns:
            Dictionary with formatting results
        """
        self.logger.info(f"Formatting {len(file_paths)} files")

        results: Dict[str, Any] = {
            "files_formatted": 0,
            "formatters": [],
            "success": True,
        }

        try:
            for file_path in file_paths:
                if file_path.suffix == ".py":
                    # Run Black formatter
                    black_result = self.black_formatter.format_files(file_path)
                    results["formatters"].append(
                        {
                            "type": "black",
                            "file": str(file_path),
                            "result": black_result,
                        }
                    )
                    if black_result.get("status") == "success":
                        results["files_formatted"] += len(
                            black_result.get("files_formatted", [])
                        )

                    # Run isort formatter
                    isort_result = self.isort_formatter.format_imports(file_path)
                    results["formatters"].append(
                        {
                            "type": "isort",
                            "file": str(file_path),
                            "result": isort_result,
                        }
                    )
                    if isort_result.get("status") == "success":
                        results["files_formatted"] += len(
                            isort_result.get("files_formatted", [])
                        )

            self.logger.success(f"Formatted {results['files_formatted']} files")

        except Exception as e:
            self.logger.exception(f"Error during formatting: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results
