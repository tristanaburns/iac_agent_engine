#!/usr/bin/env python3
"""
Python Quality Manager Module.

=============================

Comprehensive Python code quality management including:
- Linting (ruff, flake8, pylint)
- Type checking (mypy)
- Complexity analysis (radon, xenon)
- SAST security analysis (bandit, safety)
- Formatting (black, isort, autopep8)
- Auto-fixing (autoflake, unify, pyupgrade)

Author: System
Version: 1.0.0
"""

import json
import logging
import shutil
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PythonQualityManager:
    """
    Manages comprehensive Python code quality operations using external tools only.

    IMPORTANT: This class does NOT implement custom fixing or analysis logic.
    All actual work is performed by external tools:
    - Formatting: black, isort, autopep8
    - Auto-fixing: autoflake, pyupgrade, unify
    - Linting: ruff, flake8, pylint
    - Type checking: mypy
    - Complexity: radon, xenon
    - Security: bandit, safety

    This manager only orchestrates tool execution and aggregates results.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize Python Quality Manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_default_config()
        self.pyproject_config: Dict[str, Any] = self._discover_pyproject_config()
        self.stats: Dict[str, int] = {
            "files_processed": 0,
            "files_modified": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "errors": 0,
        }

        if config_path and Path(config_path).exists():
            self._load_config(config_path)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "tools": {
                "formatters": {
                    "black": {
                        "enabled": True,
                        "line_length": 120,
                        "target_version": ["py311"],
                        "args": ["--line-length", "120", "--target-version", "py311"],
                    },
                    "isort": {
                        "enabled": True,
                        "profile": "black",
                        "args": ["--profile", "black"],
                    },
                    "autopep8": {
                        "enabled": False,
                        "args": ["--in-place", "--aggressive", "--aggressive"],
                    },
                },
                "auto_fixers": {
                    "autoflake": {
                        "enabled": True,
                        "args": [
                            "--in-place",
                            "--remove-all-unused-imports",
                            "--remove-unused-variables",
                            "--remove-duplicate-keys",
                            "--expand-star-imports",
                        ],
                    },
                    "pyupgrade": {"enabled": True, "args": ["--py311-plus"]},
                    "unify": {"enabled": True, "args": ["--in-place", "--quote", '"']},
                },
                "linters": {
                    "ruff": {"enabled": True, "fix": True, "args": ["check", "--fix"]},
                    "flake8": {
                        "enabled": True,
                        "args": ["--max-line-length=120", "--extend-ignore=E203,W503"],
                    },
                    "pylint": {"enabled": False, "args": ["--rcfile=.pylintrc"]},
                    "pydocstyle": {
                        "enabled": True,
                        "args": ["--convention=pep257", "--add-ignore=D213,D203"],
                    },
                    "pycodestyle": {
                        "enabled": False,
                        "args": ["--max-line-length=120"],
                    },
                },
                "type_checkers": {
                    "mypy": {
                        "enabled": True,
                        "args": ["--strict", "--ignore-missing-imports"],
                    }
                },
                "complexity_analyzers": {
                    "radon": {"enabled": True, "cc_threshold": 10, "mi_threshold": "B"},
                    "xenon": {"enabled": True, "max_absolute": "B", "max_modules": "A"},
                },
                "security_analyzers": {
                    "bandit": {"enabled": True, "args": ["-r", "-f", "json"]},
                    "safety": {"enabled": True, "args": ["check", "--json"]},
                },
            },
            "file_patterns": ["*.py"],
            "excluded_dirs": [
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
            ],
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "create_reports": True,
            "auto_fix_enabled": True,
        }

    def _load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Deep merge with defaults
            self._deep_merge_config(self.config, user_config)
            logger.info(f"Loaded configuration from: {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")

    def _deep_merge_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value

    def _discover_pyproject_config(self) -> Dict[str, Any]:
        """
        Discover and load pyproject.toml configuration from current directory upward.

        Returns:
            Dictionary with pyproject.toml tool configurations or empty dict
        """
        current_dir = Path.cwd()

        # Search upward for pyproject.toml
        for parent in [current_dir] + list(current_dir.parents):
            pyproject_path = parent / "pyproject.toml"
            if pyproject_path.exists():
                try:
                    with open(pyproject_path, "rb") as f:
                        return tomllib.load(f)
                except Exception as e:
                    logger.warning(
                        f"Failed to load pyproject.toml from {pyproject_path}: {e}"
                    )
                    continue

        return {}

    def _apply_black_config(
        self, merged_config: Dict[str, Any], pyproject_tool_config: Dict[str, Any]
    ) -> None:
        """
        Apply black-specific configuration from pyproject.toml.

        Args:
            merged_config: Configuration to update
            pyproject_tool_config: Configuration from pyproject.toml
        """
        if "line-length" in pyproject_tool_config:
            merged_config["line_length"] = pyproject_tool_config["line-length"]
            merged_config["args"] = [
                "--line-length",
                str(pyproject_tool_config["line-length"]),
            ]
            if "target-version" in pyproject_tool_config:
                for version in pyproject_tool_config["target-version"]:
                    merged_config["args"].extend(["--target-version", version])

    def _apply_ruff_config(
        self, merged_config: Dict[str, Any], pyproject_tool_config: Dict[str, Any]
    ) -> None:
        """
        Apply ruff-specific configuration from pyproject.toml.

        Args:
            merged_config: Configuration to update
            pyproject_tool_config: Configuration from pyproject.toml
        """
        if "line-length" in pyproject_tool_config:
            merged_config["line_length"] = pyproject_tool_config["line-length"]
            # Update existing args or add new ones
            args = merged_config.get("args", [])
            # Remove existing line-length args
            args = [
                arg
                for i, arg in enumerate(args)
                if not (
                    arg == "--line-length" or (i > 0 and args[i - 1] == "--line-length")
                )
            ]
            args.extend(["--line-length", str(pyproject_tool_config["line-length"])])
            merged_config["args"] = args

    def _apply_isort_config(
        self, merged_config: Dict[str, Any], pyproject_tool_config: Dict[str, Any]
    ) -> None:
        """
        Apply isort-specific configuration from pyproject.toml.

        Args:
            merged_config: Configuration to update
            pyproject_tool_config: Configuration from pyproject.toml
        """
        if "profile" in pyproject_tool_config:
            merged_config["profile"] = pyproject_tool_config["profile"]
            merged_config["args"] = [
                "--profile",
                pyproject_tool_config["profile"],
            ]

    def _apply_pydocstyle_config(
        self, merged_config: Dict[str, Any], pyproject_tool_config: Dict[str, Any]
    ) -> None:
        """
        Apply pydocstyle-specific configuration from pyproject.toml.

        Args:
            merged_config: Configuration to update
            pyproject_tool_config: Configuration from pyproject.toml
        """
        if "convention" in pyproject_tool_config:
            merged_config["convention"] = pyproject_tool_config["convention"]
            # Update args to include convention
            args = merged_config.get("args", [])
            args = [arg for arg in args if not arg.startswith("--convention")]
            args.extend(["--convention", pyproject_tool_config["convention"]])
            merged_config["args"] = args

    def _get_tool_config(self, tool_name: str, category: str) -> Dict[str, Any]:
        """
        Get tool configuration with pyproject.toml override and fallback to defaults.

        Args:
            tool_name: Name of the tool (e.g., 'black', 'ruff', 'mypy')
            category: Tool category (e.g., 'formatters', 'linters', 'type_checkers')

        Returns:
            Merged configuration dictionary
        """
        # Start with default config
        default_config = self.config["tools"].get(category, {}).get(tool_name, {})
        merged_config = default_config.copy()

        # Check for pyproject.toml tool configuration
        pyproject_tool_config = self.pyproject_config.get("tool", {}).get(tool_name, {})

        # Apply tool-specific configurations if present
        if pyproject_tool_config:
            # Use dispatch pattern for tool-specific configurations
            tool_config_handlers = {
                "black": self._apply_black_config,
                "ruff": self._apply_ruff_config,
                "isort": self._apply_isort_config,
                "pydocstyle": self._apply_pydocstyle_config,
                "mypy": lambda config, pyproject: None,  # mypy uses pyproject.toml directly
            }

            handler = tool_config_handlers.get(tool_name)
            if handler:
                handler(merged_config, pyproject_tool_config)

        return merged_config

    def _is_ui_component(self, file_path: Path) -> bool:
        """
        Detect if a file is a UI component based on common patterns.

        Args:
            file_path: Path to the Python file

        Returns:
            True if file appears to be a UI component
        """
        # Common UI patterns to check
        ui_patterns = [
            # Framework patterns
            "ui/",
            "gui/",
            "frontend/",
            "templates/",
            "views/",
            "components/",
            # File name patterns
            "_ui.py",
            "_gui.py",
            "_view.py",
            "_widget.py",
            "_component.py",
            "ui_",
            "gui_",
            "view_",
            "widget_",
            "component_",
            # Framework-specific patterns
            "tkinter",
            "qt",
            "gtk",
            "kivy",
            "flet",
            "streamlit",
            "gradio",
            "dash",
            "flask",
            "django",
            "fastapi",
            "starlette",
        ]

        file_path_str = str(file_path).lower()

        # Check path components and filename
        for pattern in ui_patterns:
            if pattern in file_path_str:
                return True

        # Check file content for UI imports (quick scan)
        import contextlib

        with contextlib.suppress(Exception):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)  # Read first 2KB for performance
                ui_imports = [
                    "tkinter",
                    "PyQt",
                    "PySide",
                    "gtk",
                    "kivy",
                    "flet",
                    "streamlit",
                    "gradio",
                    "dash",
                    "flask",
                    "django",
                    "fastapi",
                    "starlette",
                    "tornado",
                    "bottle",
                ]
                for ui_import in ui_imports:
                    if ui_import in content:
                        return True

        return False

    def _get_complexity_threshold(self, file_path: Path) -> int:
        """
        Get complexity threshold based on component type.

        Args:
            file_path: Path to the Python file

        Returns:
            Complexity threshold (<10 for non-UI, <15 for UI components)
        """
        return 15 if self._is_ui_component(file_path) else 10

    def _is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available in the system."""
        return shutil.which(tool_name) is not None

    def _run_command(
        self, cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300
    ) -> Tuple[bool, str, str]:
        """
        Run external tool command and return success status, stdout, stderr.

        This method ONLY executes external tools - no custom logic or modifications.
        The tools themselves (black, ruff, mypy, etc.) do all the actual work.

        Args:
            cmd: Command to run (external tool only)
            cwd: Working directory
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Execute the external tool as-is, no custom modifications
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)

    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed."""
        # Skip backup files
        if file_path.name.endswith(".backup"):
            return False

        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.config["excluded_dirs"]:
                return False

        # Check file extension
        if not any(
            file_path.match(pattern) for pattern in self.config["file_patterns"]
        ):
            return False

        # Check file size
        try:
            if file_path.stat().st_size > self.config["max_file_size"]:
                return False
        except OSError:
            return False

        return True

    def format_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Format a Python file using external formatting tools only.

        Uses actual tools (black, isort, autoflake, etc.) - no custom formatting logic.
        The tools themselves handle all formatting and fixing operations.
        """
        result: Dict[str, Any] = {
            "file": str(file_path),
            "formatted": False,
            "tools_used": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        # Run formatters in order: autoflake -> pyupgrade -> unify -> black -> isort
        formatter_order = ["autoflake", "pyupgrade", "unify", "black", "isort"]

        for formatter_name in formatter_order:
            # Get tool config with pyproject.toml override
            if formatter_name in ["autoflake", "pyupgrade", "unify"]:
                tool_config = self._get_tool_config(formatter_name, "auto_fixers")
            else:
                tool_config = self._get_tool_config(formatter_name, "formatters")

            if not tool_config.get("enabled", False):
                continue

            if not self._is_tool_available(formatter_name):
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"{formatter_name} not available")
                continue

            cmd = [formatter_name] + tool_config["args"] + [str(file_path)]
            success, stdout, stderr = self._run_command(cmd)

            if success:
                tools_used = result.get("tools_used", [])
                if isinstance(tools_used, list):
                    tools_used.append(formatter_name)
                result["formatted"] = True
            else:
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"{formatter_name}: {stderr}")

        return result

    def _get_enabled_linters(self) -> List[str]:
        """
        Get list of enabled linter names.

        Returns:
            List of enabled linter names
        """
        linter_names = ["ruff", "flake8", "pylint", "pydocstyle", "pycodestyle"]
        enabled_linters = []

        for linter_name in linter_names:
            linter_config = self._get_tool_config(linter_name, "linters")
            if linter_config.get("enabled", False) and self._is_tool_available(
                linter_name
            ):
                enabled_linters.append(linter_name)

        return enabled_linters

    def _run_single_linter(
        self, linter_name: str, file_path: Path
    ) -> Tuple[bool, str, str]:
        """
        Run a single linter on the file.

        Args:
            linter_name: Name of the linter to run
            file_path: Path to the file to lint

        Returns:
            Tuple of (success, stdout, stderr)
        """
        linter_config = self._get_tool_config(linter_name, "linters")
        cmd = [linter_name] + linter_config["args"] + [str(file_path)]
        return self._run_command(cmd)

    def _process_ruff_results(
        self,
        linter_config: Dict[str, Any],
        success: bool,
        stdout: str,
        stderr: str,
        result: Dict[str, Any],
    ) -> None:
        """
        Process ruff linter results with fix capability.

        Args:
            linter_config: Configuration for ruff
            success: Whether the command succeeded
            stdout: Standard output
            stderr: Standard error
            result: Result dictionary to update
        """
        if linter_config.get("fix", False):
            if success:
                result["issues_fixed"] += stdout.count("Fixed")
            else:
                result["issues"].append({"tool": "ruff", "output": stderr})
        else:
            self._process_standard_linter_results("ruff", success, stderr, result)

    def _process_standard_linter_results(
        self, linter_name: str, success: bool, stderr: str, result: Dict[str, Any]
    ) -> None:
        """
        Process standard linter results.

        Args:
            linter_name: Name of the linter
            success: Whether the command succeeded
            stderr: Standard error output
            result: Result dictionary to update
        """
        if not success and stderr:
            result["issues"].append({"tool": linter_name, "output": stderr})
            result["issues_found"] += stderr.count("\n") if stderr else 0

    def lint_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Lint a Python file using external linting tools only.

        Uses actual tools (ruff, flake8, pylint) - no custom linting logic.
        Tools with --fix capabilities handle their own auto-fixing.
        """
        result: Dict[str, Any] = {
            "file": str(file_path),
            "issues_found": 0,
            "issues_fixed": 0,
            "tools_used": [],
            "issues": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        enabled_linters = self._get_enabled_linters()

        for linter_name in enabled_linters:
            success, stdout, stderr = self._run_single_linter(linter_name, file_path)
            result["tools_used"].append(linter_name)

            if linter_name == "ruff":
                linter_config = self._get_tool_config(linter_name, "linters")
                self._process_ruff_results(
                    linter_config, success, stdout, stderr, result
                )
            else:
                self._process_standard_linter_results(
                    linter_name, success, stderr, result
                )

        # Add errors for unavailable linters
        all_linters = ["ruff", "flake8", "pylint", "pydocstyle", "pycodestyle"]
        for linter_name in all_linters:
            linter_config = self._get_tool_config(linter_name, "linters")
            if linter_config.get("enabled", False) and not self._is_tool_available(
                linter_name
            ):
                result["errors"].append(f"{linter_name} not available")

        return result

    def type_check_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Type check a Python file using external mypy tool only.

        Uses actual mypy tool - no custom type checking logic.
        """
        result: Dict[str, Any] = {
            "file": str(file_path),
            "type_errors": 0,
            "issues": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        mypy_config = self._get_tool_config("mypy", "type_checkers")
        if not mypy_config.get("enabled", False):
            return result

        if not self._is_tool_available("mypy"):
            result["errors"].append("mypy not available")
            return result

        cmd = ["mypy"] + mypy_config["args"] + [str(file_path)]
        success, stdout, stderr = self._run_command(cmd)

        if not success:
            result["type_errors"] = stderr.count("error:")
            result["issues"].append({"tool": "mypy", "output": stderr})

        return result

    def analyze_complexity(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze code complexity using external tools (radon, xenon) only.

        Uses actual complexity analysis tools - no custom analysis logic.
        Applies differential thresholds: <10 for non-UI, <15 for UI components.
        """
        logger.debug(f"Starting complexity analysis for: {file_path}")

        result: Dict[str, Any] = {
            "file": str(file_path),
            "is_ui_component": False,
            "complexity_threshold": 10,
            "complexity_score": None,
            "maintainability_index": None,
            "complexity_violations": [],
            "issues": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            logger.debug(f"File excluded from processing: {file_path}")
            result["errors"].append("File excluded from processing")
            return result

        # Determine if this is a UI component and set threshold
        result["is_ui_component"] = self._is_ui_component(file_path)
        result["complexity_threshold"] = self._get_complexity_threshold(file_path)
        logger.debug(
            f"UI component: {result['is_ui_component']}, threshold: {result['complexity_threshold']}"
        )

        # Perform radon complexity analysis
        self._handle_radon_complexity_analysis(file_path, result)

        # Perform radon maintainability analysis
        self._handle_radon_maintainability_analysis(file_path, result)

        # Perform xenon complexity analysis
        self._handle_xenon_complexity_analysis(file_path, result)

        logger.debug(
            f"Completed complexity analysis for: {file_path}, violations: {len(result['complexity_violations'])}"
        )
        return result

    def _handle_radon_complexity_analysis(
        self, file_path: Path, result: Dict[str, Any]
    ) -> None:
        """
        Handle radon cyclomatic complexity analysis with comprehensive logging.

        Args:
            file_path: Path to the Python file being analyzed
            result: Result dictionary to update with complexity data
        """
        logger.debug(f"Starting radon complexity analysis for: {file_path}")

        radon_config = self._get_tool_config("radon", "complexity_analyzers")

        if not radon_config.get("enabled", False):
            logger.debug("Radon complexity analysis disabled in configuration")
            return

        if not self._is_tool_available("radon"):
            logger.warning("Radon tool not available for complexity analysis")
            result["errors"].append("radon not available")
            return

        cmd = ["radon", "cc", str(file_path), "-j"]
        logger.debug(f"Executing radon complexity command: {' '.join(cmd)}")

        success, stdout, stderr = self._run_command(cmd)

        if success and stdout:
            logger.debug("Radon complexity analysis completed successfully")
            try:
                cc_data = json.loads(stdout)
                result["complexity_score"] = cc_data
                logger.debug(f"Parsed complexity data for {len(cc_data)} file(s)")

                # Process complexity violations
                self._process_complexity_violations(cc_data, result)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse radon complexity output: {e}")
                result["errors"].append("Failed to parse radon complexity output")
        else:
            logger.warning(f"Radon complexity analysis failed: {stderr}")
            if stderr:
                result["errors"].append(f"radon cc error: {stderr}")

    def _handle_radon_maintainability_analysis(
        self, file_path: Path, result: Dict[str, Any]
    ) -> None:
        """
        Handle radon maintainability index analysis with comprehensive logging.

        Args:
            file_path: Path to the Python file being analyzed
            result: Result dictionary to update with maintainability data
        """
        logger.debug(f"Starting radon maintainability analysis for: {file_path}")

        radon_config = self._get_tool_config("radon", "complexity_analyzers")

        if not radon_config.get("enabled", False):
            logger.debug("Radon maintainability analysis disabled in configuration")
            return

        if not self._is_tool_available("radon"):
            logger.warning("Radon tool not available for maintainability analysis")
            return

        cmd = ["radon", "mi", str(file_path), "-j"]
        logger.debug(f"Executing radon maintainability command: {' '.join(cmd)}")

        success, stdout, stderr = self._run_command(cmd)

        if success and stdout:
            logger.debug("Radon maintainability analysis completed successfully")
            try:
                mi_data = json.loads(stdout)
                result["maintainability_index"] = mi_data
                logger.debug(f"Parsed maintainability data: {mi_data}")

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse radon maintainability output: {e}")
                result["errors"].append("Failed to parse radon maintainability output")
        else:
            logger.warning(f"Radon maintainability analysis failed: {stderr}")
            if stderr:
                result["errors"].append(f"radon mi error: {stderr}")

    def _handle_xenon_complexity_analysis(
        self, file_path: Path, result: Dict[str, Any]
    ) -> None:
        """
        Handle xenon complexity analysis with comprehensive logging.

        Args:
            file_path: Path to the Python file being analyzed
            result: Result dictionary to update with xenon analysis data
        """
        logger.debug(f"Starting xenon complexity analysis for: {file_path}")

        xenon_config = self._get_tool_config("xenon", "complexity_analyzers")

        if not xenon_config.get("enabled", False):
            logger.debug("Xenon complexity analysis disabled in configuration")
            return

        if not self._is_tool_available("xenon"):
            logger.warning("Xenon tool not available for complexity analysis")
            result["errors"].append("xenon not available")
            return

        # Use dynamic threshold based on component type
        threshold_flag = (
            "--max-average=B"
            if result["complexity_threshold"] >= 15
            else "--max-average=A"
        )

        cmd = ["xenon", str(file_path), threshold_flag]
        logger.debug(
            f"Executing xenon command: {' '.join(cmd)} (threshold: {threshold_flag})"
        )

        success, stdout, stderr = self._run_command(cmd)

        if not success and stderr:
            logger.warning(f"Xenon complexity violations detected: {stderr}")
            result["issues"].append({"tool": "xenon", "output": stderr})
        else:
            logger.debug("Xenon complexity analysis passed without violations")

    def _process_complexity_violations(
        self, cc_data: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """
        Process complexity violations from radon data with comprehensive logging.

        Args:
            cc_data: Complexity data from radon
            result: Result dictionary to update with violation information
        """
        logger.debug("Processing complexity violations from radon data")
        violations_found = 0

        for file_results in cc_data.values():
            if isinstance(file_results, list):
                logger.debug(f"Processing {len(file_results)} complexity items")

                for item in file_results:
                    if isinstance(item, dict) and "complexity" in item:
                        complexity = item["complexity"]
                        function_name = item.get("name", "unknown")
                        line_number = item.get("lineno", 0)

                        logger.debug(
                            f"Function '{function_name}' at line {line_number}: complexity {complexity}"
                        )

                        if complexity >= result["complexity_threshold"]:
                            violation = {
                                "function": function_name,
                                "complexity": complexity,
                                "threshold": result["complexity_threshold"],
                                "line": line_number,
                            }
                            result["complexity_violations"].append(violation)
                            violations_found += 1

                            logger.warning(
                                f"Complexity violation: {function_name} ({complexity}) exceeds threshold ({result['complexity_threshold']}) at line {line_number}"
                            )

        logger.debug(f"Found {violations_found} complexity violations")

    def validate_docstrings(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate docstrings using external pydocstyle tool only.

        Uses actual pydocstyle tool - no custom docstring validation logic.
        Checks for missing docstrings in modules, classes, and functions.
        """
        result = self._initialize_docstring_result(file_path)

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        # Get pydocstyle configuration and run validation
        pydocstyle_config = self._get_tool_config("pydocstyle", "linters")

        if self._should_run_pydocstyle(pydocstyle_config):
            self._run_pydocstyle_validation(file_path, pydocstyle_config, result)

        return result

    def _initialize_docstring_result(self, file_path: Path) -> Dict[str, Any]:
        """Initialize result dictionary for docstring validation.

        Args:
            file_path: Path to the file being validated

        Returns:
            Initialized result dictionary
        """
        return {
            "file": str(file_path),
            "docstring_issues": 0,
            "missing_docstrings": [],
            "style_violations": [],
            "issues": [],
            "errors": [],
        }

    def _should_run_pydocstyle(self, pydocstyle_config: Dict[str, Any]) -> bool:
        """Check if pydocstyle should be run.

        Args:
            pydocstyle_config: Configuration for pydocstyle

        Returns:
            True if pydocstyle should be run, False otherwise
        """
        return pydocstyle_config.get("enabled", False) and self._is_tool_available(
            "pydocstyle"
        )

    def _run_pydocstyle_validation(
        self, file_path: Path, pydocstyle_config: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Run pydocstyle validation and process results.

        Args:
            file_path: Path to the file being validated
            pydocstyle_config: Configuration for pydocstyle
            result: Result dictionary to update
        """
        cmd = ["pydocstyle"] + pydocstyle_config["args"] + [str(file_path)]
        success, stdout, stderr = self._run_command(cmd)

        if not success and stdout:
            self._process_pydocstyle_violations(stdout, result)
        elif stderr:
            result["errors"].append(f"pydocstyle error: {stderr}")

    def _process_pydocstyle_violations(
        self, stdout: str, result: Dict[str, Any]
    ) -> None:
        """Process pydocstyle violations and categorize them.

        Args:
            stdout: pydocstyle output containing violations
            result: Result dictionary to update
        """
        violations = stdout.strip().split("\n") if stdout.strip() else []
        result["docstring_issues"] = len(violations)

        for violation in violations:
            if violation.strip():
                violation_info = self._parse_pydocstyle_violation(violation)
                if violation_info:
                    self._categorize_violation(violation_info, result)

        result["issues"].append({"tool": "pydocstyle", "output": stdout})

    def _parse_pydocstyle_violation(self, violation: str) -> Optional[Dict[str, str]]:
        """Parse a single pydocstyle violation.

        Args:
            violation: Violation string from pydocstyle

        Returns:
            Parsed violation info or None if parsing failed
        """
        if ":" in violation:
            parts = violation.split(":", 3)
            if len(parts) >= 4:
                return {
                    "line": parts[1].strip(),
                    "code": parts[2].strip(),
                    "message": parts[3].strip(),
                    "full_text": violation,
                }
        return None

    def _categorize_violation(
        self, violation_info: Dict[str, str], result: Dict[str, Any]
    ) -> None:
        """Categorize violation as missing docstring or style violation.

        Args:
            violation_info: Parsed violation information
            result: Result dictionary to update
        """
        missing_docstring_codes = {
            "D100",
            "D101",
            "D102",
            "D103",
            "D104",
            "D105",
            "D106",
            "D107",
        }

        if violation_info["code"] in missing_docstring_codes:
            result["missing_docstrings"].append(violation_info)
        else:
            result["style_violations"].append(violation_info)

    def _run_py_compile_check(self, file_path: Path) -> Tuple[bool, str, str]:
        """
        Run py_compile syntax check on file.

        Args:
            file_path: Path to Python file to check

        Returns:
            Tuple of (success, stdout, stderr)
        """
        syntax_check_cmd = ["python", "-m", "py_compile", str(file_path)]
        return self._run_command(syntax_check_cmd)

    def _process_compilation_errors(self, stderr: str, result: Dict[str, Any]) -> None:
        """
        Process compilation errors from py_compile output.

        Args:
            stderr: Error output from py_compile
            result: Result dictionary to update
        """
        if not stderr:
            return

        error_lines = stderr.strip().split("\n")
        for error_line in error_lines:
            if error_line.strip():
                self._categorize_compilation_error(error_line, stderr, result)

    def _categorize_compilation_error(
        self, error_line: str, stderr: str, result: Dict[str, Any]
    ) -> None:
        """
        Categorize a single compilation error.

        Args:
            error_line: Individual error line
            stderr: Full error output
            result: Result dictionary to update
        """
        if "SyntaxError:" in error_line or "IndentationError:" in error_line:
            result["syntax_errors"].append(
                {
                    "type": "syntax_error",
                    "message": error_line.strip(),
                    "full_output": stderr,
                }
            )
        else:
            result["compilation_errors"].append(
                {
                    "type": "compilation_error",
                    "message": error_line.strip(),
                    "full_output": stderr,
                }
            )

    def _run_ast_validation(self, file_path: Path, result: Dict[str, Any]) -> None:
        """
        Run AST parsing validation as additional syntax check.

        Args:
            file_path: Path to Python file to validate
            result: Result dictionary to update
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            self._validate_with_ast(source_code, file_path, result)

        except Exception as e:
            result["errors"].append(f"Failed to read file for AST parsing: {str(e)}")

    def _validate_with_ast(
        self, source_code: str, file_path: Path, result: Dict[str, Any]
    ) -> None:
        """
        Validate source code using AST parsing.

        Args:
            source_code: Python source code to validate
            file_path: Path to the file being validated
            result: Result dictionary to update
        """
        import ast

        try:
            ast.parse(source_code, filename=str(file_path))
            if not result["syntax_valid"]:
                # AST parsing succeeded but py_compile failed - unusual case
                result["errors"].append("AST parsing succeeded but py_compile failed")
        except SyntaxError as e:
            result["syntax_valid"] = False
            result["compiles"] = False
            result["syntax_errors"].append(
                {
                    "type": "ast_syntax_error",
                    "message": f"Line {e.lineno}: {e.msg}",
                    "line": e.lineno,
                    "offset": e.offset,
                    "full_output": str(e),
                }
            )
        except Exception as e:
            result["errors"].append(f"AST parsing error: {str(e)}")

    def check_syntax_compilation(self, file_path: Path) -> Dict[str, Any]:
        """
        Check if Python file compiles and has valid syntax using external python tool only.

        Uses actual Python interpreter - no custom syntax checking logic.
        Ensures code compiles before other quality checks are meaningful.
        """
        result: Dict[str, Any] = {
            "file": str(file_path),
            "compiles": False,
            "syntax_valid": False,
            "compilation_errors": [],
            "syntax_errors": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        # Run py_compile check
        success, stdout, stderr = self._run_py_compile_check(file_path)

        if success:
            result["syntax_valid"] = True
            result["compiles"] = True
        else:
            result["syntax_valid"] = False
            result["compiles"] = False
            self._process_compilation_errors(stderr, result)

        # Run additional AST validation
        self._run_ast_validation(file_path, result)

        return result

    def security_scan_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Security scan a Python file using external bandit tool only.

        Uses actual bandit security scanner - no custom security analysis.
        """
        result: Dict[str, Any] = {
            "file": str(file_path),
            "security_issues": 0,
            "issues": [],
            "errors": [],
        }

        if not self._should_process_file(file_path):
            result["errors"].append("File excluded from processing")
            return result

        bandit_config = self.config["tools"]["security_analyzers"]["bandit"]
        if not bandit_config["enabled"]:
            return result

        if not self._is_tool_available("bandit"):
            result["errors"].append("bandit not available")
            return result

        cmd = ["bandit"] + bandit_config["args"] + [str(file_path)]
        success, stdout, stderr = self._run_command(cmd)

        if stdout:
            try:
                bandit_data = json.loads(stdout)
                result["security_issues"] = len(bandit_data.get("results", []))
                result["issues"] = bandit_data.get("results", [])
            except json.JSONDecodeError:
                result["errors"].append("Failed to parse bandit output")

        return result

    def _check_compilation_prerequisite(
        self, file_path: Path, operations: List[str], result: Dict[str, Any]
    ) -> bool:
        """
        Check compilation prerequisite for other operations.

        Args:
            file_path: Path to the file to check
            operations: List of requested operations
            result: Result dictionary to update

        Returns:
            True if compilation passed or not required, False otherwise
        """
        if "compile" not in operations:
            return True

        compile_result = self.check_syntax_compilation(file_path)
        result["details"]["compilation"] = compile_result
        result["operations_completed"].append("compile")
        result["summary"]["compiles"] = compile_result["compiles"]
        result["summary"]["syntax_errors"] = len(compile_result["syntax_errors"]) + len(
            compile_result["compilation_errors"]
        )

        if not compile_result["compiles"]:
            result["errors"].append(
                "File does not compile - skipping other quality checks"
            )
            return False
        return True

    def _execute_operation(
        self, operation: str, file_path: Path, result: Dict[str, Any]
    ) -> None:
        """
        Execute a single operation on the file.

        Args:
            operation: Operation to execute
            file_path: Path to the file
            result: Result dictionary to update
        """
        if operation == "format":
            format_result = self.format_file(file_path)
            result["details"]["formatting"] = format_result
            result["operations_completed"].append("format")
            if format_result["formatted"]:
                result["summary"]["formatted"] = True
                self.stats["files_modified"] += 1

        elif operation == "lint":
            lint_result = self.lint_file(file_path)
            result["details"]["linting"] = lint_result
            result["operations_completed"].append("lint")
            result["summary"]["issues_found"] += lint_result["issues_found"]
            result["summary"]["issues_fixed"] += lint_result["issues_fixed"]
            self.stats["issues_found"] += lint_result["issues_found"]
            self.stats["issues_fixed"] += lint_result["issues_fixed"]

        elif operation == "type_check":
            type_result = self.type_check_file(file_path)
            result["details"]["type_checking"] = type_result
            result["operations_completed"].append("type_check")
            result["summary"]["type_errors"] = type_result["type_errors"]

        elif operation == "complexity":
            complexity_result = self.analyze_complexity(file_path)
            result["details"]["complexity"] = complexity_result
            result["operations_completed"].append("complexity")

        elif operation == "security":
            security_result = self.security_scan_file(file_path)
            result["details"]["security"] = security_result
            result["operations_completed"].append("security")
            result["summary"]["security_issues"] = security_result["security_issues"]

        elif operation == "docstrings":
            docstring_result = self.validate_docstrings(file_path)
            result["details"]["docstrings"] = docstring_result
            result["operations_completed"].append("docstrings")
            result["summary"]["docstring_issues"] = docstring_result["docstring_issues"]

    def _initialize_result(
        self, file_path: Path, operations: List[str]
    ) -> Dict[str, Any]:
        """
        Initialize the result dictionary for file processing.

        Args:
            file_path: Path to the file being processed
            operations: List of operations to perform

        Returns:
            Initialized result dictionary
        """
        return {
            "file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "operations_requested": operations,
            "operations_completed": [],
            "summary": {
                "formatted": False,
                "issues_found": 0,
                "issues_fixed": 0,
                "type_errors": 0,
                "security_issues": 0,
                "docstring_issues": 0,
                "compiles": False,
                "syntax_errors": 0,
            },
            "details": {},
            "errors": [],
        }

    def process_file(
        self, file_path: Path, operations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a file with specified operations.

        Args:
            file_path: Path to process
            operations: List of operations to perform.
                       Options: ["format", "lint", "type_check", "complexity", "security"]
                       If None, all operations are performed.

        Returns:
            Comprehensive processing result
        """
        if operations is None:
            operations = [
                "compile",
                "format",
                "lint",
                "type_check",
                "complexity",
                "security",
                "docstrings",
            ]

        result = self._initialize_result(file_path, operations)
        self.stats["files_processed"] += 1

        try:
            # Check compilation prerequisite first
            compilation_passed = self._check_compilation_prerequisite(
                file_path, operations, result
            )
            if not compilation_passed:
                return result

            # Execute remaining operations that require compilation
            for operation in operations:
                if operation != "compile" and compilation_passed:
                    self._execute_operation(operation, file_path, result)

        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            self.stats["errors"] += 1

        return result

    def verify_post_processing_compilation(
        self, file_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Verify that all processed files still compile after automated fixes.

        This is critical to ensure that formatting and auto-fixing didn't break the code.
        Should be called after format_file, lint_file with --fix flags, etc.

        Args:
            file_paths: List of file paths that were processed

        Returns:
            Dictionary with compilation verification results
        """
        result: Dict[str, Any] = {
            "verification_passed": True,
            "files_checked": 0,
            "compilation_failures": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            for file_path in file_paths:
                if not self._should_process_file(file_path):
                    continue

                result["files_checked"] += 1

                # Use the same compilation check as before
                compile_result = self.check_syntax_compilation(file_path)

                if not compile_result["compiles"]:
                    result["verification_passed"] = False
                    result["compilation_failures"].append(
                        {
                            "file": str(file_path),
                            "syntax_errors": compile_result["syntax_errors"],
                            "compilation_errors": compile_result["compilation_errors"],
                            "total_errors": len(compile_result["syntax_errors"])
                            + len(compile_result["compilation_errors"]),
                        }
                    )

            if not result["verification_passed"]:
                result["errors"].append(
                    f"POST-PROCESSING CRITICAL: {len(result['compilation_failures'])} files failed to compile after automated fixes!"
                )

        except Exception as e:
            result["errors"].append(
                f"Error during post-processing compilation verification: {str(e)}"
            )
            result["verification_passed"] = False

        return result

    def process_directory(
        self,
        directory: Path,
        operations: Optional[List[str]] = None,
        recursive: bool = True,
    ) -> Dict[str, Any]:
        """Process all Python files in a directory."""
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        results: Dict[str, Any] = {
            "directory": str(directory),
            "timestamp": datetime.now().isoformat(),
            "operations": operations
            or ["format", "lint", "type_check", "complexity", "security"],
            "summary": {
                "files_processed": 0,
                "files_modified": 0,
                "total_issues_found": 0,
                "total_issues_fixed": 0,
                "total_type_errors": 0,
                "total_security_issues": 0,
            },
            "files": [],
        }

        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if file_path.is_file() and self._should_process_file(file_path):
                file_result = self.process_file(file_path, operations)
                results["files"].append(file_result)

                # Update summary
                if file_result["summary"]["formatted"]:
                    results["summary"]["files_modified"] += 1
                results["summary"]["files_processed"] += 1
                results["summary"]["total_issues_found"] += file_result["summary"][
                    "issues_found"
                ]
                results["summary"]["total_issues_fixed"] += file_result["summary"][
                    "issues_fixed"
                ]
                results["summary"]["total_type_errors"] += file_result["summary"][
                    "type_errors"
                ]
                results["summary"]["total_security_issues"] += file_result["summary"][
                    "security_issues"
                ]

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "errors": 0,
        }

    def generate_report(
        self, results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> str:
        """Generate a comprehensive quality report."""
        report_lines = [
            "=" * 80,
            "PYTHON CODE QUALITY REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY:",
            f"  Files Processed: {results['summary']['files_processed']}",
            f"  Files Modified: {results['summary']['files_modified']}",
            f"  Issues Found: {results['summary']['total_issues_found']}",
            f"  Issues Fixed: {results['summary']['total_issues_fixed']}",
            f"  Type Errors: {results['summary']['total_type_errors']}",
            f"  Security Issues: {results['summary']['total_security_issues']}",
            "",
            "=" * 80,
        ]

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
                f.write("\n\nDETAILED RESULTS:\n")
                json.dump(results, f, indent=2, ensure_ascii=False)

        return report


def main() -> None:
    """Example usage of PythonQualityManager."""
    manager = PythonQualityManager()

    # Process a single file
    file_path = Path("example.py")
    if file_path.exists():
        result = manager.process_file(file_path)
        print(f"Processed {file_path}: {result['summary']}")

    # Process a directory
    directory = Path(".")
    results = manager.process_directory(directory, recursive=False)
    report = manager.generate_report(results)
    print(report)


if __name__ == "__main__":
    main()
