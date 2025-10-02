"""
Plugin adapter for Terraform Executor service.

This adapter transforms the Terraform Executor into a plugin-based architecture
while maintaining backward compatibility with existing code.
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from celery import Celery

from services.plugin_system.core import (
    Plugin,
    PluginCapability,
    PluginMetadata,
    PluginState,
)
from services.plugin_system.events import PluginEvent

# Import existing terraform executor components
from services.terraform_agent.app import app as terraform_app
from services.terraform_agent.models import (
    JobInfo,
    JobStatus,
    TerraformApplyRequest,
    TerraformDestroyRequest,
    TerraformOperationType,
    TerraformPlanRequest,
    WorkspaceInfo,
    WorkspaceStatus,
)
from services.terraform_agent.tasks import (
    execute_terraform_apply,
    execute_terraform_destroy,
    execute_terraform_plan,
)

logger = logging.getLogger(__name__)


class TerraformExecutorPlugin(Plugin):
    """Terraform Executor as a plugin."""

    def __init__(self) -> None:
        """Initialize the Terraform Executor plugin."""
        metadata = PluginMetadata(
            id="terraform-executor",
            name="Terraform Executor Plugin",
            version="2.0.0",
            description="Terraform infrastructure automation engine as a plugin",
            author="N8N IAC Team",
            license="Apache-2.0",
            tags=["infrastructure", "terraform", "iac", "automation"],
            capabilities={
                PluginCapability.HOT_RELOAD,
                PluginCapability.CONFIGURATION,
                PluginCapability.EVENT_HANDLING,
                PluginCapability.STATE_PRESERVATION,
                PluginCapability.ASYNC_OPERATIONS,
                PluginCapability.MONITORING,
            },
            dependencies=["vault-integration", "git-operations"],
            provides=[
                "terraform-execution",
                "infrastructure-automation",
                "iac-agent",
            ],
            consumes=["vault-secrets", "git-repositories"],
        )
        super().__init__(metadata)

        # Plugin components
        self.app_instance = None
        self.redis_client: Optional[Any] = None
        self.celery_app: Optional[Any] = None

        # Plugin state
        self._active_jobs: Dict[str, JobInfo] = {}
        self._workspaces: Dict[str, WorkspaceInfo] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._metrics_data = {
            "plans_executed": 0,
            "applies_executed": 0,
            "destroys_executed": 0,
            "jobs_succeeded": 0,
            "jobs_failed": 0,
            "avg_execution_time": 0.0,
        }

    async def _on_initialize(self) -> None:
        """Initialize the plugin components."""
        logger.debug(f"[{self.metadata.id}] Starting plugin initialization")

        try:
            # Initialize Redis connection
            redis_url = self.config.get("redis_url", "redis://localhost:6379/0")
            logger.debug(
                f"[{self.metadata.id}] Initializing Redis connection to {redis_url}"
            )
            self.redis_client = await self._init_redis(redis_url)

            # Initialize Celery
            broker_url = self.config.get("broker_url", redis_url)
            backend_url = self.config.get("backend_url", redis_url)
            logger.debug(
                f"[{self.metadata.id}] Initializing Celery with broker: {broker_url}"
            )

            self.celery_app = Celery(
                "terraform_agent",
                broker=broker_url,
                backend=backend_url,
            )

            # Store app reference
            self.app_instance = terraform_app
            logger.debug(f"[{self.metadata.id}] Terraform app instance stored")

            logger.info(
                f"[{self.metadata.id}] Terraform Executor plugin initialized successfully"
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
            # Register event handlers
            logger.debug(f"[{self.metadata.id}] Registering event handlers")
            await self._register_event_handlers()

            # Start monitoring
            logger.debug(f"[{self.metadata.id}] Starting job monitoring task")
            asyncio.create_task(self._monitor_jobs())

            logger.info(
                f"[{self.metadata.id}] Terraform Executor plugin started successfully"
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
            # Cancel active jobs
            active_jobs = list(self._active_jobs.keys())
            if active_jobs:
                logger.debug(
                    f"[{self.metadata.id}] Cancelling {len(active_jobs)} active jobs"
                )
                for job_id in active_jobs:
                    await self._cancel_job(job_id)

            # Close Redis connection
            if self.redis_client:
                logger.debug(f"[{self.metadata.id}] Closing Redis connection")
                await self.redis_client.close()
                self.redis_client = None

            logger.info(
                f"[{self.metadata.id}] Terraform Executor plugin stopped successfully"
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
            # Clear state
            logger.debug(f"[{self.metadata.id}] Clearing plugin state")
            self._active_jobs.clear()
            self._workspaces.clear()
            self._execution_history.clear()

            # Clear app references
            self.app_instance = None
            self.celery_app = None

            logger.info(
                f"[{self.metadata.id}] Terraform Executor plugin destroyed successfully"
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
                "active_jobs": {
                    k: v.dict() if hasattr(v, "dict") else v
                    for k, v in self._active_jobs.items()
                },
                "workspaces": {
                    k: v.dict() if hasattr(v, "dict") else v
                    for k, v in self._workspaces.items()
                },
                "execution_history": self._execution_history[-100:],  # Keep last 100
                "metrics": self._metrics_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.debug(
                f"[{self.metadata.id}] Saved state with {len(state['active_jobs'])} active jobs, "
                f"{len(state['workspaces'])} workspaces, {len(state['execution_history'])} history entries"
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
            self._workspaces = state.get("workspaces", {})
            self._execution_history = state.get("execution_history", [])
            self._metrics_data = state.get("metrics", self._metrics_data)

            timestamp = state.get("timestamp", "unknown")
            logger.debug(
                f"[{self.metadata.id}] Restored state from {timestamp} with "
                f"{len(self._active_jobs)} active jobs, {len(self._workspaces)} workspaces, "
                f"{len(self._execution_history)} history entries"
            )

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error restoring custom state: {e}", exc_info=True
            )
            raise

    def _validate_config(self) -> bool:
        """Validate plugin configuration."""
        required = ["redis_url"]
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
            state: Dict[str, Any] = await super().save_state()
            logger.debug(f"[{self.metadata.id}] Plugin state saved successfully")
            return state

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

    async def execute_plan(
        self,
        request: TerraformPlanRequest,
        user: str = "plugin",
    ) -> str:
        """Execute a Terraform plan."""
        job_id = str(uuid4())
        logger.info(
            f"[{self.metadata.id}] Executing plan for workspace '{request.workspace}' (job: {job_id})"
        )

        try:
            # Submit to Celery
            logger.debug(
                f"[{self.metadata.id}] Submitting plan job to Celery: {job_id}"
            )
            execute_terraform_plan.delay(
                job_id=job_id,
                workspace=request.workspace,
                variables=request.variables,
                target=request.target,
                destroy=request.destroy,
            )

            # Track job
            job_info = JobInfo(
                id=job_id,
                operation=TerraformOperationType.PLAN,
                status=JobStatus.PENDING,
                workspace=request.workspace,
                created_at=datetime.utcnow(),
                created_by=user,
            )
            self._active_jobs[job_id] = job_info

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="terraform.plan.started",
                    plugin_id=self.metadata.id,
                    data={
                        "job_id": job_id,
                        "workspace": request.workspace,
                        "user": user,
                    },
                )
            )

            logger.info(
                f"[{self.metadata.id}] Plan job {job_id} submitted successfully"
            )
            return job_id

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to execute plan for workspace '{request.workspace}': {e}",
                exc_info=True,
            )
            raise

    async def execute_apply(
        self,
        request: TerraformApplyRequest,
        user: str = "plugin",
    ) -> str:
        """Execute a Terraform apply."""
        job_id = str(uuid4())
        logger.info(
            f"[{self.metadata.id}] Executing apply for workspace '{request.workspace}' (job: {job_id})"
        )

        try:
            # Submit to Celery
            logger.debug(
                f"[{self.metadata.id}] Submitting apply job to Celery: {job_id}"
            )
            execute_terraform_apply.delay(
                job_id=job_id,
                workspace=request.workspace,
                plan_id=request.plan_id,
                auto_approve=request.auto_approve,
                target=request.target,
            )

            # Track job
            job_info = JobInfo(
                id=job_id,
                operation=TerraformOperationType.APPLY,
                status=JobStatus.PENDING,
                workspace=request.workspace,
                created_at=datetime.utcnow(),
                created_by=user,
            )
            self._active_jobs[job_id] = job_info

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="terraform.apply.started",
                    plugin_id=self.metadata.id,
                    data={
                        "job_id": job_id,
                        "workspace": request.workspace,
                        "user": user,
                    },
                )
            )

            logger.info(
                f"[{self.metadata.id}] Apply job {job_id} submitted successfully"
            )
            return job_id

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to execute apply for workspace '{request.workspace}': {e}",
                exc_info=True,
            )
            raise

    async def execute_destroy(
        self,
        request: TerraformDestroyRequest,
        user: str = "plugin",
    ) -> str:
        """Execute a Terraform destroy."""
        job_id = str(uuid4())
        logger.info(
            f"[{self.metadata.id}] Executing destroy for workspace '{request.workspace}' (job: {job_id})"
        )

        try:
            # Submit to Celery
            logger.debug(
                f"[{self.metadata.id}] Submitting destroy job to Celery: {job_id}"
            )
            execute_terraform_destroy.delay(
                job_id=job_id,
                workspace=request.workspace,
                target=request.target,
                force=request.force,
            )

            # Track job
            job_info = JobInfo(
                id=job_id,
                operation=TerraformOperationType.DESTROY,
                status=JobStatus.PENDING,
                workspace=request.workspace,
                created_at=datetime.utcnow(),
                created_by=user,
            )
            self._active_jobs[job_id] = job_info

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="terraform.destroy.started",
                    plugin_id=self.metadata.id,
                    data={
                        "job_id": job_id,
                        "workspace": request.workspace,
                        "user": user,
                    },
                )
            )

            logger.info(
                f"[{self.metadata.id}] Destroy job {job_id} submitted successfully"
            )
            return job_id

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to execute destroy for workspace '{request.workspace}': {e}",
                exc_info=True,
            )
            raise

    async def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get the status of a job."""
        logger.debug(f"[{self.metadata.id}] Checking status for job {job_id}")

        if job_id in self._active_jobs:
            logger.debug(f"[{self.metadata.id}] Found job {job_id} in active jobs")
            return self._active_jobs[job_id]

        # Check history
        for job in self._execution_history:
            if job.get("id") == job_id:
                logger.debug(
                    f"[{self.metadata.id}] Found job {job_id} in execution history"
                )
                return JobInfo(**job)

        logger.debug(f"[{self.metadata.id}] Job {job_id} not found")
        return None

    async def list_workspaces(self) -> List[WorkspaceInfo]:
        """List all Terraform workspaces."""
        workspace_count = len(self._workspaces)
        logger.debug(f"[{self.metadata.id}] Listing {workspace_count} workspaces")
        return list(self._workspaces.values())

    async def create_workspace(
        self,
        name: str,
        description: str = "",
        user: str = "plugin",
    ) -> WorkspaceInfo:
        """Create a new Terraform workspace."""
        logger.info(
            f"[{self.metadata.id}] Creating workspace '{name}' for user '{user}'"
        )

        try:
            if name in self._workspaces:
                logger.warning(
                    f"[{self.metadata.id}] Workspace '{name}' already exists"
                )
                return self._workspaces[name]

            workspace = WorkspaceInfo(
                name=name,
                description=description,
                status=WorkspaceStatus.ACTIVE,
                created_at=datetime.utcnow(),
                created_by=user,
            )
            self._workspaces[name] = workspace

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="terraform.workspace.created",
                    plugin_id=self.metadata.id,
                    data={
                        "workspace": name,
                        "user": user,
                    },
                )
            )

            logger.info(f"[{self.metadata.id}] Successfully created workspace '{name}'")
            return workspace

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Failed to create workspace '{name}': {e}",
                exc_info=True,
            )
            raise

    async def _cancel_job(self, job_id: str) -> bool:
        """Internal method to cancel a job."""
        logger.debug(f"[{self.metadata.id}] Attempting to cancel job {job_id}")

        if job_id not in self._active_jobs:
            logger.warning(
                f"[{self.metadata.id}] Job {job_id} not found in active jobs"
            )
            return False

        try:
            # Update job status
            job = self._active_jobs[job_id]
            logger.debug(
                f"[{self.metadata.id}] Cancelling job {job_id} (operation: {job.operation.value})"
            )

            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()

            # Move to history
            self._execution_history.append(job.dict() if hasattr(job, "dict") else job)
            del self._active_jobs[job_id]

            # Emit event
            await self._emit_event(
                PluginEvent(
                    type="terraform.job.cancelled",
                    plugin_id=self.metadata.id,
                    data={"job_id": job_id},
                )
            )

            logger.info(f"[{self.metadata.id}] Successfully cancelled job {job_id}")
            return True

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
                await self._check_active_jobs()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(
                    f"[{self.metadata.id}] Error monitoring jobs: {e}", exc_info=True
                )
                await asyncio.sleep(10)

        logger.debug(f"[{self.metadata.id}] Job monitoring task ended")

    async def _check_active_jobs(self) -> None:
        """Check status of all active jobs."""
        active_jobs_count = len(self._active_jobs)
        if active_jobs_count > 0:
            logger.debug(
                f"[{self.metadata.id}] Monitoring {active_jobs_count} active jobs"
            )

        for job_id, job in list(self._active_jobs.items()):
            await self._process_job(job_id, job)

    async def _process_job(self, job_id: str, job: JobInfo) -> None:
        """Process a single job's status check."""
        if not self.celery_app:
            return

        result = self.celery_app.AsyncResult(job_id)
        if not result.ready():
            return

        logger.debug(f"[{self.metadata.id}] Job {job_id} completed, checking result")

        if result.successful():
            await self._handle_successful_job(job_id, job)
        else:
            await self._handle_failed_job(job_id, job, result.result)

        await self._finalize_job(job_id, job)

    async def _handle_successful_job(self, job_id: str, job: JobInfo) -> None:
        """Handle a successfully completed job."""
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        self._metrics_data["jobs_succeeded"] += 1
        logger.info(f"[{self.metadata.id}] Job {job_id} completed successfully")

    async def _handle_failed_job(self, job_id: str, job: JobInfo, error: Any) -> None:
        """Handle a failed job."""
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        self._metrics_data["jobs_failed"] += 1
        logger.warning(f"[{self.metadata.id}] Job {job_id} failed: {error}")

    async def _finalize_job(self, job_id: str, job: JobInfo) -> None:
        """Finalize job processing: update metrics, history, and emit events."""
        # Update operation-specific metrics
        operation_key = f"{job.operation.value}s_executed"
        if operation_key in self._metrics_data:
            self._metrics_data[operation_key] += 1

        # Move to history
        self._execution_history.append(job.dict() if hasattr(job, "dict") else job)
        del self._active_jobs[job_id]

        # Emit completion event
        event_type = f"terraform.job.{job.status.value}"
        await self._emit_event(
            PluginEvent(
                type=event_type,
                plugin_id=self.metadata.id,
                data={
                    "job_id": job_id,
                    "status": job.status.value,
                    "operation": job.operation.value,
                },
            )
        )

    async def _register_event_handlers(self) -> None:
        """Register handlers for plugin events."""

        # Handler for state lock requests
        async def handle_state_lock(event: PluginEvent) -> None:
            workspace = event.data.get("workspace")
            if workspace:
                # Implement state locking logic
                locked = await self._lock_workspace_state(workspace)
                await self._emit_event(
                    PluginEvent(
                        type="terraform.state.lock.response",
                        plugin_id=self.metadata.id,
                        data={"workspace": workspace, "locked": locked},
                        correlation_id=event.correlation_id,
                    )
                )

        # Register with event bus if available
        if hasattr(self, "event_bus"):
            await self.event_bus.subscribe(
                "terraform.state.lock.request", handle_state_lock
            )

    async def _lock_workspace_state(self, workspace: str) -> bool:
        """Lock workspace state."""
        # Implement actual state locking logic
        if workspace in self._workspaces:
            ws = self._workspaces[workspace]
            if ws.status == WorkspaceStatus.ACTIVE:
                ws.status = WorkspaceStatus.LOCKED
                return True
        return False

    async def _init_redis(self, redis_url: str) -> Optional[Any]:
        """Initialize Redis connection."""
        try:
            import redis.asyncio as redis

            return await redis.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Could not initialize Redis: {e}")
            return None

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

    def get_health(self) -> Dict[str, Any]:
        """Get plugin health status."""
        logger.debug(f"[{self.metadata.id}] Getting plugin health status")

        try:
            health: Dict[str, Any] = super().get_health()
            health.update(
                {
                    "active_jobs": len(self._active_jobs),
                    "workspaces": len(self._workspaces),
                    "redis_connected": self.redis_client is not None,
                    "celery_connected": self.celery_app is not None,
                }
            )

            logger.debug(
                f"[{self.metadata.id}] Health status: {health['status']}, "
                f"Active jobs: {health['active_jobs']}, Workspaces: {health['workspaces']}"
            )

            return health

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error getting health status: {e}", exc_info=True
            )
            return {"status": "unhealthy", "error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin metrics."""
        logger.debug(f"[{self.metadata.id}] Getting plugin metrics")

        try:
            metrics: Dict[str, Any] = super().get_metrics()
            metrics.update(self._metrics_data)
            metrics["active_jobs"] = len(self._active_jobs)
            metrics["total_workspaces"] = len(self._workspaces)
            metrics["history_size"] = len(self._execution_history)

            logger.debug(
                f"[{self.metadata.id}] Metrics - Jobs succeeded: {metrics.get('jobs_succeeded', 0)}, "
                f"Jobs failed: {metrics.get('jobs_failed', 0)}, Active jobs: {metrics['active_jobs']}"
            )

            return metrics

        except Exception as e:
            logger.error(
                f"[{self.metadata.id}] Error getting metrics: {e}", exc_info=True
            )
            return {"error": str(e)}


# Plugin registration helper
def register_plugin(registry: Any) -> Any:
    """Register the Terraform Executor plugin with a registry."""
    return registry.register(TerraformExecutorPlugin)
