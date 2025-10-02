"""
Redis-Based Distributed State Locking
Production-ready distributed locking coordination for Terraform state management
"""

from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from config import RedisConfig
from exceptions import (
    LockNotFoundError,
    RedisConnectionError,
    StateLockedError,
    StateLockError,
)
from models import LockInfo, LockStatus
import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)


class StateLocker:
    """Distributed state locking using Redis coordination"""

    def __init__(self, redis_client: redis.Redis, config: RedisConfig) -> None:
        """Initialize state locker

        Args:
            redis_client: Redis client instance
            config: Redis configuration
        """
        self.redis_client = redis_client
        self.config = config
        self._lock_prefix = "terraform:lock:"
        self._lock_info_prefix = "terraform:lock:info:"

    def _get_lock_key(self, backend_id: str, workspace: str) -> str:
        """Generate Redis lock key

        Args:
            backend_id: Backend identifier
            workspace: Workspace name

        Returns:
            Redis lock key
        """
        return f"{self._lock_prefix}{backend_id}:{workspace}"

    def _get_lock_info_key(self, backend_id: str, workspace: str) -> str:
        """Generate Redis lock info key

        Args:
            backend_id: Backend identifier
            workspace: Workspace name

        Returns:
            Redis lock info key
        """
        return f"{self._lock_info_prefix}{backend_id}:{workspace}"

    async def _check_existing_lock(
        self, backend_id: str, workspace: str, lock_key: str
    ) -> None:
        """Check if lock already exists and is valid"""
        existing_lock = await self.redis_client.get(lock_key)
        if existing_lock:
            # Verify lock hasn't expired
            existing_info = await self.get_lock_info(backend_id, workspace)
            if existing_info is not None:
                raise StateLockedError(
                    backend_id, workspace, lock_info=existing_info.dict()
                )

    def _prepare_lock_data(
        self,
        lock_id: str,
        backend_id: str,
        workspace: str,
        timeout: int,
        expires_at: datetime,
    ) -> Dict[str, Any]:
        """Prepare lock data dictionary"""
        return {
            "lock_id": lock_id,
            "backend_id": backend_id,
            "workspace": workspace,
            "acquired_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "timeout": timeout,
        }

    async def _execute_lock_acquisition(
        self,
        lock_key: str,
        lock_info_key: str,
        lock_id: str,
        lock_info: LockInfo,
        lock_data: Dict[str, Any],
        timeout: int,
    ) -> None:
        """Execute atomic lock acquisition"""
        async with self.redis_client.pipeline(transaction=True) as pipe:
            # Set lock with expiration
            await pipe.set(lock_key, lock_id, ex=timeout, nx=True)

            # Store lock info
            await pipe.set(
                lock_info_key, json.dumps({**lock_info.dict(), **lock_data}), ex=timeout
            )

            result = await pipe.execute()

            if not result[0]:  # SET NX failed
                raise StateLockedError(
                    lock_data["backend_id"],
                    lock_data["workspace"],
                    lock_info={
                        "error": "Lock acquisition failed - state already locked"
                    },
                )

    async def acquire_lock(
        self, backend_id: str, workspace: str, lock_info: LockInfo, timeout: int = 1800
    ) -> Dict[str, Any]:
        """Acquire distributed lock for state operations

        Args:
            backend_id: Backend identifier
            workspace: Workspace name
            lock_info: Lock information
            timeout: Lock timeout in seconds

        Returns:
            Lock acquisition result

        Raises:
            StateLockedError: If state is already locked
            StateLockError: If lock acquisition fails
            RedisConnectionError: If Redis operation fails
        """
        lock_key = self._get_lock_key(backend_id, workspace)
        lock_info_key = self._get_lock_info_key(backend_id, workspace)

        try:
            await self._check_existing_lock(backend_id, workspace, lock_key)

            # Generate unique lock ID
            lock_id = str(uuid4())
            lock_info.id = lock_id

            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=timeout)

            # Prepare lock data
            lock_data = self._prepare_lock_data(
                lock_id, backend_id, workspace, timeout, expires_at
            )

            # Execute atomic lock acquisition
            await self._execute_lock_acquisition(
                lock_key, lock_info_key, lock_id, lock_info, lock_data, timeout
            )

            logger.info(
                "Lock acquired successfully",
                backend_id=backend_id,
                workspace=workspace,
                lock_id=lock_id,
                expires_at=expires_at.isoformat(),
            )

            return {
                "lock_id": lock_id,
                "backend_id": backend_id,
                "workspace": workspace,
                "acquired_at": datetime.utcnow(),
                "expires_at": expires_at,
                "timeout": timeout,
                "success": True,
            }

        except StateLockedError:
            raise
        except redis.RedisError as e:
            logger.error("Redis error during lock acquisition", error=str(e))
            raise RedisConnectionError(f"Redis error during lock acquisition: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during lock acquisition", error=str(e))
            raise StateLockError(f"Unexpected lock error: {str(e)}")

    async def release_lock(
        self, backend_id: str, workspace: str, lock_id: str
    ) -> Dict[str, Any]:
        """Release distributed lock

        Args:
            backend_id: Backend identifier
            workspace: Workspace name
            lock_id: Lock ID to release

        Returns:
            Lock release result

        Raises:
            LockNotFoundError: If lock doesn't exist
            StateLockError: If lock release fails
            RedisConnectionError: If Redis operation fails
        """
        lock_key = self._get_lock_key(backend_id, workspace)
        lock_info_key = self._get_lock_info_key(backend_id, workspace)

        try:
            # Verify lock exists and belongs to this lock_id
            current_lock_id = await self.redis_client.get(lock_key)
            if not current_lock_id:
                raise LockNotFoundError(backend_id, workspace, lock_id)

            if current_lock_id != lock_id:
                raise StateLockError(
                    f"Lock ID mismatch: expected {lock_id}, found {current_lock_id}"
                )

            # Atomic lock release
            async with self.redis_client.pipeline(transaction=True) as pipe:
                await pipe.delete(lock_key)
                await pipe.delete(lock_info_key)
                await pipe.execute()

            logger.info(
                "Lock released successfully",
                backend_id=backend_id,
                workspace=workspace,
                lock_id=lock_id,
            )

            return {
                "lock_id": lock_id,
                "backend_id": backend_id,
                "workspace": workspace,
                "released_at": datetime.utcnow(),
                "success": True,
            }

        except (LockNotFoundError, StateLockError):
            raise
        except redis.RedisError as e:
            logger.error("Redis error during lock release", error=str(e))
            raise RedisConnectionError(f"Redis error during lock release: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during lock release", error=str(e))
            raise StateLockError(f"Unexpected unlock error: {str(e)}")

    async def get_lock_info(
        self, backend_id: str, workspace: str
    ) -> Optional[LockInfo]:
        """Get current lock information

        Args:
            backend_id: Backend identifier
            workspace: Workspace name

        Returns:
            Lock information or None if not locked

        Raises:
            RedisConnectionError: If Redis operation fails
        """
        lock_key = self._get_lock_key(backend_id, workspace)
        lock_info_key = self._get_lock_info_key(backend_id, workspace)

        try:
            # Check if lock exists
            lock_id = await self.redis_client.get(lock_key)
            if not lock_id:
                return None

            # Get lock info
            lock_info_data = await self.redis_client.get(lock_info_key)
            if not lock_info_data:
                # Lock exists but no info - treat as locked
                return LockInfo(
                    id=lock_id,
                    operation="unknown",
                    info="Lock exists but no details available",
                    who="unknown",
                    version="unknown",
                    path=f"{backend_id}/{workspace}",
                )

            # Parse lock info
            lock_data = json.loads(lock_info_data)

            # Check if lock has expired
            if "expires_at" in lock_data:
                expires_at = datetime.fromisoformat(lock_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    # Lock has expired - clean it up
                    await self.force_unlock(backend_id, workspace, "Lock expired")
                    return None

            return LockInfo(
                id=lock_data.get("id", lock_id),
                operation=lock_data.get("operation", "unknown"),
                info=lock_data.get("info", "No info available"),
                who=lock_data.get("who", "unknown"),
                version=lock_data.get("version", "unknown"),
                created=datetime.fromisoformat(
                    lock_data.get("created", datetime.utcnow().isoformat())
                ),
                path=lock_data.get("path", f"{backend_id}/{workspace}"),
            )

        except redis.RedisError as e:
            logger.error("Redis error getting lock info", error=str(e))
            raise RedisConnectionError(f"Redis error getting lock info: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error getting lock info", error=str(e))
            return None

    async def force_unlock(
        self, backend_id: str, workspace: str, force_reason: str
    ) -> Dict[str, Any]:
        """Force unlock with audit trail

        Args:
            backend_id: Backend identifier
            workspace: Workspace name
            force_reason: Reason for force unlock

        Returns:
            Force unlock result

        Raises:
            RedisConnectionError: If Redis operation fails
        """
        lock_key = self._get_lock_key(backend_id, workspace)
        lock_info_key = self._get_lock_info_key(backend_id, workspace)

        try:
            # Get current lock info for audit
            current_info = await self.get_lock_info(backend_id, workspace)

            # Force remove lock
            async with self.redis_client.pipeline(transaction=True) as pipe:
                await pipe.delete(lock_key)
                await pipe.delete(lock_info_key)
                await pipe.execute()

            # Log force unlock for audit
            logger.warning(
                "Force unlock performed",
                backend_id=backend_id,
                workspace=workspace,
                force_reason=force_reason,
                previous_lock=current_info.dict() if current_info else None,
            )

            return {
                "backend_id": backend_id,
                "workspace": workspace,
                "force_reason": force_reason,
                "forced_at": datetime.utcnow(),
                "previous_lock": current_info.dict() if current_info else None,
                "success": True,
            }

        except redis.RedisError as e:
            logger.error("Redis error during force unlock", error=str(e))
            raise RedisConnectionError(f"Redis error during force unlock: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during force unlock", error=str(e))
            raise StateLockError(f"Unexpected force unlock error: {str(e)}")

    async def get_lock_status(self, backend_id: str, workspace: str) -> LockStatus:
        """Get lock status for workspace

        Args:
            backend_id: Backend identifier
            workspace: Workspace name

        Returns:
            Current lock status

        Raises:
            RedisConnectionError: If Redis operation fails
        """
        try:
            lock_info = await self.get_lock_info(backend_id, workspace)

            if not lock_info:
                return LockStatus.UNLOCKED

            # Check if lock has expired
            lock_key = self._get_lock_key(backend_id, workspace)
            ttl = await self.redis_client.ttl(lock_key)

            if ttl <= 0:
                # Lock has expired
                await self.force_unlock(backend_id, workspace, "Lock expired")
                return LockStatus.EXPIRED

            return LockStatus.LOCKED

        except redis.RedisError as e:
            logger.error("Redis error getting lock status", error=str(e))
            raise RedisConnectionError(f"Redis error getting lock status: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error getting lock status", error=str(e))
            return LockStatus.UNLOCKED

    async def extend_lock(
        self, backend_id: str, workspace: str, lock_id: str, extend_seconds: int = 1800
    ) -> Dict[str, Any]:
        """Extend lock expiration time

        Args:
            backend_id: Backend identifier
            workspace: Workspace name
            lock_id: Lock ID to extend
            extend_seconds: Seconds to extend the lock

        Returns:
            Lock extension result

        Raises:
            LockNotFoundError: If lock doesn't exist
            StateLockError: If lock extension fails
            RedisConnectionError: If Redis operation fails
        """
        lock_key = self._get_lock_key(backend_id, workspace)
        lock_info_key = self._get_lock_info_key(backend_id, workspace)

        try:
            # Verify lock exists and belongs to this lock_id
            current_lock_id = await self.redis_client.get(lock_key)
            if not current_lock_id or current_lock_id != lock_id:
                raise LockNotFoundError(backend_id, workspace, lock_id)

            # Extend lock expiration
            new_expires_at = datetime.utcnow() + timedelta(seconds=extend_seconds)

            async with self.redis_client.pipeline(transaction=True) as pipe:
                await pipe.expire(lock_key, extend_seconds)
                await pipe.expire(lock_info_key, extend_seconds)
                await pipe.execute()

            logger.info(
                "Lock extended successfully",
                backend_id=backend_id,
                workspace=workspace,
                lock_id=lock_id,
                new_expires_at=new_expires_at.isoformat(),
            )

            return {
                "lock_id": lock_id,
                "backend_id": backend_id,
                "workspace": workspace,
                "extended_at": datetime.utcnow(),
                "new_expires_at": new_expires_at,
                "extend_seconds": extend_seconds,
                "success": True,
            }

        except LockNotFoundError:
            raise
        except redis.RedisError as e:
            logger.error("Redis error during lock extension", error=str(e))
            raise RedisConnectionError(f"Redis error during lock extension: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during lock extension", error=str(e))
            raise StateLockError(f"Unexpected lock extension error: {str(e)}")

    async def _get_all_lock_keys(self) -> List[str]:
        """Get all lock keys from Redis"""
        lock_pattern = f"{self._lock_prefix}*"
        lock_keys = []
        async for key in self.redis_client.scan_iter(match=lock_pattern):
            lock_keys.append(key)
        return lock_keys

    def _extract_backend_workspace_from_key(
        self, lock_key: str
    ) -> Optional[Tuple[str, str]]:
        """Extract backend_id and workspace from lock key"""
        try:
            key_parts = lock_key.replace(self._lock_prefix, "").split(":")
            if len(key_parts) >= 2:
                backend_id = key_parts[0]
                workspace = ":".join(key_parts[1:])
                return backend_id, workspace
        except Exception as e:
            logger.warning(
                "Skipping invalid lock entry", error=str(e), key=str(lock_key)
            )
        return None

    async def _create_lock_dict(
        self, backend_id: str, workspace: str
    ) -> Optional[Dict[str, Any]]:
        """Create lock dictionary for monitoring"""
        try:
            lock_info = await self.get_lock_info(backend_id, workspace)
            if lock_info:
                return {
                    "backend_id": backend_id,
                    "workspace": workspace,
                    "lock_info": lock_info.dict(),
                }
        except Exception as e:
            logger.warning(
                "Failed to get lock info",
                error=str(e),
                backend_id=backend_id,
                workspace=workspace,
            )
        return None

    async def list_all_locks(self) -> List[Dict[str, Any]]:
        """List all active locks (for monitoring/debugging)

        Returns:
            List of all active locks

        Raises:
            RedisConnectionError: If Redis operation fails
        """
        try:
            lock_keys = await self._get_all_lock_keys()
            locks = []

            for lock_key in lock_keys:
                backend_workspace = self._extract_backend_workspace_from_key(lock_key)
                if backend_workspace:
                    backend_id, workspace = backend_workspace
                    lock_dict = await self._create_lock_dict(backend_id, workspace)
                    if lock_dict:
                        locks.append(lock_dict)

            return locks

        except redis.RedisError as e:
            logger.error("Redis error listing locks", error=str(e))
            raise RedisConnectionError(f"Redis error listing locks: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error listing locks", error=str(e))
            return []
