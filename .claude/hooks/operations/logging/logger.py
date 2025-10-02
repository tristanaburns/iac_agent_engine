"""Unified logging module following SOLID principles.

Single Responsibility: Handles all logging operations through a single interface.
"""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SUCCESS = "SUCCESS"  # Custom level for success messages


class LogFormat(Enum):
    """Log format enumeration."""

    SIMPLE = "[{timestamp}] [{level}] {message}"
    DETAILED = "[{timestamp}] [{level}] [{module}:{function}:{line}] {message}"
    JSON = '{"timestamp": "{timestamp}", "level": "{level}", "message": "{message}", "context": {context}}'


class Logger:
    """Unified logger with file, console, and JSON logging capabilities."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger with default configuration."""
        if not Logger._initialized:
            self._setup_default_configuration()
            Logger._initialized = True

    def _setup_default_configuration(self):
        """Set up default logging configuration."""
        try:
            from utils.path_resolver import PathResolver

            resolver = PathResolver()
        except (ImportError, ValueError):
            # Fallback if relative import fails
            import sys
            from pathlib import Path

            hooks_dir = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(hooks_dir))
            from utils.path_resolver import PathResolver

            resolver = PathResolver()

        # Configuration
        self.log_dir = resolver.logs_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.main_log_file = self.log_dir / "hooks.log"
        self.error_log_file = self.log_dir / "errors.log"
        self.json_log_file = (
            self.log_dir / f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        )

        # Settings
        self.console_enabled = True
        self.file_enabled = True
        self.json_enabled = True
        self.verbose = False
        self.format = LogFormat.SIMPLE

        # Color settings for console
        self.use_colors = sys.stdout.isatty()
        self.colors = {
            LogLevel.DEBUG: "\033[90m",  # Gray
            LogLevel.INFO: "\033[0m",  # Default
            LogLevel.WARNING: "\033[93m",  # Yellow
            LogLevel.ERROR: "\033[91m",  # Red
            LogLevel.CRITICAL: "\033[95m",  # Magenta
            LogLevel.SUCCESS: "\033[92m",  # Green
        }
        self.reset_color = "\033[0m"

        # Python's logging module setup
        self._setup_python_logging()

    def _setup_python_logging(self):
        """Configure Python's logging module."""
        # Create logger
        self.python_logger = logging.getLogger("hooks")
        self.python_logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.python_logger.handlers.clear()

        # File handler for all logs
        if self.file_enabled:
            file_handler = logging.FileHandler(self.main_log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.python_logger.addHandler(file_handler)

            # Error file handler
            error_handler = logging.FileHandler(self.error_log_file, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            self.python_logger.addHandler(error_handler)

        # Console handler
        if self.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
            console_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.python_logger.addHandler(console_handler)

    def configure(
        self,
        console: Optional[bool] = None,
        file: Optional[bool] = None,
        json: Optional[bool] = None,
        verbose: Optional[bool] = None,
        log_dir: Optional[Path] = None,
        format: Optional[LogFormat] = None,
        use_colors: Optional[bool] = None,
    ):
        """Configure logger settings.

        Args:
            console: Enable/disable console logging
            file: Enable/disable file logging
            json: Enable/disable JSON logging
            verbose: Enable/disable verbose output
            log_dir: Custom log directory
            format: Log format to use
            use_colors: Enable/disable colored console output
        """
        if console is not None:
            self.console_enabled = console
        if file is not None:
            self.file_enabled = file
        if json is not None:
            self.json_enabled = json
        if verbose is not None:
            self.verbose = verbose
        if log_dir is not None:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self._update_log_paths()
        if format is not None:
            self.format = format
        if use_colors is not None:
            self.use_colors = use_colors

        # Reconfigure Python logging
        self._setup_python_logging()

    def _update_log_paths(self):
        """Update log file paths after directory change."""
        self.main_log_file = self.log_dir / "hooks.log"
        self.error_log_file = self.log_dir / "errors.log"
        self.json_log_file = (
            self.log_dir / f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        )

    def _format_message(
        self,
        message: str,
        level: LogLevel,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format log message based on configured format.

        Args:
            message: Log message
            level: Log level
            context: Optional context dictionary

        Returns:
            Formatted message string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.format == LogFormat.JSON:
            log_dict: Dict[str, Any] = {
                "timestamp": timestamp,
                "level": level.value,
                "message": message,
            }
            if context:
                log_dict["context"] = context
            return json.dumps(log_dict)
        elif self.format == LogFormat.DETAILED:
            import inspect

            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                caller = frame.f_back.f_back
                return self.format.value.format(
                    timestamp=timestamp,
                    level=level.value,
                    module=Path(caller.f_code.co_filename).stem,
                    function=caller.f_code.co_name,
                    line=caller.f_lineno,
                    message=message,
                )

        # Default SIMPLE format
        return self.format.value.format(
            timestamp=timestamp,
            level=level.value,
            message=message,
        )

    def _write_to_file(self, formatted_message: str, level: LogLevel):
        """Write message to log file.

        Args:
            formatted_message: Formatted log message
            level: Log level
        """
        if not self.file_enabled:
            return

        try:
            with open(self.main_log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")

            # Also write to error log if error or critical
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                with open(self.error_log_file, "a", encoding="utf-8") as f:
                    f.write(formatted_message + "\n")
        except Exception:
            pass  # Silent fail

    def _write_to_console(self, formatted_message: str, level: LogLevel):
        """Write message to console with optional color.

        Args:
            formatted_message: Formatted log message
            level: Log level
        """
        if not self.console_enabled:
            return

        if level == LogLevel.DEBUG and not self.verbose:
            return

        if self.use_colors and level in self.colors:
            print(f"{self.colors[level]}{formatted_message}{self.reset_color}")
        else:
            print(formatted_message)

    def _write_to_json(
        self,
        message: str,
        level: LogLevel,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Write message to JSON log file.

        Args:
            message: Log message
            level: Log level
            context: Optional context dictionary
        """
        if not self.json_enabled:
            return

        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
        }
        if context:
            log_entry["context"] = context

        try:
            with open(self.json_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Silent fail

    def log(
        self,
        message: str,
        level: Union[str, LogLevel] = LogLevel.INFO,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Main logging method.

        Args:
            message: Message to log
            level: Log level (string or LogLevel enum)
            context: Optional context dictionary
        """
        # Convert string level to enum
        if isinstance(level, str):
            try:
                level = LogLevel[level.upper()]
            except KeyError:
                level = LogLevel.INFO

        # Format message
        formatted_message = self._format_message(message, level, context)

        # Write to outputs
        self._write_to_file(formatted_message, level)
        self._write_to_console(formatted_message, level)
        self._write_to_json(message, level, context)

        # Also use Python logger
        py_level = getattr(logging, level.value, logging.INFO)
        self.python_logger.log(py_level, message)

    # Convenience methods
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.log(message, LogLevel.DEBUG, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.log(message, LogLevel.INFO, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.log(message, LogLevel.WARNING, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.log(message, LogLevel.ERROR, context)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.log(message, LogLevel.CRITICAL, context)

    def success(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log success message."""
        self.log(message, LogLevel.SUCCESS, context)

    def exception(self, message: str, exc_info: bool = True):
        """Log exception with traceback.

        Args:
            message: Error message
            exc_info: Include exception info
        """
        if exc_info:
            import traceback

            tb = traceback.format_exc()
            self.error(f"{message}\n{tb}")
        else:
            self.error(message)

    def progress(self, current: int, total: int, message: str = ""):
        """Log progress information.

        Args:
            current: Current item number
            total: Total items
            message: Optional progress message
        """
        if not self.console_enabled:
            return

        percentage = (current / total * 100) if total > 0 else 0
        progress_msg = f"Progress: {current}/{total} ({percentage:.1f}%)"
        if message:
            progress_msg += f" - {message}"

        print(f"\r{progress_msg}", end="", flush=True)
        if current >= total:
            print()  # New line when complete

    def section(self, title: str, char: str = "=", width: int = 60):
        """Log a section header.

        Args:
            title: Section title
            char: Character to use for line
            width: Width of section line
        """
        line = char * width
        self.info(line)
        self.info(title.center(width))
        self.info(line)

    def dict_log(self, data: Dict[str, Any], title: Optional[str] = None):
        """Log a dictionary in readable format.

        Args:
            data: Dictionary to log
            title: Optional title for the data
        """
        if title:
            self.info(f"{title}:")

        for key, value in data.items():
            self.info(f"  {key}: {value}")

    def list_log(self, items: List[Any], title: Optional[str] = None):
        """Log a list in readable format.

        Args:
            items: List to log
            title: Optional title for the list
        """
        if title:
            self.info(f"{title}:")

        for i, item in enumerate(items, 1):
            self.info(f"  {i}. {item}")


# Global logger instance
logger = Logger()


# Module-level convenience functions
def configure(**kwargs):
    """Configure the global logger."""
    logger.configure(**kwargs)


def log(
    message: str,
    level: Union[str, LogLevel] = LogLevel.INFO,
    context: Optional[Dict[str, Any]] = None,
):
    """Log a message using global logger."""
    logger.log(message, level, context)


def debug(message: str, context: Optional[Dict[str, Any]] = None):
    """Log debug message."""
    logger.debug(message, context)


def info(message: str, context: Optional[Dict[str, Any]] = None):
    """Log info message."""
    logger.info(message, context)


def warning(message: str, context: Optional[Dict[str, Any]] = None):
    """Log warning message."""
    logger.warning(message, context)


def error(message: str, context: Optional[Dict[str, Any]] = None):
    """Log error message."""
    logger.error(message, context)


def critical(message: str, context: Optional[Dict[str, Any]] = None):
    """Log critical message."""
    logger.critical(message, context)


def success(message: str, context: Optional[Dict[str, Any]] = None):
    """Log success message."""
    logger.success(message, context)


def exception(message: str, exc_info: bool = True):
    """Log exception with traceback."""
    logger.exception(message, exc_info)


def progress(current: int, total: int, message: str = ""):
    """Log progress information."""
    logger.progress(current, total, message)


def section(title: str, char: str = "=", width: int = 60):
    """Log a section header."""
    logger.section(title, char, width)
