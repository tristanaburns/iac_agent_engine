"""
Pydantic models for Terraform Executor API
Enhanced data models for comprehensive IaC automation
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class TerraformOperationType(str, Enum):
    """Terraform operation types"""

    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    IMPORT = "import"
    REFRESH = "refresh"
    VALIDATE = "validate"
    INIT = "init"


class JobStatus(str, Enum):
    """Job execution status"""

    SUBMITTED = "submitted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class WorkspaceStatus(str, Enum):
    """Workspace status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    ERROR = "error"


class GitCredentialType(str, Enum):
    """Git credential types"""

    TOKEN = "token"  # nosec B105
    SSH_KEY = "ssh_key"  # nosec B105
    USERNAME_PASSWORD = "username_password"  # nosec B105


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
    correlation_id: Optional[str] = Field(
        default=None, description="Request correlation ID"
    )


# Git Integration Models
class GitCredentials(BaseModel):
    """Git repository credentials"""

    credential_type: GitCredentialType = Field(..., description="Credential type")
    username: Optional[str] = Field(None, description="Git username")
    password: Optional[str] = Field(None, description="Git password or token")
    ssh_key: Optional[str] = Field(None, description="SSH private key")
    ssh_passphrase: Optional[str] = Field(None, description="SSH key passphrase")


class GitRepository(BaseModel):
    """Git repository configuration"""

    url: HttpUrl = Field(..., description="Git repository URL")
    branch: str = Field(default="main", description="Git branch to use")
    path: Optional[str] = Field(None, description="Path within repository")
    credentials: Optional[GitCredentials] = Field(
        None, description="Repository credentials"
    )


# Terraform Variable Models
class TerraformVariable(BaseModel):
    """Terraform variable definition"""

    name: str = Field(..., description="Variable name")
    value: Union[str, int, float, bool, Dict[str, Any], List[Any]] = Field(
        ..., description="Variable value"
    )
    type: Optional[str] = Field(None, description="Variable type")
    description: Optional[str] = Field(None, description="Variable description")
    sensitive: bool = Field(default=False, description="Whether variable is sensitive")


# Workspace Models
class WorkspaceCreateRequest(BaseRequest):
    """Request to create a new workspace"""

    name: str = Field(..., description="Workspace name", pattern=r"^[a-zA-Z0-9_-]+$")
    description: Optional[str] = Field(None, description="Workspace description")
    git_repository: Optional[GitRepository] = Field(
        None, description="Git repository configuration"
    )
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Terraform variables"
    )
    auto_apply: bool = Field(default=False, description="Enable auto-apply for plans")


class WorkspaceUpdateRequest(BaseRequest):
    """Request to update an existing workspace"""

    description: Optional[str] = Field(None, description="Workspace description")
    git_repository: Optional[GitRepository] = Field(
        None, description="Git repository configuration"
    )
    variables: Optional[List[TerraformVariable]] = Field(
        None, description="Terraform variables"
    )
    auto_apply: Optional[bool] = Field(None, description="Enable auto-apply for plans")


class WorkspaceResponse(BaseResponse):
    """Workspace information response"""

    workspace: "WorkspaceInfo" = Field(..., description="Workspace information")


class WorkspaceInfo(BaseModel):
    """Workspace information"""

    id: UUID = Field(..., description="Workspace ID")
    name: str = Field(..., description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    status: WorkspaceStatus = Field(..., description="Workspace status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    locked_by: Optional[str] = Field(
        default=None, description="User who locked the workspace"
    )
    locked_at: Optional[datetime] = Field(default=None, description="Lock timestamp")
    git_repository: Optional[GitRepository] = Field(
        default=None, description="Git repository configuration"
    )
    variables_count: int = Field(..., description="Number of variables")
    last_job_id: Optional[UUID] = Field(default=None, description="Last job ID")
    last_job_status: Optional[JobStatus] = Field(
        default=None, description="Last job status"
    )


class WorkspaceListResponse(BaseResponse):
    """List of workspaces response"""

    workspaces: List[WorkspaceInfo] = Field(..., description="List of workspaces")
    total: int = Field(..., description="Total workspace count")


# Terraform Operation Models
class TerraformPlanRequest(BaseRequest):
    """Request to execute terraform plan"""

    workspace_name: str = Field(..., description="Workspace name")
    destroy: bool = Field(default=False, description="Plan for destroy operation")
    target_resources: List[str] = Field(
        default_factory=list, description="Target specific resources"
    )
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Additional variables"
    )
    refresh: bool = Field(default=True, description="Refresh state before planning")


class TerraformApplyRequest(BaseRequest):
    """Request to execute terraform apply"""

    workspace_name: str = Field(..., description="Workspace name")
    plan_id: Optional[UUID] = Field(
        None, description="Plan ID to apply (if None, applies latest plan)"
    )
    auto_approve: bool = Field(default=False, description="Auto-approve the apply")
    target_resources: List[str] = Field(
        default_factory=list, description="Target specific resources"
    )
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Additional variables"
    )


class TerraformDestroyRequest(BaseRequest):
    """Request to execute terraform destroy"""

    workspace_name: str = Field(..., description="Workspace name")
    target_resources: List[str] = Field(
        default_factory=list, description="Target specific resources"
    )
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Additional variables"
    )
    auto_approve: bool = Field(default=False, description="Auto-approve the destroy")


class TerraformImportRequest(BaseRequest):
    """Request to import existing infrastructure"""

    workspace_name: str = Field(..., description="Workspace name")
    address: str = Field(..., description="Terraform resource address")
    id: str = Field(..., description="Resource ID to import")
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Additional variables"
    )


class TerraformRefreshRequest(BaseRequest):
    """Request to refresh terraform state"""

    workspace_name: str = Field(..., description="Workspace name")
    variables: List[TerraformVariable] = Field(
        default_factory=list, description="Additional variables"
    )


class TerraformValidateRequest(BaseRequest):
    """Request to validate terraform configuration"""

    workspace_name: str = Field(..., description="Workspace name")


# Job Models
class JobResponse(BaseResponse):
    """Job submission response"""

    job: "JobInfo" = Field(..., description="Job information")


class JobInfo(BaseModel):
    """Job execution information"""

    id: UUID = Field(..., description="Job ID")
    operation: TerraformOperationType = Field(
        ..., description="Terraform operation type"
    )
    workspace_name: str = Field(..., description="Workspace name")
    status: JobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(
        default=None, description="Job start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Job completion timestamp"
    )
    duration_seconds: Optional[float] = Field(
        default=None, description="Job duration in seconds"
    )
    progress: int = Field(
        default=0, description="Job progress percentage", ge=0, le=100
    )
    logs: List[str] = Field(default_factory=list, description="Job execution logs")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Job execution result"
    )


class JobStatusResponse(BaseResponse):
    """Job status response"""

    job: JobInfo = Field(..., description="Job information")


class JobListResponse(BaseResponse):
    """Job list response"""

    jobs: List[JobInfo] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total job count")


# State Management Models
class StateInfo(BaseModel):
    """Terraform state information"""

    version: int = Field(..., description="State file version")
    terraform_version: str = Field(..., description="Terraform version")
    serial: int = Field(..., description="State serial number")
    lineage: str = Field(..., description="State lineage")
    resources_count: int = Field(..., description="Number of resources in state")
    outputs: Dict[str, Any] = Field(
        default_factory=dict, description="Terraform outputs"
    )
    last_modified: datetime = Field(..., description="Last modification timestamp")
    size_bytes: int = Field(..., description="State file size in bytes")


class StateResponse(BaseResponse):
    """State information response"""

    state: StateInfo = Field(..., description="State information")


class StateLockRequest(BaseRequest):
    """Request to lock state"""

    workspace_name: str = Field(..., description="Workspace name")
    operation: TerraformOperationType = Field(
        ..., description="Operation requesting the lock"
    )
    info: Optional[str] = Field(None, description="Lock information")


class StateLockResponse(BaseResponse):
    """State lock response"""

    lock_id: str = Field(..., description="Lock ID")
    locked_by: str = Field(..., description="User who acquired the lock")
    locked_at: datetime = Field(..., description="Lock timestamp")


# Health and Monitoring Models
class HealthResponse(BaseResponse):
    """Health check response"""

    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    terraform_version: str = Field(..., description="Terraform version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    active_jobs: int = Field(..., description="Number of active jobs")
    total_workspaces: int = Field(..., description="Total workspace count")
    system_info: Dict[str, Any] = Field(
        default_factory=dict, description="System information"
    )


# Error Models
class ErrorResponse(BaseResponse):
    """Error response model"""

    error_code: str = Field(..., description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace for debugging"
    )


# Update forward references
WorkspaceResponse.model_rebuild()
JobResponse.model_rebuild()
