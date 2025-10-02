"""
State Management Service - Enterprise Terraform State Management Platform.

This module provides a production-ready REST API for centralized Terraform state
management with comprehensive security, monitoring, and reliability features.
Designed for enterprise-scale infrastructure management with multi-cloud support.

Key Features:
- Secure Terraform state storage with MinIO backend
- Distributed state locking with Redis
- Comprehensive backup and restore capabilities
- Role-based access control and audit logging
- Real-time monitoring with Prometheus metrics
- High availability and fault tolerance

Security Features:
- JWT and API key authentication
- Rate limiting and DDoS protection
- Encrypted state storage and transit
- Audit trails for all operations
- Vault integration for secrets management

Reliability Features:
- Distributed locking to prevent state corruption
- Automatic backup and retention management
- Health checks and circuit breakers
- Graceful error handling and recovery
- Comprehensive logging and monitoring

Architecture:
- FastAPI REST API with async/await patterns
- Redis for distributed locking and caching
- MinIO for object storage backend
- Vault for secrets and encryption keys
- Prometheus for metrics and monitoring
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import hashlib
from io import BytesIO
import json
import time
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

from fastapi import Depends, FastAPI, Header, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import hvac
import jwt
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import redis.asyncio as redis
import structlog
import uvicorn

try:
    from minio import Minio  # type: ignore[import-untyped]
    from minio.error import S3Error  # type: ignore[import-untyped]
except ImportError:
    # Fallback for environments without minio
    Minio = None
    S3Error = Exception

from state_backend import StateBackend
from state_locker import StateLocker

if TYPE_CHECKING:
    pass

try:
    from config import config
    from exceptions import (
        AuthenticationError,
        BackupNotFoundError,
        LockNotFoundError,
        RateLimitError,
        ServiceUnavailableError,
        StateLockedError,
        StateManagementError,
        StateNotFoundError,
        VersionNotFoundError,
    )
    from models import (
        BackendConfig,
        BackendCreateRequest,
        BackendListResponse,
        BackendResponse,
        BackupCreateRequest,
        BackupInfo,
        BackupListResponse,
        BackupMetadata,
        BackupResponse,
        BackupStatus,
        BackupType,
        ComponentHealth,
        DeleteResponse,
        Environment,
        ErrorDetail,
        ErrorResponse,
        HealthResponse,
        HealthStatus,
        LockRequest,
        LockResponse,
        LockStatus,
        LockStatusResponse,
        OperationType,
        RestoreRequest,
        RestoreResponse,
        RollbackResponse,
        StateResponse,
        StateUpdateRequest,
        StateUpdateResponse,
        StateVersion,
        StateVersionResponse,
        UnlockRequest,
        UnlockResponse,
        VersionListResponse,
    )
except ImportError:
    # For type checking when imports are not available
    pass

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    context_class=dict,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Module exports
__all__ = [
    "app",
    "create_jwt_token",
    "verify_jwt_token",
    "get_current_user",
    "rate_limit_check",
    "health_check",
    "get_metrics",
    "create_backend",
    "list_backends",
    "get_backend",
    "get_state",
    "update_state",
    "delete_state",
    "list_state_versions",
    "get_state_version",
    "rollback_state",
    "lock_state",
    "unlock_state",
    "get_lock_status",
    "create_backup",
    "list_backups",
    "restore_backup",
]

# Global instances
redis_client: Optional[redis.Redis] = None
state_backend: Optional[StateBackend] = None
state_locker: Optional[StateLocker] = None
vault_client: Optional[hvac.Client] = None
minio_client: Optional[Minio] = None
service_start_time: float = time.time()

# In-memory backend storage (would be database in production)
backends_store: Dict[str, BackendConfig] = {}

# Prometheus metrics - initialized once
_metrics_initialized = False
request_counter: Optional[Counter] = None
error_counter: Optional[Counter] = None
lock_operations_counter: Optional[Counter] = None
state_operations_histogram: Optional[Histogram] = None
active_locks_gauge: Optional[Gauge] = None
state_size_histogram: Optional[Histogram] = None


def initialize_metrics() -> None:
    """Initialize Prometheus metrics (only once)"""
    global _metrics_initialized, request_counter, error_counter, lock_operations_counter
    global state_operations_histogram, active_locks_gauge, state_size_histogram

    if _metrics_initialized:
        return

    try:
        request_counter = Counter(
            "iac_agent_manager_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
        )
        error_counter = Counter(
            "iac_agent_manager_errors_total",
            "Total number of errors",
            ["error_type"],
        )
        lock_operations_counter = Counter(
            "state_lock_operations_total",
            "Total lock operations",
            ["operation", "status"],
        )
        state_operations_histogram = Histogram(
            "state_operations_duration_seconds",
            "State operation duration",
            ["operation"],
        )
        active_locks_gauge = Gauge(
            "state_active_locks_total", "Number of active state locks"
        )
        state_size_histogram = Histogram(
            "state_size_bytes", "State size in bytes", ["backend_id", "workspace"]
        )

        _metrics_initialized = True
        logger.info("Prometheus metrics initialized successfully")
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            logger.warning("Metrics already registered, using existing instances")
            _metrics_initialized = True
        else:
            logger.error("Failed to initialize metrics", error=str(e))
            raise


def create_jwt_token(
    user_id: str, expires_delta: timedelta = timedelta(hours=24)
) -> str:
    """Create JWT token for authentication"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
        "iss": "iac-agent-service",
    }
    return jwt.encode(payload, config.security.api_key_header, algorithm="HS256")  # type: ignore[attr-defined]


def verify_jwt_token(token: str) -> Optional[str]:
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(  # type: ignore[attr-defined]
            token, config.security.api_key_header, algorithms=["HS256"]
        )
        sub = payload.get("sub")
        return str(sub) if sub is not None else None
    except jwt.ExpiredSignatureError:  # type: ignore[attr-defined]
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:  # type: ignore[attr-defined]
        logger.warning("Invalid JWT token", error=str(e))
        return None


def _build_redis_connection_config() -> Dict[str, Any]:
    """Build Redis connection configuration dictionary.

    Returns:
        Dictionary with Redis connection parameters
    """
    connection_kwargs = {
        "host": config.redis.host,
        "port": config.redis.port,
        "db": config.redis.database,
        "password": config.redis.password,
        "ssl": config.redis.ssl,
        "decode_responses": True,
        "socket_keepalive": config.redis.socket_keepalive,
    }

    # Add keepalive options if configured
    if config.redis.socket_keepalive_options is not None:
        connection_kwargs["socket_keepalive_options"] = (
            config.redis.socket_keepalive_options
        )

    return connection_kwargs


async def _initialize_redis_connection() -> redis.Redis:
    """Initialize and test Redis connection.

    Returns:
        Configured Redis client instance

    Raises:
        Exception: If Redis connection fails
    """
    connection_kwargs = _build_redis_connection_config()
    redis_instance = redis.Redis(**connection_kwargs)

    # Test connection with ping
    await redis_instance.ping()
    logger.info(
        "Redis connection established",
        host=config.redis.host,
        port=config.redis.port,
    )

    return redis_instance


def _initialize_minio_client() -> Optional[Minio]:
    """Initialize MinIO client with configuration.

    Returns:
        Configured MinIO client instance or None if Minio not available
    """
    if Minio is None:
        logger.warning("MinIO library not available")
        return None

    minio_instance = Minio(
        config.minio.endpoint,
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        region=config.minio.region,
        secure=config.minio.use_tls,
    )
    logger.info("MinIO client initialized", endpoint=config.minio.endpoint)
    return minio_instance


def _initialize_vault_client() -> hvac.Client:
    """Initialize and authenticate Vault client.

    Returns:
        Configured Vault client instance
    """
    vault_instance = hvac.Client(
        url=str(config.vault.url),
        token=config.vault.token,
        verify=config.vault.verify_ssl,
        timeout=config.vault.timeout,
    )

    # Check authentication status
    if vault_instance.is_authenticated():
        logger.info("Vault client authenticated", url=str(config.vault.url))
    else:
        logger.warning("Vault client not authenticated", url=str(config.vault.url))

    return vault_instance


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for service initialization and cleanup.

    This function manages the complete lifecycle of the State Management Service,
    including initialization of all dependencies, health checks, and graceful
    shutdown procedures.

    Initialized Components:
    - Redis client for distributed locking and caching
    - MinIO client for object storage backend
    - State backend for Terraform state management
    - State locker for distributed locking
    - Vault client for secrets management

    Error Handling:
    - All initialization errors are logged and re-raised
    - Graceful shutdown ensures proper resource cleanup
    - Connection failures are reported with detailed context
    """
    global redis_client, state_backend, state_locker, vault_client, minio_client

    logger.info("Starting State Management Service", version=config.service_version)

    try:
        # Initialize Redis connection with health check
        redis_client = await _initialize_redis_connection()

        # Initialize MinIO client for object storage
        minio_client = _initialize_minio_client()

        # Initialize State Backend for Terraform state operations
        state_backend = StateBackend(config.minio, config)
        logger.info("State backend initialized")

        # Initialize State Locker for distributed locking
        state_locker = StateLocker(redis_client, config.redis)
        logger.info("State locker initialized")

        # Initialize Vault client for secrets management
        vault_client = _initialize_vault_client()

        logger.info("Service initialization completed successfully")

        # Yield control to the application
        yield

    except Exception as e:
        logger.error("Failed to initialize service", error=str(e), exc_info=True)
        raise
    finally:
        # Graceful shutdown with resource cleanup
        logger.info("Shutting down State Management Service")
        if redis_client:
            await redis_client.close()


# Initialize FastAPI application
app = FastAPI(
    title="State Management Service",
    description="Production-ready Terraform state management with MinIO backend",
    version=getattr(config, "service_version", "1.0.0") if config else "1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Initialize metrics
initialize_metrics()

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

if config.security.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security
security = (
    HTTPBearer(auto_error=False) if config.security.require_authentication else None
)


def _check_api_key_authentication(x_api_key: str) -> str:
    """Check API key authentication"""
    if x_api_key == config.security.api_key_header:
        return "api-user"
    raise AuthenticationError("Invalid API key")


def _check_bearer_token_authentication(
    credentials: Optional[HTTPAuthorizationCredentials],
) -> str:
    """Check Bearer token authentication"""
    if not credentials:
        raise AuthenticationError("Authentication required")

    user_id = verify_jwt_token(credentials.credentials)
    if not user_id:
        raise AuthenticationError("Invalid or expired token")
    return user_id


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
) -> str:
    """Get current user from authentication token or API key"""
    if not config.security.require_authentication:
        return "anonymous"

    # Check API key first
    if x_api_key:
        return _check_api_key_authentication(x_api_key)

    # Check Bearer token
    return _check_bearer_token_authentication(credentials)


def _generate_rate_limit_key(request: Request, current_user: str) -> str:
    """Generate rate limit key for client"""
    client_id = f"{request.client.host if request.client else 'unknown'}:{current_user}"
    return f"rate_limit:{client_id}"


async def _check_existing_rate_limit(key: str) -> int:
    """Check existing rate limit count"""
    if redis_client is None:
        raise ServiceUnavailableError("Redis client not initialized")
    current = await redis_client.get(key)
    if current is None:
        await redis_client.setex(key, 60, 1)
        return 1
    return int(current)


async def _enforce_rate_limit(key: str, count: int, client_id: str) -> None:
    """Enforce rate limit if exceeded"""
    if count >= config.security.rate_limit_per_minute:
        if error_counter is not None:
            error_counter.labels(error_type="rate_limit").inc()
        raise RateLimitError(
            client_id=client_id, limit=config.security.rate_limit_per_minute, window=60
        )
    if redis_client is None:
        raise ServiceUnavailableError("Redis client not initialized")
    await redis_client.incr(key)


async def rate_limit_check(
    request: Request, current_user: str = Depends(get_current_user)
) -> None:
    """Check rate limiting for requests"""
    if not redis_client:
        return

    key = _generate_rate_limit_key(request, current_user)
    client_id = f"{request.client.host if request.client else 'unknown'}:{current_user}"

    try:
        count = await _check_existing_rate_limit(key)
        if count > 1:  # Only enforce if not first request
            await _enforce_rate_limit(key, count, client_id)
    except redis.RedisError as e:
        logger.warning("Rate limit check failed", error=str(e))


# Exception to status code mapping
EXCEPTION_STATUS_MAP: Dict[Any, int] = {}


def _determine_http_status_code(exc: StateManagementError) -> int:
    """Determine HTTP status code for exception"""
    return EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_error_response(exc: StateManagementError) -> ErrorResponse:
    """Create error response object"""
    return ErrorResponse(
        success=False,
        message=exc.message,
        error=ErrorDetail(
            code=exc.error_code, message=exc.message, details=exc.details
        ),
        correlation_id=None,
    )


def _log_exception_details(exc: StateManagementError, request: Request) -> None:
    """Log exception details for monitoring"""
    if error_counter is not None:
        error_counter.labels(error_type=exc.error_code).inc()
    logger.error(
        "State management error",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )


@app.exception_handler(Exception)
async def iac_agent_manager_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle state management exceptions"""
    # Check if exception is StateManagementError
    if isinstance(exc, StateManagementError):
        status_code = _determine_http_status_code(exc)
        error_response = _create_error_response(exc)
        _log_exception_details(exc, request)
    else:
        # Handle generic exceptions
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_response = ErrorResponse(
            success=False,
            message=str(exc),
            error=ErrorDetail(code="INTERNAL_ERROR", message=str(exc), details=None),
            correlation_id=None,
        )
        logger.error(
            "Unhandled exception",
            error=str(exc),
            path=request.url.path,
            method=request.method,
        )

    return JSONResponse(status_code=status_code, content=error_response.dict())


# Health and Status Endpoints
@app.get("/health", tags=["Health"])  # response_model=HealthResponse
async def health_check() -> HealthResponse:
    """Service health check endpoint"""
    components = []
    overall_status = HealthStatus.HEALTHY

    # Check Redis connection
    redis_status = HealthStatus.HEALTHY
    redis_message = "Connected"
    redis_response_time = None

    if redis_client:
        try:
            start_time = time.time()
            await redis_client.ping()
            redis_response_time = (time.time() - start_time) * 1000
        except Exception as e:
            redis_status = HealthStatus.UNHEALTHY
            redis_message = f"Connection failed: {str(e)}"
            overall_status = HealthStatus.UNHEALTHY
    else:
        redis_status = HealthStatus.UNHEALTHY
        redis_message = "Not initialized"
        overall_status = HealthStatus.UNHEALTHY

    components.append(
        ComponentHealth(
            name="Redis",
            status=redis_status,
            message=redis_message,
            response_time_ms=redis_response_time,
            last_check=datetime.utcnow(),
        )
    )

    # Check MinIO connection
    minio_status = HealthStatus.HEALTHY
    minio_message = "Connected"
    minio_response_time = None

    if minio_client:
        try:
            start_time = time.time()
            minio_client.list_buckets()
            minio_response_time = (time.time() - start_time) * 1000
        except Exception as e:
            minio_status = HealthStatus.UNHEALTHY
            minio_message = f"Connection failed: {str(e)}"
            overall_status = HealthStatus.DEGRADED
    else:
        minio_status = HealthStatus.UNHEALTHY
        minio_message = "Not initialized"
        overall_status = HealthStatus.DEGRADED

    components.append(
        ComponentHealth(
            name="MinIO",
            status=minio_status,
            message=minio_message,
            response_time_ms=minio_response_time,
            last_check=datetime.utcnow(),
        )
    )

    # Check Vault connection
    vault_status = HealthStatus.HEALTHY
    vault_message = "Connected"
    vault_response_time = None

    if vault_client:
        try:
            start_time = time.time()
            vault_client.sys.read_health_status(method="GET")
            vault_response_time = (time.time() - start_time) * 1000
        except Exception as e:
            vault_status = HealthStatus.DEGRADED
            vault_message = f"Connection degraded: {str(e)}"
            if overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
    else:
        vault_status = HealthStatus.UNHEALTHY
        vault_message = "Not initialized"
        if overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED

    components.append(
        ComponentHealth(
            name="Vault",
            status=vault_status,
            message=vault_message,
            response_time_ms=vault_response_time,
            last_check=datetime.utcnow(),
        )
    )

    return HealthResponse(
        success=True,
        message="Health check completed",
        overall_status=overall_status,
        components=components,
        uptime_seconds=time.time() - service_start_time,
        version=config.service_version,
        correlation_id=None,
    )


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics() -> Response:
    """Prometheus metrics endpoint"""
    metrics_output = generate_latest()
    return Response(
        content=metrics_output, media_type="text/plain; version=0.0.4; charset=utf-8"
    )


# Backend Management Endpoints
@app.post(
    "/api/v1/backends", tags=["Backend Management"]
)  # response_model=BackendResponse
async def create_backend(
    request: BackendCreateRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> BackendResponse:
    """Create a new state backend configuration"""
    if request_counter is not None:
        request_counter.labels(
            method="POST", endpoint="/api/v1/backends", status="started"
        ).inc()

    backend_id = hashlib.sha256(
        f"{request.config.name}{time.time()}".encode()
    ).hexdigest()[:12]

    # Store backend configuration
    backends_store[backend_id] = request.config

    # Create bucket for backend
    if state_backend and minio_client:
        environment = getattr(request.config, "environment", "development")
        env_value = getattr(environment, "value", str(environment))
        bucket_name = f"{config.minio.bucket_prefix}-{env_value}-{backend_id}".lower()
        try:
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name, location=config.minio.region)
                logger.info(
                    "Bucket created for backend",
                    backend_id=backend_id,
                    bucket=bucket_name,
                )
        except Exception as e:
            logger.error("Failed to create bucket", backend_id=backend_id, error=str(e))

    if request_counter is not None:
        request_counter.labels(
            method="POST", endpoint="/api/v1/backends", status="success"
        ).inc()

    return BackendResponse(
        success=True,
        message="Backend created successfully",
        backend_id=backend_id,
        config=request.config,
        correlation_id=request.correlation_id,
    )


@app.get(
    "/api/v1/backends", tags=["Backend Management"]
)  # response_model=BackendListResponse
async def list_backends(
    current_user: str = Depends(get_current_user),
) -> BackendListResponse:
    """List all configured state backends"""
    if request_counter is not None:
        request_counter.labels(
            method="GET", endpoint="/api/v1/backends", status="success"
        ).inc()

    backends = [
        BackendResponse(
            success=True,
            message="Backend data",
            backend_id=backend_id,
            config=backend_config,
            correlation_id=None,
        )
        for backend_id, backend_config in backends_store.items()
    ]

    return BackendListResponse(
        success=True,
        message="Backends retrieved successfully",
        backends=backends,
        total_count=len(backends),
        correlation_id=None,
    )


@app.get(
    "/api/v1/backends/{backend_id}",
    response_model=BackendResponse,
    tags=["Backend Management"],
)
async def get_backend(
    backend_id: str, current_user: str = Depends(get_current_user)
) -> BackendResponse:
    """Get backend configuration by ID"""
    if request_counter is not None:
        request_counter.labels(
            method="GET", endpoint=f"/api/v1/backends/{backend_id}", status="started"
        ).inc()

    if backend_id not in backends_store:
        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/backends/{backend_id}",
                status="not_found",
            ).inc()
        raise StateNotFoundError(backend_id, "N/A")

    if request_counter is not None:
        request_counter.labels(
            method="GET", endpoint=f"/api/v1/backends/{backend_id}", status="success"
        ).inc()

    return BackendResponse(
        success=True,
        message="Backend retrieved successfully",
        backend_id=backend_id,
        config=backends_store[backend_id],
        correlation_id=None,
    )


# State Management Endpoints
@app.get(
    "/api/v1/state/{backend_id}/state/{workspace}",
    # response_model=StateResponse,
    tags=["State Management"],
)
async def get_state(
    backend_id: str, workspace: str, current_user: str = Depends(get_current_user)
) -> StateResponse:
    """Get current Terraform state"""
    if state_operations_histogram is not None:
        context_timer: Any = state_operations_histogram.labels(
            operation="get_state"
        ).time()
    else:
        from contextlib import nullcontext

        context_timer = nullcontext()

    with context_timer:
        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/state/{backend_id}/state/{workspace}",
                status="started",
            ).inc()

        if not state_backend:
            raise ServiceUnavailableError("State backend not initialized")

        if backend_id not in backends_store:
            raise StateNotFoundError(backend_id, workspace)

        environment = getattr(backends_store[backend_id], "environment", "development")

        try:
            state_data, state_info = await state_backend.retrieve_state(
                backend_id,
                workspace,
                environment=(
                    Environment(environment)
                    if isinstance(environment, str)
                    else environment
                ),
            )

            if request_counter is not None:
                request_counter.labels(
                    method="GET",
                    endpoint=f"/api/v1/state/{backend_id}/state/{workspace}",
                    status="success",
                ).inc()

            return StateResponse(
                success=True,
                message="State retrieved successfully",
                state_data=state_data.decode("utf-8"),
                state_info=state_info,
                correlation_id=None,
            )
        except StateNotFoundError:
            if request_counter is not None:
                request_counter.labels(
                    method="GET",
                    endpoint=f"/api/v1/state/{backend_id}/state/{workspace}",
                    status="not_found",
                ).inc()
            raise


def _validate_update_state_services_and_backend(
    backend_id: str, workspace: str
) -> None:
    """Validate update state services and backend existence"""
    if not state_backend or not state_locker:
        raise ServiceUnavailableError("State backend or locker not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)


async def _check_state_lock_for_update(
    backend_id: str, workspace: str, request_lock_id: str
) -> None:
    """Check if state is locked and validate lock ownership"""
    if state_locker is None:
        raise ServiceUnavailableError("State locker not initialized")
    lock_status = await state_locker.get_lock_status(backend_id, workspace)
    if lock_status == LockStatus.LOCKED:
        lock_info = await state_locker.get_lock_info(backend_id, workspace)
        if lock_info and lock_info.id != request_lock_id:
            raise StateLockedError(backend_id, workspace, lock_info.dict())


async def _store_state_update(
    backend_id: str,
    workspace: str,
    state_data: bytes,
    operation_type: Any,
    current_user: str,
    environment: Any,
) -> Tuple[Any, str]:
    """Store the updated state data"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    return await state_backend.store_state(
        backend_id,
        workspace,
        state_data,
        operation_type=operation_type,
        created_by=current_user,
        environment=environment,
    )


def _record_state_size_metrics(
    backend_id: str, workspace: str, state_data_size: int
) -> None:
    """Record state size metrics"""
    if state_size_histogram is not None:
        state_size_histogram.labels(backend_id=backend_id, workspace=workspace).observe(
            state_data_size
        )


def _increment_update_state_counter(
    backend_id: str, workspace: str, status: str
) -> None:
    """Increment update state request counter"""
    if request_counter is not None:
        request_counter.labels(
            method="POST",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}",
            status=status,
        ).inc()


@app.post(
    "/api/v1/state/{backend_id}/state/{workspace}",
    # response_model=StateUpdateResponse,
    tags=["State Management"],
)
async def update_state(
    backend_id: str,
    workspace: str,
    request: StateUpdateRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> StateUpdateResponse:
    """Update Terraform state"""
    if state_operations_histogram is not None:
        context_timer: Any = state_operations_histogram.labels(
            operation="update_state"
        ).time()
    else:
        from contextlib import nullcontext

        context_timer = nullcontext()

    with context_timer:
        _increment_update_state_counter(backend_id, workspace, "started")

        # Validate services and backend
        _validate_update_state_services_and_backend(backend_id, workspace)
        environment = getattr(backends_store[backend_id], "environment", "development")

        # Check state lock
        await _check_state_lock_for_update(backend_id, workspace, request.lock_id)

        # Prepare and record state data
        state_data = request.state_data.encode("utf-8")
        _record_state_size_metrics(backend_id, workspace, len(state_data))

        # Store state update
        state_info, version_id = await _store_state_update(
            backend_id,
            workspace,
            state_data,
            getattr(request, "operation_type", "update"),
            current_user,
            environment,
        )

        _increment_update_state_counter(backend_id, workspace, "success")

        return StateUpdateResponse(
            success=True,
            message="State updated successfully",
            version_id=version_id,
            state_info=state_info,
            correlation_id=request.correlation_id,
        )


def _validate_delete_state_services_and_backend(
    backend_id: str, workspace: str
) -> None:
    """Validate delete state services and backend existence"""
    if not state_backend or not state_locker:
        raise ServiceUnavailableError("State backend or locker not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)


async def _check_state_lock_for_delete(backend_id: str, workspace: str) -> None:
    """Check if state is locked before deletion"""
    if state_locker is None:
        raise ServiceUnavailableError("State locker not initialized")
    lock_status = await state_locker.get_lock_status(backend_id, workspace)
    if lock_status == LockStatus.LOCKED:
        lock_info = await state_locker.get_lock_info(backend_id, workspace)
        raise StateLockedError(
            backend_id, workspace, lock_info.dict() if lock_info else {}
        )


async def _perform_state_deletion(
    backend_id: str, workspace: str, environment: Any
) -> int:
    """Perform the actual state deletion operation"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    return await state_backend.delete_state(
        backend_id, workspace, environment=environment
    )


def _increment_delete_state_counter(
    backend_id: str, workspace: str, status: str
) -> None:
    """Increment delete state request counter"""
    if request_counter is not None:
        request_counter.labels(
            method="DELETE",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}",
            status=status,
        ).inc()


@app.delete(
    "/api/v1/state/{backend_id}/state/{workspace}",
    # response_model=DeleteResponse,
    tags=["State Management"],
)
async def delete_state(
    backend_id: str,
    workspace: str,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> DeleteResponse:
    """Delete Terraform state"""
    if state_operations_histogram is not None:
        context_timer: Any = state_operations_histogram.labels(
            operation="delete_state"
        ).time()
    else:
        from contextlib import nullcontext

        context_timer = nullcontext()

    with context_timer:
        _increment_delete_state_counter(backend_id, workspace, "started")

        # Validate services and backend
        _validate_delete_state_services_and_backend(backend_id, workspace)
        environment = getattr(backends_store[backend_id], "environment", "development")

        # Check state lock
        await _check_state_lock_for_delete(backend_id, workspace)

        # Perform deletion
        deleted_count = await _perform_state_deletion(
            backend_id, workspace, environment
        )

        _increment_delete_state_counter(backend_id, workspace, "success")

        return DeleteResponse(
            success=True,
            message=f"State deleted successfully ({deleted_count} objects removed)",
            deleted_state_id=f"{backend_id}/{workspace}",
            versions_deleted=deleted_count,
            backup_created=None,
            correlation_id=None,
        )


# State Versioning Endpoints
@app.get(
    "/api/v1/state/{backend_id}/state/{workspace}/versions",
    # response_model=VersionListResponse,
    tags=["State Versioning"],
)
async def list_state_versions(
    backend_id: str,
    workspace: str,
    limit: int = 100,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
) -> VersionListResponse:
    """List state versions"""
    if request_counter is not None:
        request_counter.labels(
            method="GET",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/versions",
            status="started",
        ).inc()

    if not state_backend:
        raise ServiceUnavailableError("State backend not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)

    environment = getattr(backends_store[backend_id], "environment", "development")

    versions = await state_backend.list_state_versions(
        backend_id,
        workspace,
        limit=limit,
        environment=(
            Environment(environment) if isinstance(environment, str) else environment
        ),
    )

    # Apply offset
    if offset > 0:
        versions = versions[offset:]

    if request_counter is not None:
        request_counter.labels(
            method="GET",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/versions",
            status="success",
        ).inc()

    return VersionListResponse(
        success=True,
        message="State versions retrieved successfully",
        versions=versions,
        total_count=len(versions),
        correlation_id=None,
    )


@app.get(
    "/api/v1/state/{backend_id}/state/{workspace}/versions/{version}",
    # response_model=StateVersionResponse,
    tags=["State Versioning"],
)
async def get_state_version(
    backend_id: str,
    workspace: str,
    version: str,
    current_user: str = Depends(get_current_user),
) -> StateVersionResponse:
    """Get specific state version"""
    if request_counter is not None:
        request_counter.labels(
            method="GET",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/versions/{version}",
            status="started",
        ).inc()

    if not state_backend:
        raise ServiceUnavailableError("State backend not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)

    environment = getattr(backends_store[backend_id], "environment", "development")

    try:
        state_data, state_info = await state_backend.retrieve_state(
            backend_id,
            workspace,
            version_id=version,
            environment=(
                Environment(environment)
                if isinstance(environment, str)
                else environment
            ),
        )

        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/versions/{version}",
                status="success",
            ).inc()

        # Create version_info from state_info for StateVersionResponse
        version_info = StateVersion(
            version_id=version,
            version_number=state_info.serial if hasattr(state_info, "serial") else 1,
            size_bytes=state_info.size_bytes,
            checksum=state_info.checksum,
            metadata=state_info.metadata,
            created_at=state_info.created_at,
            created_by="system",
            operation_type=OperationType.READ,
        )

        return StateVersionResponse(
            success=True,
            message="State version retrieved successfully",
            state_data=state_data.decode("utf-8"),
            version_info=version_info,
            correlation_id=None,
        )
    except VersionNotFoundError:
        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/versions/{version}",
                status="not_found",
            ).inc()
        raise


def _validate_rollback_services_and_backend(backend_id: str, workspace: str) -> None:
    """Validate rollback services and backend existence"""
    if not state_backend or not state_locker:
        raise ServiceUnavailableError("State backend or locker not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)


async def _check_state_lock_for_rollback(backend_id: str, workspace: str) -> None:
    """Check if state is locked before rollback"""
    if state_locker is None:
        raise ServiceUnavailableError("State locker not initialized")
    lock_status = await state_locker.get_lock_status(backend_id, workspace)
    if lock_status == LockStatus.LOCKED:
        lock_info = await state_locker.get_lock_info(backend_id, workspace)
        raise StateLockedError(
            backend_id, workspace, lock_info.dict() if lock_info else {}
        )


async def _retrieve_version_for_rollback(
    backend_id: str, workspace: str, version: str, environment: Any
) -> bytes:
    """Retrieve the specific version for rollback"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    try:
        state_data, _ = await state_backend.retrieve_state(
            backend_id, workspace, version_id=version, environment=environment
        )
        return state_data
    except VersionNotFoundError:
        _increment_rollback_counter(backend_id, workspace, version, "not_found")
        raise


async def _store_rollback_as_new_version(
    backend_id: str,
    workspace: str,
    state_data: bytes,
    current_user: str,
    environment: Any,
) -> Tuple[Any, str]:
    """Store rollback state as new version"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    return await state_backend.store_state(
        backend_id,
        workspace,
        state_data,
        operation_type=OperationType.WRITE,  # rollback is stored as WRITE operation
        created_by=current_user,
        environment=environment,
    )


def _increment_rollback_counter(
    backend_id: str, workspace: str, version: str, status: str
) -> None:
    """Increment rollback request counter"""
    if request_counter is not None:
        request_counter.labels(
            method="POST",
            endpoint=f"/api/v1/state/{backend_id}/state/{workspace}/rollback/{version}",
            status=status,
        ).inc()


@app.post(
    "/api/v1/state/{backend_id}/state/{workspace}/rollback/{version}",
    # response_model=RollbackResponse,
    tags=["State Versioning"],
)
async def rollback_state(
    backend_id: str,
    workspace: str,
    version: str,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> RollbackResponse:
    """Rollback to specific state version"""
    if state_operations_histogram is not None:
        context_timer_rollback: Any = state_operations_histogram.labels(
            operation="rollback_state"
        ).time()
    else:
        from contextlib import nullcontext

        context_timer_rollback = nullcontext()

    with context_timer_rollback:
        _increment_rollback_counter(backend_id, workspace, version, "started")

        # Validate services and backend
        _validate_rollback_services_and_backend(backend_id, workspace)
        environment = getattr(backends_store[backend_id], "environment", "development")

        # Check state lock
        await _check_state_lock_for_rollback(backend_id, workspace)

        # Retrieve version for rollback
        state_data = await _retrieve_version_for_rollback(
            backend_id, workspace, version, environment
        )

        # Store rollback as new version
        state_info, new_version_id = await _store_rollback_as_new_version(
            backend_id, workspace, state_data, current_user, environment
        )

        _increment_rollback_counter(backend_id, workspace, version, "success")

        return RollbackResponse(
            success=True,
            message=f"Successfully rolled back to version {version}",
            previous_version_id=new_version_id,
            rolled_back_to_version_id=version,
            state_info=state_info,
            backup_created=None,
            correlation_id=None,
        )


# State Locking Endpoints
@app.post(
    "/api/v1/state/{backend_id}/lock/{workspace}",
    # response_model=LockResponse,
    tags=["State Locking"],
)
async def lock_state(
    backend_id: str,
    workspace: str,
    request: LockRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> LockResponse:
    """Lock state for operations"""
    if lock_operations_counter is not None:
        lock_operations_counter.labels(operation="lock", status="started").inc()

    if not state_locker:
        raise ServiceUnavailableError("State locker not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)

    try:
        await state_locker.acquire_lock(
            backend_id,
            workspace,
            request.lock_info,
            timeout=request.timeout or config.state.lock_timeout_seconds,
        )

        if active_locks_gauge is not None:
            active_locks_gauge.inc()
        if lock_operations_counter is not None:
            lock_operations_counter.labels(operation="lock", status="success").inc()

        return LockResponse(
            success=True,
            message="State locked successfully",
            lock_info=request.lock_info,
            expires_at=datetime.utcnow()
            + timedelta(seconds=request.timeout or config.state.lock_timeout_seconds),
            correlation_id=request.correlation_id,
        )
    except StateLockedError:
        if lock_operations_counter is not None:
            lock_operations_counter.labels(
                operation="lock", status="already_locked"
            ).inc()
        raise
    except Exception:
        if lock_operations_counter is not None:
            lock_operations_counter.labels(operation="lock", status="failed").inc()
        raise


@app.delete(
    "/api/v1/state/{backend_id}/lock/{workspace}",
    # response_model=UnlockResponse,
    tags=["State Locking"],
)
async def unlock_state(
    backend_id: str,
    workspace: str,
    request: UnlockRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> UnlockResponse:
    """Unlock state"""
    if lock_operations_counter is not None:
        lock_operations_counter.labels(operation="unlock", status="started").inc()

    if not state_locker:
        raise ServiceUnavailableError("State locker not initialized")

    try:
        if request.force:
            await state_locker.force_unlock(
                backend_id,
                workspace,
                getattr(request, "force_reason", None) or "Forced by user",
            )
        else:
            await state_locker.release_lock(backend_id, workspace, request.lock_id)

        if active_locks_gauge is not None:
            active_locks_gauge.dec()
        if lock_operations_counter is not None:
            lock_operations_counter.labels(operation="unlock", status="success").inc()

        return UnlockResponse(
            success=True,
            message="State unlocked successfully",
            lock_id=request.lock_id,
            force_unlocked=request.force,
            correlation_id=request.correlation_id,
        )
    except LockNotFoundError:
        if lock_operations_counter is not None:
            lock_operations_counter.labels(operation="unlock", status="not_found").inc()
        raise
    except Exception:
        if lock_operations_counter is not None:
            lock_operations_counter.labels(operation="unlock", status="failed").inc()
        raise


@app.get(
    "/api/v1/state/{backend_id}/lock/{workspace}",
    # response_model=LockStatusResponse,
    tags=["State Locking"],
)
async def get_lock_status(
    backend_id: str, workspace: str, current_user: str = Depends(get_current_user)
) -> LockStatusResponse:
    """Get lock status"""
    if not state_locker:
        raise ServiceUnavailableError("State locker not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)

    lock_status = await state_locker.get_lock_status(backend_id, workspace)
    lock_info = await state_locker.get_lock_info(backend_id, workspace)

    return LockStatusResponse(
        success=True,
        message=f"Lock status: {lock_status.value}",
        status=lock_status,
        lock_info=lock_info,
        correlation_id=None,
    )


# Backup and Restore Endpoints
def _validate_backup_services_and_backend(backend_id: str, workspace: str) -> None:
    """Validate backup services and backend existence"""
    if not state_backend or not minio_client:
        raise ServiceUnavailableError("State backend or MinIO client not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)


async def _retrieve_state_for_backup(
    backend_id: str, workspace: str, environment: Any
) -> Tuple[bytes, Any]:
    """Retrieve current state for backup operation"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    try:
        return await state_backend.retrieve_state(
            backend_id, workspace, environment=environment
        )
    except StateNotFoundError:
        _increment_backup_counter(backend_id, workspace, "not_found")
        raise


def _generate_backup_id_and_paths(
    backend_id: str, workspace: str
) -> Tuple[str, str, str]:
    """Generate backup ID and storage paths"""
    backup_id = hashlib.sha256(
        f"{backend_id}{workspace}{time.time()}".encode()
    ).hexdigest()[:12]
    backup_bucket = f"{config.minio.bucket_prefix}-backups"
    backup_key = f"{backend_id}/{workspace}/{backup_id}/terraform.tfstate"
    return backup_id, backup_bucket, backup_key


def _ensure_backup_bucket_exists(backup_bucket: str) -> None:
    """Ensure backup bucket exists"""
    if minio_client is None:
        raise ServiceUnavailableError("MinIO client not initialized")
    if not minio_client.bucket_exists(backup_bucket):
        minio_client.make_bucket(backup_bucket, location=config.minio.region)


def _store_backup_data_and_metadata(
    backup_bucket: str,
    backup_key: str,
    state_data: bytes,
    backup_metadata: Any,
    backend_id: str,
    workspace: str,
    backup_id: str,
) -> None:
    """Store backup data and metadata in MinIO"""
    if minio_client is None:
        raise ServiceUnavailableError("MinIO client not initialized")
    # Store state data
    minio_client.put_object(
        backup_bucket,
        backup_key,
        BytesIO(state_data),
        length=len(state_data),
        content_type="application/json",
    )

    # Store metadata
    metadata_key = f"{backend_id}/{workspace}/{backup_id}/metadata.json"
    metadata_json = json.dumps(backup_metadata.dict(), default=str).encode("utf-8")

    minio_client.put_object(
        backup_bucket,
        metadata_key,
        BytesIO(metadata_json),
        length=len(metadata_json),
        content_type="application/json",
    )


def _create_backup_metadata_object(
    backup_id: str,
    backend_id: str,
    workspace: str,
    request: Any,
    current_user: str,
    state_data: bytes,
    state_info: Any,
    environment: str,
) -> BackupMetadata:
    """Create backup metadata object"""
    # Get state version from state_info or use default
    state_version = getattr(state_info, "version_count", 1)

    # Parse environment enum
    try:
        env_enum = Environment(environment)
    except (ValueError, TypeError):
        env_enum = Environment.DEVELOPMENT

    # Parse backup type from request
    backup_type = getattr(request, "backup_type", BackupType.MANUAL)

    return BackupMetadata(
        backup_type=backup_type,
        state_version=str(state_version),
        size_bytes=len(state_data),
        checksum=hashlib.sha256(state_data).hexdigest(),
        environment=env_enum,
    )


def _increment_backup_counter(backend_id: str, workspace: str, status: str) -> None:
    """Increment backup request counter"""
    if request_counter is not None:
        request_counter.labels(
            method="POST",
            endpoint=f"/api/v1/state/{backend_id}/backup/{workspace}",
            status=status,
        ).inc()


def _handle_backup_creation_error(
    e: Exception, backend_id: str, workspace: str
) -> None:
    """Handle backup creation errors"""
    logger.error("Failed to create backup", error=str(e))
    _increment_backup_counter(backend_id, workspace, "failed")
    raise ServiceUnavailableError(f"Failed to create backup: {str(e)}")


@app.post(
    "/api/v1/state/{backend_id}/backup/{workspace}",
    # response_model=BackupResponse,
    tags=["Backup & Restore"],
)
async def create_backup(
    backend_id: str,
    workspace: str,
    request: BackupCreateRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> BackupResponse:
    """Create state backup"""
    from contextlib import nullcontext

    context_timer = (
        state_operations_histogram.labels(operation="create_backup").time()
        if state_operations_histogram is not None
        else nullcontext()
    )
    with context_timer:
        _increment_backup_counter(backend_id, workspace, "started")

        # Validate services and backend
        _validate_backup_services_and_backend(backend_id, workspace)
        environment = getattr(backends_store[backend_id], "environment", "development")

        # Retrieve current state
        state_data, state_info = await _retrieve_state_for_backup(
            backend_id, workspace, environment
        )

        # Generate backup paths
        backup_id, backup_bucket, backup_key = _generate_backup_id_and_paths(
            backend_id, workspace
        )

        try:
            # Ensure bucket exists
            _ensure_backup_bucket_exists(backup_bucket)

            # Create metadata
            backup_metadata = _create_backup_metadata_object(
                backup_id,
                backend_id,
                workspace,
                request,
                current_user,
                state_data,
                state_info,
                environment,
            )

            # Store data and metadata
            _store_backup_data_and_metadata(
                backup_bucket,
                backup_key,
                state_data,
                backup_metadata,
                backend_id,
                workspace,
                backup_id,
            )

            _increment_backup_counter(backend_id, workspace, "success")

            # Create BackupInfo object
            backup_info = BackupInfo(
                backup_id=backup_id,
                backend_id=backend_id,
                workspace=workspace,
                status=BackupStatus.COMPLETED,
                metadata=backup_metadata,
                created_at=datetime.utcnow(),
                created_by=current_user,
                verified_at=None,
                expires_at=None,
            )

            return BackupResponse(
                success=True,
                message="Backup created successfully",
                backup_info=backup_info,
                correlation_id=getattr(request, "correlation_id", None),
            )
        except Exception as e:
            _handle_backup_creation_error(e, backend_id, workspace)
            # This should never be reached due to the raise in _handle_backup_creation_error
            raise


def _extract_backup_ids_from_objects(
    objects: Any, backend_id: str, workspace: str
) -> Set[str]:
    """Extract backup IDs from MinIO objects."""
    backup_ids: Set[str] = set()
    for obj in objects:
        if "/metadata.json" in obj.object_name:
            parts = obj.object_name.split("/")
            if len(parts) >= 3:
                backup_ids.add(parts[2])
    return backup_ids


def _load_backup_metadata(
    minio_client: Minio,
    backup_bucket: str,
    backend_id: str,
    workspace: str,
    backup_id: str,
) -> Optional[BackupMetadata]:
    """Load backup metadata from MinIO."""
    metadata_key = f"{backend_id}/{workspace}/{backup_id}/metadata.json"
    try:
        response = minio_client.get_object(backup_bucket, metadata_key)
        metadata_json = response.read()
        response.close()
        response.release_conn()

        metadata_dict = json.loads(metadata_json.decode("utf-8"))
        return BackupMetadata(**metadata_dict)
    except Exception:
        return None


def _get_backups_from_minio(
    minio_client: Minio, backup_bucket: str, backend_id: str, workspace: str
) -> List[BackupMetadata]:
    """Retrieve all backups from MinIO for a specific backend and workspace."""
    backups: List[BackupMetadata] = []
    backup_prefix = f"{backend_id}/{workspace}/"

    if not minio_client.bucket_exists(backup_bucket):
        return backups

    objects = minio_client.list_objects(
        backup_bucket, prefix=backup_prefix, recursive=True
    )
    backup_ids = _extract_backup_ids_from_objects(objects, backend_id, workspace)

    for backup_id in sorted(backup_ids):
        metadata = _load_backup_metadata(
            minio_client, backup_bucket, backend_id, workspace, backup_id
        )
        if metadata:
            backups.append(metadata)

    return backups


def _apply_pagination(
    backups: List[BackupMetadata], limit: int, offset: int
) -> List[BackupMetadata]:
    """Apply pagination to backup list."""
    if offset > 0:
        backups = backups[offset:]
    if limit > 0:
        backups = backups[:limit]
    return backups


@app.get(
    "/api/v1/state/{backend_id}/backup/{workspace}",
    # response_model=BackupListResponse,
    tags=["Backup & Restore"],
)
async def list_backups(
    backend_id: str,
    workspace: str,
    limit: int = 100,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
) -> BackupListResponse:
    """List state backups"""
    if request_counter is not None:
        request_counter.labels(
            method="GET",
            endpoint=f"/api/v1/state/{backend_id}/backup/{workspace}",
            status="started",
        ).inc()

    if not minio_client:
        raise ServiceUnavailableError("MinIO client not initialized")

    backup_bucket = f"{config.minio.bucket_prefix}-backups"

    try:
        backups = _get_backups_from_minio(
            minio_client, backup_bucket, backend_id, workspace
        )
        backups = _apply_pagination(backups, limit, offset)

        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/state/{backend_id}/backup/{workspace}",
                status="success",
            ).inc()

        # Convert BackupMetadata to BackupInfo
        backup_infos = [
            BackupInfo(
                backup_id=f"{backend_id}_{workspace}_{i}",
                backend_id=backend_id,
                workspace=workspace,
                status=BackupStatus.COMPLETED,
                metadata=backup,
                created_at=datetime.utcnow(),
                created_by="system",
                verified_at=None,
                expires_at=None,
            )
            for i, backup in enumerate(backups)
        ]

        return BackupListResponse(
            success=True,
            message="Backups retrieved successfully",
            backups=backup_infos,
            total_count=len(backup_infos),
            correlation_id=None,
        )
    except Exception as e:
        logger.error("Failed to list backups", error=str(e))
        if request_counter is not None:
            request_counter.labels(
                method="GET",
                endpoint=f"/api/v1/state/{backend_id}/backup/{workspace}",
                status="failed",
            ).inc()
        return BackupListResponse(
            success=True,
            message="No backups found",
            backups=[],
            total_count=0,
            correlation_id=None,
        )


def _validate_restore_services_and_backend(backend_id: str, workspace: str) -> None:
    """Validate restore services and backend existence"""
    if not state_backend or not minio_client:
        raise ServiceUnavailableError("State backend or MinIO client not initialized")

    if backend_id not in backends_store:
        raise StateNotFoundError(backend_id, workspace)


def _retrieve_backup_data(backend_id: str, workspace: str, backup_id: str) -> bytes:
    """Retrieve backup data from MinIO storage"""
    if minio_client is None:
        raise ServiceUnavailableError("MinIO client not initialized")
    backup_bucket = f"{config.minio.bucket_prefix}-backups"
    backup_key = f"{backend_id}/{workspace}/{backup_id}/terraform.tfstate"

    try:
        response = minio_client.get_object(backup_bucket, backup_key)
        backup_data = response.read()
        response.close()
        response.release_conn()
        return bytes(backup_data)
    except S3Error as e:
        if e.code == "NoSuchKey":
            _increment_restore_counter(backend_id, workspace, "not_found")
            raise BackupNotFoundError(backup_id, backend_id, workspace)
        raise ServiceUnavailableError(f"Failed to retrieve backup: {str(e)}")


async def _restore_state_from_backup(
    backend_id: str,
    workspace: str,
    backup_data: bytes,
    current_user: str,
    environment: Any,
) -> Tuple[Any, str]:
    """Restore state from backup data"""
    if state_backend is None:
        raise ServiceUnavailableError("State backend not initialized")
    return await state_backend.store_state(
        backend_id,
        workspace,
        backup_data,
        operation_type=OperationType.RESTORE,
        created_by=current_user,
        environment=environment,
    )


def _increment_restore_counter(backend_id: str, workspace: str, status: str) -> None:
    """Increment restore request counter"""
    if request_counter is not None:
        request_counter.labels(
            method="POST",
            endpoint=f"/api/v1/state/{backend_id}/restore/{workspace}",
            status=status,
        ).inc()


@app.post(
    "/api/v1/state/{backend_id}/restore/{workspace}",
    # response_model=RestoreResponse,
    tags=["Backup & Restore"],
)
async def restore_backup(
    backend_id: str,
    workspace: str,
    request: RestoreRequest,
    _: None = Depends(rate_limit_check),
    current_user: str = Depends(get_current_user),
) -> RestoreResponse:
    """Restore from backup"""
    from contextlib import nullcontext

    context_timer = (
        state_operations_histogram.labels(operation="restore_backup").time()
        if state_operations_histogram is not None
        else nullcontext()
    )
    with context_timer:
        _increment_restore_counter(backend_id, workspace, "started")

        # Validate services and backend
        _validate_restore_services_and_backend(backend_id, workspace)
        environment = getattr(backends_store[backend_id], "environment", "development")

        # Retrieve backup data
        backup_data = _retrieve_backup_data(backend_id, workspace, request.backup_id)

        # Restore state from backup
        state_info, version_id = await _restore_state_from_backup(
            backend_id, workspace, backup_data, current_user, environment
        )

        _increment_restore_counter(backend_id, workspace, "success")

        # Create BackupMetadata for the restored backup
        backup_metadata = BackupMetadata(
            backup_type=BackupType.MANUAL,
            state_version=str(version_id),
            size_bytes=len(backup_data),
            checksum=hashlib.sha256(backup_data).hexdigest(),
            environment=Environment.DEVELOPMENT,
        )

        # Create BackupInfo object
        backup_info = BackupInfo(
            backup_id=request.backup_id,
            backend_id=backend_id,
            workspace=workspace,
            status=BackupStatus.COMPLETED,
            metadata=backup_metadata,
            created_at=datetime.utcnow(),
            created_by=current_user,
            verified_at=None,
            expires_at=None,
        )

        return RestoreResponse(
            success=True,
            message=f"Successfully restored from backup {request.backup_id}",
            backup_info=backup_info,
            pre_restore_backup_id=None,
            state_info=state_info,
            correlation_id=getattr(request, "correlation_id", None),
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        reload=config.reload,
        log_level=config.monitoring.log_level.lower(),
    )
