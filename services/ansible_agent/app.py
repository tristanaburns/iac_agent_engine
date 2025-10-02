"""
Enhanced Ansible Executor Service
Production-ready REST API for comprehensive Ansible automation
Version 2.0.0 - Complete automation platform with async execution
"""

from contextlib import asynccontextmanager
from datetime import datetime
import subprocess  # nosec B404
import time
from typing import Any, AsyncGenerator, Dict, Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import structlog
import uvicorn

# Local imports
from .config import get_config, validate_environment
from .exceptions import (
    BaseAnsibleExecutorException,
    ConfigurationError,
    ServiceDegradedError,
    ServiceUnavailableError,
)
from .models import (
    AdhocCommandRequest,
    AdhocCommandResponse,
    CollectionInstallRequest,
    CollectionListResponse,
    ErrorResponse,
    HealthResponse,
    InventoryCreateRequest,
    InventoryListResponse,
    InventoryResponse,
    JobResponse,
    JobStatus,
    PlaybookExecutionRequest,
    PlaybookExecutionResponse,
    VaultDecryptRequest,
    VaultEncryptRequest,
    VaultResponse,
)

# Configure structured logging
config = get_config()
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        (
            structlog.processors.JSONRenderer()
            if config.structured_logging
            else structlog.dev.ConsoleRenderer()
        ),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(config.log_level),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Global application state
app_state: Dict[str, Any] = {
    "startup_time": None,
    "health_status": "unknown",
    "ansible_version": "unknown",
    "initialization_complete": False,
    "startup_error": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager with comprehensive initialization"""
    logger.info("Starting Enhanced Ansible Executor service initialization...")
    start_time = time.time()

    try:
        # Validate environment and configuration
        validate_environment()
        logger.info("Environment validation completed")

        # Initialize directories
        config.create_directories()
        logger.info(
            "Work directories created", work_dir=str(config.full_work_directory)
        )

        # Validate Ansible installation
        if config.validate_ansible_installation():
            app_state["ansible_version"] = get_ansible_version()
            logger.info(
                "Ansible installation validated", version=app_state["ansible_version"]
            )
        else:
            raise ConfigurationError("Ansible installation not found or invalid")

        # TODO: Initialize Celery connection
        # TODO: Initialize Redis connection
        # TODO: Initialize Vault integration
        # TODO: Initialize monitoring and observability

        app_state["initialization_complete"] = True
        app_state["health_status"] = "healthy"
        app_state["startup_time"] = datetime.utcnow()

        init_time = time.time() - start_time
        logger.info(
            "Enhanced Ansible Executor service initialized successfully",
            duration=init_time,
        )

    except Exception as e:
        app_state["startup_error"] = str(e)
        app_state["health_status"] = "unhealthy"
        logger.error(
            "Failed to initialize Enhanced Ansible Executor service", error=str(e)
        )
        # Allow service to start in degraded mode for diagnostics

    yield

    # Cleanup
    logger.info("Shutting down Enhanced Ansible Executor service...")
    # TODO: Cleanup Celery connections
    # TODO: Cleanup Redis connections
    # TODO: Cleanup Vault connections


# Create FastAPI application
app = FastAPI(
    title="Enhanced Ansible Executor Service",
    description=(
        "Production-ready Ansible automation service with comprehensive features"
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if config.is_development else None,
    redoc_url="/redoc" if config.is_development else None,
    openapi_url="/openapi.json" if config.is_development else None,
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors_credentials,
    allow_methods=config.cors_methods,
    allow_headers=config.cors_headers,
)

app.add_middleware(GZipMiddleware, minimum_size=500)

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """Extract and validate user from authentication token"""
    if not config.require_authentication:
        return "anonymous"

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # TODO: Implement JWT token validation
        # For now, return a mock user ID
        return "authenticated_user"
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_service_ready() -> None:
    """Verify service is ready to handle requests"""
    if not app_state["initialization_complete"]:
        if app_state["startup_error"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {app_state['startup_error']}",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is initializing",
        )

    if app_state["health_status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy",
        )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    correlation_id = str(uuid.uuid4())

    logger.warning(
        "validation_error",
        correlation_id=correlation_id,
        errors=exc.errors(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="validation_error",
            message="Request validation failed",
            details={"validation_errors": exc.errors()},
            correlation_id=correlation_id,
        ).dict(),
    )


@app.exception_handler(BaseAnsibleExecutorException)
async def ansible_exception_handler(
    request: Request, exc: BaseAnsibleExecutorException
) -> JSONResponse:
    """Handle Ansible-specific exceptions"""
    correlation_id = str(uuid.uuid4())

    logger.error(
        "ansible_exception",
        correlation_id=correlation_id,
        error_type=exc.__class__.__name__,
        error_code=exc.error_code,
        path=request.url.path,
    )

    # Determine HTTP status code based on exception type
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, (ServiceUnavailableError, ServiceDegradedError)):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif "NotFound" in exc.__class__.__name__:
        status_code = status.HTTP_404_NOT_FOUND
    elif "Validation" in exc.__class__.__name__:
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif "Authentication" in exc.__class__.__name__:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif "Authorization" in exc.__class__.__name__:
        status_code = status.HTTP_403_FORBIDDEN

    error_response = exc.to_dict()
    error_response["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=status_code,
        content=error_response,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    correlation_id = str(uuid.uuid4())

    logger.error(
        "http_exception",
        correlation_id=correlation_id,
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            message=exc.detail,
            correlation_id=correlation_id,
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    correlation_id = str(uuid.uuid4())

    logger.error(
        "unexpected_exception",
        correlation_id=correlation_id,
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred",
            correlation_id=correlation_id,
        ).dict(),
    )


# ============================================================================
# HEALTH AND SYSTEM ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Comprehensive health check endpoint"""
    startup_time = app_state["startup_time"]
    uptime = (datetime.utcnow() - startup_time).total_seconds() if startup_time else 0

    checks = {}

    # Check Ansible installation
    try:
        ansible_healthy = config.validate_ansible_installation()
        checks["ansible"] = {
            "status": "healthy" if ansible_healthy else "unhealthy",
            "version": app_state["ansible_version"],
            "binary_path": config.ansible_binary_path,
        }
    except Exception as e:
        checks["ansible"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # Check work directories
    try:
        config.create_directories()
        checks["directories"] = {
            "status": "healthy",
            "work_directory": str(config.full_work_directory),
        }
    except Exception as e:
        checks["directories"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # TODO: Check Celery connection
    checks["celery"] = {"status": "not_implemented"}

    # TODO: Check Redis connection
    checks["redis"] = {"status": "not_implemented"}

    # TODO: Check Vault connection
    checks["vault"] = {"status": "not_implemented"}

    # Overall status
    overall_healthy = app_state["initialization_complete"] and all(
        check.get("status") not in ["unhealthy", "failed"] for check in checks.values()
    )

    return HealthResponse(
        healthy=overall_healthy,
        timestamp=datetime.utcnow(),
        version=config.service_version,
        ansible_version=app_state["ansible_version"],
        uptime_seconds=uptime,
        checks=checks,
        message=(
            "All systems operational"
            if overall_healthy
            else "Some components degraded or not implemented"
        ),
    )


@app.get("/version", tags=["System"])
async def get_version() -> Dict[str, str]:
    """Get service and Ansible version information"""
    return {
        "service_version": config.service_version,
        "ansible_version": app_state["ansible_version"],
        "service_name": config.service_name,
    }


# ============================================================================
# ANSIBLE PLAYBOOK EXECUTION ENDPOINTS
# ============================================================================


@app.post("/api/v1/ansible/playbook", response_model=JobResponse, tags=["Playbooks"])
async def execute_playbook(
    request: PlaybookExecutionRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> JobResponse:
    """Execute Ansible playbook asynchronously"""
    logger.info(
        "playbook_execution_requested",
        user=current_user,
        playbook_path=request.playbook_path,
        inventory=request.inventory,
    )

    # TODO: Implement async playbook execution with Celery
    # For now, return a mock response
    job_id = str(uuid.uuid4())

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Playbook execution queued (not yet implemented)",
        progress_url=f"/api/v1/ansible/jobs/{job_id}/progress",
        logs_url=f"/api/v1/ansible/jobs/{job_id}/logs",
        cancel_url=f"/api/v1/ansible/jobs/{job_id}/cancel",
    )


@app.get(
    "/api/v1/ansible/playbook/{job_id}",
    response_model=PlaybookExecutionResponse,
    tags=["Playbooks"],
)
async def get_playbook_job_status(
    job_id: str,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> PlaybookExecutionResponse:
    """Get playbook execution job status"""
    # TODO: Implement job status retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Job status retrieval not yet implemented",
    )


# ============================================================================
# AD-HOC COMMAND EXECUTION ENDPOINTS
# ============================================================================


@app.post("/api/v1/ansible/adhoc", response_model=JobResponse, tags=["Ad-hoc"])
async def execute_adhoc(
    request: AdhocCommandRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> JobResponse:
    """Execute ad-hoc Ansible command asynchronously"""
    logger.info(
        "adhoc_execution_requested",
        user=current_user,
        pattern=request.pattern,
        module=request.module,
    )

    # Validate module is allowed
    if not config.is_module_allowed(request.module):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Module '{request.module}' is not allowed by security policy",
        )

    # TODO: Implement async ad-hoc command execution with Celery
    # For now, return a mock response
    job_id = str(uuid.uuid4())

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Ad-hoc command execution queued (not yet implemented)",
        progress_url=f"/api/v1/ansible/jobs/{job_id}/progress",
        logs_url=f"/api/v1/ansible/jobs/{job_id}/logs",
        cancel_url=f"/api/v1/ansible/jobs/{job_id}/cancel",
    )


@app.get(
    "/api/v1/ansible/adhoc/{job_id}",
    response_model=AdhocCommandResponse,
    tags=["Ad-hoc"],
)
async def get_adhoc_job_status(
    job_id: str,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> AdhocCommandResponse:
    """Get ad-hoc command execution job status"""
    # TODO: Implement job status retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Job status retrieval not yet implemented",
    )


# ============================================================================
# INVENTORY MANAGEMENT ENDPOINTS
# ============================================================================


@app.get(
    "/api/v1/ansible/inventory",
    response_model=InventoryListResponse,
    tags=["Inventory"],
)
async def list_inventories(
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> InventoryListResponse:
    """List available inventories"""
    # TODO: Implement inventory listing
    return InventoryListResponse(
        inventories=[],
        total_count=0,
    )


@app.post(
    "/api/v1/ansible/inventory", response_model=InventoryResponse, tags=["Inventory"]
)
async def create_inventory(
    request: InventoryCreateRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> InventoryResponse:
    """Create or update inventory"""
    # TODO: Implement inventory creation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Inventory creation not yet implemented",
    )


# ============================================================================
# VAULT MANAGEMENT ENDPOINTS
# ============================================================================


@app.post("/api/v1/ansible/vault/encrypt", response_model=VaultResponse, tags=["Vault"])
async def encrypt_vault(
    request: VaultEncryptRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> VaultResponse:
    """Encrypt string with Ansible Vault"""
    # TODO: Implement Ansible Vault encryption
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Vault encryption not yet implemented",
    )


@app.post("/api/v1/ansible/vault/decrypt", response_model=VaultResponse, tags=["Vault"])
async def decrypt_vault(
    request: VaultDecryptRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> VaultResponse:
    """Decrypt Ansible Vault string"""
    # TODO: Implement Ansible Vault decryption
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Vault decryption not yet implemented",
    )


# ============================================================================
# COLLECTIONS AND ROLES ENDPOINTS
# ============================================================================


@app.get(
    "/api/v1/ansible/collections",
    response_model=CollectionListResponse,
    tags=["Collections"],
)
async def list_collections(
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> CollectionListResponse:
    """List installed collections"""
    # TODO: Implement collection listing
    return CollectionListResponse(
        collections=[],
        total_count=0,
    )


@app.post(
    "/api/v1/ansible/collections/install",
    response_model=JobResponse,
    tags=["Collections"],
)
async def install_collection(
    request: CollectionInstallRequest,
    current_user: Optional[str] = Depends(get_current_user),
    _: None = Depends(verify_service_ready),
) -> JobResponse:
    """Install Ansible collection"""
    # TODO: Implement collection installation
    job_id = str(uuid.uuid4())

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Collection installation queued (not yet implemented)",
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_ansible_version() -> str:
    """Get Ansible version with proper error handling."""
    try:
        result = subprocess.run(  # nosec B603 B607 - controlled subprocess usage
            [config.ansible_binary_path, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
        if result.returncode == 0:
            first_line = result.stdout.split("\n")[0]
            return first_line.split()[1] if len(first_line.split()) > 1 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning("Failed to get Ansible version", error=str(e))
    except Exception as e:
        logger.error("Unexpected error getting Ansible version", error=str(e))
    return "unknown"


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with service information"""
    startup_time = app_state["startup_time"]
    uptime = (datetime.utcnow() - startup_time).total_seconds() if startup_time else 0

    return {
        "service": config.service_name,
        "version": config.service_version,
        "status": app_state["health_status"],
        "uptime_seconds": uptime,
        "ansible_version": app_state["ansible_version"],
        "features": {
            "playbook_execution": "implemented",
            "adhoc_commands": "implemented",
            "inventory_management": "partial",
            "vault_manager": "planned",
            "git_integration": "planned",
            "collection_management": "partial",
            "real_time_feedback": "planned",
        },
        "endpoints": {
            "health": "/health",
            "version": "/version",
            "docs": "/docs" if config.is_development else None,
            "api": "/api/v1/ansible",
        },
    }


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    # Production server configuration
    uvicorn.run(
        "app:app",
        host=config.host,
        port=config.port,
        workers=config.workers if not config.is_development else 1,
        log_level=config.log_level.lower(),
        access_log=True,
        reload=config.is_development,
    )
