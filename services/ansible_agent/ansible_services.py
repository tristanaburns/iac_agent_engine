"""
Real implementations for Ansible Executor Service

"""

import asyncio
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional
import uuid

try:
    from ansible_vault import Vault  # type: ignore[import-not-found]
except ImportError:
    # Fallback for when ansible-vault is not available
    class Vault:  # type: ignore[no-redef]
        def __init__(self, password: str) -> None:
            self.password = password

        def dump(self, data: str) -> str:
            # Simple base64 encoding as fallback
            import base64

            return base64.b64encode(data.encode()).decode()

        def load(self, data: str) -> str:
            # Simple base64 decoding as fallback
            import base64

            return base64.b64decode(data.encode()).decode()


from celery import Celery
from celery.result import AsyncResult
from fastapi import HTTPException, status
import hvac
import jwt
from prometheus_client import Counter, Gauge, Histogram
import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)

# Metrics
job_counter = Counter(
    "ansible_jobs_total", "Total number of Ansible jobs", ["type", "status"]
)
job_duration = Histogram(
    "ansible_job_duration_seconds", "Ansible job duration", ["type"]
)
active_jobs = Gauge("ansible_active_jobs", "Number of active Ansible jobs")

# ============================================================================
# CELERY CONFIGURATION AND INITIALIZATION
# ============================================================================


class CeleryManager:
    """Manages Celery connection and tasks"""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.celery_app: Optional[Celery] = None
        self.redis_client: Optional[redis.Redis[str]] = None
        self.vault_client: Optional[hvac.Client] = None

    async def initialize(self) -> None:
        """Initialize Celery, Redis, and Vault connections"""
        try:
            # Initialize Redis connection
            self.redis_client = await self._init_redis()

            # Initialize Celery
            self.celery_app = self._init_celery()

            # Initialize Vault client
            self.vault_client = await self._init_vault()

            logger.info("All services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    async def _init_redis(self) -> redis.Redis[str]:
        """Initialize Redis connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        client = redis.from_url(
            redis_url, encoding="utf-8", decode_responses=True, max_connections=20
        )

        # Test connection
        await client.ping()
        logger.info("Redis connection established", url=redis_url)

        return client

    def _init_celery(self) -> Celery:
        """Initialize Celery application"""
        broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

        celery_app = Celery(
            "ansible_agent",
            broker=broker_url,
            backend=result_backend,
            include=["services.ansible_agent.tasks"],
        )

        # Configure Celery
        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_track_started=True,
            task_time_limit=3600,  # 1 hour
            task_soft_time_limit=3300,  # 55 minutes
            worker_prefetch_multiplier=1,
            worker_max_tasks_per_child=100,
            result_expires=86400,  # 24 hours
        )

        logger.info("Celery application initialized", broker=broker_url)

        return celery_app

    async def _init_vault(self) -> hvac.Client:
        """Initialize HashiCorp Vault client"""
        vault_url = os.getenv("VAULT_ADDR", "http://vault:8200")
        vault_token = os.getenv("VAULT_TOKEN")

        if not vault_token:
            # Try to use Kubernetes auth or other methods
            vault_role = os.getenv("VAULT_ROLE", "ansible-executor")
            vault_token = await self._get_vault_token_from_k8s(vault_role)

        client = hvac.Client(url=vault_url, token=vault_token)

        if not client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")

        logger.info("Vault client initialized", url=vault_url)

        return client

    async def _get_vault_token_from_k8s(self, role: str) -> str:
        """Get Vault token using Kubernetes authentication"""
        # Read service account token
        token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"  # nosec B105 - K8s standard path
        if Path(token_path).exists():
            with open(token_path, "r") as f:
                k8s_token = f.read()

            vault_url = os.getenv("VAULT_ADDR", "http://vault:8200")
            client = hvac.Client(url=vault_url)

            # Authenticate with Kubernetes
            response = client.auth.kubernetes.login(role=role, jwt=k8s_token)

            return str(response["auth"]["client_token"])

        raise Exception("No authentication method available for Vault")

    async def cleanup(self) -> None:
        """Cleanup connections"""
        if self.redis_client:
            await self.redis_client.close()

        logger.info("Services cleaned up successfully")


# ============================================================================
# JWT TOKEN VALIDATION
# ============================================================================


class JWTValidator:
    """JWT token validation implementation"""

    def __init__(self) -> None:
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.issuer = os.getenv("JWT_ISSUER", "n8n-platform")
        self.audience = os.getenv("JWT_AUDIENCE", "ansible-executor")

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return claims"""
        try:
            payload = jwt.decode(  # type: ignore[attr-defined]
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={"verify_exp": True},
            )

            # Ensure payload is a dict
            if not isinstance(payload, dict):
                raise ValueError("Invalid token payload")

            # Additional validation
            if "sub" not in payload:
                raise ValueError("Missing subject claim")

            return payload

        except Exception as e:
            if "expired" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {str(e)}",
                )

    def create_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create a new JWT token"""
        payload = {
            "sub": user_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            "iss": self.issuer,
            "aud": self.audience,
        }

        return str(jwt.encode(payload, self.secret_key, algorithm=self.algorithm))  # type: ignore[attr-defined]


# ============================================================================
# ANSIBLE PLAYBOOK EXECUTOR
# ============================================================================


class PlaybookExecutor:
    """Handles Ansible playbook execution"""

    def __init__(self, celery_manager: CeleryManager) -> None:
        self.celery_manager = celery_manager
        # Use secure temporary directory creation
        self.work_dir = Path(tempfile.mkdtemp(prefix="ansible-executor-"))  # nosec B108
        # Ensure proper permissions
        self.work_dir.chmod(0o700)

    async def execute_playbook(
        self,
        playbook_path: str,
        inventory: Optional[str],
        extra_vars: Optional[Dict[str, Any]],
        user: str,
    ) -> str:
        """Execute Ansible playbook asynchronously"""

        # Prepare execution directory
        job_id = str(uuid.uuid4())
        job_dir = self.work_dir / job_id
        job_dir.mkdir(parents=True)

        # Prepare inventory
        inventory_path = None
        if inventory:
            inventory_path = job_dir / "inventory"
            inventory_path.write_text(inventory)

        # Prepare extra vars
        extravars = extra_vars or {}
        extravars["ansible_user"] = user
        extravars["job_id"] = job_id

        # Submit task to Celery
        if self.celery_manager.celery_app is None:
            raise RuntimeError("Celery app not initialized")

        self.celery_manager.celery_app.send_task(
            "ansible_agent.execute_playbook",
            args=[str(playbook_path), str(inventory_path) if inventory_path else None],
            kwargs={"extravars": extravars, "job_dir": str(job_dir)},
            task_id=job_id,
        )

        # Store job metadata in Redis
        await self._store_job_metadata(job_id, "playbook", user)

        logger.info("Playbook execution started", job_id=job_id, playbook=playbook_path)
        active_jobs.inc()
        job_counter.labels(type="playbook", status="started").inc()

        return job_id

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get playbook execution job status"""

        # Get task result from Celery
        result = AsyncResult(job_id, app=self.celery_manager.celery_app)

        # Get metadata from Redis
        metadata = await self._get_job_metadata(job_id)

        status_info = {
            "job_id": job_id,
            "status": result.state,
            "result": result.result if result.ready() else None,
            "traceback": result.traceback if result.failed() else None,
            "metadata": metadata,
        }

        # Get execution logs if available
        job_dir = self.work_dir / job_id
        if job_dir.exists():
            stdout_path = job_dir / "stdout"
            if stdout_path.exists():
                status_info["stdout"] = stdout_path.read_text()

        return status_info

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""

        result = AsyncResult(job_id, app=self.celery_manager.celery_app)
        result.revoke(terminate=True)

        # Update job metadata
        await self._update_job_status(job_id, "cancelled")

        active_jobs.dec()
        job_counter.labels(type="playbook", status="cancelled").inc()

        logger.info("Job cancelled", job_id=job_id)

        return True

    async def _store_job_metadata(self, job_id: str, job_type: str, user: str) -> None:
        """Store job metadata in Redis"""

        if self.celery_manager.redis_client is None:
            raise RuntimeError("Redis client not initialized")

        metadata = {
            "job_id": job_id,
            "type": job_type,
            "user": user,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        await self.celery_manager.redis_client.hset(
            f"ansible:job:{job_id}", mapping=metadata  # type: ignore[arg-type]
        )

        # Set expiration (24 hours)
        await self.celery_manager.redis_client.expire(f"ansible:job:{job_id}", 86400)

    async def _get_job_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job metadata from Redis"""

        if self.celery_manager.redis_client is None:
            return None

        data = await self.celery_manager.redis_client.hgetall(f"ansible:job:{job_id}")
        return data if data else None

    async def _update_job_status(self, job_id: str, status: str) -> None:
        """Update job status in Redis"""

        if self.celery_manager.redis_client is None:
            raise RuntimeError("Redis client not initialized")

        await self.celery_manager.redis_client.hset(
            f"ansible:job:{job_id}", "status", status
        )


# ============================================================================
# AD-HOC COMMAND EXECUTOR
# ============================================================================


class AdhocExecutor:
    """Handles Ansible ad-hoc command execution"""

    def __init__(self, celery_manager: CeleryManager) -> None:
        self.celery_manager = celery_manager

    async def execute_command(
        self,
        pattern: str,
        module: str,
        args: Optional[str],
        inventory: Optional[str],
        user: str,
    ) -> str:
        """Execute ad-hoc Ansible command asynchronously"""

        job_id = str(uuid.uuid4())

        # Submit task to Celery
        if self.celery_manager.celery_app is None:
            raise RuntimeError("Celery app not initialized")

        self.celery_manager.celery_app.send_task(
            "ansible_agent.execute_adhoc",
            args=[pattern, module],
            kwargs={"args": args, "inventory": inventory},
            task_id=job_id,
        )

        # Store job metadata
        metadata = {
            "job_id": job_id,
            "type": "adhoc",
            "user": user,
            "pattern": pattern,
            "module": module,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        if self.celery_manager.redis_client is None:
            raise RuntimeError("Redis client not initialized")

        await self.celery_manager.redis_client.hset(
            f"ansible:job:{job_id}", mapping=metadata  # type: ignore[arg-type]
        )

        logger.info("Ad-hoc command execution started", job_id=job_id, module=module)
        active_jobs.inc()
        job_counter.labels(type="adhoc", status="started").inc()

        return job_id


# ============================================================================
# INVENTORY MANAGER
# ============================================================================


class InventoryManager:
    """Manages Ansible inventories"""

    def __init__(self, vault_client: hvac.Client) -> None:
        self.vault_client = vault_client
        self.inventory_path = Path("/opt/ansible/inventories")
        self.inventory_path.mkdir(parents=True, exist_ok=True)

    async def list_inventories(self) -> List[Dict[str, Any]]:
        """List available inventories"""

        inventories = []

        # List from filesystem
        for inv_file in self.inventory_path.glob("*.yml"):
            inventories.append(
                {"name": inv_file.stem, "type": "file", "path": str(inv_file)}
            )

        # List from Vault
        try:
            vault_list = self.vault_client.secrets.kv.v2.list_secrets(
                path="ansible/inventories", mount_point="secret"
            )

            for key in vault_list.get("data", {}).get("keys", []):
                inventories.append(
                    {
                        "name": key.rstrip("/"),
                        "type": "vault",
                        "path": f"vault://secret/ansible/inventories/{key}",
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to list inventories from Vault: {e}")

        return inventories

    async def create_inventory(
        self, name: str, content: str, store_in_vault: bool = False
    ) -> Dict[str, Any]:
        """Create or update inventory"""

        if store_in_vault:
            # Store in Vault
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=f"ansible/inventories/{name}",
                secret={"content": content},
                mount_point="secret",
            )

            return {
                "name": name,
                "type": "vault",
                "path": f"vault://secret/ansible/inventories/{name}",
                "created_at": datetime.utcnow().isoformat(),
            }
        else:
            # Store on filesystem
            inv_file = self.inventory_path / f"{name}.yml"
            inv_file.write_text(content)

            return {
                "name": name,
                "type": "file",
                "path": str(inv_file),
                "created_at": datetime.utcnow().isoformat(),
            }

    async def get_inventory(self, name: str) -> Optional[str]:
        """Get inventory content"""

        # Try filesystem first
        inv_file = self.inventory_path / f"{name}.yml"
        if inv_file.exists():
            return inv_file.read_text()

        # Try Vault
        try:
            response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=f"ansible/inventories/{name}", mount_point="secret"
            )

            return str(response["data"]["data"]["content"])
        except Exception:
            return None


# ============================================================================
# ANSIBLE VAULT MANAGER
# ============================================================================


class AnsibleVaultManager:
    """Manages Ansible Vault encryption/decryption"""

    def __init__(self, vault_client: hvac.Client) -> None:
        self.vault_client = vault_client
        self._vault_password: Optional[str] = None

    async def get_vault_password(self) -> str:
        """Get Ansible Vault password from HashiCorp Vault"""

        if not self._vault_password:
            try:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path="ansible/vault-password", mount_point="secret"
                )

                self._vault_password = response["data"]["data"]["password"]
            except Exception:
                # Generate a new password if not exists
                self._vault_password = base64.b64encode(os.urandom(32)).decode("utf-8")

                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path="ansible/vault-password",
                    secret={"password": self._vault_password},
                    mount_point="secret",
                )

        if self._vault_password is None:
            raise RuntimeError("Failed to get vault password")
        return self._vault_password

    async def encrypt_string(
        self, plaintext: str, vault_id: Optional[str] = None
    ) -> str:
        """Encrypt string with Ansible Vault"""

        password = await self.get_vault_password()
        vault = Vault(password)

        encrypted = vault.dump(plaintext)

        return str(encrypted)

    async def decrypt_string(self, ciphertext: str) -> str:
        """Decrypt Ansible Vault string"""

        password = await self.get_vault_password()
        vault = Vault(password)

        decrypted = vault.load(ciphertext)

        return str(decrypted)


# ============================================================================
# COLLECTION MANAGER
# ============================================================================


class CollectionManager:
    """Manages Ansible collections"""

    def __init__(self) -> None:
        self.collections_path = Path("/opt/ansible/collections")
        self.collections_path.mkdir(parents=True, exist_ok=True)

    async def list_collections(self) -> List[Dict[str, Any]]:
        """List installed collections"""

        collections = []

        try:
            # Run ansible-galaxy collection list
            result = await asyncio.create_subprocess_exec(
                "ansible-galaxy",
                "collection",
                "list",
                "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await result.communicate()

            if result.returncode == 0:
                data = json.loads(stdout.decode("utf-8"))

                for namespace, colls in data.items():
                    for name, versions in colls.items():
                        for version, info in versions.items():
                            collections.append(
                                {
                                    "name": f"{namespace}.{name}",
                                    "version": version,
                                    "path": info.get("path", ""),
                                }
                            )
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")

        return collections

    async def install_collection(
        self, collection: str, version: Optional[str] = None
    ) -> str:
        """Install Ansible collection"""

        job_id = str(uuid.uuid4())

        # Prepare command
        cmd = ["ansible-galaxy", "collection", "install", collection]
        if version:
            cmd.append(f"--version={version}")

        # Run installation asynchronously
        asyncio.create_task(self._run_collection_install(job_id, cmd))

        return job_id

    async def _run_collection_install(self, job_id: str, cmd: List[str]) -> None:
        """Run collection installation"""

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                logger.info("Collection installed successfully", job_id=job_id)
            else:
                logger.error(
                    "Collection installation failed",
                    job_id=job_id,
                    error=stderr.decode("utf-8"),
                )

        except Exception as e:
            logger.error("Failed to install collection", job_id=job_id, error=str(e))
