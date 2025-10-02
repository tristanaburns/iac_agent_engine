"""
State Management Service Custom Exceptions
Comprehensive exception hierarchy for state management operations
"""

from typing import Any, Dict, Optional


class StateManagementError(Exception):
    """Base exception for state management operations"""

    def __init__(
        self,
        message: str,
        error_code: str = "iac_agent_manager_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(StateManagementError):
    """Configuration-related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR", details)


class BackendError(StateManagementError):
    """Backend storage errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "BACKEND_ERROR", details)


class MinIOConnectionError(BackendError):
    """MinIO connection errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class MinIOBucketError(BackendError):
    """MinIO bucket operation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class StateNotFoundError(StateManagementError):
    """State not found errors"""

    def __init__(
        self, backend_id: str, workspace: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        message = f"State not found for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, "STATE_NOT_FOUND", details)
        self.backend_id = backend_id
        self.workspace = workspace


class StateLockedError(StateManagementError):
    """State locked errors"""

    def __init__(
        self,
        backend_id: str,
        workspace: str,
        lock_info: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"State is locked for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, "STATE_LOCKED", details)
        self.backend_id = backend_id
        self.workspace = workspace
        self.lock_info = lock_info or {}


class StateLockError(StateManagementError):
    """State locking operation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "STATE_LOCK_ERROR", details)


class LockNotFoundError(StateLockError):
    """Lock not found errors"""

    def __init__(
        self,
        backend_id: str,
        workspace: str,
        lock_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Lock '{lock_id}' not found for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, details)
        self.backend_id = backend_id
        self.workspace = workspace
        self.lock_id = lock_id


class LockExpiredError(StateLockError):
    """Lock expired errors"""

    def __init__(
        self,
        backend_id: str,
        workspace: str,
        lock_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Lock '{lock_id}' has expired for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, details)
        self.backend_id = backend_id
        self.workspace = workspace
        self.lock_id = lock_id


class StateVersionError(StateManagementError):
    """State version management errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "STATE_VERSION_ERROR", details)


class VersionNotFoundError(StateVersionError):
    """Version not found errors"""

    def __init__(
        self,
        backend_id: str,
        workspace: str,
        version_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Version '{version_id}' not found for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, details)
        self.backend_id = backend_id
        self.workspace = workspace
        self.version_id = version_id


class StateValidationError(StateManagementError):
    """State data validation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "STATE_VALIDATION_ERROR", details)


class StateCorruptedError(StateValidationError):
    """State data corruption errors"""

    def __init__(
        self,
        backend_id: str,
        workspace: str,
        checksum_expected: str,
        checksum_actual: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = (
            f"State corrupted for backend '{backend_id}' workspace '{workspace}': "
            f"checksum mismatch (expected: {checksum_expected}, actual: {checksum_actual})"
        )
        super().__init__(message, details)
        self.backend_id = backend_id
        self.workspace = workspace
        self.checksum_expected = checksum_expected
        self.checksum_actual = checksum_actual


class EncryptionError(StateManagementError):
    """Encryption/decryption errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "ENCRYPTION_ERROR", details)


class VaultConnectionError(EncryptionError):
    """Vault connection errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class VaultAuthenticationError(EncryptionError):
    """Vault authentication errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class EncryptionKeyError(EncryptionError):
    """Encryption key management errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class BackupError(StateManagementError):
    """Backup operation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "BACKUP_ERROR", details)


class BackupNotFoundError(BackupError):
    """Backup not found errors"""

    def __init__(
        self,
        backup_id: str,
        backend_id: str,
        workspace: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Backup '{backup_id}' not found for backend '{backend_id}' workspace '{workspace}'"
        super().__init__(message, details)
        self.backup_id = backup_id
        self.backend_id = backend_id
        self.workspace = workspace


class BackupCorruptedError(BackupError):
    """Backup corruption errors"""

    def __init__(
        self,
        backup_id: str,
        checksum_expected: str,
        checksum_actual: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = (
            f"Backup '{backup_id}' is corrupted: "
            f"checksum mismatch (expected: {checksum_expected}, actual: {checksum_actual})"
        )
        super().__init__(message, details)
        self.backup_id = backup_id
        self.checksum_expected = checksum_expected
        self.checksum_actual = checksum_actual


class RestoreError(BackupError):
    """Restore operation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details)


class RedisConnectionError(StateManagementError):
    """Redis connection errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "REDIS_CONNECTION_ERROR", details)


class RateLimitError(StateManagementError):
    """Rate limiting errors"""

    def __init__(
        self,
        client_id: str,
        limit: int,
        window: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Rate limit exceeded for client '{client_id}': {limit} requests per {window} seconds"
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)
        self.client_id = client_id
        self.limit = limit
        self.window = window


class AuthenticationError(StateManagementError):
    """Authentication errors"""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(StateManagementError):
    """Authorization errors"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationError(StateManagementError):
    """Request validation errors"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class TimeoutError(StateManagementError):
    """Operation timeout errors"""

    def __init__(
        self, operation: str, timeout: int, details: Optional[Dict[str, Any]] = None
    ) -> None:
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.operation = operation
        self.timeout = timeout


class QuotaExceededError(StateManagementError):
    """Resource quota exceeded errors"""

    def __init__(
        self,
        resource: str,
        current: int,
        limit: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"Quota exceeded for {resource}: {current}/{limit}"
        super().__init__(message, "QUOTA_EXCEEDED", details)
        self.resource = resource
        self.current = current
        self.limit = limit


class ServiceUnavailableError(StateManagementError):
    """Service unavailable errors"""

    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None) -> None:
        message = f"Service '{service}' is currently unavailable"
        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service = service


class MaintenanceModeError(StateManagementError):
    """Maintenance mode errors"""

    def __init__(
        self,
        message: str = "Service is in maintenance mode",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, "MAINTENANCE_MODE", details)
