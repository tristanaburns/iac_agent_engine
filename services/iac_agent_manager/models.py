"""
State Management Service Data Models
Comprehensive Pydantic models for Terraform state management with MinIO backend
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BackendType(str, Enum):
    """State backend types"""

    S3 = "s3"
    MINIO = "minio"
    LOCAL = "local"
    REMOTE = "remote"


class StateStatus(str, Enum):
    """State status enumeration"""

    ACTIVE = "active"
    LOCKED = "locked"
    CORRUPTED = "corrupted"
    MIGRATING = "migrating"
    ARCHIVED = "archived"


class LockStatus(str, Enum):
    """Lock status enumeration"""

    UNLOCKED = "unlocked"
    LOCKED = "locked"
    FORCE_UNLOCKED = "force_unlocked"
    EXPIRED = "expired"


class BackupType(str, Enum):
    """Backup type enumeration"""

    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PRE_OPERATION = "pre_operation"
    DISASTER_RECOVERY = "disaster_recovery"


class BackupStatus(str, Enum):
    """Backup status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class Environment(str, Enum):
    """Environment enumeration"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class OperationType(str, Enum):
    """State operation types"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LOCK = "lock"
    UNLOCK = "unlock"
    BACKUP = "backup"
    RESTORE = "restore"
    MIGRATE = "migrate"


# Base models
class BaseRequest(BaseModel):
    """Base request model with common fields"""

    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    timeout: Optional[int] = Field(
        300, description="Operation timeout in seconds", ge=30, le=3600
    )


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")


# Backend Configuration Models
class S3Config(BaseModel):
    """S3/MinIO backend configuration"""

    endpoint: str = Field(..., description="S3 endpoint URL")
    access_key: str = Field(..., description="S3 access key")
    secret_key: str = Field(..., description="S3 secret key")
    bucket_prefix: str = Field(default="terraform-state", description="Bucket prefix")
    region: str = Field(default="us-east-1", description="S3 region")
    use_tls: bool = Field(default=True, description="Use TLS for connections")
    skip_ssl_verify: bool = Field(default=False, description="Skip SSL verification")


class BackendConfig(BaseModel):
    """State backend configuration"""

    backend_type: BackendType = Field(..., description="Backend type")
    name: str = Field(..., description="Backend name")
    description: Optional[str] = Field(None, description="Backend description")
    s3_config: Optional[S3Config] = Field(None, description="S3/MinIO configuration")
    encryption_enabled: bool = Field(default=True, description="Enable encryption")
    versioning_enabled: bool = Field(default=True, description="Enable versioning")
    max_versions: int = Field(
        default=100, description="Maximum versions to keep", ge=1, le=1000
    )


# Backend Management Models
class BackendCreateRequest(BaseRequest):
    """Request to create a new backend"""

    config: BackendConfig = Field(..., description="Backend configuration")


class BackendResponse(BaseResponse):
    """Backend configuration response"""

    backend_id: str = Field(..., description="Backend unique identifier")
    config: BackendConfig = Field(..., description="Backend configuration")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )


class BackendListResponse(BaseResponse):
    """List of backend configurations"""

    backends: List[BackendResponse] = Field(..., description="List of backends")
    total_count: int = Field(..., description="Total number of backends")


# State Models
class StateMetadata(BaseModel):
    """State metadata information"""

    version: str = Field(..., description="State format version")
    terraform_version: str = Field(..., description="Terraform version")
    serial: int = Field(..., description="State serial number")
    lineage: str = Field(..., description="State lineage")
    modules: List[Dict[str, Any]] = Field(
        default_factory=list, description="Module information"
    )
    resources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Resource information"
    )
    outputs: Dict[str, Any] = Field(default_factory=dict, description="State outputs")


class StateInfo(BaseModel):
    """State information"""

    backend_id: str = Field(..., description="Backend identifier")
    workspace: str = Field(..., description="Workspace name")
    status: StateStatus = Field(..., description="State status")
    size_bytes: int = Field(..., description="State size in bytes")
    checksum: str = Field(..., description="State checksum")
    encrypted: bool = Field(..., description="Whether state is encrypted")
    metadata: Optional[StateMetadata] = Field(None, description="State metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    version_count: int = Field(..., description="Number of versions")


class StateVersion(BaseModel):
    """State version information"""

    version_id: str = Field(..., description="Version unique identifier")
    version_number: int = Field(..., description="Version number")
    size_bytes: int = Field(..., description="Version size in bytes")
    checksum: str = Field(..., description="Version checksum")
    metadata: Optional[StateMetadata] = Field(None, description="Version metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="User who created this version")
    operation_type: OperationType = Field(
        ..., description="Operation that created this version"
    )


# State Operation Models
class StateUpdateRequest(BaseRequest):
    """Request to update state"""

    state_data: str = Field(..., description="Base64 encoded state data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    lock_id: str = Field(..., description="Lock ID for operation")


class StateResponse(BaseResponse):
    """State data response"""

    state_data: str = Field(..., description="Base64 encoded state data")
    state_info: StateInfo = Field(..., description="State information")


class StateUpdateResponse(BaseResponse):
    """State update response"""

    state_info: StateInfo = Field(..., description="Updated state information")
    version_id: str = Field(..., description="New version ID")


class StateVersionResponse(BaseResponse):
    """State version response"""

    state_data: str = Field(..., description="Base64 encoded state data")
    version_info: StateVersion = Field(..., description="Version information")


class VersionListResponse(BaseResponse):
    """List of state versions"""

    versions: List[StateVersion] = Field(..., description="List of state versions")
    total_count: int = Field(..., description="Total number of versions")


# Lock Models
class LockInfo(BaseModel):
    """State lock information"""

    id: str = Field(..., description="Lock ID")
    operation: str = Field(..., description="Operation type")
    info: str = Field(..., description="Lock info")
    who: str = Field(..., description="Who holds the lock")
    version: str = Field(..., description="Lock version")
    created: datetime = Field(
        default_factory=datetime.utcnow, description="Lock creation time"
    )
    path: str = Field(..., description="State path")


class LockRequest(BaseRequest):
    """Request to lock state"""

    lock_info: LockInfo = Field(..., description="Lock information")


class UnlockRequest(BaseRequest):
    """Request to unlock state"""

    lock_id: str = Field(..., description="Lock ID to release")
    force: bool = Field(default=False, description="Force unlock if true")


class LockResponse(BaseResponse):
    """Lock operation response"""

    lock_info: LockInfo = Field(..., description="Lock information")
    expires_at: datetime = Field(..., description="Lock expiration time")


class UnlockResponse(BaseResponse):
    """Unlock operation response"""

    lock_id: str = Field(..., description="Released lock ID")
    force_unlocked: bool = Field(..., description="Whether force unlock was used")


class LockStatusResponse(BaseResponse):
    """Lock status response"""

    status: LockStatus = Field(..., description="Current lock status")
    lock_info: Optional[LockInfo] = Field(
        None, description="Lock information if locked"
    )


# Backup Models
class BackupSchedule(BaseModel):
    """Backup schedule configuration"""

    enabled: bool = Field(default=True, description="Enable scheduled backups")
    cron_expression: str = Field(..., description="Cron expression for schedule")
    retention_days: int = Field(
        default=30, description="Backup retention in days", ge=1, le=365
    )
    max_backups: int = Field(
        default=100, description="Maximum backups to keep", ge=1, le=1000
    )


class BackupMetadata(BaseModel):
    """Backup metadata"""

    backup_type: BackupType = Field(..., description="Type of backup")
    state_version: str = Field(..., description="State version at backup time")
    size_bytes: int = Field(..., description="Backup size in bytes")
    checksum: str = Field(..., description="Backup checksum")
    environment: Environment = Field(..., description="Environment")


class BackupInfo(BaseModel):
    """Backup information"""

    backup_id: str = Field(..., description="Backup unique identifier")
    backend_id: str = Field(..., description="Backend identifier")
    workspace: str = Field(..., description="Workspace name")
    status: BackupStatus = Field(..., description="Backup status")
    metadata: BackupMetadata = Field(..., description="Backup metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="User who created backup")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class BackupCreateRequest(BaseRequest):
    """Request to create backup"""

    backup_type: BackupType = Field(..., description="Type of backup")
    description: Optional[str] = Field(None, description="Backup description")
    verify_integrity: bool = Field(default=True, description="Verify backup integrity")


class RestoreRequest(BaseRequest):
    """Request to restore from backup"""

    backup_id: str = Field(..., description="Backup ID to restore from")
    verify_before_restore: bool = Field(
        default=True, description="Verify backup before restore"
    )
    create_backup_before_restore: bool = Field(
        default=True, description="Create backup before restore"
    )


class BackupResponse(BaseResponse):
    """Backup operation response"""

    backup_info: BackupInfo = Field(..., description="Backup information")


class BackupListResponse(BaseResponse):
    """List of backups"""

    backups: List[BackupInfo] = Field(..., description="List of backups")
    total_count: int = Field(..., description="Total number of backups")


class RestoreResponse(BaseResponse):
    """Restore operation response"""

    backup_info: BackupInfo = Field(..., description="Restored backup information")
    pre_restore_backup_id: Optional[str] = Field(
        None, description="Pre-restore backup ID"
    )
    state_info: StateInfo = Field(..., description="Restored state information")


# Analytics Models
class StateStats(BaseModel):
    """State statistics"""

    total_size_bytes: int = Field(..., description="Total state size")
    resource_count: int = Field(..., description="Total number of resources")
    module_count: int = Field(..., description="Total number of modules")
    version_count: int = Field(..., description="Total number of versions")
    backup_count: int = Field(..., description="Total number of backups")
    last_modified: datetime = Field(..., description="Last modification time")
    change_frequency: float = Field(..., description="Changes per day")


class DriftDetection(BaseModel):
    """Drift detection result"""

    has_drift: bool = Field(..., description="Whether drift was detected")
    drift_count: int = Field(..., description="Number of drifted resources")
    drift_details: List[Dict[str, Any]] = Field(
        default_factory=list, description="Drift details"
    )
    checked_at: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp"
    )


# Health and Monitoring Models
class HealthStatus(str, Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Individual component health"""

    name: str = Field(..., description="Component name")
    status: HealthStatus = Field(..., description="Component health status")
    message: str = Field(..., description="Health message")
    response_time_ms: Optional[float] = Field(
        None, description="Response time in milliseconds"
    )
    last_check: datetime = Field(
        default_factory=datetime.utcnow, description="Last health check"
    )


class HealthResponse(BaseResponse):
    """Service health response"""

    overall_status: HealthStatus = Field(..., description="Overall health status")
    components: List[ComponentHealth] = Field(
        ..., description="Component health details"
    )
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="Service version")


# Error Models
class ErrorDetail(BaseModel):
    """Error detail information"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class ErrorResponse(BaseResponse):
    """Error response model"""

    error: ErrorDetail = Field(..., description="Error details")
    success: bool = Field(default=False, description="Always false for errors")


# Rollback Models
class RollbackResponse(BaseResponse):
    """Rollback operation response"""

    previous_version_id: str = Field(..., description="Previous version ID")
    rolled_back_to_version_id: str = Field(..., description="Version rolled back to")
    state_info: StateInfo = Field(..., description="State information after rollback")
    backup_created: Optional[str] = Field(
        None, description="Backup ID created before rollback"
    )


# Delete Models
class DeleteResponse(BaseResponse):
    """Delete operation response"""

    deleted_state_id: str = Field(..., description="ID of deleted state")
    backup_created: Optional[str] = Field(
        None, description="Backup ID created before deletion"
    )
    versions_deleted: int = Field(..., description="Number of versions deleted")
