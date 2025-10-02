"""Quality operations - formatting and code quality checks.

This module provides comprehensive quality operations with robust error handling,
logging, retry mechanisms, and validation.
"""

import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional

from process_runner import ProcessRunner


class QualityErrorType(Enum):
    """Classification of quality operation errors."""

    TOOL_NOT_FOUND = "tool_not_found"
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    TEMPORARY_ERROR = "temporary_error"
    CRITICAL_ERROR = "critical_error"
    UNKNOWN_ERROR = "unknown_error"


class QualityOperationError(Exception):
    """Base exception for quality operation errors.

    Provides context preservation and error classification.
    """

    def __init__(
        self,
        message: str,
        error_type: QualityErrorType,
        operation: str,
        target_path: Optional[Path] = None,
        original_error: Optional[Exception] = None,
        recoverable: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize quality operation error.

        Args:
            message: Human-readable error message
            error_type: Classification of the error type
            operation: The operation that failed (e.g., 'black_format', 'isort_check')
            target_path: Path that was being processed when error occurred
            original_error: The original exception that caused this error
            recoverable: Whether this error can be retried
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.error_type = error_type
        self.operation = operation
        self.target_path = target_path
        self.original_error = original_error
        self.recoverable = recoverable
        self.context = context or {}
        self.timestamp = time.time()

    def is_recoverable(self) -> bool:
        """Check if this error is recoverable through retry."""
        return self.recoverable and self.error_type in {
            QualityErrorType.TEMPORARY_ERROR,
            QualityErrorType.TIMEOUT_ERROR,
            QualityErrorType.NETWORK_ERROR,
        }

    def should_escalate(self) -> bool:
        """Check if this error should be escalated."""
        return self.error_type in {
            QualityErrorType.CRITICAL_ERROR,
            QualityErrorType.CONFIGURATION_ERROR,
            QualityErrorType.TOOL_NOT_FOUND,
        }

    def get_context_summary(self) -> str:
        """Get a summary of error context for logging."""
        context_parts = [
            f"operation={self.operation}",
            f"error_type={self.error_type.value}",
            f"recoverable={self.recoverable}",
        ]

        if self.target_path:
            context_parts.append(f"target_path={self.target_path}")

        if self.original_error:
            context_parts.append(f"original_error={type(self.original_error).__name__}")

        if self.context:
            for key, value in self.context.items():
                context_parts.append(f"{key}={value}")

        return ", ".join(context_parts)


class QualityOperations:
    """Handles all quality operations with comprehensive error handling.

    Features:
    - Robust error classification and handling
    - Comprehensive logging for all operations
    - Intelligent retry mechanisms for recoverable errors
    - Validation of tool execution and results
    - Error escalation for critical issues
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize quality operations.

        Args:
            max_retries: Maximum number of retry attempts for recoverable errors
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.black_line_length = 88
        self.isort_profile = "black"
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configure logging for quality operations
        self.logger = self._setup_logger()

        # Track operation statistics
        self.stats = {
            "operations_attempted": 0,
            "operations_successful": 0,
            "operations_failed": 0,
            "retries_attempted": 0,
            "errors_escalated": 0,
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup dedicated logger for quality operations."""
        logger = logging.getLogger(f"{__name__}.QualityOperations")

        # Only add handler if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def _classify_error(
        self, error: Exception, operation: str, result: Optional[Dict[str, Any]] = None
    ) -> QualityErrorType:
        """Classify an error based on its type and context.

        Args:
            error: The exception that occurred
            operation: The operation being performed
            result: Optional result dictionary from process execution

        Returns:
            Classified error type for appropriate handling
        """
        error_message = str(error).lower()

        # Check for specific exception types first
        if isinstance(error, FileNotFoundError):
            return self._classify_file_not_found_error(error_message)

        if isinstance(error, PermissionError):
            return QualityErrorType.PERMISSION_ERROR

        # Check for specific error patterns in message
        return self._classify_message_based_error(error_message, result)

    def _classify_file_not_found_error(self, error_message: str) -> QualityErrorType:
        """Classify FileNotFoundError based on message content."""
        tool_names = ["black", "isort", "python"]
        if any(tool in error_message for tool in tool_names):
            return QualityErrorType.TOOL_NOT_FOUND
        return QualityErrorType.CONFIGURATION_ERROR

    def _classify_message_based_error(
        self, error_message: str, result: Optional[Dict[str, Any]]
    ) -> QualityErrorType:
        """Classify error based on message content patterns."""
        # Process and timeout errors
        if self._is_timeout_error(error_message):
            return QualityErrorType.TIMEOUT_ERROR

        # Network and connectivity errors
        if self._is_network_error(error_message):
            return QualityErrorType.NETWORK_ERROR

        # Configuration and validation errors
        if self._is_config_or_validation_error(error_message, result):
            if result and not result.get("success", True):
                return QualityErrorType.VALIDATION_ERROR
            return QualityErrorType.CONFIGURATION_ERROR

        # Temporary errors (often recoverable)
        if self._is_temporary_error(error_message):
            return QualityErrorType.TEMPORARY_ERROR

        # Critical system errors
        if self._is_critical_system_error(error_message):
            return QualityErrorType.CRITICAL_ERROR

        return QualityErrorType.UNKNOWN_ERROR

    def _is_timeout_error(self, error_message: str) -> bool:
        """Check if error message indicates a timeout."""
        return "timeout" in error_message or "timed out" in error_message

    def _is_network_error(self, error_message: str) -> bool:
        """Check if error message indicates a network issue."""
        network_terms = ["network", "connection", "dns", "resolve"]
        return any(term in error_message for term in network_terms)

    def _is_config_or_validation_error(
        self, error_message: str, result: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if error message indicates configuration or validation issues."""
        config_terms = ["config", "invalid", "syntax", "parse"]
        return any(term in error_message for term in config_terms)

    def _is_temporary_error(self, error_message: str) -> bool:
        """Check if error message indicates a temporary issue."""
        temp_terms = ["temporary", "busy", "locked", "unavailable"]
        return any(term in error_message for term in temp_terms)

    def _is_critical_system_error(self, error_message: str) -> bool:
        """Check if error message indicates a critical system issue."""
        critical_terms = ["memory", "disk", "space", "critical"]
        return any(term in error_message for term in critical_terms)

    def _is_error_recoverable(self, error_type: QualityErrorType, attempt: int) -> bool:
        """Determine if an error should be retried.

        Args:
            error_type: The classified error type
            attempt: Current attempt number (1-based)

        Returns:
            Whether the error should be retried
        """
        if attempt >= self.max_retries:
            return False

        recoverable_types = {
            QualityErrorType.TEMPORARY_ERROR,
            QualityErrorType.TIMEOUT_ERROR,
            QualityErrorType.NETWORK_ERROR,
        }

        return error_type in recoverable_types

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry with exponential backoff.

        Args:
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds before next retry
        """
        return self.retry_delay * (2 ** (attempt - 1))

    def _validate_tool_result(
        self, result: Dict[str, Any], operation: str, target_path: Path
    ) -> None:
        """Validate that a quality tool actually performed its operation.

        Args:
            result: Result dictionary from process execution
            operation: The operation that was performed
            target_path: Path that was processed

        Raises:
            QualityOperationError: If validation fails
        """
        # Check if result structure is valid
        if not isinstance(result, dict):
            raise QualityOperationError(
                f"Invalid result structure for {operation}: expected dict, got {type(result)}",
                QualityErrorType.VALIDATION_ERROR,
                operation,
                target_path,
                context={"result_type": str(type(result))},
            )

        # Check if required fields are present based on operation type
        if "format" in operation:
            # Format operations need success, returncode, stdout, stderr
            required_fields = ["status", "returncode", "stdout", "stderr"]
        else:
            # Check operations need returncode, stdout, stderr
            required_fields = ["returncode", "stdout", "stderr"]

        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise QualityOperationError(
                f"Missing required fields in {operation} result: {missing_fields}",
                QualityErrorType.VALIDATION_ERROR,
                operation,
                target_path,
                context={
                    "missing_fields": missing_fields,
                    "available_fields": list(result.keys()),
                },
            )

        # Check if the tool actually ran (not just returned success=False)
        if result.get("returncode") is None:
            raise QualityOperationError(
                f"Tool execution validation failed for {operation}: no return code",
                QualityErrorType.VALIDATION_ERROR,
                operation,
                target_path,
                context={"result": result},
            )

        # Log validation success
        self.logger.debug(
            f"Tool result validation passed for {operation} on {target_path}"
        )

    def _execute_with_retry(
        self, operation_func, operation_name: str, target_path: Path, **kwargs
    ) -> Dict[str, Any]:
        """Execute an operation with retry logic and comprehensive error handling.

        Args:
            operation_func: Function to execute
            operation_name: Name of the operation for logging
            target_path: Path being processed
            **kwargs: Additional arguments for the operation function

        Returns:
            Result dictionary from successful execution

        Raises:
            QualityOperationError: If operation fails after all retries
        """
        self.stats["operations_attempted"] += 1
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._execute_single_attempt(
                    operation_func, operation_name, target_path, attempt, **kwargs
                )
                return result
            except Exception as e:
                last_error = e
                handled_error = self._handle_retry_attempt_error(
                    e, operation_name, target_path, attempt
                )
                if handled_error is not None:
                    last_error = handled_error

        # Fallback error handling
        return self._handle_fallback_error(last_error, operation_name, target_path)

    def _execute_single_attempt(
        self,
        operation_func,
        operation_name: str,
        target_path: Path,
        attempt: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a single retry attempt.

        Returns:
            Result dictionary from successful execution

        Raises:
            Exception: If attempt fails
        """
        self._log_operation_attempt(operation_name, target_path, attempt)
        result = operation_func(target_path, **kwargs)
        self._validate_tool_result(result, operation_name, target_path)
        self._log_operation_success(operation_name, target_path)
        self.stats["operations_successful"] += 1
        return result

    def _handle_retry_attempt_error(
        self, error: Exception, operation_name: str, target_path: Path, attempt: int
    ) -> Exception | None:
        """Handle error from a failed retry attempt.

        Args:
            error: The exception that occurred
            operation_name: Name of the operation
            target_path: Path being processed
            attempt: Current attempt number

        Returns:
            Exception for fallback handling, or None if error was escalated

        Raises:
            QualityOperationError: If error should be escalated immediately
        """
        quality_error = self._create_operation_error(
            error, operation_name, target_path, attempt
        )

        if self._should_escalate_error(quality_error, operation_name, error):
            raise quality_error

        if self._should_retry_operation(quality_error, attempt, operation_name):
            return error  # Continue with retry

        # No more retries - finalize error
        self._finalize_operation_error(operation_name, target_path)
        raise quality_error

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get statistics about quality operations.

        Returns:
            Dictionary containing operation statistics
        """
        total_attempted = self.stats["operations_attempted"]
        success_rate = (
            (self.stats["operations_successful"] / total_attempted * 100)
            if total_attempted > 0
            else 0.0
        )

        return {**self.stats, "success_rate_percent": round(success_rate, 2)}

    def _log_operation_attempt(
        self, operation_name: str, target_path: Path, attempt: int
    ) -> None:
        """Log operation attempt with context."""
        self.logger.info(
            f"Executing {operation_name} on {target_path} (attempt {attempt}/{self.max_retries})"
        )

    def _log_operation_success(self, operation_name: str, target_path: Path) -> None:
        """Log successful operation completion."""
        self.logger.info(f"Successfully completed {operation_name} on {target_path}")

    def _create_operation_error(
        self, error: Exception, operation_name: str, target_path: Path, attempt: int
    ) -> QualityOperationError:
        """Create structured operation error with full context."""
        error_type = self._classify_error(error, operation_name)

        return QualityOperationError(
            f"Operation {operation_name} failed on {target_path}: {str(error)}",
            error_type,
            operation_name,
            target_path,
            original_error=error,
            recoverable=self._is_error_recoverable(error_type, attempt),
            context={
                "attempt": attempt,
                "max_retries": self.max_retries,
                "error_message": str(error),
                "error_type_name": type(error).__name__,
            },
        )

    def _should_escalate_error(
        self,
        quality_error: QualityOperationError,
        operation_name: str,
        original_error: Exception,
    ) -> bool:
        """Determine if error should be escalated immediately."""
        if quality_error.should_escalate():
            self.logger.critical(
                f"Critical error in {operation_name} - escalating: {str(original_error)}"
            )
            self.stats["errors_escalated"] += 1
            return True
        return False

    def _should_retry_operation(
        self, quality_error: QualityOperationError, attempt: int, operation_name: str
    ) -> bool:
        """Determine if operation should be retried."""
        # Log the error with appropriate level
        log_level = logging.WARNING if quality_error.is_recoverable() else logging.ERROR
        self.logger.log(
            log_level,
            f"Error in {operation_name}: {quality_error.get_context_summary()}",
        )

        if quality_error.is_recoverable() and attempt < self.max_retries:
            retry_delay = self._calculate_retry_delay(attempt)
            self.logger.info(
                f"Retrying {operation_name} in {retry_delay:.2f} seconds..."
            )
            self.stats["retries_attempted"] += 1
            time.sleep(retry_delay)
            return True
        return False

    def _finalize_operation_error(self, operation_name: str, target_path: Path) -> None:
        """Log final error state when all retries are exhausted."""
        self.logger.error(
            f"All retry attempts exhausted for {operation_name} on {target_path}"
        )
        self.stats["operations_failed"] += 1

    def _handle_fallback_error(
        self, last_error: Optional[Exception], operation_name: str, target_path: Path
    ) -> NoReturn:
        """Handle fallback error cases that should never occur."""
        if last_error:
            raise QualityOperationError(
                f"Operation {operation_name} failed after all retries",
                QualityErrorType.UNKNOWN_ERROR,
                operation_name,
                target_path,
                original_error=last_error,
            )

        raise QualityOperationError(
            f"Operation {operation_name} failed with unknown error",
            QualityErrorType.UNKNOWN_ERROR,
            operation_name,
            target_path,
        )

    def format_python_files(self, target_path: Path) -> Dict[str, Any]:
        """Format Python files with Black and isort.

        Args:
            target_path: Path to format

        Returns:
            Dictionary with results including comprehensive error information

        Raises:
            QualityOperationError: If critical errors occur that prevent formatting
        """
        self.logger.info(f"Starting Python file formatting for {target_path}")
        results = self._initialize_format_results()
        start_time = time.time()

        try:
            # Run formatting tools
            self._run_black_formatting(results, target_path)
            self._run_isort_formatting(results, target_path)

            # Finalize results
            self._finalize_format_results(results, start_time, target_path)
            return results

        except Exception as e:
            return self._handle_format_error(e, results, start_time, target_path)

    def _initialize_format_results(self) -> Dict[str, Any]:
        """Initialize results dictionary for formatting operations."""
        return {
            "black": {},
            "isort": {},
            "success": True,
            "errors": [],
            "warnings": [],
            "operation_stats": {},
        }

    def _run_black_formatting(self, results: Dict[str, Any], target_path: Path) -> None:
        """Run Black formatting and update results."""
        try:
            results["black"] = self._execute_with_retry(
                self._run_black, "black_format", target_path
            )
            if results["black"]["status"] != "success":
                results["success"] = False
                results["errors"].extend(results["black"]["errors"])
        except QualityOperationError as e:
            self._handle_tool_formatting_error(results, "black", e)

    def _run_isort_formatting(self, results: Dict[str, Any], target_path: Path) -> None:
        """Run isort formatting and update results."""
        try:
            results["isort"] = self._execute_with_retry(
                self._run_isort, "isort_format", target_path
            )
            if results["isort"]["status"] != "success":
                results["success"] = False
                results["errors"].extend(results["isort"]["errors"])
        except QualityOperationError as e:
            self._handle_tool_formatting_error(results, "isort", e)

    def _handle_tool_formatting_error(
        self, results: Dict[str, Any], tool_name: str, error: QualityOperationError
    ) -> None:
        """Handle errors from formatting tools."""
        results["success"] = False
        results["errors"].append(f"{tool_name} formatting failed: {str(error)}")
        results[tool_name] = {"status": "failed", "error": str(error)}

        if error.should_escalate():
            self.logger.critical(
                f"Critical {tool_name} formatting error: {error.get_context_summary()}"
            )
            raise error

    def _finalize_format_results(
        self, results: Dict[str, Any], start_time: float, target_path: Path
    ) -> None:
        """Finalize formatting results with timing and logging."""
        operation_time = time.time() - start_time
        results["operation_stats"] = {
            "duration_seconds": round(operation_time, 3),
            "timestamp": time.time(),
        }

        # Log final result
        if results["success"]:
            self.logger.info(
                f"Python file formatting completed successfully for {target_path} in {operation_time:.3f}s"
            )
        else:
            self.logger.warning(
                f"Python file formatting completed with errors for {target_path}: {results['errors']}"
            )

    def _handle_format_error(
        self,
        error: Exception,
        results: Dict[str, Any],
        start_time: float,
        target_path: Path,
    ) -> Dict[str, Any]:
        """Handle unexpected errors during formatting."""
        operation_time = time.time() - start_time
        error_msg = f"Unexpected error during Python file formatting: {str(error)}"

        self.logger.error(f"{error_msg} (operation time: {operation_time:.3f}s)")

        # Create comprehensive error result
        results.update(
            {
                "success": False,
                "errors": [error_msg],
                "operation_stats": {
                    "duration_seconds": round(operation_time, 3),
                    "timestamp": time.time(),
                    "unexpected_error": True,
                },
            }
        )

        # Escalate unexpected errors
        raise QualityOperationError(
            error_msg,
            QualityErrorType.CRITICAL_ERROR,
            "format_python_files",
            target_path,
            original_error=error,
            context={"operation_time": operation_time},
        )

    def check_quality(self, target_path: Path) -> Dict[str, Any]:
        """Check code quality without modifying files.

        Args:
            target_path: Path to check

        Returns:
            Dictionary with check results including comprehensive validation

        Raises:
            QualityOperationError: If critical errors occur during quality checks
        """
        self.logger.info(f"Starting quality checks for {target_path}")
        results = self._initialize_check_results()
        start_time = time.time()

        try:
            # Run quality checks
            self._run_black_check(results, target_path)
            self._run_isort_check(results, target_path)

            # Finalize results
            self._finalize_check_results(results, start_time, target_path)
            return results

        except Exception as e:
            return self._handle_check_error(e, results, start_time, target_path)

    def _initialize_check_results(self) -> Dict[str, Any]:
        """Initialize results dictionary for quality check operations."""
        return {
            "black": {},
            "isort": {},
            "needs_formatting": False,
            "check_successful": True,
            "errors": [],
            "warnings": [],
            "operation_stats": {},
        }

    def _run_black_check(self, results: Dict[str, Any], target_path: Path) -> None:
        """Run Black quality check and update results."""
        try:
            results["black"] = self._execute_with_retry(
                self._check_black, "black_check", target_path
            )
            if results["black"].get("needs_formatting", False):
                results["needs_formatting"] = True
                self.logger.info(f"Black formatting needed for {target_path}")
        except QualityOperationError as e:
            self._handle_tool_check_error(results, "black", e)

    def _run_isort_check(self, results: Dict[str, Any], target_path: Path) -> None:
        """Run isort quality check and update results."""
        try:
            results["isort"] = self._execute_with_retry(
                self._check_isort, "isort_check", target_path
            )
            if results["isort"].get("needs_formatting", False):
                results["needs_formatting"] = True
                self.logger.info(f"isort formatting needed for {target_path}")
        except QualityOperationError as e:
            self._handle_tool_check_error(results, "isort", e)

    def _handle_tool_check_error(
        self, results: Dict[str, Any], tool_name: str, error: QualityOperationError
    ) -> None:
        """Handle errors from quality check tools."""
        results["check_successful"] = False
        results["errors"].append(f"{tool_name} check failed: {str(error)}")
        results[tool_name] = {"error": str(error), "needs_formatting": None}

        if error.should_escalate():
            self.logger.critical(
                f"Critical {tool_name} check error: {error.get_context_summary()}"
            )
            raise error

    def _finalize_check_results(
        self, results: Dict[str, Any], start_time: float, target_path: Path
    ) -> None:
        """Finalize quality check results with timing and validation."""
        operation_time = time.time() - start_time
        results["operation_stats"] = {
            "duration_seconds": round(operation_time, 3),
            "timestamp": time.time(),
        }

        # Validate that we got meaningful results
        self._validate_quality_check_results(results, target_path)

        # Log final result
        if results["check_successful"]:
            formatting_status = (
                "needed" if results["needs_formatting"] else "not needed"
            )
            self.logger.info(
                f"Quality checks completed successfully for {target_path} in {operation_time:.3f}s - "
                f"formatting {formatting_status}"
            )
        else:
            self.logger.warning(
                f"Quality checks completed with errors for {target_path}: {results['errors']}"
            )

    def _handle_check_error(
        self,
        error: Exception,
        results: Dict[str, Any],
        start_time: float,
        target_path: Path,
    ) -> Dict[str, Any]:
        """Handle unexpected errors during quality checks."""
        operation_time = time.time() - start_time
        error_msg = f"Unexpected error during quality checks: {str(error)}"

        self.logger.error(f"{error_msg} (operation time: {operation_time:.3f}s)")

        # Create comprehensive error result
        results.update(
            {
                "check_successful": False,
                "errors": [error_msg],
                "operation_stats": {
                    "duration_seconds": round(operation_time, 3),
                    "timestamp": time.time(),
                    "unexpected_error": True,
                },
            }
        )

        # Escalate unexpected errors
        raise QualityOperationError(
            error_msg,
            QualityErrorType.CRITICAL_ERROR,
            "check_quality",
            target_path,
            original_error=error,
            context={"operation_time": operation_time},
        )

    def _validate_quality_check_results(
        self, results: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that quality check results are meaningful and complete.

        Args:
            results: Results dictionary to validate
            target_path: Path that was checked

        Raises:
            QualityOperationError: If validation fails
        """
        self._validate_tool_results_presence(results, target_path)
        self._validate_formatting_flag_consistency(results, target_path)

    def _validate_tool_results_presence(
        self, results: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that results contain data for all required tools.

        Args:
            results: Results dictionary to validate
            target_path: Path that was checked

        Raises:
            QualityOperationError: If required tool results are missing
        """
        required_tools = ["black", "isort"]

        for tool in required_tools:
            if self._is_tool_result_missing(results, tool):
                self._raise_missing_tool_result_error(tool, target_path, results)

    def _is_tool_result_missing(self, results: Dict[str, Any], tool: str) -> bool:
        """Check if a tool's result is missing from results.

        Args:
            results: Results dictionary to check
            tool: Tool name to check

        Returns:
            True if tool result is missing and no error was reported
        """
        has_tool_result = tool in results and results[tool]
        has_error_reported = "errors" in results and any(
            tool in error for error in results["errors"]
        )

        return not has_tool_result and not has_error_reported

    def _raise_missing_tool_result_error(
        self, tool: str, target_path: Path, results: Dict[str, Any]
    ) -> None:
        """Raise error for missing tool result.

        Args:
            tool: Tool name that is missing
            target_path: Path that was checked
            results: Results dictionary for context
        """
        raise QualityOperationError(
            f"No {tool} check results and no error reported for {target_path}",
            QualityErrorType.VALIDATION_ERROR,
            f"validate_{tool}_results",
            target_path,
            context={"results": results},
        )

    def _validate_formatting_flag_consistency(
        self, results: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate consistency of formatting flags across tools.

        Args:
            results: Results dictionary to validate
            target_path: Path that was checked
        """
        if not results.get("check_successful", False):
            return

        formatting_flags = self._extract_formatting_flags(results)
        if self._should_validate_flag_consistency(formatting_flags):
            self._check_overall_flag_consistency(formatting_flags, target_path)

    def _extract_formatting_flags(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract formatting flags from results.

        Args:
            results: Results dictionary

        Returns:
            Dictionary containing formatting flags
        """
        return {
            "black_needs": results.get("black", {}).get("needs_formatting"),
            "isort_needs": results.get("isort", {}).get("needs_formatting"),
            "overall_needs": results.get("needs_formatting", False),
        }

    def _should_validate_flag_consistency(
        self, formatting_flags: Dict[str, Any]
    ) -> bool:
        """Check if flag consistency validation should be performed.

        Args:
            formatting_flags: Dictionary of formatting flags

        Returns:
            True if validation should be performed
        """
        return (
            formatting_flags["black_needs"] is not None
            and formatting_flags["isort_needs"] is not None
        )

    def _check_overall_flag_consistency(
        self, formatting_flags: Dict[str, Any], target_path: Path
    ) -> None:
        """Check if overall formatting flag matches individual tool flags.

        Args:
            formatting_flags: Dictionary of formatting flags
            target_path: Path that was checked
        """
        expected_overall = (
            formatting_flags["black_needs"] or formatting_flags["isort_needs"]
        )
        actual_overall = formatting_flags["overall_needs"]

        if actual_overall != expected_overall:
            self._log_formatting_flag_inconsistency(
                target_path, actual_overall, expected_overall, formatting_flags
            )

    def _log_formatting_flag_inconsistency(
        self,
        target_path: Path,
        actual_overall: bool,
        expected_overall: bool,
        formatting_flags: Dict[str, Any],
    ) -> None:
        """Log inconsistency in formatting flags.

        Args:
            target_path: Path that was checked
            actual_overall: Actual overall formatting flag
            expected_overall: Expected overall formatting flag
            formatting_flags: Dictionary of all formatting flags
        """
        self.logger.warning(
            f"Inconsistent needs_formatting flag for {target_path}: "
            f"overall={actual_overall}, expected={expected_overall} "
            f"(black={formatting_flags['black_needs']}, isort={formatting_flags['isort_needs']})"
        )

    def _run_black(self, target_path: Path) -> Dict[str, Any]:
        """Run Black formatter with comprehensive error handling.

        Args:
            target_path: Path to format with Black

        Returns:
            Dictionary with formatting results and validation

        Raises:
            QualityOperationError: If Black execution fails critically
        """
        try:
            self._validate_black_format_target_path(target_path)
            command = self._build_black_format_command(target_path)
            result = self._execute_black_format_command(command, target_path)
            formatted_files = self._process_black_format_output(result)
            black_result = self._build_black_format_result(
                result, command, formatted_files
            )
            self._handle_black_format_failures(
                result, black_result, command, target_path
            )
            self._validate_black_format_execution(result, target_path)

            self.logger.debug(
                f"Black formatting completed: {len(formatted_files)} files formatted, "
                f"return code: {result.get('returncode')}"
            )

            return black_result

        except QualityOperationError:
            raise
        except Exception as e:
            raise QualityOperationError(
                f"Unexpected error during Black formatting: {str(e)}",
                QualityErrorType.UNKNOWN_ERROR,
                "black_format",
                target_path,
                original_error=e,
            )

    def _check_black(self, target_path: Path) -> Dict[str, Any]:
        """Check Black formatting with comprehensive validation.

        Args:
            target_path: Path to check with Black

        Returns:
            Dictionary with check results and validation

        Raises:
            QualityOperationError: If Black check fails critically
        """
        try:
            self._validate_black_check_target_path(target_path)
            command = self._build_black_check_command(target_path)
            result = self._execute_black_check_command(command, target_path)
            files_need_formatting = self._process_black_check_output(result)
            check_result = self._build_black_check_result(
                result, command, files_need_formatting
            )
            self._analyze_black_stderr(result, check_result, command, target_path)
            self._validate_black_check_execution(result, target_path)
            self._validate_black_check_consistency(result, target_path)

            self.logger.debug(
                f"Black check completed: {len(files_need_formatting)} files need formatting, "
                f"return code: {result.get('returncode', 0)}"
            )

            return check_result

        except QualityOperationError:
            raise
        except Exception as e:
            raise QualityOperationError(
                f"Unexpected error during Black check: {str(e)}",
                QualityErrorType.UNKNOWN_ERROR,
                "black_check",
                target_path,
                original_error=e,
            )

    def _validate_black_format_target_path(self, target_path: Path) -> None:
        """Validate that the target path exists for Black formatting."""
        if not target_path.exists():
            raise QualityOperationError(
                f"Target path does not exist: {target_path}",
                QualityErrorType.CONFIGURATION_ERROR,
                "black_format_validate_path",
                target_path,
            )

    def _build_black_format_command(self, target_path: Path) -> List[str]:
        """Build the Black formatting command."""
        return [
            "python",
            "-m",
            "black",
            "--line-length",
            str(self.black_line_length),
            str(target_path),
        ]

    def _execute_black_format_command(
        self, command: List[str], target_path: Path
    ) -> Dict[str, Any]:
        """Execute the Black formatting command."""
        working_dir = target_path.parent if target_path.is_file() else target_path
        runner = ProcessRunner(working_dir=working_dir, timeout=120)
        self.logger.debug(f"Executing Black command: {' '.join(command)}")
        return runner.run_command(command, timeout=120)

    def _process_black_format_output(self, result: Dict[str, Any]) -> List[str]:
        """Process formatted files from Black output."""
        formatted_files = []
        if result["success"] and result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "reformatted" in line.lower():
                    parts = line.split()
                    if parts:
                        formatted_files.append(parts[0])
        return formatted_files

    def _build_black_format_result(
        self, result: Dict[str, Any], command: List[str], formatted_files: List[str]
    ) -> Dict[str, Any]:
        """Build the comprehensive Black format result."""
        return {
            "status": "success" if result["success"] else "failed",
            "files_formatted": formatted_files,
            "files_count": len(formatted_files),
            "command": " ".join(command),
            "returncode": result.get("returncode"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "errors": [],
        }

    def _handle_black_format_failures(
        self,
        result: Dict[str, Any],
        black_result: Dict[str, Any],
        command: List[str],
        target_path: Path,
    ) -> None:
        """Handle Black formatting failures with detailed error analysis."""
        if not result["success"]:
            error_msg = result.get("error", "Black formatting failed")
            stderr = result.get("stderr", "")

            # Analyze error for better classification
            if (
                "not found" in error_msg.lower()
                or "command not found" in stderr.lower()
            ):
                raise QualityOperationError(
                    f"Black tool not found: {error_msg}",
                    QualityErrorType.TOOL_NOT_FOUND,
                    "black_format",
                    target_path,
                    context={"command": " ".join(command), "stderr": stderr},
                )

            if "syntax error" in stderr.lower() or "invalid syntax" in stderr.lower():
                black_result["errors"].append(f"Syntax error in source code: {stderr}")
            else:
                black_result["errors"].append(error_msg)

            # Add stderr to errors if it contains useful information
            if stderr and stderr not in error_msg:
                black_result["errors"].append(f"Black stderr: {stderr}")

    def _validate_black_format_execution(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that Black formatting actually executed."""
        if result.get("returncode") is None:
            raise QualityOperationError(
                "Black execution validation failed: no return code",
                QualityErrorType.VALIDATION_ERROR,
                "black_format",
                target_path,
                context={"result": result},
            )

    def _validate_black_check_target_path(self, target_path: Path) -> None:
        """Validate that the target path exists for Black check."""
        if not target_path.exists():
            raise QualityOperationError(
                f"Target path does not exist: {target_path}",
                QualityErrorType.CONFIGURATION_ERROR,
                "black_check_validate_path",
                target_path,
            )

    def _build_black_check_command(self, target_path: Path) -> List[str]:
        """Build the Black check command."""
        return [
            "python",
            "-m",
            "black",
            "--check",
            "--line-length",
            str(self.black_line_length),
            str(target_path),
        ]

    def _execute_black_check_command(
        self, command: List[str], target_path: Path
    ) -> Dict[str, Any]:
        """Execute the Black check command."""
        working_dir = target_path.parent if target_path.is_file() else target_path
        runner = ProcessRunner(working_dir=working_dir)
        self.logger.debug(f"Executing Black check command: {' '.join(command)}")
        return runner.run_command(command)

    def _process_black_check_output(self, result: Dict[str, Any]) -> List[str]:
        """Process files that need formatting from Black check output."""
        files_need_formatting = []
        if not result["success"] and result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "would be reformatted" in line.lower():
                    parts = line.split()
                    if parts:
                        files_need_formatting.append(parts[0])
        return files_need_formatting

    def _build_black_check_result(
        self,
        result: Dict[str, Any],
        command: List[str],
        files_need_formatting: List[str],
    ) -> Dict[str, Any]:
        """Build the comprehensive Black check result."""
        return {
            "needs_formatting": len(files_need_formatting) > 0,
            "files": files_need_formatting,
            "files_count": len(files_need_formatting),
            "command": " ".join(command),
            "returncode": result.get("returncode"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "check_successful": True,
        }

    def _analyze_black_stderr(
        self,
        result: Dict[str, Any],
        check_result: Dict[str, Any],
        command: List[str],
        target_path: Path,
    ) -> None:
        """Analyze Black stderr for tool errors."""
        stderr = result.get("stderr", "")
        if stderr and "error" in stderr.lower():
            # Check for tool not found
            if "not found" in stderr.lower() or "command not found" in stderr.lower():
                raise QualityOperationError(
                    f"Black tool not found: {stderr}",
                    QualityErrorType.TOOL_NOT_FOUND,
                    "black_check",
                    target_path,
                    context={"command": " ".join(command), "stderr": stderr},
                )

            # Check for syntax errors in source code
            if "syntax error" in stderr.lower() or "invalid syntax" in stderr.lower():
                self.logger.warning(f"Syntax error detected in {target_path}: {stderr}")
                check_result["syntax_error"] = stderr
                check_result["needs_formatting"] = (
                    None  # Cannot determine due to syntax error
                )
            else:
                # Other errors
                self.logger.warning(f"Black check warning for {target_path}: {stderr}")
                check_result["warnings"] = [stderr]

    def _validate_black_check_execution(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that Black check actually executed."""
        if result.get("returncode") is None:
            raise QualityOperationError(
                "Black check validation failed: no return code",
                QualityErrorType.VALIDATION_ERROR,
                "black_check",
                target_path,
                context={"result": result},
            )

    def _validate_black_check_consistency(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate Black check return code consistency."""
        # Black check success means no formatting needed (returncode 0)
        # Black check "failure" usually means formatting needed (returncode 1)
        # Other return codes indicate actual errors
        returncode = result.get("returncode", 0)
        if returncode not in [0, 1]:
            self.logger.warning(
                f"Unexpected Black check return code {returncode} for {target_path}"
            )

    def _run_isort(self, target_path: Path) -> Dict[str, Any]:
        """Run isort formatter with comprehensive error handling.

        Args:
            target_path: Path to format with isort

        Returns:
            Dictionary with formatting results and validation

        Raises:
            QualityOperationError: If isort execution fails critically
        """
        try:
            self._validate_isort_format_target_path(target_path)
            command = self._build_isort_format_command(target_path)
            result = self._execute_isort_format_command(command, target_path)
            formatted_files = self._process_isort_format_output(result)
            isort_result = self._build_isort_format_result(
                result, command, formatted_files
            )
            self._handle_isort_format_failures(
                result, isort_result, command, target_path
            )
            self._validate_isort_format_execution(result, target_path)

            self.logger.debug(
                f"isort formatting completed: {len(formatted_files)} files formatted, "
                f"return code: {result.get('returncode')}"
            )

            return isort_result

        except QualityOperationError:
            raise
        except Exception as e:
            raise QualityOperationError(
                f"Unexpected error during isort formatting: {str(e)}",
                QualityErrorType.UNKNOWN_ERROR,
                "isort_format",
                target_path,
                original_error=e,
            )

    def _validate_isort_format_target_path(self, target_path: Path) -> None:
        """Validate that the target path exists for isort formatting."""
        if not target_path.exists():
            raise QualityOperationError(
                f"Target path does not exist: {target_path}",
                QualityErrorType.CONFIGURATION_ERROR,
                "isort_format_validate_path",
                target_path,
            )

    def _build_isort_format_command(self, target_path: Path) -> list[str]:
        """Build the isort format command."""
        return [
            "python",
            "-m",
            "isort",
            "--profile",
            self.isort_profile,
            str(target_path),
        ]

    def _execute_isort_format_command(
        self, command: list[str], target_path: Path
    ) -> Dict[str, Any]:
        """Execute the isort format command."""
        working_dir = target_path.parent if target_path.is_file() else target_path
        runner = ProcessRunner(working_dir=working_dir, timeout=60)

        self.logger.debug(f"Executing isort command: {' '.join(command)}")
        return runner.run_command(command, timeout=60)

    def _process_isort_format_output(self, result: Dict[str, Any]) -> list[str]:
        """Process isort output to extract formatted files."""
        formatted_files = []
        if result["stdout"]:
            for line in result["stdout"].split("\n"):
                if "Fixing" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".py"):
                            formatted_files.append(part)
        return formatted_files

    def _build_isort_format_result(
        self, result: Dict[str, Any], command: list[str], formatted_files: list[str]
    ) -> Dict[str, Any]:
        """Build the comprehensive isort format result."""
        return {
            "status": "success" if result["success"] else "failed",
            "files_formatted": formatted_files,
            "files_count": len(formatted_files),
            "command": " ".join(command),
            "returncode": result.get("returncode"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "errors": [],
        }

    def _handle_isort_format_failures(
        self,
        result: Dict[str, Any],
        isort_result: Dict[str, Any],
        command: list[str],
        target_path: Path,
    ) -> None:
        """Handle isort format failures with detailed error analysis."""
        if not result["success"]:
            error_msg = result.get("error", "isort formatting failed")
            stderr = result.get("stderr", "")

            self._check_isort_format_tool_availability(
                error_msg, stderr, command, target_path
            )
            self._categorize_isort_format_error(stderr, error_msg, isort_result)
            self._append_stderr_if_different(stderr, error_msg, isort_result)

    def _check_isort_format_tool_availability(
        self, error_msg: str, stderr: str, command: list[str], target_path: Path
    ) -> None:
        """Check if isort tool is available and raise error if not found."""
        if "not found" in error_msg.lower() or "command not found" in stderr.lower():
            raise QualityOperationError(
                f"isort tool not found: {error_msg}",
                QualityErrorType.TOOL_NOT_FOUND,
                "isort_format",
                target_path,
                context={"command": " ".join(command), "stderr": stderr},
            )

    def _categorize_isort_format_error(
        self, stderr: str, error_msg: str, isort_result: Dict[str, Any]
    ) -> None:
        """Categorize the isort format error and add to result."""
        if "syntax error" in stderr.lower() or "invalid syntax" in stderr.lower():
            isort_result["errors"].append(f"Syntax error in source code: {stderr}")
        elif "config" in stderr.lower() or "configuration" in stderr.lower():
            isort_result["errors"].append(f"Configuration error: {stderr}")
        else:
            isort_result["errors"].append(error_msg)

    def _append_stderr_if_different(
        self, stderr: str, error_msg: str, isort_result: Dict[str, Any]
    ) -> None:
        """Append stderr to errors if it contains different information."""
        if stderr and stderr not in error_msg:
            isort_result["errors"].append(f"isort stderr: {stderr}")

    def _validate_isort_format_execution(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that isort actually executed."""
        if result.get("returncode") is None:
            raise QualityOperationError(
                "isort execution validation failed: no return code",
                QualityErrorType.VALIDATION_ERROR,
                "isort_format",
                target_path,
                context={"result": result},
            )

    def _check_isort(self, target_path: Path) -> Dict[str, Any]:
        """Check isort formatting with comprehensive validation.

        Args:
            target_path: Path to check with isort

        Returns:
            Dictionary with check results and validation

        Raises:
            QualityOperationError: If isort check fails critically
        """
        try:
            self._validate_isort_check_target_path(target_path)
            command = self._build_isort_check_command(target_path)
            result = self._execute_isort_check_command(command, target_path)
            files_need_formatting = self._process_isort_diff_output(result)
            check_result = self._build_isort_check_result(
                result, command, files_need_formatting
            )
            self._analyze_isort_stderr(result, check_result, command, target_path)
            self._validate_isort_check_execution(result, target_path)
            self._validate_isort_check_consistency(result, target_path)

            self.logger.debug(
                f"isort check completed: {len(files_need_formatting)} files need formatting, "
                f"return code: {result.get('returncode', 0)}"
            )

            return check_result

        except QualityOperationError:
            raise
        except Exception as e:
            raise QualityOperationError(
                f"Unexpected error during isort check: {str(e)}",
                QualityErrorType.UNKNOWN_ERROR,
                "isort_check",
                target_path,
                original_error=e,
            )

    def _validate_isort_check_target_path(self, target_path: Path) -> None:
        """Validate that the target path exists for isort check."""
        if not target_path.exists():
            raise QualityOperationError(
                f"Target path does not exist: {target_path}",
                QualityErrorType.CONFIGURATION_ERROR,
                "isort_check_validate_path",
                target_path,
            )

    def _build_isort_check_command(self, target_path: Path) -> list[str]:
        """Build the isort check command."""
        return [
            "python",
            "-m",
            "isort",
            "--profile",
            self.isort_profile,
            "--check-only",
            "--diff",
            str(target_path),
        ]

    def _execute_isort_check_command(
        self, command: list[str], target_path: Path
    ) -> Dict[str, Any]:
        """Execute the isort check command."""
        working_dir = target_path.parent if target_path.is_file() else target_path
        runner = ProcessRunner(working_dir=working_dir)

        self.logger.debug(f"Executing isort check command: {' '.join(command)}")
        return runner.run_command(command)

    def _process_isort_diff_output(self, result: Dict[str, Any]) -> list[str]:
        """Process isort diff output to extract files that need formatting."""
        files_need_formatting = []
        if not result["success"] and result["stdout"]:
            for line in result["stdout"].split("\n"):
                if line.startswith("---") or line.startswith("+++"):
                    file_path = line[4:].strip()
                    if file_path and file_path not in files_need_formatting:
                        files_need_formatting.append(file_path)
        return files_need_formatting

    def _build_isort_check_result(
        self,
        result: Dict[str, Any],
        command: list[str],
        files_need_formatting: list[str],
    ) -> Dict[str, Any]:
        """Build the comprehensive isort check result."""
        return {
            "needs_formatting": not result["success"],
            "files": files_need_formatting,
            "files_count": len(files_need_formatting),
            "command": " ".join(command),
            "returncode": result.get("returncode"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "check_successful": True,
        }

    def _analyze_isort_stderr(
        self,
        result: Dict[str, Any],
        check_result: Dict[str, Any],
        command: list[str],
        target_path: Path,
    ) -> None:
        """Analyze isort stderr for errors and warnings."""
        stderr = result.get("stderr", "")
        if not (stderr and "error" in stderr.lower()):
            return

        self._handle_isort_tool_not_found_error(stderr, command, target_path)
        self._classify_and_handle_isort_stderr_error(stderr, check_result, target_path)

    def _handle_isort_tool_not_found_error(
        self, stderr: str, command: list[str], target_path: Path
    ) -> None:
        """Handle isort tool not found errors."""
        if "not found" in stderr.lower() or "command not found" in stderr.lower():
            raise QualityOperationError(
                f"isort tool not found: {stderr}",
                QualityErrorType.TOOL_NOT_FOUND,
                "isort_check",
                target_path,
                context={"command": " ".join(command), "stderr": stderr},
            )

    def _classify_and_handle_isort_stderr_error(
        self, stderr: str, check_result: Dict[str, Any], target_path: Path
    ) -> None:
        """Classify and handle different types of isort stderr errors."""
        if "syntax error" in stderr.lower() or "invalid syntax" in stderr.lower():
            self.logger.warning(f"Syntax error detected in {target_path}: {stderr}")
            check_result["syntax_error"] = stderr
            check_result["needs_formatting"] = None
        elif "config" in stderr.lower() or "configuration" in stderr.lower():
            self.logger.warning(f"Configuration issue in {target_path}: {stderr}")
            check_result["config_error"] = stderr
        else:
            self.logger.warning(f"isort check warning for {target_path}: {stderr}")
            check_result["warnings"] = [stderr]

    def _validate_isort_check_execution(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate that isort check actually executed."""
        if result.get("returncode") is None:
            raise QualityOperationError(
                "isort check validation failed: no return code",
                QualityErrorType.VALIDATION_ERROR,
                "isort_check",
                target_path,
                context={"result": result},
            )

        returncode = result.get("returncode", 0)
        if returncode not in [0, 1]:
            self.logger.warning(
                f"Unexpected isort check return code {returncode} for {target_path}"
            )

    def _validate_isort_check_consistency(
        self, result: Dict[str, Any], target_path: Path
    ) -> None:
        """Validate consistency between isort check result and diff output."""
        has_diff = bool(result.get("stdout", "").strip())
        if has_diff and result["success"]:
            self.logger.warning(
                f"Inconsistent isort check result for {target_path}: "
                f"has diff output but returned success"
            )

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on quality tools.

        Returns:
            Dictionary with health check results for all tools
        """
        self.logger.info("Starting quality tools health check")

        health_results: Dict[str, Any] = {
            "overall_healthy": True,
            "tools": {},
            "timestamp": time.time(),
        }

        # Check Black availability
        try:
            runner = ProcessRunner()
            result = runner.run_command(["python", "-m", "black", "--version"])

            health_results["tools"]["black"] = {
                "available": result["success"],
                "version": (
                    result.get("stdout", "").strip() if result["success"] else None
                ),
                "error": result.get("error") if not result["success"] else None,
            }

            if not result["success"]:
                health_results["overall_healthy"] = False

        except Exception as e:
            health_results["tools"]["black"] = {"available": False, "error": str(e)}
            health_results["overall_healthy"] = False

        # Check isort availability
        try:
            runner = ProcessRunner()
            result = runner.run_command(["python", "-m", "isort", "--version"])

            health_results["tools"]["isort"] = {
                "available": result["success"],
                "version": (
                    result.get("stdout", "").strip() if result["success"] else None
                ),
                "error": result.get("error") if not result["success"] else None,
            }

            if not result["success"]:
                health_results["overall_healthy"] = False

        except Exception as e:
            health_results["tools"]["isort"] = {"available": False, "error": str(e)}
            health_results["overall_healthy"] = False

        # Log health check results
        if health_results["overall_healthy"]:
            self.logger.info("Quality tools health check passed")
        else:
            self.logger.error(f"Quality tools health check failed: {health_results}")

        return health_results
