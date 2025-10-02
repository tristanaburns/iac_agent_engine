"""
State Management Service Configuration
Production-ready configuration management with environment variable support
"""

import os
import socket
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class RedisConfig(BaseModel):
    """Redis configuration for distributed locking"""

    host: str = Field(default="redis", description="Redis host")
    port: int = Field(default=6379, description="Redis port", ge=1, le=65535)
    database: int = Field(default=0, description="Redis database number", ge=0, le=15)
    password: Optional[str] = Field(None, description="Redis password")
    ssl: bool = Field(default=False, description="Use SSL connection")
    ssl_cert_reqs: str = Field(
        default="required", description="SSL certificate requirements"
    )
    socket_keepalive: bool = Field(default=False, description="Enable socket keepalive")
    socket_keepalive_options: Optional[Dict[int, int]] = Field(
        default=None,
        description="Socket keepalive options (automatically configured based on OS)",
    )

    @classmethod
    def _get_linux_keepalive_options(cls) -> Dict[int, int]:
        """Get Linux-specific keepalive options."""
        options = {}
        if hasattr(socket, "TCP_KEEPIDLE"):
            options[socket.TCP_KEEPIDLE] = 60  # Start probes after 60s
        if hasattr(socket, "TCP_KEEPINTVL"):
            options[socket.TCP_KEEPINTVL] = 10  # Probe every 10s
        if hasattr(socket, "TCP_KEEPCNT"):
            options[socket.TCP_KEEPCNT] = 6  # Drop after 6 failed probes
        return options

    @classmethod
    def _get_macos_keepalive_options(cls) -> Dict[int, int]:
        """Get macOS-specific keepalive options."""
        options = {}
        if hasattr(socket, "TCP_KEEPALIVE"):
            options[socket.TCP_KEEPALIVE] = 60  # macOS equivalent of TCP_KEEPIDLE
        return options

    @classmethod
    def _validate_explicit_options(
        cls, v: Optional[Dict[int, int]]
    ) -> Optional[Dict[int, int]]:
        """Validate explicitly provided keepalive options."""
        if v is not None and all(isinstance(k, int) for k in v.keys()):
            return v
        return None

    @classmethod
    def _build_platform_options(cls) -> Optional[Dict[int, int]]:
        """Build platform-specific keepalive options."""
        try:
            keepalive_options = {}
            keepalive_options.update(cls._get_linux_keepalive_options())
            keepalive_options.update(cls._get_macos_keepalive_options())
            return keepalive_options if keepalive_options else None
        except (AttributeError, TypeError):
            return {}

    @validator("socket_keepalive_options", pre=True, always=True)
    def build_keepalive_options(
        cls, v: Optional[Dict[int, int]], values: Dict[str, Any]
    ) -> Optional[Dict[int, int]]:
        """Build socket keepalive options based on OS and socket availability."""
        # Return None if keepalive is disabled
        if not values.get("socket_keepalive", False):
            return None

        # Use explicitly provided options if valid
        explicit_options = cls._validate_explicit_options(v)
        if explicit_options is not None:
            return explicit_options

        # Build platform-specific options
        return cls._build_platform_options()


class MinIOConfig(BaseModel):
    """MinIO S3-compatible configuration"""

    endpoint: str = Field(default="minio:9000", description="MinIO endpoint")
    access_key: str = Field(..., description="MinIO access key")
    secret_key: str = Field(..., description="MinIO secret key")
    region: str = Field(default="us-east-1", description="MinIO region")
    use_tls: bool = Field(default=False, description="Use TLS connection")
    bucket_prefix: str = Field(
        default="terraform-state", description="Bucket prefix for state storage"
    )
    versioning_enabled: bool = Field(
        default=True, description="Enable bucket versioning"
    )
    encryption_enabled: bool = Field(
        default=True, description="Enable server-side encryption"
    )


class VaultConfig(BaseModel):
    """HashiCorp Vault configuration"""

    url: HttpUrl = Field(..., description="Vault server URL")
    token: Optional[str] = Field(None, description="Vault authentication token")
    role_id: Optional[str] = Field(None, description="AppRole role ID")
    secret_id: Optional[str] = Field(None, description="AppRole secret ID")
    transit_engine_path: str = Field(
        default="transit", description="Transit engine path"
    )
    key_name: str = Field(default="terraform-state", description="Encryption key name")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    timeout: int = Field(
        default=30, description="Request timeout in seconds", ge=5, le=300
    )


class SecurityConfig(BaseModel):
    """Security configuration"""

    require_authentication: bool = Field(
        default=True, description="Require API authentication"
    )
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    allowed_origins: List[str] = Field(
        default_factory=list, description="CORS allowed origins"
    )
    max_request_size: int = Field(
        default=100 * 1024 * 1024, description="Maximum request size in bytes"
    )
    rate_limit_per_minute: int = Field(
        default=1000, description="Rate limit per minute per client"
    )


class BackupConfig(BaseModel):
    """Backup configuration"""

    default_retention_days: int = Field(
        default=30, description="Default backup retention in days", ge=1, le=365
    )
    max_backups_per_workspace: int = Field(
        default=100, description="Maximum backups per workspace", ge=1, le=1000
    )
    verify_backups: bool = Field(
        default=True, description="Verify backup integrity after creation"
    )
    backup_compression: bool = Field(
        default=True, description="Enable backup compression"
    )
    scheduled_backup_enabled: bool = Field(
        default=True, description="Enable scheduled backups"
    )


class StateConfig(BaseModel):
    """State management configuration"""

    max_state_size: int = Field(
        default=500 * 1024 * 1024, description="Maximum state size in bytes"
    )
    max_versions_per_workspace: int = Field(
        default=100, description="Maximum versions per workspace", ge=1, le=1000
    )
    version_cleanup_enabled: bool = Field(
        default=True, description="Enable automatic version cleanup"
    )
    lock_timeout_seconds: int = Field(
        default=1800, description="Default lock timeout in seconds", ge=60, le=7200
    )
    state_validation_enabled: bool = Field(
        default=True, description="Enable state validation"
    )


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration"""

    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    health_check_enabled: bool = Field(default=True, description="Enable health checks")
    audit_logging_enabled: bool = Field(
        default=True, description="Enable audit logging"
    )
    performance_tracking_enabled: bool = Field(
        default=True, description="Enable performance tracking"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    structured_logging: bool = Field(
        default=True, description="Enable structured logging"
    )


class ServiceConfig(BaseModel):
    """Main service configuration"""

    service_name: str = Field(default="iac-agent", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")
    host: str = Field(
        default="0.0.0.0",  # nosec B104 - Container service requires binding to all interfaces
        description="Service host",
    )
    port: int = Field(default=8003, description="Service port", ge=1, le=65535)
    workers: int = Field(
        default=1, description="Number of worker processes", ge=1, le=32
    )
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on changes")

    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(password=None),
        description="Redis configuration",
    )
    minio: MinIOConfig = Field(..., description="MinIO configuration")
    vault: VaultConfig = Field(..., description="Vault configuration")
    security: SecurityConfig = Field(
        default_factory=SecurityConfig, description="Security configuration"
    )
    backup: BackupConfig = Field(
        default_factory=BackupConfig, description="Backup configuration"
    )
    state: StateConfig = Field(
        default_factory=StateConfig, description="State configuration"
    )
    monitoring: MonitoringConfig = Field(
        default_factory=MonitoringConfig, description="Monitoring configuration"
    )

    @validator("minio", pre=True)
    def validate_minio_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MinIO configuration"""
        if isinstance(v, dict):
            # Load from environment variables if not provided
            if "access_key" not in v:
                v["access_key"] = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            if "secret_key" not in v:
                v["secret_key"] = os.getenv(
                    "MINIO_SECRET_KEY", "minioadmin_secure_password"
                )
        return v

    @validator("vault", pre=True)
    def validate_vault_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Vault configuration"""
        if isinstance(v, dict):
            # Load from environment variables if not provided
            if "url" not in v:
                v["url"] = os.getenv("VAULT_ADDR", "http://vault:8200")
            if "token" not in v and not v.get("role_id"):
                v["token"] = os.getenv("VAULT_TOKEN")
        return v


def load_config() -> ServiceConfig:
    """Load configuration from environment variables"""

    # Redis configuration
    redis_config = RedisConfig(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        database=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
        socket_keepalive=os.getenv("REDIS_SOCKET_KEEPALIVE", "true").lower() == "true",
        # socket_keepalive_options will be automatically configured by the validator
    )

    # MinIO configuration
    minio_config = MinIOConfig(
        endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin_secure_password"),
        region=os.getenv("MINIO_REGION", "us-east-1"),
        use_tls=os.getenv("MINIO_USE_TLS", "false").lower() == "true",
        bucket_prefix=os.getenv("MINIO_BUCKET_PREFIX", "terraform-state"),
    )

    # Vault configuration
    vault_config = VaultConfig(
        url=HttpUrl(os.getenv("VAULT_ADDR", "http://vault:8200")),
        token=os.getenv("VAULT_TOKEN"),
        role_id=os.getenv("VAULT_ROLE_ID"),
        secret_id=os.getenv("VAULT_SECRET_ID"),
        transit_engine_path=os.getenv("VAULT_TRANSIT_PATH", "transit"),
        key_name=os.getenv("VAULT_KEY_NAME", "terraform-state"),
        verify_ssl=os.getenv("VAULT_VERIFY_SSL", "true").lower() == "true",
    )

    # Security configuration
    security_config = SecurityConfig(
        require_authentication=os.getenv("REQUIRE_AUTH", "true").lower() == "true",
        api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
        allowed_origins=(
            os.getenv("ALLOWED_ORIGINS", "").split(",")
            if os.getenv("ALLOWED_ORIGINS")
            else []
        ),
        max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(100 * 1024 * 1024))),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT", "1000")),
    )

    # Backup configuration
    backup_config = BackupConfig(
        default_retention_days=int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
        max_backups_per_workspace=int(os.getenv("MAX_BACKUPS", "100")),
        verify_backups=os.getenv("VERIFY_BACKUPS", "true").lower() == "true",
        backup_compression=os.getenv("BACKUP_COMPRESSION", "true").lower() == "true",
        scheduled_backup_enabled=os.getenv("SCHEDULED_BACKUP", "true").lower()
        == "true",
    )

    # State configuration
    state_config = StateConfig(
        max_state_size=int(os.getenv("MAX_STATE_SIZE", str(500 * 1024 * 1024))),
        max_versions_per_workspace=int(os.getenv("MAX_VERSIONS", "100")),
        version_cleanup_enabled=os.getenv("VERSION_CLEANUP", "true").lower() == "true",
        lock_timeout_seconds=int(os.getenv("LOCK_TIMEOUT", "1800")),
        state_validation_enabled=os.getenv("STATE_VALIDATION", "true").lower()
        == "true",
    )

    # Monitoring configuration
    monitoring_config = MonitoringConfig(
        metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
        health_check_enabled=os.getenv("HEALTH_CHECK_ENABLED", "true").lower()
        == "true",
        audit_logging_enabled=os.getenv("AUDIT_LOGGING", "true").lower() == "true",
        performance_tracking_enabled=os.getenv("PERFORMANCE_TRACKING", "true").lower()
        == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        structured_logging=os.getenv("STRUCTURED_LOGGING", "true").lower() == "true",
    )

    # Main service configuration
    return ServiceConfig(
        service_name=os.getenv("SERVICE_NAME", "iac-agent"),
        service_version=os.getenv("SERVICE_VERSION", "1.0.0"),
        host=os.getenv(
            "SERVICE_HOST", "0.0.0.0"
        ),  # nosec B104 - Container service requires binding to all interfaces
        port=int(os.getenv("SERVICE_PORT", "8003")),
        workers=int(os.getenv("WORKERS", "1")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        reload=os.getenv("RELOAD", "false").lower() == "true",
        redis=redis_config,
        minio=minio_config,
        vault=vault_config,
        security=security_config,
        backup=backup_config,
        state=state_config,
        monitoring=monitoring_config,
    )


# Global configuration instance
config = load_config()
