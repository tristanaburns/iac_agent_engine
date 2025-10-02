"""
Ansible Executor Service Exception Classes
Comprehensive exception hierarchy for robust error handling
"""

from typing import Any, Dict, Optional


class BaseAnsibleExecutorException(Exception):
    """Base exception for Ansible Executor service"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.correlation_id = correlation_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "correlation_id": self.correlation_id,
        }


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================


class ValidationError(BaseAnsibleExecutorException):
    """Raised when input validation fails"""


class PlaybookValidationError(ValidationError):
    """Raised when playbook validation fails"""


class InventoryValidationError(ValidationError):
    """Raised when inventory validation fails"""


class ConfigurationError(ValidationError):
    """Raised when configuration is invalid"""


# ============================================================================
# EXECUTION EXCEPTIONS
# ============================================================================


class ExecutionError(BaseAnsibleExecutorException):
    """Base class for execution-related errors"""


class PlaybookExecutionError(ExecutionError):
    """Raised when playbook execution fails"""

    def __init__(
        self,
        message: str,
        playbook_path: Optional[str] = None,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.playbook_path = playbook_path
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with execution details"""
        result = super().to_dict()
        result["details"].update(
            {
                "playbook_path": self.playbook_path,
                "exit_code": self.exit_code,
                "stdout": self.stdout,
                "stderr": self.stderr,
            }
        )
        return result


class AdhocExecutionError(ExecutionError):
    """Raised when ad-hoc command execution fails"""

    def __init__(
        self,
        message: str,
        module: Optional[str] = None,
        pattern: Optional[str] = None,
        exit_code: Optional[int] = None,
        failed_hosts: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.module = module
        self.pattern = pattern
        self.exit_code = exit_code
        self.failed_hosts = failed_hosts

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with execution details"""
        result = super().to_dict()
        result["details"].update(
            {
                "module": self.module,
                "pattern": self.pattern,
                "exit_code": self.exit_code,
                "failed_hosts": self.failed_hosts,
            }
        )
        return result


class TimeoutError(ExecutionError):
    """Raised when execution times out"""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with timeout details"""
        result = super().to_dict()
        result["details"]["timeout_seconds"] = self.timeout_seconds
        return result


# ============================================================================
# RESOURCE EXCEPTIONS
# ============================================================================


class ResourceError(BaseAnsibleExecutorException):
    """Base class for resource-related errors"""


class PlaybookNotFoundError(ResourceError):
    """Raised when playbook file is not found"""

    def __init__(
        self,
        message: str,
        playbook_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.playbook_path = playbook_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with path details"""
        result = super().to_dict()
        result["details"]["playbook_path"] = self.playbook_path
        return result


class InventoryNotFoundError(ResourceError):
    """Raised when inventory is not found"""

    def __init__(
        self,
        message: str,
        inventory_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.inventory_name = inventory_name

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with inventory details"""
        result = super().to_dict()
        result["details"]["inventory_name"] = self.inventory_name
        return result


class RoleNotFoundError(ResourceError):
    """Raised when role is not found"""

    def __init__(
        self,
        message: str,
        role_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.role_name = role_name

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with role details"""
        result = super().to_dict()
        result["details"]["role_name"] = self.role_name
        return result


class CollectionNotFoundError(ResourceError):
    """Raised when collection is not found"""

    def __init__(
        self,
        message: str,
        collection_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.collection_name = collection_name

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with collection details"""
        result = super().to_dict()
        result["details"]["collection_name"] = self.collection_name
        return result


# ============================================================================
# VAULT EXCEPTIONS
# ============================================================================


class VaultError(BaseAnsibleExecutorException):
    """Base class for Vault-related errors"""


class VaultEncryptionError(VaultError):
    """Raised when Vault encryption fails"""


class VaultDecryptionError(VaultError):
    """Raised when Vault decryption fails"""


class VaultPasswordError(VaultError):
    """Raised when Vault password is invalid or missing"""


class HashiCorpVaultError(VaultError):
    """Raised when HashiCorp Vault integration fails"""

    def __init__(
        self,
        message: str,
        vault_path: Optional[str] = None,
        vault_status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.vault_path = vault_path
        self.vault_status_code = vault_status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with Vault details"""
        result = super().to_dict()
        result["details"].update(
            {
                "vault_path": self.vault_path,
                "vault_status_code": self.vault_status_code,
            }
        )
        return result


# ============================================================================
# GIT EXCEPTIONS
# ============================================================================


class GitError(BaseAnsibleExecutorException):
    """Base class for Git-related errors"""


class GitCloneError(GitError):
    """Raised when Git clone operation fails"""

    def __init__(
        self,
        message: str,
        repository_url: Optional[str] = None,
        branch: Optional[str] = None,
        exit_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.repository_url = repository_url
        self.branch = branch
        self.exit_code = exit_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with Git details"""
        result = super().to_dict()
        result["details"].update(
            {
                "repository_url": self.repository_url,
                "branch": self.branch,
                "exit_code": self.exit_code,
            }
        )
        return result


class GitAuthenticationError(GitError):
    """Raised when Git authentication fails"""


# ============================================================================
# SYSTEM EXCEPTIONS
# ============================================================================


class SystemError(BaseAnsibleExecutorException):
    """Base class for system-level errors"""


class AnsibleNotFoundError(SystemError):
    """Raised when Ansible is not installed or not found"""


class InsufficientPermissionsError(SystemError):
    """Raised when insufficient permissions to perform operation"""


class DiskSpaceError(SystemError):
    """Raised when insufficient disk space"""

    def __init__(
        self,
        message: str,
        required_space: Optional[int] = None,
        available_space: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.required_space = required_space
        self.available_space = available_space

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with disk space details"""
        result = super().to_dict()
        result["details"].update(
            {
                "required_space": self.required_space,
                "available_space": self.available_space,
            }
        )
        return result


# ============================================================================
# CELERY/ASYNC EXCEPTIONS
# ============================================================================


class TaskError(BaseAnsibleExecutorException):
    """Base class for async task errors"""


class JobNotFoundError(TaskError):
    """Raised when job is not found"""

    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.job_id = job_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with job details"""
        result = super().to_dict()
        result["details"]["job_id"] = self.job_id
        return result


class JobCancellationError(TaskError):
    """Raised when job cancellation fails"""


class CeleryConnectionError(TaskError):
    """Raised when Celery connection fails"""


# ============================================================================
# SECURITY EXCEPTIONS
# ============================================================================


class SecurityError(BaseAnsibleExecutorException):
    """Base class for security-related errors"""


class AuthenticationError(SecurityError):
    """Raised when authentication fails"""


class AuthorizationError(SecurityError):
    """Raised when authorization fails"""

    def __init__(
        self,
        message: str,
        required_permission: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.required_permission = required_permission

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with authorization details"""
        result = super().to_dict()
        result["details"]["required_permission"] = self.required_permission
        return result


class SecurityPolicyViolationError(SecurityError):
    """Raised when security policy is violated"""

    def __init__(
        self,
        message: str,
        policy_name: Optional[str] = None,
        violation_details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.policy_name = policy_name
        self.violation_details = violation_details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with policy violation details"""
        result = super().to_dict()
        result["details"].update(
            {
                "policy_name": self.policy_name,
                "violation_details": self.violation_details,
            }
        )
        return result


# ============================================================================
# SERVICE EXCEPTIONS
# ============================================================================


class ServiceUnavailableError(BaseAnsibleExecutorException):
    """Raised when service is temporarily unavailable"""


class ServiceDegradedError(BaseAnsibleExecutorException):
    """Raised when service is running in degraded mode"""


class CircuitBreakerOpenError(BaseAnsibleExecutorException):
    """Raised when circuit breaker is open"""

    def __init__(
        self,
        message: str,
        retry_after_seconds: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with retry information"""
        result = super().to_dict()
        result["details"]["retry_after_seconds"] = self.retry_after_seconds
        return result


# ============================================================================
# EXCEPTION MAPPING UTILITIES
# ============================================================================


def map_ansible_exit_code_to_exception(
    exit_code: int,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
) -> BaseAnsibleExecutorException:
    """Map Ansible exit codes to appropriate exceptions"""

    error_messages = {
        1: "General errors",
        2: "Misuse of shell builtins",
        4: "Ansible could not be run",
        5: "Host is unreachable",
        99: "Unexpected failure",
        250: "Unexpected error",
    }

    message = error_messages.get(exit_code, f"Unknown error (exit code: {exit_code})")

    if exit_code == 4:
        return AnsibleNotFoundError(
            message=f"Ansible execution failed: {message}",
            error_code="ANSIBLE_NOT_EXECUTABLE",
        )
    elif exit_code == 5:
        return ExecutionError(
            message=f"Host unreachable: {message}",
            error_code="HOST_UNREACHABLE",
            details={"exit_code": exit_code, "stdout": stdout, "stderr": stderr},
        )
    else:
        return ExecutionError(
            message=f"Ansible execution failed: {message}",
            error_code="ANSIBLE_EXECUTION_FAILED",
            details={"exit_code": exit_code, "stdout": stdout, "stderr": stderr},
        )


def is_retryable_error(exception: BaseAnsibleExecutorException) -> bool:
    """Determine if an error is retryable"""

    retryable_errors = (
        TimeoutError,
        ServiceUnavailableError,
        CeleryConnectionError,
        SystemError,  # Some system errors may be temporary
    )

    non_retryable_errors = (
        ValidationError,
        PlaybookNotFoundError,
        InventoryNotFoundError,
        AuthenticationError,
        AuthorizationError,
        SecurityPolicyViolationError,
        AnsibleNotFoundError,
    )

    if isinstance(exception, non_retryable_errors):
        return False

    if isinstance(exception, retryable_errors):
        return True

    # For ExecutionError, check exit code if available
    if isinstance(exception, ExecutionError):
        if hasattr(exception, "exit_code") and exception.exit_code:
            # Exit code 4 (Ansible not executable) is not retryable
            if exception.exit_code == 4:
                return False
            # Other execution errors might be retryable
            return True

    return False
