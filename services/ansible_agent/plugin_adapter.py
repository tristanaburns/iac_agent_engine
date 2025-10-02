"""
Plugin adapter for Ansible Executor service.

This adapter transforms the Ansible Executor into a plugin-based architecture
while maintaining backward compatibility with existing code.
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from ..plugin_system.core import (  # type: ignore[import-not-found]
    Plugin,
    PluginCapability,
    PluginMetadata,
    PluginState,
)
from ..plugin_system.events import PluginEvent  # type: ignore[import-not-found]
from .ansible_services import (
    AdhocExecutor,
    AnsibleVaultManager,
    CeleryManager,
    CollectionManager,
    InventoryManager,
    JWTValidator,
    PlaybookExecutor,
)
from .config import AnsibleExecutorConfig

logger = logging.getLogger(__name__)


class AnsibleExecutorPlugin(Plugin):  # type: ignore[misc]
    """Ansible Executor as a plugin."""

    def __init__(self) -> None:
        """Initialize the Ansible Executor plugin."""
        metadata = PluginMetadata(
            id="ansible-executor",
            name="Ansible Executor Plugin",
            version="2.0.0",
            description="Ansible automation execution engine as a plugin",
            author="N8N IAC Team",
            license="Apache-2.0",
            tags=["automation", "ansible", "executor", "iac"],
            capabilities={
                PluginCapability.HOT_RELOAD,
                PluginCapability.CONFIGURATION,
                PluginCapability.EVENT_HANDLING,
                PluginCapability.STATE_PRESERVATION,
                PluginCapability.ASYNC_OPERATIONS,
                PluginCapability.MONITORING,
            },
            dependencies=["vault-integration", "git-operations"],
            provides=["ansible-execution", "playbook-runner", "adhoc-commands"],
            consumes=["vault-secrets", "git-repositories"],
        )
        super().__init__(metadata)

        # Plugin components
        self.config_manager: Optional[AnsibleExecutorConfig] = None
        self.celery_manager: Optional[CeleryManager] = None
        self.jwt_validator: Optional[JWTValidator] = None
        self.playbook_executor: Optional[PlaybookExecutor] = None
        self.adhoc_executor: Optional[AdhocExecutor] = None
        self.inventory_manager: Optional[InventoryManager] = None
        self.vault_manager: Optional[AnsibleVaultManager] = None
        self.collection_manager: Optional[CollectionManager] = None

        # Plugin state
        self._active_jobs: Dict[str, Any] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._metrics_data = {
            "jobs_executed": 0,
            "jobs_succeeded": 0,
            "jobs_failed": 0,
            "avg_execution_time": 0.0,
        }

    async def _on_initialize(self) -> None:
        """Initialize the plugin components."""
        logger.debug(f"[{self.metadata.id}] Starting plugin initialization")

        try:
            # Load configuration
            logger.debug(f"[{self.metadata.id}] Loading configuration")
            self.config_manager = AnsibleExecutorConfig()

            # Initialize Celery manager
            self.celery_manager = CeleryManager(config=self.config)

            # Initialize JWT validator
            self.jwt_validator = JWTValidator()

            # Initialize executors
            self.playbook_executor = PlaybookExecutor(
                celery_manager=self.celery_manager,
            )

            self.adhoc_executor = AdhocExecutor(
                celery_manager=self.celery_manager,
            )

            # Initialize managers
            if self.celery_manager.vault_client is None:
                raise RuntimeError("Vault client not initialized")

            self.inventory_manager = InventoryManager(
                vault_client=self.celery_manager.vault_client
            )
            self.vault_manager = AnsibleVaultManager(
                vault_client=self.celery_manager.vault_client
            )
            self.collection_manager = CollectionManager()

            logger.info(
                f"[{self.metadata.id}] Ansible Executor plugin initialized successfully"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to initialize plugin: {e}", exc_info=True
            )
            raise

    async def _on_start(self) -> None:
        """Start the plugin services."""
        logger.debug(f"[{self.metadata.id}] Starting plugin services")

        try:
            # Initialize Celery services
            if self.celery_manager:
                logger.debug(f"[{self.metadata.id}] Initializing Celery services")
                await self.celery_manager.initialize()

            # Register event handlers
            logger.debug(f"[{self.metadata.id}] Registering event handlers")
            await self._register_event_handlers()

            # Start monitoring
            logger.debug(f"[{self.metadata.id}] Starting job monitoring task")
            asyncio.create_task(self._monitor_jobs())

            logger.info(
                f"[{self.metadata.id}] Ansible Executor plugin started successfully"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to start plugin: {e}", exc_info=True
            )
            raise

    async def _on_stop(self) -> None:
        """Stop the plugin services."""
        logger.debug(f"[{self.metadata.id}] Stopping plugin services")

        try:
            # Cleanup Celery services
            if self.celery_manager:
                logger.debug(f"[{self.metadata.id}] Cleaning up Celery services")
                await self.celery_manager.cleanup()

            # Cancel active jobs
            active_jobs = list(self._active_jobs.keys())
            if active_jobs:
                logger.debug(
                    f"[{self.metadata.id}] Cancelling {len(active_jobs)} active jobs"
                )
                for job_id in active_jobs:
                    await self._cancel_job(job_id)

            logger.info(
                f"[{self.metadata.id}] Ansible Executor plugin stopped successfully"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error during plugin stop: {e}", exc_info=True
            )
            raise

    async def _on_destroy(self) -> None:
        """Clean up plugin resources."""
        logger.debug(f"[{self.metadata.id}] Destroying plugin resources")

        try:
            # Clean up Celery
            if self.celery_manager:
                logger.debug(f"[{self.metadata.id}] Cleaning up Celery manager")
                await self.celery_manager.cleanup()

            # Clear state
            logger.debug(f"[{self.metadata.id}] Clearing plugin state")
            self._active_jobs.clear()
            self._execution_history.clear()

            logger.info(
                f"[{self.metadata.id}] Ansible Executor plugin destroyed successfully"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error during plugin destruction: {e}",
                exc_info=True,
            )
            raise

    async def _save_custom_state(self) -> Dict[str, Any]:
        """Save plugin-specific state."""
        logger.debug(f"[{self.metadata.id}] Saving custom plugin state")

        try:
            state = {
                "active_jobs": self._active_jobs,
                "execution_history": self._execution_history[-100:],  # Keep last 100
                "metrics": self._metrics_data,
                "timestamp": self._get_safe_timestamp(),
            }

            logger.debug(
                f"[{self.metadata.id}] Saved state with {len(state['active_jobs'])} active jobs, "
                f"{len(state['execution_history'])} history entries"
            )

            return state

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error saving custom state: {e}", exc_info=True
            )
            raise

    async def _restore_custom_state(self, state: Dict[str, Any]) -> None:
        """Restore plugin-specific state."""
        logger.debug(f"[{self.metadata.id}] Restoring custom plugin state")

        try:
            self._active_jobs = state.get("active_jobs", {})
            self._execution_history = state.get("execution_history", [])
            self._metrics_data = state.get("metrics", self._metrics_data)

            timestamp = state.get("timestamp", "unknown")
            logger.debug(
                f"[{self.metadata.id}] Restored state from {timestamp} with "
                f"{len(self._active_jobs)} active jobs, {len(self._execution_history)} history entries"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error restoring custom state: {e}", exc_info=True
            )
            raise

    def _get_safe_timestamp(self) -> str:
        """Get current timestamp safely without globals() access"""
        try:
            return datetime.utcnow().isoformat()
        except Exception:
            return "unknown"

    def _validate_config(self) -> bool:
        """Validate plugin configuration."""
        required = ["broker_url", "backend_url", "jwt_secret"]
        for key in required:
            if key not in self.config:
                logger.error(
                    f"[{self.metadata.id}] Missing required configuration: {key}"
                )
                return False
        logger.debug(f"[{self.metadata.id}] Configuration validation passed")
        return True

    # PUBLIC LIFECYCLE METHODS (override abstract methods from Plugin base class)

    async def start(self) -> None:
        """Start the plugin (public method overriding abstract method)."""
        logger.debug(f"[{self.metadata.id}] Public start() called")

        try:
            # Call parent's start method to handle state transitions
            await super().start()
            logger.debug(f"[{self.metadata.id}] Plugin start completed successfully")

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Plugin start failed: {e}", exc_info=True
            )
            raise

    async def stop(self) -> None:
        """Stop the plugin (public method overriding abstract method)."""
        logger.debug(f"[{self.metadata.id}] Public stop() called")

        try:
            # Call parent's stop method to handle state transitions
            await super().stop()
            logger.debug(f"[{self.metadata.id}] Plugin stop completed successfully")

        except Exception as e:
            logger.error(f"[{self.metadata.id}] Plugin stop failed: {e}", exc_info=True)
            raise

    async def destroy(self) -> None:
        """Destroy the plugin (public method overriding abstract method)."""
        logger.debug(f"[{self.metadata.id}] Public destroy() called")

        try:
            # Call parent's destroy method to handle state transitions
            await super().destroy()
            logger.debug(f"[{self.metadata.id}] Plugin destroy completed successfully")

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Plugin destroy failed: {e}", exc_info=True
            )
            raise

    async def reload(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Hot-reload the plugin (public method overriding abstract method)."""
        logger.info(f"[{self.metadata.id}] Public reload() called with new config")

        try:
            # Call parent's reload method to handle state transitions and config updates
            await super().reload(config)
            logger.info(f"[{self.metadata.id}] Plugin reload completed successfully")

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Plugin reload failed: {e}", exc_info=True
            )
            raise

    async def save_state(self) -> Dict[str, Any]:
        """Save plugin state (public method overriding abstract method)."""
        logger.debug(f"[{self.metadata.id}] Public save_state() called")

        try:
            # Call parent's save_state method which includes custom state
            state = await super().save_state()
            logger.debug(f"[{self.metadata.id}] Plugin state saved successfully")
            return dict(state)

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Plugin save_state failed: {e}", exc_info=True
            )
            raise

    async def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore plugin state (public method overriding abstract method)."""
        logger.debug(f"[{self.metadata.id}] Public restore_state() called")

        try:
            # Call parent's restore_state method which includes custom state
            await super().restore_state(state)
            logger.debug(f"[{self.metadata.id}] Plugin state restored successfully")

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Plugin restore_state failed: {e}", exc_info=True
            )
            raise

    # Plugin API Methods

    async def execute_playbook(
        self,
        playbook_path: str,
        inventory_path: Optional[str] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
        user: str = "plugin",
    ) -> str:
        """Execute an Ansible playbook."""
        logger.info(
            f"[{self.metadata.id}] Executing playbook '{playbook_path}' for user '{user}'"
        )

        try:
            if not self.playbook_executor:
                logger.error(f"[{self.metadata.id}] Playbook executor not initialized")
                raise RuntimeError("Playbook executor not initialized")

            logger.debug(f"[{self.metadata.id}] Submitting playbook job to executor")
            job_id = await self.playbook_executor.execute_playbook(
                playbook_path=playbook_path,
                inventory=inventory_path,
                extra_vars=extra_vars,
                user=user,
            )

            # Track job
            logger.debug(f"[{self.metadata.id}] Tracking playbook job {job_id}")
            self._active_jobs[job_id] = {
                "type": "playbook",
                "path": playbook_path,
                "user": user,
                "started": asyncio.get_event_loop().time(),
            }

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="ansible.playbook.started",
                    plugin_id=self.metadata.id,
                    data={
                        "job_id": job_id,
                        "playbook": playbook_path,
                        "user": user,
                    },
                )
            )

            logger.info(
                f"[{self.metadata.id}] Playbook job {job_id} submitted successfully"
            )
            return str(job_id)

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to execute playbook '{playbook_path}': {e}",
                exc_info=True,
            )
            raise

    async def execute_adhoc(
        self,
        pattern: str,
        module: str,
        args: Optional[str] = None,
        inventory: Optional[str] = None,
    ) -> str:
        """Execute an ad-hoc Ansible command."""
        logger.info(
            f"[{self.metadata.id}] Executing ad-hoc command: module '{module}' on pattern '{pattern}'"
        )

        try:
            if not self.adhoc_executor:
                logger.error(f"[{self.metadata.id}] Ad-hoc executor not initialized")
                raise RuntimeError("Ad-hoc executor not initialized")

            logger.debug(f"[{self.metadata.id}] Submitting ad-hoc job to executor")
            job_id = await self.adhoc_executor.execute_command(
                pattern=pattern,
                module=module,
                args=args,
                inventory=inventory,
                user="plugin",
            )

            # Track job
            logger.debug(f"[{self.metadata.id}] Tracking ad-hoc job {job_id}")
            self._active_jobs[job_id] = {
                "type": "adhoc",
                "module": module,
                "pattern": pattern,
                "started": asyncio.get_event_loop().time(),
            }

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="ansible.adhoc.started",
                    plugin_id=self.metadata.id,
                    data={
                        "job_id": job_id,
                        "module": module,
                        "pattern": pattern,
                    },
                )
            )

            logger.info(
                f"[{self.metadata.id}] Ad-hoc job {job_id} submitted successfully"
            )
            return str(job_id)

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to execute ad-hoc command '{module}' on pattern '{pattern}': {e}",
                exc_info=True,
            )
            raise

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a job."""
        logger.debug(f"[{self.metadata.id}] Checking status for job {job_id}")

        if job_id not in self._active_jobs:
            # Check history
            for job in self._execution_history:
                if job["job_id"] == job_id:
                    logger.debug(
                        f"[{self.metadata.id}] Found job {job_id} in execution history"
                    )
                    return job
            logger.debug(f"[{self.metadata.id}] Job {job_id} not found")
            return {"status": "not_found"}

        logger.debug(f"[{self.metadata.id}] Found job {job_id} in active jobs")
        job_info = self._active_jobs[job_id]

        if job_info["type"] == "playbook" and self.playbook_executor:
            status = await self.playbook_executor.get_job_status(job_id)
        elif job_info["type"] == "adhoc" and self.adhoc_executor:
            # AdhocExecutor doesn't have get_job_status, use basic status
            status = {"status": "running", "job_id": job_id}
        else:
            status = {"status": "unknown"}

        return status

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        logger.info(f"[{self.metadata.id}] Cancelling job {job_id}")
        return await self._cancel_job(job_id)

    async def _cancel_job(self, job_id: str) -> bool:
        """Internal method to cancel a job."""
        logger.debug(f"[{self.metadata.id}] Attempting to cancel job {job_id}")

        if job_id not in self._active_jobs:
            logger.warning(
                f"[{self.metadata.id}] Job {job_id} not found in active jobs"
            )
            return False

        job_info = self._active_jobs[job_id]
        logger.debug(
            f"[{self.metadata.id}] Cancelling job {job_id} (type: {job_info.get('type', 'unknown')})"
        )

        try:
            if job_info["type"] == "playbook" and self.playbook_executor:
                result = await self.playbook_executor.cancel_job(job_id)
            elif job_info["type"] == "adhoc" and self.adhoc_executor:
                # AdhocExecutor doesn't have cancel_job, mark as cancelled
                result = True
            else:
                result = False

            if result:
                # Move to history
                job_info["status"] = "cancelled"
                job_info["job_id"] = job_id
                self._execution_history.append(job_info)
                del self._active_jobs[job_id]

                # Emit event
                await self._emit_event(
                    PluginEvent(
                        type="ansible.job.cancelled",
                        plugin_id=self.metadata.id,
                        data={"job_id": job_id},
                    )
                )

                logger.info(f"[{self.metadata.id}] Successfully cancelled job {job_id}")

            return result

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to cancel job {job_id}: {e}",
                exc_info=True,
            )
            return False

    async def _monitor_jobs(self) -> None:
        """Monitor active jobs and update status."""
        logger.debug(f"[{self.metadata.id}] Job monitoring task started")

        while self.state == PluginState.RUNNING:
            try:
                active_jobs_count = len(self._active_jobs)
                if active_jobs_count > 0:
                    logger.debug(
                        f"[{self.metadata.id}] Monitoring {active_jobs_count} active jobs"
                    )

                for job_id in list(self._active_jobs.keys()):
                    status = await self.get_job_status(job_id)

                    if status.get("status") in ["completed", "failed"]:
                        job_info = self._active_jobs[job_id]
                        job_info["status"] = status["status"]
                        job_info["job_id"] = job_id

                        logger.debug(
                            f"[{self.metadata.id}] Job {job_id} {status['status']}, updating metrics"
                        )

                        # Update metrics
                        self._metrics_data["jobs_executed"] += 1
                        if status["status"] == "completed":
                            self._metrics_data["jobs_succeeded"] += 1
                            logger.info(
                                f"[{self.metadata.id}] Job {job_id} completed successfully"
                            )
                        else:
                            self._metrics_data["jobs_failed"] += 1
                            logger.warning(f"[{self.metadata.id}] Job {job_id} failed")

                        # Move to history
                        self._execution_history.append(job_info)
                        del self._active_jobs[job_id]

                        # Emit completion event
                        event_type = f"ansible.job.{status['status']}"
                        await self._emit_event(
                            PluginEvent(
                                type=event_type,
                                plugin_id=self.metadata.id,
                                data={
                                    "job_id": job_id,
                                    "status": status,
                                },
                            )
                        )

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(
                    f"[{self.metadata.id}] Error monitoring jobs: {e}", exc_info=True
                )
                await asyncio.sleep(10)

        logger.debug(f"[{self.metadata.id}] Job monitoring task ended")

    async def _register_event_handlers(self) -> None:
        """Register handlers for plugin events."""

        # Handler for vault secret requests
        async def handle_vault_request(event: PluginEvent) -> None:
            if event.data.get("type") == "ansible_vault":
                secret = await self._get_vault_secret(event.data.get("key"))
                await self._emit_event(
                    PluginEvent(
                        type="vault.secret.response",
                        plugin_id=self.metadata.id,
                        data={"secret": secret},
                        correlation_id=event.correlation_id,
                    )
                )

        # Register with event bus if available
        if hasattr(self, "event_bus"):
            await self.event_bus.subscribe("vault.secret.request", handle_vault_request)

    async def _emit_event(self, event: PluginEvent) -> None:
        """Emit an event to the event bus."""
        logger.debug(f"[{self.metadata.id}] Emitting event: {event.type}")

        try:
            if hasattr(self, "event_bus"):
                await self.event_bus.emit(event)
                logger.debug(
                    f"[{self.metadata.id}] Event {event.type} emitted successfully"
                )
            else:
                logger.debug(
                    f"[{self.metadata.id}] Event bus not available, event {event.type} not emitted"
                )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to emit event {event.type}: {e}",
                exc_info=True,
            )

    async def _get_vault_secret(self, key: str) -> Optional[str]:
        """Get a secret from vault."""
        logger.debug(f"[{self.metadata.id}] Requesting vault secret for key: {key}")

        try:
            if self.vault_manager:
                # AnsibleVaultManager doesn't have get_secret, use vault password method
                secret = await self.vault_manager.get_vault_password()
                logger.debug(
                    f"[{self.metadata.id}] Successfully retrieved vault secret for key: {key}"
                )
                return str(secret) if secret else None
            else:
                logger.warning(f"[{self.metadata.id}] Vault manager not available")
                return None

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to get vault secret for key '{key}': {e}",
                exc_info=True,
            )
            return None

    def get_health(self) -> Dict[str, Any]:
        """Get plugin health status."""
        logger.debug(f"[{self.metadata.id}] Getting plugin health status")

        try:
            health = super().get_health()
            health.update(
                {
                    "active_jobs": len(self._active_jobs),
                    "celery_status": (
                        "connected" if self.celery_manager else "disconnected"
                    ),
                    "executors_ready": bool(
                        self.playbook_executor and self.adhoc_executor
                    ),
                }
            )

            logger.debug(
                f"[{self.metadata.id}] Health status: {health['status']}, "
                f"Active jobs: {health['active_jobs']}, Executors ready: {health['executors_ready']}"
            )

            return dict(health)

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error getting health status: {e}", exc_info=True
            )
            return {"status": "unhealthy", "error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin metrics."""
        logger.debug(f"[{self.metadata.id}] Getting plugin metrics")

        try:
            metrics = super().get_metrics()
            metrics.update(self._metrics_data)
            metrics["active_jobs"] = len(self._active_jobs)
            metrics["history_size"] = len(self._execution_history)

            logger.debug(
                f"[{self.metadata.id}] Metrics - Jobs succeeded: {metrics.get('jobs_succeeded', 0)}, "
                f"Jobs failed: {metrics.get('jobs_failed', 0)}, Active jobs: {metrics['active_jobs']}"
            )

            return dict(metrics)

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error getting metrics: {e}", exc_info=True
            )
            return {"error": str(e)}


# Plugin registration helper
def register_plugin(registry: Any) -> Any:
    """Register the Ansible Executor plugin with a registry."""
    return registry.register(AnsibleExecutorPlugin)
