"""
Enhanced Terraform Executor Service
Production-ready REST API for comprehensive Terraform automation with async job execution
"""

from contextlib import asynccontextmanager
from datetime import datetime
import json
import logging
import os
import subprocess  # nosec B404
import time
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Optional
from uuid import UUID, uuid4

from celery import Celery
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import redis.asyncio as redis
from redis.asyncio import Redis
import structlog
import uvicorn

from services.terraform_agent.models import (
    ErrorResponse,
    HealthResponse,
    JobInfo,
    JobListResponse,
    JobResponse,
    JobStatus,
    JobStatusResponse,
    StateInfo,
    StateLockRequest,
    StateLockResponse,
    StateResponse,
    TerraformApplyRequest,
    TerraformDestroyRequest,
    TerraformImportRequest,
    TerraformOperationType,
    TerraformPlanRequest,
    TerraformRefreshRequest,
    TerraformValidateRequest,
    WorkspaceCreateRequest,
    WorkspaceInfo,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceStatus,
    WorkspaceUpdateRequest,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "terraform_agent_requests_total", "Total requests", ["method", "endpoint"]
)
REQUEST_DURATION = Histogram(
    "terraform_agent_request_duration_seconds", "Request duration"
)
ACTIVE_JOBS = Gauge("terraform_agent_active_jobs", "Number of active jobs")
WORKSPACE_COUNT = Gauge(
    "terraform_agent_workspaces_total", "Total number of workspaces"
)
OPERATION_COUNT = Counter(
    "terraform_agent_operations_total", "Total operations", ["operation", "status"]
)

# Global state
redis_client: Optional[Redis[str]] = None
celery_app: Optional[Celery] = None
service_start_time = time.time()

# In-memory storage (should be replaced with persistent storage in production)
workspaces: Dict[str, WorkspaceInfo] = {}
jobs: Dict[UUID, JobInfo] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management"""
    global redis_client, celery_app

    logger.info("Starting Enhanced Terraform Executor Service...")

    try:
        # Initialize Redis connection with authentication
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_host = os.getenv("REDIS_HOST", "redis")

        # Handle Redis port with fallback for service env vars
        redis_port_str = os.getenv("REDIS_PORT", "6379")
        try:
            # Extract just the port number if it's a full URL
            if ":" in redis_port_str and "tcp://" in redis_port_str:
                redis_port = int(redis_port_str.split(":")[-1])
            else:
                redis_port = int(redis_port_str)
        except ValueError:
            logger.warning(
                f"Invalid REDIS_PORT value: {redis_port_str}, using default 6379"
            )
            redis_port = 6379

        redis_db = int(os.getenv("REDIS_DB", "0"))

        if redis_password:
            redis_url = (
                f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
            )
        else:
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info(
            "Connected to Redis",
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db,
        )

        # Initialize Celery
        broker_url = os.getenv("CELERY_BROKER_URL", redis_url)
        celery_app = Celery(
            "terraform_agent",
            broker=broker_url,
            backend=broker_url,
            include=["terraform_agent.tasks"],
        )

        # Configure Celery
        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_routes={
                "terraform_agent.tasks.*": {"queue": "terraform"},
            },
            worker_concurrency=int(os.getenv("CELERY_WORKER_CONCURRENCY", "4")),
            task_soft_time_limit=int(
                os.getenv("CELERY_SOFT_TIME_LIMIT", "1800")
            ),  # 30 minutes
            task_time_limit=int(os.getenv("CELERY_TIME_LIMIT", "3600")),  # 60 minutes
        )

        logger.info("Celery configured", broker=broker_url)

        # Verify Terraform installation
        terraform_version = get_terraform_version()
        logger.info("Terraform version detected", version=terraform_version)

        yield

    except Exception as e:
        logger.error("Failed to initialize service", error=str(e))
        raise
    finally:
        # Cleanup
        if redis_client is not None:
            await redis_client.close()
        logger.info("Enhanced Terraform Executor Service stopped")


app = FastAPI(
    title="Enhanced Terraform Executor Service",
    description="Production-ready REST API for comprehensive Terraform automation with async job execution",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)  # Configure appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request metrics
@app.middleware("http")
async def metrics_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Any]]
) -> Any:
    """Middleware to collect request metrics"""
    time.time()

    with REQUEST_DURATION.time():
        response = await call_next(request)

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()

    return response


# Dependency functions
async def get_redis() -> Redis[str]:
    """Get Redis client"""
    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis connection not available",
        )
    return redis_client


async def get_celery() -> Celery:
    """Get Celery app"""
    if not celery_app:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Celery not available",
        )
    return celery_app


def get_terraform_version() -> str:
    """Get Terraform version with proper error handling."""
    try:
        # Security: Using shell=False and explicit command list for safety
        result = subprocess.run(  # nosec B603 B607
            ["terraform", "version", "-json"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
        if result.returncode == 0:
            version_data = json.loads(result.stdout)
            version = version_data.get("terraform_version")
            return str(version) if version else "unknown"
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning("Failed to get Terraform version", error=str(e))
    except Exception as e:
        logger.error("Unexpected error getting Terraform version", error=str(e))
    return "unknown"


# API Endpoints


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Enhanced health check endpoint"""
    uptime = time.time() - service_start_time
    active_jobs_count = len([j for j in jobs.values() if j.status == JobStatus.RUNNING])

    return HealthResponse(
        success=True,
        message="Service is healthy",
        service="terraform-executor",
        version="2.0.0",
        terraform_version=get_terraform_version(),
        uptime_seconds=uptime,
        active_jobs=active_jobs_count,
        total_workspaces=len(workspaces),
        system_info={
            "redis_connected": redis_client is not None,
            "celery_available": celery_app is not None,
        },
    )


@app.get("/metrics")
async def get_metrics() -> bytes:
    """Prometheus metrics endpoint"""
    return generate_latest()


# Workspace Management Endpoints


@app.post(
    "/api/v1/workspaces",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    request: WorkspaceCreateRequest,
    background_tasks: BackgroundTasks,
    redis_conn: Redis[str] = Depends(get_redis),
) -> WorkspaceResponse:
    """Create a new Terraform workspace"""
    if request.name in workspaces:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workspace '{request.name}' already exists",
        )

    workspace_id = uuid4()
    workspace = WorkspaceInfo(
        id=workspace_id,
        name=request.name,
        description=request.description,
        status=WorkspaceStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        git_repository=request.git_repository,
        variables_count=len(request.variables),
    )

    workspaces[request.name] = workspace
    WORKSPACE_COUNT.set(len(workspaces))

    # Store workspace data in Redis for persistence
    await redis_conn.set(
        f"workspace:{request.name}", workspace.model_dump_json(), ex=86400 * 30
    )  # 30 days TTL

    logger.info(
        "Workspace created", workspace_name=request.name, workspace_id=str(workspace_id)
    )

    return WorkspaceResponse(
        success=True,
        message=f"Workspace '{request.name}' created successfully",
        workspace=workspace,
        correlation_id=request.correlation_id,
    )


@app.get("/api/v1/workspaces", response_model=WorkspaceListResponse)
async def list_workspaces() -> WorkspaceListResponse:
    """List all workspaces"""
    workspace_list = list(workspaces.values())

    return WorkspaceListResponse(
        success=True,
        message=f"Retrieved {len(workspace_list)} workspaces",
        workspaces=workspace_list,
        total=len(workspace_list),
    )


@app.get("/api/v1/workspaces/{workspace_name}", response_model=WorkspaceResponse)
async def get_workspace(workspace_name: str) -> WorkspaceResponse:
    """Get workspace details"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    workspace = workspaces[workspace_name]

    return WorkspaceResponse(
        success=True,
        message=f"Workspace '{workspace_name}' retrieved successfully",
        workspace=workspace,
    )


@app.put("/api/v1/workspaces/{workspace_name}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_name: str,
    request: WorkspaceUpdateRequest,
    redis_conn: Redis[str] = Depends(get_redis),
) -> WorkspaceResponse:
    """Update workspace configuration"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    workspace = workspaces[workspace_name]

    # Update fields if provided
    if request.description is not None:
        workspace.description = request.description
    if request.git_repository is not None:
        workspace.git_repository = request.git_repository
    if request.variables is not None:
        workspace.variables_count = len(request.variables)
    if request.auto_apply is not None:
        # Store auto_apply setting (would need to extend WorkspaceInfo model)
        pass

    workspace.updated_at = datetime.utcnow()
    workspaces[workspace_name] = workspace

    # Update in Redis
    await redis_conn.set(
        f"workspace:{workspace_name}", workspace.model_dump_json(), ex=86400 * 30
    )

    logger.info("Workspace updated", workspace_name=workspace_name)

    return WorkspaceResponse(
        success=True,
        message=f"Workspace '{workspace_name}' updated successfully",
        workspace=workspace,
        correlation_id=request.correlation_id,
    )


@app.delete("/api/v1/workspaces/{workspace_name}", response_model=WorkspaceResponse)
async def delete_workspace(
    workspace_name: str, redis_conn: Redis[str] = Depends(get_redis)
) -> WorkspaceResponse:
    """Delete a workspace"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    workspace = workspaces.pop(workspace_name)
    WORKSPACE_COUNT.set(len(workspaces))

    # Remove from Redis
    await redis_conn.delete(f"workspace:{workspace_name}")

    logger.info("Workspace deleted", workspace_name=workspace_name)

    return WorkspaceResponse(
        success=True,
        message=f"Workspace '{workspace_name}' deleted successfully",
        workspace=workspace,
    )


# Terraform Operation Endpoints


@app.post(
    "/api/v1/terraform/plan",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_plan(
    request: TerraformPlanRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Execute terraform plan asynchronously"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.PLAN,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="plan", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_plan

    _task = execute_terraform_plan.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        destroy=request.destroy,
        target_resources=request.target_resources,
        variables=[var.model_dump() for var in request.variables],
        refresh=request.refresh,
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform plan job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform plan job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


@app.post(
    "/api/v1/terraform/apply",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_apply(
    request: TerraformApplyRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Execute terraform apply asynchronously"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.APPLY,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="apply", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_apply

    _task = execute_terraform_apply.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        plan_id=str(request.plan_id) if request.plan_id else None,
        auto_approve=request.auto_approve,
        target_resources=request.target_resources,
        variables=[var.model_dump() for var in request.variables],
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform apply job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform apply job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


@app.post(
    "/api/v1/terraform/destroy",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_destroy(
    request: TerraformDestroyRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Execute terraform destroy asynchronously"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.DESTROY,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="destroy", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_destroy

    _task = execute_terraform_destroy.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        auto_approve=request.auto_approve,
        target_resources=request.target_resources,
        variables=[var.model_dump() for var in request.variables],
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform destroy job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform destroy job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


@app.post(
    "/api/v1/terraform/import",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_import(
    request: TerraformImportRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Import existing infrastructure into Terraform state"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.IMPORT,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="import", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_import

    _task = execute_terraform_import.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        address=request.address,
        resource_id=request.id,
        variables=[var.model_dump() for var in request.variables],
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform import job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform import job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


@app.post(
    "/api/v1/terraform/refresh",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_refresh(
    request: TerraformRefreshRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Refresh Terraform state"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.REFRESH,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="refresh", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_refresh

    _task = execute_terraform_refresh.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        variables=[var.model_dump() for var in request.variables],
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform refresh job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform refresh job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


@app.post(
    "/api/v1/terraform/validate",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def terraform_validate(
    request: TerraformValidateRequest, celery: Celery = Depends(get_celery)
) -> JobResponse:
    """Validate Terraform configuration"""
    if request.workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{request.workspace_name}' not found",
        )

    job_id = uuid4()
    job = JobInfo(
        id=job_id,
        operation=TerraformOperationType.VALIDATE,
        workspace_name=request.workspace_name,
        status=JobStatus.SUBMITTED,
        created_at=datetime.utcnow(),
    )

    jobs[job_id] = job
    ACTIVE_JOBS.inc()
    OPERATION_COUNT.labels(operation="validate", status="submitted").inc()

    # Submit Celery task
    from tasks import execute_terraform_validate

    _task = execute_terraform_validate.delay(  # noqa: F841
        job_id=str(job_id),
        workspace_name=request.workspace_name,
        timeout=request.timeout,
    )

    job.status = JobStatus.QUEUED
    jobs[job_id] = job

    logger.info(
        "Terraform validate job submitted",
        job_id=str(job_id),
        workspace=request.workspace_name,
    )

    return JobResponse(
        success=True,
        message=f"Terraform validate job submitted for workspace '{request.workspace_name}'",
        job=job,
        correlation_id=request.correlation_id,
    )


# Job Management Endpoints


@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID) -> JobStatusResponse:
    """Get job status and details"""
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found"
        )

    job = jobs[job_id]

    return JobStatusResponse(
        success=True, message=f"Job '{job_id}' status retrieved", job=job
    )


@app.get("/api/v1/jobs", response_model=JobListResponse)
async def list_jobs(
    workspace_name: Optional[str] = None,
    operation: Optional[TerraformOperationType] = None,
    status: Optional[JobStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> JobListResponse:
    """List jobs with optional filtering"""
    filtered_jobs = list(jobs.values())

    # Apply filters
    if workspace_name:
        filtered_jobs = [j for j in filtered_jobs if j.workspace_name == workspace_name]
    if operation:
        filtered_jobs = [j for j in filtered_jobs if j.operation == operation]
    if status:
        filtered_jobs = [j for j in filtered_jobs if j.status == status]

    # Sort by creation time (newest first)
    filtered_jobs.sort(key=lambda x: x.created_at, reverse=True)

    # Apply pagination
    total = len(filtered_jobs)
    paginated_jobs = filtered_jobs[offset : offset + limit]

    return JobListResponse(
        success=True,
        message=f"Retrieved {len(paginated_jobs)} of {total} jobs",
        jobs=paginated_jobs,
        total=total,
    )


@app.delete("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def cancel_job(
    job_id: UUID, celery: Celery = Depends(get_celery)
) -> JobStatusResponse:
    """Cancel a running or queued job"""
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found"
        )

    job = jobs[job_id]

    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job '{job_id}' cannot be cancelled (status: {job.status})",
        )

    # Revoke Celery task
    celery.control.revoke(str(job_id), terminate=True)

    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow()
    if job.started_at:
        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()

    jobs[job_id] = job
    ACTIVE_JOBS.dec()
    OPERATION_COUNT.labels(operation=job.operation.value, status="cancelled").inc()

    logger.info("Job cancelled", job_id=str(job_id))

    return JobStatusResponse(
        success=True, message=f"Job '{job_id}' cancelled successfully", job=job
    )


# State Management Endpoints


@app.get("/api/v1/terraform/state/{workspace_name}", response_model=StateResponse)
async def get_state(workspace_name: str) -> StateResponse:
    """Get current Terraform state information"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    # This would integrate with actual state backend (MinIO/S3)
    # For now, returning mock data
    state_info = StateInfo(
        version=4,
        terraform_version=get_terraform_version(),
        serial=1,
        lineage="mock-lineage-12345",
        resources_count=0,
        outputs={},
        last_modified=datetime.utcnow(),
        size_bytes=0,
    )

    return StateResponse(
        success=True,
        message=f"State retrieved for workspace '{workspace_name}'",
        state=state_info,
    )


@app.post(
    "/api/v1/terraform/state/{workspace_name}/lock", response_model=StateLockResponse
)
async def lock_state(
    workspace_name: str,
    request: StateLockRequest,
    redis_conn: Redis[str] = Depends(get_redis),
) -> StateLockResponse:
    """Lock Terraform state for operations"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    lock_key = f"terraform:state:lock:{workspace_name}"

    # Check if already locked
    existing_lock = await redis_conn.get(lock_key)
    if existing_lock:
        lock_data = json.loads(existing_lock)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"State is already locked by {lock_data['locked_by']} since {lock_data['locked_at']}",
        )

    # Acquire lock
    lock_id = str(uuid4())
    lock_data = {
        "lock_id": lock_id,
        "workspace_name": workspace_name,
        "operation": request.operation.value,
        "locked_by": "terraform-executor",
        "locked_at": datetime.utcnow().isoformat(),
        "info": request.info or "",
    }

    await redis_conn.set(lock_key, json.dumps(lock_data), ex=3600)  # 1 hour TTL

    logger.info(
        "State locked",
        workspace=workspace_name,
        lock_id=lock_id,
        operation=request.operation.value,
    )

    return StateLockResponse(
        success=True,
        message=f"State locked for workspace '{workspace_name}'",
        lock_id=lock_id,
        locked_by="terraform-executor",
        locked_at=datetime.utcnow(),
        correlation_id=request.correlation_id,
    )


@app.delete(
    "/api/v1/terraform/state/{workspace_name}/lock", response_model=StateLockResponse
)
async def unlock_state(
    workspace_name: str, redis_conn: Redis[str] = Depends(get_redis)
) -> StateLockResponse:
    """Unlock Terraform state"""
    if workspace_name not in workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_name}' not found",
        )

    lock_key = f"terraform:state:lock:{workspace_name}"

    # Get existing lock
    existing_lock = await redis_conn.get(lock_key)
    if not existing_lock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lock found for workspace '{workspace_name}'",
        )

    lock_data = json.loads(existing_lock)

    # Remove lock
    await redis_conn.delete(lock_key)

    logger.info(
        "State unlocked", workspace=workspace_name, lock_id=lock_data["lock_id"]
    )

    return StateLockResponse(
        success=True,
        message=f"State unlocked for workspace '{workspace_name}'",
        lock_id=lock_data["lock_id"],
        locked_by=lock_data["locked_by"],
        locked_at=datetime.fromisoformat(lock_data["locked_at"].replace("Z", "+00:00")),
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            error_details={"type": type(exc).__name__},
        ).model_dump(),
    )


if __name__ == "__main__":
    # Configure host and port via environment variables
    # Security Note: Binding to 0.0.0.0 is required for container deployment
    # In production, use firewall rules and security groups to restrict access
    host = os.getenv("UVICORN_HOST", "0.0.0.0")  # nosec B104
    port = int(os.getenv("UVICORN_PORT", "8080"))

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    uvicorn.run(
        "app:app", host=host, port=port, reload=False, log_level="info", access_log=True
    )
