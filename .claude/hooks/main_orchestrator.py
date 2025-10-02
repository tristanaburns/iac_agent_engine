"""Main orchestrator following SOLID principles.

Single Responsibility: Coordinates all hook operations through sub-orchestrators.
"""

import threading
import time
import weakref
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class ResourceType(Enum):
    """Types of resources that need cleanup."""

    SDK_CLIENT = "sdk_client"
    SUB_ORCHESTRATOR = "sub_orchestrator"
    DATABASE_CONNECTION = "database_connection"
    FILE_HANDLE = "file_handle"
    NETWORK_CONNECTION = "network_connection"
    TEMPORARY_FILE = "temporary_file"
    CACHE = "cache"
    THREAD = "thread"
    PROCESS = "process"
    MEMORY_BUFFER = "memory_buffer"


@dataclass
class ResourceInfo:
    """Information about a registered resource."""

    resource_id: str
    resource_type: ResourceType
    resource_ref: weakref.ReferenceType
    cleanup_func: Callable
    cleanup_args: tuple = field(default_factory=tuple)
    cleanup_kwargs: dict = field(default_factory=dict)
    critical: bool = True  # Critical resources must be cleaned up
    retry_count: int = 3
    timeout: float = 30.0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

    def update_access_time(self):
        """Update the last accessed timestamp."""
        self.last_accessed = time.time()

    def is_alive(self) -> bool:
        """Check if the resource reference is still alive."""
        return self.resource_ref() is not None


@dataclass
class CleanupResult:
    """Result of cleanup operations."""

    success: bool
    success_count: int = 0
    failed_count: int = 0
    duration: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class ResourceRegistry:
    """Registry for tracking and cleaning up resources with retry logic and verification."""

    def __init__(self, logger=None):
        """Initialize the resource registry."""
        self.logger = logger
        self._resources: Dict[str, ResourceInfo] = {}
        self._lock = threading.RLock()
        self._cleanup_hooks: List[Callable] = []
        self._emergency_procedures: List[Callable] = []

    def register_resource(
        self,
        resource_id: str,
        resource: Any,
        resource_type: ResourceType,
        cleanup_func: Callable,
        cleanup_args: tuple = (),
        cleanup_kwargs: dict = None,
        critical: bool = True,
        retry_count: int = 3,
        timeout: float = 30.0,
    ) -> bool:
        """Register a resource for cleanup.

        Args:
            resource_id: Unique identifier for the resource
            resource: The actual resource object
            resource_type: Type of resource
            cleanup_func: Function to call for cleanup
            cleanup_args: Arguments for cleanup function
            cleanup_kwargs: Keyword arguments for cleanup function
            critical: Whether this resource is critical and must be cleaned
            retry_count: Number of retry attempts for cleanup
            timeout: Timeout for cleanup operation

        Returns:
            True if registration successful, False otherwise
        """
        try:
            with self._lock:
                if cleanup_kwargs is None:
                    cleanup_kwargs = {}

                # Create weak reference to avoid circular dependencies
                resource_ref = weakref.ref(resource)

                resource_info = ResourceInfo(
                    resource_id=resource_id,
                    resource_type=resource_type,
                    resource_ref=resource_ref,
                    cleanup_func=cleanup_func,
                    cleanup_args=cleanup_args,
                    cleanup_kwargs=cleanup_kwargs,
                    critical=critical,
                    retry_count=retry_count,
                    timeout=timeout,
                )

                self._resources[resource_id] = resource_info

                if self.logger:
                    self.logger.debug(
                        f"ResourceRegistry: Registered {resource_type.value} resource '{resource_id}' "
                        f"(critical={critical}, timeout={timeout}s)"
                    )

                return True

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"ResourceRegistry: Failed to register resource '{resource_id}': {e}"
                )
            return False

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource."""
        try:
            with self._lock:
                if resource_id in self._resources:
                    del self._resources[resource_id]
                    if self.logger:
                        self.logger.debug(
                            f"ResourceRegistry: Unregistered resource '{resource_id}'"
                        )
                    return True
                return False
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"ResourceRegistry: Failed to unregister resource '{resource_id}': {e}"
                )
            return False

    def _validate_resource_for_cleanup(
        self, resource_id: str
    ) -> Tuple[bool, Optional["ResourceInfo"]]:
        """Validate that a resource exists and can be cleaned up.

        Args:
            resource_id: ID of resource to validate

        Returns:
            Tuple of (success, resource_info or None)
        """
        if resource_id not in self._resources:
            if self.logger:
                self.logger.warning(
                    f"ResourceRegistry: Resource '{resource_id}' not found for cleanup"
                )
            return False, None

        return True, self._resources[resource_id]

    def _handle_garbage_collected_resource(
        self, resource_id: str, resource_info: "ResourceInfo"
    ) -> Optional[bool]:
        """Handle cleanup of a garbage collected resource.

        Args:
            resource_id: ID of resource to check
            resource_info: Resource information object

        Returns:
            True if resource was garbage collected and cleaned up,
            None if resource is still alive (no action taken)
        """
        if not resource_info.is_alive():
            if self.logger:
                self.logger.debug(
                    f"ResourceRegistry: Resource '{resource_id}' already garbage collected"
                )
            del self._resources[resource_id]
            return True

        return None

    def _execute_cleanup_function(
        self, resource_info: "ResourceInfo", resource
    ) -> None:
        """Execute the cleanup function for a resource.

        Args:
            resource_info: Resource information containing cleanup details
            resource: The actual resource object to cleanup
        """
        resource_info.cleanup_func(
            resource,
            *resource_info.cleanup_args,
            **resource_info.cleanup_kwargs,
        )

    def _cleanup_with_timeout_handling(
        self,
        resource_id: str,
        resource_info: "ResourceInfo",
        resource,
        timeout: float,
        attempt: int,
    ) -> bool:
        """Execute cleanup with timeout handling.

        Args:
            resource_id: ID of resource being cleaned up
            resource_info: Resource information object
            resource: The actual resource object
            timeout: Timeout in seconds
            attempt: Current attempt number (1-based)

        Returns:
            True if cleanup successful, False if timeout occurred
        """
        import concurrent.futures

        def cleanup_with_timeout():
            return self._execute_cleanup_function(resource_info, resource)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(cleanup_with_timeout)
            try:
                future.result(timeout=timeout)
                return True
            except concurrent.futures.TimeoutError:
                if self.logger:
                    self.logger.warning(
                        f"ResourceRegistry: Cleanup timeout for '{resource_id}' "
                        f"(attempt {attempt})"
                    )
                return False

    def _execute_resource_cleanup_attempt(
        self,
        resource_id: str,
        resource_info: "ResourceInfo",
        attempt: int,
        total_attempts: int,
        timeout: Optional[float],
    ) -> bool:
        """Execute a single cleanup attempt for a resource.

        Args:
            resource_id: ID of resource to cleanup
            resource_info: Resource information object
            attempt: Current attempt number (0-based)
            total_attempts: Total number of attempts
            timeout: Optional timeout in seconds

        Returns:
            True if cleanup successful, False otherwise
        """
        if self.logger:
            self.logger.debug(
                f"ResourceRegistry: Cleaning up '{resource_id}' "
                f"(attempt {attempt + 1}/{total_attempts})"
            )

        # Get the actual resource
        resource = resource_info.resource_ref()
        if resource is None:
            if self.logger:
                self.logger.debug(
                    f"ResourceRegistry: Resource '{resource_id}' already gone"
                )
            del self._resources[resource_id]
            return True

        # Execute cleanup with or without timeout
        if timeout:
            cleanup_success = self._cleanup_with_timeout_handling(
                resource_id, resource_info, resource, timeout, attempt + 1
            )
            if not cleanup_success:
                return False
        else:
            self._execute_cleanup_function(resource_info, resource)

        # Verify cleanup if possible
        if hasattr(resource, "__del__") or not resource_info.is_alive():
            if self.logger:
                self.logger.debug(
                    f"ResourceRegistry: Successfully cleaned up '{resource_id}'"
                )

        return True

    def _execute_cleanup_with_retries(
        self,
        resource_id: str,
        resource_info: "ResourceInfo",
        retry_count: int,
        timeout: Optional[float],
    ) -> bool:
        """Execute cleanup with retry logic.

        Args:
            resource_id: ID of resource to cleanup
            resource_info: Resource information object
            retry_count: Number of retry attempts
            timeout: Optional timeout in seconds

        Returns:
            True if cleanup successful, False otherwise
        """
        for attempt in range(retry_count):
            try:
                success = self._execute_resource_cleanup_attempt(
                    resource_id, resource_info, attempt, retry_count, timeout
                )
                if success:
                    return True

            except Exception as cleanup_error:
                if self.logger:
                    self.logger.warning(
                        f"ResourceRegistry: Cleanup attempt {attempt + 1} failed for '{resource_id}': "
                        f"{cleanup_error}"
                    )

                if attempt == retry_count - 1:  # Last attempt
                    if self.logger:
                        self.logger.error(
                            f"ResourceRegistry: All cleanup attempts failed for '{resource_id}': "
                            f"{cleanup_error}"
                        )
                    return False

                # Wait before retry with exponential backoff
                time.sleep(0.1 * (attempt + 1))

        return False

    def cleanup_resource(self, resource_id: str, force: bool = False) -> bool:
        """Cleanup a specific resource with retry logic.

        Args:
            resource_id: ID of resource to cleanup
            force: If True, ignore timeout and retry settings

        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            with self._lock:
                # Validate resource exists
                is_valid, resource_info = self._validate_resource_for_cleanup(
                    resource_id
                )
                if not is_valid or resource_info is None:
                    return False

                # Handle garbage collected resources
                gc_result = self._handle_garbage_collected_resource(
                    resource_id, resource_info
                )
                if gc_result is not None:
                    return gc_result

                # Determine retry and timeout settings
                retry_count = 1 if force else resource_info.retry_count
                timeout = None if force else resource_info.timeout

                # Execute cleanup with retries
                cleanup_success = self._execute_cleanup_with_retries(
                    resource_id, resource_info, retry_count, timeout
                )

                if cleanup_success:
                    del self._resources[resource_id]
                    return True

                return False

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"ResourceRegistry: Unexpected error during cleanup of '{resource_id}': {e}"
                )
            return False

    def cleanup_all_resources(self, critical_only: bool = False) -> CleanupResult:
        """Cleanup all registered resources.

        Args:
            critical_only: If True, only cleanup critical resources

        Returns:
            CleanupResult with summary of cleanup operation
        """
        start_time = time.time()
        success_count = 0
        failed_count = 0
        errors: list[str] = []

        try:
            with self._lock:
                resources_to_cleanup = self._prepare_resources_for_cleanup(
                    critical_only
                )
                self._log_cleanup_start(resources_to_cleanup, critical_only)

                success_count, failed_count, errors = self._execute_resource_cleanup(
                    resources_to_cleanup
                )

        except Exception as e:
            self._handle_critical_cleanup_error(e, errors)

        duration = time.time() - start_time
        result = self._create_cleanup_result(
            success_count, failed_count, duration, critical_only, errors
        )

        self._log_cleanup_completion(success_count, failed_count, duration)
        return result

    def _prepare_resources_for_cleanup(
        self, critical_only: bool
    ) -> List[Tuple[str, ResourceInfo]]:
        """Prepare list of resources for cleanup with appropriate filtering and sorting.

        Args:
            critical_only: If True, only include critical resources

        Returns:
            List of resource tuples sorted for cleanup
        """
        # Get resources to cleanup (copy to avoid modification during iteration)
        resources_to_cleanup = list(self._resources.items())

        if critical_only:
            resources_to_cleanup = [
                (rid, rinfo) for rid, rinfo in resources_to_cleanup if rinfo.critical
            ]

        # Sort by creation time (cleanup in reverse order)
        resources_to_cleanup.sort(key=lambda x: x[1].created_at, reverse=True)
        return resources_to_cleanup

    def _log_cleanup_start(
        self, resources_to_cleanup: List[Tuple[str, ResourceInfo]], critical_only: bool
    ) -> None:
        """Log the start of cleanup operation.

        Args:
            resources_to_cleanup: List of resources to be cleaned up
            critical_only: Whether only critical resources are being cleaned
        """
        if self.logger:
            self.logger.info(
                f"ResourceRegistry: Starting cleanup of {len(resources_to_cleanup)} resources "
                f"(critical_only={critical_only})"
            )

    def _execute_resource_cleanup(
        self, resources_to_cleanup: List[Tuple[str, ResourceInfo]]
    ) -> Tuple[int, int, List[str]]:
        """Execute cleanup for all resources in the list.

        Args:
            resources_to_cleanup: List of resources to clean up

        Returns:
            Tuple of (success_count, failed_count, errors)
        """
        success_count = 0
        failed_count = 0
        errors = []

        for resource_id, resource_info in resources_to_cleanup:
            try:
                if self.cleanup_resource(resource_id, force=False):
                    success_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed to cleanup resource '{resource_id}'")
            except Exception as e:
                failed_count += 1
                error_msg = f"Exception during cleanup of '{resource_id}': {e}"
                errors.append(error_msg)
                if self.logger:
                    self.logger.error(f"ResourceRegistry: {error_msg}")

        return success_count, failed_count, errors

    def _handle_critical_cleanup_error(
        self, error: Exception, errors: List[str]
    ) -> None:
        """Handle critical errors during cleanup operation.

        Args:
            error: The exception that occurred
            errors: List to append error message to
        """
        error_msg = f"Critical error during resource cleanup: {error}"
        errors.append(error_msg)
        if self.logger:
            self.logger.critical(f"ResourceRegistry: {error_msg}")

    def _create_cleanup_result(
        self,
        success_count: int,
        failed_count: int,
        duration: float,
        critical_only: bool,
        errors: List[str],
    ) -> CleanupResult:
        """Create CleanupResult object with calculated metrics.

        Args:
            success_count: Number of successful cleanups
            failed_count: Number of failed cleanups
            duration: Time taken for cleanup
            critical_only: Whether only critical resources were cleaned
            errors: List of error messages

        Returns:
            CleanupResult object
        """
        success = failed_count == 0
        total_resources = success_count + failed_count

        return CleanupResult(
            success=success,
            success_count=success_count,
            failed_count=failed_count,
            duration=duration,
            summary={
                "total_resources": total_resources,
                "success_rate": success_count / max(total_resources, 1) * 100,
                "critical_only": critical_only,
                "remaining_resources": len(self._resources),
            },
            errors=errors,
        )

    def _log_cleanup_completion(
        self, success_count: int, failed_count: int, duration: float
    ) -> None:
        """Log the completion of cleanup operation.

        Args:
            success_count: Number of successful cleanups
            failed_count: Number of failed cleanups
            duration: Time taken for cleanup
        """
        if self.logger:
            self.logger.info(
                f"ResourceRegistry: Cleanup completed - Success: {success_count}, "
                f"Failed: {failed_count}, Duration: {duration:.3f}s"
            )

    def emergency_cleanup(self) -> CleanupResult:
        """Emergency cleanup procedures for critical failures."""
        self._log_emergency_start()

        start_time = time.time()
        success_count = 0
        failed_count = 0
        errors = []

        try:
            # Execute emergency procedures
            procedure_success, procedure_failed, procedure_errors = (
                self._execute_emergency_procedures()
            )
            success_count += procedure_success
            failed_count += procedure_failed
            errors.extend(procedure_errors)

            # Force cleanup of all remaining resources
            resource_success, resource_failed, resource_errors = (
                self._force_cleanup_remaining_resources()
            )
            success_count += resource_success
            failed_count += resource_failed
            errors.extend(resource_errors)

        except Exception as e:
            self._handle_emergency_critical_error(e, errors)

        duration = time.time() - start_time
        result = self._create_emergency_cleanup_result(
            success_count, failed_count, duration, errors
        )

        self._log_emergency_completion(success_count, failed_count, duration)
        return result

    def _log_emergency_start(self) -> None:
        """Log the start of emergency cleanup procedures."""
        if self.logger:
            self.logger.critical(
                "ResourceRegistry: Initiating emergency cleanup procedures"
            )

    def _execute_emergency_procedures(self) -> Tuple[int, int, List[str]]:
        """Execute all registered emergency procedures.

        Returns:
            Tuple of (success_count, failed_count, errors)
        """
        success_count = 0
        failed_count = 0
        errors = []

        for procedure in self._emergency_procedures:
            try:
                procedure()
                success_count += 1
            except Exception as e:
                failed_count += 1
                error_msg = f"Emergency procedure failed: {e}"
                errors.append(error_msg)
                if self.logger:
                    self.logger.error(f"ResourceRegistry: {error_msg}")

        return success_count, failed_count, errors

    def _force_cleanup_remaining_resources(self) -> Tuple[int, int, List[str]]:
        """Force cleanup of all remaining resources.

        Returns:
            Tuple of (success_count, failed_count, errors)
        """
        success_count = 0
        failed_count = 0
        errors = []

        with self._lock:
            remaining_resources = list(self._resources.keys())
            for resource_id in remaining_resources:
                try:
                    if self.cleanup_resource(resource_id, force=True):
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Emergency cleanup failed for '{resource_id}'")
                except Exception as e:
                    failed_count += 1
                    error_msg = f"Emergency cleanup exception for '{resource_id}': {e}"
                    errors.append(error_msg)
                    if self.logger:
                        self.logger.error(f"ResourceRegistry: {error_msg}")

        return success_count, failed_count, errors

    def _handle_emergency_critical_error(
        self, error: Exception, errors: List[str]
    ) -> None:
        """Handle critical errors during emergency cleanup.

        Args:
            error: The exception that occurred
            errors: List to append error message to
        """
        error_msg = f"Critical error during emergency cleanup: {error}"
        errors.append(error_msg)
        if self.logger:
            self.logger.critical(f"ResourceRegistry: {error_msg}")

    def _create_emergency_cleanup_result(
        self, success_count: int, failed_count: int, duration: float, errors: List[str]
    ) -> CleanupResult:
        """Create CleanupResult for emergency cleanup operation.

        Args:
            success_count: Number of successful operations
            failed_count: Number of failed operations
            duration: Time taken for cleanup
            errors: List of error messages

        Returns:
            CleanupResult object
        """
        success = failed_count == 0

        return CleanupResult(
            success=success,
            success_count=success_count,
            failed_count=failed_count,
            duration=duration,
            summary={
                "emergency_mode": True,
                "remaining_resources": len(self._resources),
            },
            errors=errors,
        )

    def _log_emergency_completion(
        self, success_count: int, failed_count: int, duration: float
    ) -> None:
        """Log the completion of emergency cleanup.

        Args:
            success_count: Number of successful operations
            failed_count: Number of failed operations
            duration: Time taken for cleanup
        """
        if self.logger:
            self.logger.critical(
                f"ResourceRegistry: Emergency cleanup completed - Success: {success_count}, "
                f"Failed: {failed_count}, Duration: {duration:.3f}s"
            )

    def add_emergency_procedure(self, procedure: Callable):
        """Add an emergency cleanup procedure."""
        self._emergency_procedures.append(procedure)

    def get_resource_status(self) -> Dict[str, Any]:
        """Get status of all registered resources."""
        with self._lock:
            status: Dict[str, Any] = {
                "total_resources": len(self._resources),
                "critical_resources": sum(
                    1 for r in self._resources.values() if r.critical
                ),
                "alive_resources": sum(
                    1 for r in self._resources.values() if r.is_alive()
                ),
                "resource_types": {},
                "oldest_resource_age": 0,
            }

            current_time = time.time()
            oldest_age = 0.0

            for resource_info in self._resources.values():
                # Count by type
                resource_type = resource_info.resource_type.value
                if resource_type not in status["resource_types"]:
                    status["resource_types"][resource_type] = 0
                status["resource_types"][resource_type] += 1

                # Track oldest resource
                age = current_time - resource_info.created_at
                if age > oldest_age:
                    oldest_age = age

            status["oldest_resource_age"] = oldest_age
            return status


class MainOrchestrator:
    """Main orchestrator that coordinates all hook operations."""

    def __init__(self):
        """Initialize main orchestrator with sub-orchestrators."""
        # Import logger with proper error handling
        try:
            from operations.logging.logger import logger

            self.logger = logger
            self.logger.debug("MainOrchestrator: Logger imported successfully")
        except ImportError as e:
            import logging
            import sys

            # Create a fallback logger for critical error reporting
            logging.basicConfig(level=logging.ERROR)
            fallback_logger = logging.getLogger(__name__)
            fallback_logger.error(f"CRITICAL: Failed to import logger: {e}")
            fallback_logger.debug(f"Current working directory: {Path.cwd()}")
            fallback_logger.debug(f"Script location: {Path(__file__)}")
            fallback_logger.debug(f"sys.path[0]: {sys.path[0] if sys.path else 'None'}")
            raise ImportError(
                f"Critical import failure - cannot load logger: {e}"
            ) from e

        # Initialize resource registry for proper cleanup tracking
        self.resource_registry = ResourceRegistry(logger=self.logger)
        self._setup_emergency_procedures()

        # Initialize path resolver with proper error handling
        try:
            from utils.path_resolver import PathResolver

            self.path_resolver = PathResolver()
            self.logger.debug("MainOrchestrator: PathResolver imported successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import PathResolver: {e}")
            self.logger.debug(f"Current working directory: {Path.cwd()}")
            self.logger.debug(f"Script location: {Path(__file__)}")
            self.logger.debug(
                f"sys.path contains: {[p for p in sys.path if 'hooks' in p]}"
            )
            raise ImportError(
                f"Cannot load PathResolver - check package structure: {e}"
            ) from e

        # Initialize sub-orchestrators (lazy loading)
        self._quality_orchestrator = None
        self._cleanup_orchestrator = None
        self._remediation_orchestrator = None
        self._sdk_client = None

    def _setup_emergency_procedures(self):
        """Setup emergency cleanup procedures for critical failures."""
        # Register emergency procedures
        self.resource_registry.add_emergency_procedure(self._emergency_sdk_shutdown)
        self.resource_registry.add_emergency_procedure(
            self._emergency_orchestrator_cleanup
        )

    def _emergency_sdk_shutdown(self):
        """Emergency SDK client shutdown."""
        if not self._sdk_client:
            return

        try:
            self._execute_sdk_shutdown()
            self._sdk_client = None
            self.logger.debug("Emergency SDK shutdown completed")
        except Exception as e:
            self.logger.error(f"Emergency SDK shutdown failed: {e}")

    def _execute_sdk_shutdown(self):
        """Execute SDK shutdown with proper method detection."""
        if hasattr(self._sdk_client, "close"):
            self._sdk_client.close()
        elif hasattr(self._sdk_client, "shutdown"):
            self._sdk_client.shutdown()

    def _emergency_orchestrator_cleanup(self):
        """Emergency cleanup of sub-orchestrators."""
        orchestrator_names = [
            "_quality_orchestrator",
            "_cleanup_orchestrator",
            "_remediation_orchestrator",
        ]

        for attr_name in orchestrator_names:
            self._cleanup_single_orchestrator(attr_name)

    def _cleanup_single_orchestrator(self, attr_name: str):
        """Cleanup a single orchestrator by attribute name."""
        orchestrator = getattr(self, attr_name, None)
        if not orchestrator:
            return

        try:
            self._execute_orchestrator_cleanup(orchestrator)
            setattr(self, attr_name, None)
            self.logger.debug(f"Emergency cleanup of {attr_name} completed")
        except Exception as e:
            self.logger.error(f"Emergency cleanup of {attr_name} failed: {e}")

    def _execute_orchestrator_cleanup(self, orchestrator):
        """Execute orchestrator cleanup with proper method detection."""
        if hasattr(orchestrator, "cleanup"):
            orchestrator.cleanup()
        elif hasattr(orchestrator, "close"):
            orchestrator.close()

    @property
    def quality_orchestrator(self):
        """Lazy load quality orchestrator."""
        if self._quality_orchestrator is None:
            from orchestrators.quality_orchestrator import QualityOrchestrator

            self._quality_orchestrator = QualityOrchestrator()

            # Register with resource registry
            self.resource_registry.register_resource(
                resource_id="quality_orchestrator",
                resource=self._quality_orchestrator,
                resource_type=ResourceType.SUB_ORCHESTRATOR,
                cleanup_func=self._cleanup_orchestrator,
                cleanup_args=(self._quality_orchestrator,),
                critical=True,
                retry_count=3,
                timeout=10.0,
            )

        return self._quality_orchestrator

    @property
    def cleanup_orchestrator(self):
        """Lazy load cleanup orchestrator."""
        if self._cleanup_orchestrator is None:
            from orchestrators.cleanup_orchestrator import CleanupOrchestrator

            self._cleanup_orchestrator = CleanupOrchestrator()

            # Register with resource registry
            self.resource_registry.register_resource(
                resource_id="cleanup_orchestrator",
                resource=self._cleanup_orchestrator,
                resource_type=ResourceType.SUB_ORCHESTRATOR,
                cleanup_func=self._cleanup_orchestrator,
                cleanup_args=(self._cleanup_orchestrator,),
                critical=True,
                retry_count=3,
                timeout=10.0,
            )

        return self._cleanup_orchestrator

    @property
    def remediation_orchestrator(self):
        """Lazy load remediation orchestrator."""
        if self._remediation_orchestrator is None:
            from orchestrators.remediation_orchestrator import RemediationOrchestrator

            self._remediation_orchestrator = RemediationOrchestrator()

            # Register with resource registry
            self.resource_registry.register_resource(
                resource_id="remediation_orchestrator",
                resource=self._remediation_orchestrator,
                resource_type=ResourceType.SUB_ORCHESTRATOR,
                cleanup_func=self._cleanup_orchestrator,
                cleanup_args=(self._remediation_orchestrator,),
                critical=True,
                retry_count=3,
                timeout=10.0,
            )

        return self._remediation_orchestrator

    @property
    def sdk_client(self):
        """Lazy load Claude SDK client."""
        if self._sdk_client is None:
            try:
                from claude_sdk.client.sdk_initializer import SDKInitializer

                initializer = SDKInitializer()
                self._sdk_client = initializer.initialize()
                self.logger.debug(
                    "MainOrchestrator: SDKInitializer imported and initialized successfully"
                )

                # Register SDK client with resource registry
                self.resource_registry.register_resource(
                    resource_id="sdk_client",
                    resource=self._sdk_client,
                    resource_type=ResourceType.SDK_CLIENT,
                    cleanup_func=self._cleanup_sdk_client,
                    cleanup_args=(self._sdk_client,),
                    critical=True,
                    retry_count=5,  # SDK cleanup is critical
                    timeout=30.0,
                )

            except ImportError as e:
                self.logger.error(f"Failed to import SDKInitializer: {e}")
                self.logger.debug(
                    "Looking for claude_sdk.client.sdk_initializer in current package structure"
                )
                self.logger.warning(
                    "SDK client will not be available - some features may be limited"
                )
                # For SDK import failures, we'll set to None and continue
                # This allows the orchestrator to work even if SDK is not available
                self._sdk_client = None
                return None
            except Exception as e:
                self.logger.error(f"Failed to initialize SDK client: {e}")
                self.logger.warning(
                    "SDK client initialization failed - some features may be limited"
                )
                self._sdk_client = None
                return None
        return self._sdk_client

    def handle_post_tool_use(
        self,
        tool_name: str,
        tool_result: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Handle PostToolUse hook event.

        Args:
            tool_name: Name of the tool that was used
            tool_result: Result from the tool
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Handling PostToolUse for tool: {tool_name}")

        results: Dict[str, Any] = {
            "hook": "PostToolUse",
            "tool": tool_name,
            "operations": [],
        }

        try:
            # Check if this is a file editing tool
            file_edit_tools = ["Edit", "MultiEdit", "Write", "edit_file"]
            if tool_name in file_edit_tools:
                # Extract file paths from tool result
                file_paths = self._extract_file_paths(tool_result, context)

                if file_paths:
                    # Run Unicode cleanup on edited files
                    cleanup_result = self.cleanup_orchestrator.cleanup_files(file_paths)
                    results["operations"].append(
                        {
                            "type": "unicode_cleanup",
                            "result": cleanup_result,
                        }
                    )

                    # Run quality check on edited files
                    quality_result = self.quality_orchestrator.check_files(file_paths)
                    results["operations"].append(
                        {
                            "type": "quality_check",
                            "result": quality_result,
                        }
                    )

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in PostToolUse handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_subagent_stop(
        self, agent_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle SubagentStop hook event.

        Args:
            agent_name: Name of the sub-agent that stopped
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Handling SubagentStop for agent: {agent_name or 'unknown'}")

        results: Dict[str, Any] = {
            "hook": "SubagentStop",
            "agent": agent_name,
            "operations": [],
        }

        try:
            # Run quality check on entire project
            quality_result = self.quality_orchestrator.check_project()
            results["operations"].append(
                {
                    "type": "project_quality_check",
                    "result": quality_result,
                }
            )

            # Check if remediation is needed
            if quality_result.get("issues_found", 0) > 0:
                # Trigger remediation if issues found
                remediation_result = self.remediation_orchestrator.remediate(
                    quality_report=quality_result
                )
                results["operations"].append(
                    {
                        "type": "remediation",
                        "result": remediation_result,
                    }
                )

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in SubagentStop handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def handle_stop(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Stop hook event (session end).

        Args:
            context: Additional context

        Returns:
            Dictionary with operation results
        """
        self.logger.info("Handling Stop hook (session end)")

        results: Dict[str, Any] = {
            "hook": "Stop",
            "operations": [],
        }

        try:
            # Run final quality check
            quality_result = self.quality_orchestrator.check_project(final_check=True)
            results["operations"].append(
                {
                    "type": "final_quality_check",
                    "result": quality_result,
                }
            )

            # Run final cleanup
            cleanup_result = self.cleanup_orchestrator.final_cleanup()
            results["operations"].append(
                {
                    "type": "final_cleanup",
                    "result": cleanup_result,
                }
            )

            # Generate session summary
            summary = self._generate_session_summary(results["operations"])
            results["summary"] = summary

            # Log session summary
            self.logger.section("Session Summary")
            self.logger.dict_log(summary)

            results["success"] = True

        except Exception as e:
            self.logger.exception(f"Error in Stop handler: {e}")
            results["success"] = False
            results["error"] = str(e)

        finally:
            # Cleanup resources
            self._cleanup_resources()

        return results

    def _extract_file_paths(
        self, tool_result: Optional[str], context: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """Extract file paths from tool result using multiple strategies.

        Args:
            tool_result: Tool execution result
            context: Additional context

        Returns:
            List of validated file paths that were edited
        """
        self.logger.debug(
            "FilePathExtraction: Starting multi-strategy file path extraction"
        )

        try:
            file_paths = self._execute_extraction_strategies(tool_result, context)
            validated_paths = self._validate_and_normalize_paths(file_paths)

            self._log_extraction_summary(file_paths, validated_paths)
            return list(validated_paths)

        except Exception as e:
            return self._handle_extraction_error(
                e, file_paths if "file_paths" in locals() else set()
            )

    def _execute_extraction_strategies(
        self, tool_result: Optional[str], context: Optional[Dict[str, Any]]
    ) -> Set[Path]:
        """Execute all file path extraction strategies.

        Args:
            tool_result: Tool execution result
            context: Additional context

        Returns:
            Set of extracted file paths
        """
        from typing import Set

        file_paths: Set[Path] = set()  # Use set to avoid duplicates

        # Strategy 1: Extract from context (highest priority)
        context_paths = self._extract_from_context(context)
        file_paths.update(context_paths)
        self._log_strategy_result("Context", len(context_paths))

        # Strategies 2-4: Extract from tool result if available
        if tool_result:
            self._extract_from_tool_result(tool_result, file_paths)

        return file_paths

    def _extract_from_tool_result(
        self, tool_result: str, file_paths: Set[Path]
    ) -> None:
        """Extract file paths from tool result using various text analysis strategies.

        Args:
            tool_result: Tool execution result text
            file_paths: Set to add found paths to
        """
        # Strategy 2: Enhanced regex patterns
        regex_paths = self._extract_with_enhanced_regex(tool_result)
        file_paths.update(regex_paths)
        self._log_strategy_result("Regex", len(regex_paths))

        # Strategy 3: Line-by-line analysis
        line_paths = self._extract_with_line_analysis(tool_result)
        file_paths.update(line_paths)
        self._log_strategy_result("Line analysis", len(line_paths))

        # Strategy 4: Extension-based detection
        extension_paths = self._extract_with_extension_detection(tool_result)
        file_paths.update(extension_paths)
        self._log_strategy_result("Extension detection", len(extension_paths))

    def _log_strategy_result(self, strategy_name: str, paths_found: int) -> None:
        """Log the result of an extraction strategy.

        Args:
            strategy_name: Name of the strategy
            paths_found: Number of paths found by the strategy
        """
        self.logger.debug(
            f"FilePathExtraction: {strategy_name} strategy found {paths_found} paths"
        )

    def _log_extraction_summary(
        self, file_paths: Set[Path], validated_paths: List[Path]
    ) -> None:
        """Log summary of the extraction process.

        Args:
            file_paths: All paths found during extraction
            validated_paths: Paths that passed validation
        """
        invalid_paths = len(file_paths) - len(validated_paths)

        self.logger.info(
            f"FilePathExtraction: Completed - Found {len(file_paths)} total paths, "
            f"validated {len(validated_paths)} paths"
        )

        if invalid_paths > 0:
            self.logger.warning(
                f"FilePathExtraction: {invalid_paths} paths failed validation"
            )

    def _handle_extraction_error(
        self, error: Exception, file_paths: Set[Path]
    ) -> List[Path]:
        """Handle errors during file path extraction.

        Args:
            error: The exception that occurred
            file_paths: Any paths found before the error

        Returns:
            List of paths (may be empty if no paths were found)
        """
        self.logger.error(
            f"FilePathExtraction: Critical error during path extraction: {error}"
        )
        self.logger.exception("FilePathExtraction: Full exception details")

        # Return any paths found before the error
        if file_paths:
            self.logger.warning(
                f"FilePathExtraction: Returning {len(file_paths)} paths found before error"
            )
            return list(file_paths)

        # Return empty list but log the failure
        self.logger.error(
            "FilePathExtraction: No paths could be extracted due to errors"
        )
        return []

    def _generate_session_summary(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of session operations.

        Args:
            operations: List of operations performed

        Returns:
            Summary dictionary
        """
        summary = {
            "total_operations": len(operations),
            "successful_operations": 0,
            "failed_operations": 0,
            "quality_issues_found": 0,
            "quality_issues_fixed": 0,
            "files_cleaned": 0,
            "files_checked": 0,
        }

        for op in operations:
            result = op.get("result", {})
            if result.get("success", False):
                summary["successful_operations"] += 1
            else:
                summary["failed_operations"] += 1

            # Aggregate specific metrics
            if op["type"] in [
                "quality_check",
                "project_quality_check",
                "final_quality_check",
            ]:
                summary["quality_issues_found"] += result.get("issues_found", 0)
                summary["files_checked"] += result.get("files_checked", 0)

            if op["type"] == "remediation":
                summary["quality_issues_fixed"] += result.get("issues_fixed", 0)

            if op["type"] in ["unicode_cleanup", "final_cleanup"]:
                summary["files_cleaned"] += result.get("files_cleaned", 0)

        return summary

    def _extract_from_context(self, context: Optional[Dict[str, Any]]) -> Set[Path]:
        """Extract file paths from context with comprehensive validation.

        Args:
            context: Context dictionary that may contain file paths

        Returns:
            Set of Path objects found in context
        """
        if not context:
            self.logger.debug("FilePathExtraction: No context provided")
            return set()

        paths: Set[Path] = set()

        try:
            self._extract_file_paths_key(context, paths)
            self._extract_alternative_context_keys(context, paths)
        except Exception as e:
            self.logger.error(
                f"FilePathExtraction: Critical error in context extraction: {e}"
            )

        return paths

    def _extract_file_paths_key(
        self, context: Dict[str, Any], paths: Set[Path]
    ) -> None:
        """Extract paths from the 'file_paths' key in context.

        Args:
            context: Context dictionary
            paths: Set to add found paths to
        """
        if "file_paths" not in context:
            return

        context_paths = context["file_paths"]
        self.logger.debug(
            f"FilePathExtraction: Found file_paths in context: {context_paths}"
        )

        if isinstance(context_paths, list):
            self._process_path_list(context_paths, paths)
        elif isinstance(context_paths, (str, Path)):
            self._process_single_path(context_paths, paths, "single context path")
        else:
            self.logger.warning(
                f"FilePathExtraction: Unexpected file_paths type in context: {type(context_paths)}"
            )

    def _process_path_list(self, path_list: List[Any], paths: Set[Path]) -> None:
        """Process a list of potential paths.

        Args:
            path_list: List of potential path objects
            paths: Set to add valid paths to
        """
        for path_item in path_list:
            try:
                if isinstance(path_item, (str, Path)):
                    path_obj = Path(path_item)
                    paths.add(path_obj)
                    self.logger.debug(
                        f"FilePathExtraction: Added context path: {path_obj}"
                    )
                else:
                    self.logger.warning(
                        f"FilePathExtraction: Invalid path type in context list: {type(path_item)}"
                    )
            except Exception as e:
                self.logger.error(
                    f"FilePathExtraction: Error processing context path '{path_item}': {e}"
                )

    def _process_single_path(
        self, path_value: Any, paths: Set[Path], description: str
    ) -> None:
        """Process a single path value.

        Args:
            path_value: Potential path value
            paths: Set to add valid path to
            description: Description for logging
        """
        try:
            path_obj = Path(path_value)
            paths.add(path_obj)
            self.logger.debug(f"FilePathExtraction: Added {description}: {path_obj}")
        except Exception as e:
            self.logger.error(
                f"FilePathExtraction: Error processing {description} '{path_value}': {e}"
            )

    def _extract_alternative_context_keys(
        self, context: Dict[str, Any], paths: Set[Path]
    ) -> None:
        """Extract paths from alternative context keys.

        Args:
            context: Context dictionary
            paths: Set to add found paths to
        """
        alternative_keys = ["file_path", "path", "file", "target_file", "source_file"]

        for key in alternative_keys:
            if key in context:
                try:
                    path_value = context[key]
                    if isinstance(path_value, (str, Path)):
                        self._process_single_path(
                            path_value, paths, f"path from '{key}'"
                        )
                except Exception as e:
                    self.logger.error(
                        f"FilePathExtraction: Error processing context key '{key}': {e}"
                    )

    def _extract_with_enhanced_regex(self, tool_result: str) -> Set[Path]:
        """Extract file paths using multiple enhanced regex patterns.

        Args:
            tool_result: Tool execution result text

        Returns:
            Set of Path objects found via regex
        """
        import re

        paths: Set[Path] = set()

        # Define common file extensions for easier maintenance
        ext_pattern = (
            r"(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml|html|css|scss|less|"
            r"xml|ini|cfg|conf|env|sh|bat|ps1)"
        )

        # Multiple regex patterns for different file path formats
        patterns = [
            # Original pattern with file prefixes
            rf"(?:File |path:|modified:|created:|editing:|writing:)\s*"
            rf"([^\s]+\.{ext_pattern})",
            # Absolute paths (Windows and Unix)
            rf"(?:^|\s)([A-Za-z]:[\\\\][^\s]+\.{ext_pattern})",
            rf"(?:^|\s)(/[^\s]+\.{ext_pattern})",
            # Relative paths
            rf"(?:^|\s)(\.[^\s]*[/\\\\][^\s]+\.{ext_pattern})",
            rf"(?:^|\s)([^\s]*[/\\\\][^\s]+\.{ext_pattern})",
            # Quoted paths
            rf'["\']([^"\']*.{ext_pattern})["\']',
            # Paths in brackets or parentheses
            rf"[\[\(]([^\]\)]+\.{ext_pattern})[\]\)]",
        ]

        for i, pattern in enumerate(patterns):
            try:
                matches = re.findall(pattern, tool_result, re.IGNORECASE | re.MULTILINE)
                pattern_paths = set()

                for match in matches:
                    try:
                        # Clean up the match
                        cleaned_match = match.strip().strip("\"'")
                        if cleaned_match:
                            path_obj = Path(cleaned_match)
                            pattern_paths.add(path_obj)

                    except Exception as e:
                        self.logger.debug(
                            f"FilePathExtraction: Error processing regex match '{match}' from pattern {i}: {e}"
                        )

                paths.update(pattern_paths)
                if pattern_paths:
                    self.logger.debug(
                        f"FilePathExtraction: Pattern {i} found {len(pattern_paths)} paths"
                    )

            except Exception as e:
                self.logger.error(
                    f"FilePathExtraction: Error in regex pattern {i}: {e}"
                )

        return paths

    def _extract_with_line_analysis(self, tool_result: str) -> Set[Path]:
        """Extract file paths by analyzing each line for potential paths.

        Args:
            tool_result: Tool execution result text

        Returns:
            Set of Path objects found via line analysis
        """
        paths: Set[Path] = set()

        try:
            lines = tool_result.split("\n")
            file_extensions = {
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml",
                ".html",
                ".css",
                ".scss",
                ".less",
                ".xml",
                ".ini",
                ".cfg",
                ".conf",
                ".env",
                ".sh",
                ".bat",
                ".ps1",
            }

            for line_num, line in enumerate(lines, 1):
                # Split line into tokens
                tokens = line.split()

                for token in tokens:
                    # Clean up token
                    cleaned_token = token.strip("\"';:,.()[]{}|\t")

                    # Check if token looks like a file path
                    if any(
                        cleaned_token.lower().endswith(ext) for ext in file_extensions
                    ):
                        try:
                            path_obj = Path(cleaned_token)
                            paths.add(path_obj)
                            self.logger.debug(
                                f"FilePathExtraction: Line analysis found path at line {line_num}: {path_obj}"
                            )
                        except Exception as e:
                            self.logger.debug(
                                f"FilePathExtraction: Invalid path token '{cleaned_token}' at line {line_num}: {e}"
                            )

        except Exception as e:
            self.logger.error(f"FilePathExtraction: Error in line analysis: {e}")

        return paths

    def _extract_with_extension_detection(self, tool_result: str) -> Set[Path]:
        """Extract file paths by detecting known file extensions.

        Args:
            tool_result: Tool execution result text

        Returns:
            Set of Path objects found via extension detection
        """
        import re

        paths: Set[Path] = set()

        try:
            # Pattern to find any text that ends with common file extensions
            ext_list = (
                r"py|js|ts|jsx|tsx|md|txt|json|yaml|yml|html|css|scss|less|"
                r"xml|ini|cfg|conf|env|sh|bat|ps1"
            )
            extension_pattern = rf"([^\s]+\.(?:{ext_list}))(?=\s|$|[^a-zA-Z0-9._-])"

            matches = re.findall(
                extension_pattern, tool_result, re.IGNORECASE | re.MULTILINE
            )

            for match in matches:
                try:
                    # Clean up the match
                    cleaned_match = match.strip().strip("\"';:,.()[]{}|\t")
                    if (
                        cleaned_match and len(cleaned_match) > 3
                    ):  # Minimum reasonable path length
                        path_obj = Path(cleaned_match)
                        paths.add(path_obj)
                        self.logger.debug(
                            f"FilePathExtraction: Extension detection found: {path_obj}"
                        )

                except Exception as e:
                    self.logger.debug(
                        f"FilePathExtraction: Error processing extension match '{match}': {e}"
                    )

        except Exception as e:
            self.logger.error(f"FilePathExtraction: Error in extension detection: {e}")

        return paths

    def _validate_and_normalize_paths(self, paths: Set[Path]) -> List[Path]:
        """Validate and normalize extracted file paths.

        Args:
            paths: Set of potentially valid Path objects

        Returns:
            List of validated and normalized Path objects
        """
        validated_paths: List[Path] = []

        for path_obj in paths:
            try:
                normalized_path = self._normalize_single_path(path_obj)
                if normalized_path and self._validate_path_existence(normalized_path):
                    validated_paths.append(normalized_path)
            except Exception as e:
                self.logger.error(
                    f"FilePathExtraction: Error validating path '{path_obj}': {e}"
                )

        self._log_validation_summary(validated_paths, paths)
        return validated_paths

    def _normalize_single_path(self, path_obj: Path) -> Optional[Path]:
        """Normalize a single path object.

        Args:
            path_obj: Path object to normalize

        Returns:
            Normalized Path object or None if normalization failed
        """
        import os

        normalized_path = Path(os.path.normpath(str(path_obj)))

        if normalized_path.is_absolute():
            return normalized_path

        return self._resolve_relative_path(normalized_path)

    def _resolve_relative_path(self, normalized_path: Path) -> Optional[Path]:
        """Resolve relative path to absolute path.

        Args:
            normalized_path: Relative path to resolve

        Returns:
            Resolved absolute path or original path if resolution failed
        """
        try:
            # Try to resolve relative to current working directory
            absolute_path = Path.cwd() / normalized_path
            if absolute_path.exists():
                return absolute_path.resolve()

            # Try relative to script directory
            script_dir = Path(__file__).parent
            script_relative = script_dir / normalized_path
            if script_relative.exists():
                return script_relative.resolve()

            return normalized_path

        except Exception as e:
            self.logger.debug(
                f"FilePathExtraction: Could not resolve relative path {normalized_path}: {e}"
            )
            return normalized_path

    def _validate_path_existence(self, normalized_path: Path) -> bool:
        """Validate path existence and file type.

        Args:
            normalized_path: Path to validate

        Returns:
            True if path is a valid file, False otherwise
        """
        if not normalized_path.exists():
            self.logger.debug(
                f"FilePathExtraction: Path does not exist: {normalized_path}"
            )
            return False

        if normalized_path.is_file():
            self.logger.debug(
                f"FilePathExtraction: Validated file path: {normalized_path}"
            )
            return True

        self.logger.warning(
            f"FilePathExtraction: Path exists but is not a file: {normalized_path}"
        )
        return False

    def _log_validation_summary(
        self, validated_paths: List[Path], original_paths: Set[Path]
    ):
        """Log summary of path validation results.

        Args:
            validated_paths: List of successfully validated paths
            original_paths: Original set of paths to validate
        """
        self.logger.info(
            f"FilePathExtraction: Validated {len(validated_paths)} out of {len(original_paths)} extracted paths"
        )

    def _cleanup_sdk_client(self, sdk_client):
        """Cleanup SDK client with proper error handling."""
        try:
            if hasattr(sdk_client, "shutdown"):
                sdk_client.shutdown()
            elif hasattr(sdk_client, "close"):
                sdk_client.close()
            self.logger.debug("SDK client cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during SDK client cleanup: {e}")
            raise  # Re-raise to trigger retry logic

    def _cleanup_orchestrator(self, orchestrator):
        """Cleanup sub-orchestrator with proper error handling."""
        try:
            if hasattr(orchestrator, "cleanup"):
                orchestrator.cleanup()
            elif hasattr(orchestrator, "close"):
                orchestrator.close()
            elif hasattr(orchestrator, "shutdown"):
                orchestrator.shutdown()
            self.logger.debug(
                f"Orchestrator {type(orchestrator).__name__} cleaned up successfully"
            )
        except Exception as e:
            self.logger.error(f"Error during orchestrator cleanup: {e}")
            raise  # Re-raise to trigger retry logic

    def _cleanup_resources(self):
        """Cleanup resources at session end with comprehensive error handling and verification."""
        cleanup_result = self.resource_registry.cleanup_all_resources()

        if not cleanup_result.success:
            self.logger.critical(
                f"Critical resource cleanup failures detected: {cleanup_result.failed_count} failed, "
                f"Emergency cleanup initiated. Details: {cleanup_result.summary}"
            )

            # Trigger emergency cleanup procedures
            emergency_result = self.resource_registry.emergency_cleanup()
            if not emergency_result.success:
                self.logger.critical(
                    f"Emergency cleanup also failed! System may have resource leaks. "
                    f"Details: {emergency_result.summary}"
                )
        else:
            self.logger.info(
                f"Resource cleanup completed successfully. "
                f"Cleaned: {cleanup_result.success_count} resources in {cleanup_result.duration:.3f}s"
            )
