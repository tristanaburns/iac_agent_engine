"""
Ansible Executor Service Data Models
Comprehensive Pydantic models for production-ready Ansible automation
"""

from datetime import datetime
from enum import Enum
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# ENUMS FOR TYPE SAFETY
# ============================================================================


class JobStatus(str, Enum):
    """Job execution status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskStatus(str, Enum):
    """Individual task status enumeration"""

    OK = "ok"
    CHANGED = "changed"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNREACHABLE = "unreachable"


class VerbosityLevel(int, Enum):
    """Ansible verbosity levels"""

    NORMAL = 0
    VERBOSE = 1
    MORE_VERBOSE = 2
    DEBUG = 3
    CONNECTION_DEBUG = 4


class InventoryType(str, Enum):
    """Inventory type enumeration"""

    STATIC = "static"
    DYNAMIC = "dynamic"
    SCRIPT = "script"
    PLUGIN = "plugin"


class VaultType(str, Enum):
    """Vault integration type"""

    ANSIBLE_VAULT = "ansible"
    HASHICORP_VAULT = "hashicorp"
    BOTH = "both"


class CollectionInstallSource(str, Enum):
    """Collection installation source"""

    GALAXY = "galaxy"
    GIT = "git"
    URL = "url"
    LOCAL = "local"


# ============================================================================
# BASE MODELS
# ============================================================================


class BaseAnsibleModel(BaseModel):
    """Base model with common fields"""

    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class JobBase(BaseAnsibleModel):
    """Base job model"""

    id: str = Field(..., description="Unique job identifier")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Job creation timestamp"
    )
    status: JobStatus = Field(
        default=JobStatus.PENDING, description="Current job status"
    )


# ============================================================================
# PLAYBOOK EXECUTION MODELS
# ============================================================================


class PlaybookExecutionRequest(BaseAnsibleModel):
    """Request model for playbook execution"""

    playbook_path: str = Field(..., description="Path to playbook file", min_length=1)
    inventory: Optional[str] = Field(
        None, description="Inventory source (file, script, or dynamic)"
    )
    limit: Optional[str] = Field(None, description="Limit execution to specific hosts")
    tags: Optional[List[str]] = Field(
        None, description="Run only tasks tagged with these values"
    )
    skip_tags: Optional[List[str]] = Field(
        None, description="Skip tasks tagged with these values"
    )
    extra_vars: Optional[Dict[str, Any]] = Field(
        None, description="Additional variables"
    )
    forks: Optional[int] = Field(
        5, description="Number of parallel processes", ge=1, le=50
    )
    verbosity: VerbosityLevel = Field(
        VerbosityLevel.NORMAL, description="Verbosity level"
    )
    check_mode: bool = Field(False, description="Run in check mode (dry run)")
    diff_mode: bool = Field(False, description="Show file differences")
    become: bool = Field(False, description="Enable privilege escalation")
    become_user: Optional[str] = Field(None, description="User to become")
    become_method: Optional[str] = Field(
        None, description="Privilege escalation method"
    )
    vault_password_file: Optional[str] = Field(None, description="Vault password file")
    vault_id: Optional[str] = Field(None, description="Vault ID for multiple vaults")
    timeout: Optional[int] = Field(
        300, description="Execution timeout in seconds", gt=0
    )
    git_repo: Optional[str] = Field(
        None, description="Git repository to clone playbook from"
    )
    git_branch: Optional[str] = Field("main", description="Git branch to use")
    git_credentials: Optional[Dict[str, str]] = Field(
        None, description="Git credentials"
    )

    @field_validator("playbook_path")
    @classmethod
    def validate_playbook_path(cls, v: str) -> str:
        if not v.endswith((".yml", ".yaml")):
            raise ValueError("Playbook path must end with .yml or .yaml")
        return v


class PlaybookExecutionResponse(JobBase):
    """Response model for playbook execution"""

    playbook_path: str
    inventory: Optional[str] = None
    total_tasks: Optional[int] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    changed_tasks: int = 0
    skipped_tasks: int = 0
    unreachable_hosts: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    output_url: Optional[str] = None
    artifacts: Optional[List[str]] = None


# ============================================================================
# AD-HOC COMMAND MODELS
# ============================================================================


class AdhocCommandRequest(BaseAnsibleModel):
    """Request model for ad-hoc command execution"""

    pattern: str = Field(..., description="Host pattern to target", min_length=1)
    module: str = Field(..., description="Ansible module to execute", min_length=1)
    args: Optional[str] = Field(None, description="Module arguments")
    inventory: Optional[str] = Field(None, description="Inventory source")
    forks: Optional[int] = Field(
        5, description="Number of parallel processes", ge=1, le=50
    )
    verbosity: VerbosityLevel = Field(
        VerbosityLevel.NORMAL, description="Verbosity level"
    )
    become: bool = Field(False, description="Enable privilege escalation")
    become_user: Optional[str] = Field(None, description="User to become")
    become_method: Optional[str] = Field(
        None, description="Privilege escalation method"
    )
    timeout: Optional[int] = Field(30, description="Module timeout in seconds", gt=0)
    extra_vars: Optional[Dict[str, Any]] = Field(
        None, description="Additional variables"
    )
    vault_password_file: Optional[str] = Field(None, description="Vault password file")

    @field_validator("module")
    @classmethod
    def validate_module_name(cls, v: str) -> str:
        # Basic validation for module names (alphanumeric, dots, underscores)
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_\.]*$", v):
            raise ValueError("Invalid module name format")
        return v


class AdhocCommandResponse(JobBase):
    """Response model for ad-hoc command execution"""

    pattern: str
    module: str
    args: Optional[str] = None
    total_hosts: Optional[int] = None
    successful_hosts: int = 0
    failed_hosts: int = 0
    unreachable_hosts: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    results: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# INVENTORY MANAGEMENT MODELS
# ============================================================================


class InventoryCreateRequest(BaseAnsibleModel):
    """Request model for inventory creation"""

    name: str = Field(..., description="Inventory name", min_length=1, max_length=100)
    inventory_type: InventoryType = Field(..., description="Type of inventory")
    content: Optional[str] = Field(None, description="Static inventory content")
    script_path: Optional[str] = Field(
        None, description="Dynamic inventory script path"
    )
    plugin_config: Optional[Dict[str, Any]] = Field(
        None, description="Inventory plugin configuration"
    )
    description: Optional[str] = Field(
        None, description="Inventory description", max_length=500
    )
    tags: Optional[List[str]] = Field(None, description="Inventory tags")

    @field_validator("name")
    @classmethod
    def validate_inventory_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError("Invalid inventory name format")
        return v


class InventoryResponse(BaseAnsibleModel):
    """Response model for inventory operations"""

    name: str
    inventory_type: InventoryType
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    host_count: int = 0
    group_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_refreshed: Optional[datetime] = None
    is_valid: bool = True
    validation_errors: Optional[List[str]] = None


class InventoryListResponse(BaseAnsibleModel):
    """Response model for inventory listing"""

    inventories: List[InventoryResponse]
    total_count: int
    page: int = 1
    per_page: int = 50


class HostInfo(BaseAnsibleModel):
    """Host information model"""

    name: str
    groups: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    connection_info: Optional[Dict[str, Any]] = None
    facts: Optional[Dict[str, Any]] = None
    last_seen: Optional[datetime] = None
    is_reachable: Optional[bool] = None


class HostListResponse(BaseAnsibleModel):
    """Response model for host listing"""

    hosts: List[HostInfo]
    total_count: int
    inventory_name: str
    groups: List[str] = Field(default_factory=list)


# ============================================================================
# VAULT MANAGEMENT MODELS
# ============================================================================


class VaultEncryptRequest(BaseAnsibleModel):
    """Request model for Vault encryption"""

    plaintext: str = Field(..., description="Text to encrypt")
    vault_id: Optional[str] = Field(None, description="Vault ID for multiple vaults")
    password_file: Optional[str] = Field(None, description="Password file path")
    vault_type: VaultType = Field(
        VaultType.ANSIBLE_VAULT, description="Vault type to use"
    )


class VaultDecryptRequest(BaseAnsibleModel):
    """Request model for Vault decryption"""

    ciphertext: str = Field(..., description="Encrypted text to decrypt")
    vault_id: Optional[str] = Field(None, description="Vault ID for multiple vaults")
    password_file: Optional[str] = Field(None, description="Password file path")
    vault_type: VaultType = Field(
        VaultType.ANSIBLE_VAULT, description="Vault type to use"
    )


class VaultResponse(BaseAnsibleModel):
    """Response model for Vault operations"""

    result: str = Field(..., description="Encryption/decryption result")
    vault_id: Optional[str] = None
    vault_type: VaultType
    success: bool = True
    message: Optional[str] = None


# ============================================================================
# COLLECTION AND ROLE MODELS
# ============================================================================


class CollectionInstallRequest(BaseAnsibleModel):
    """Request model for collection installation"""

    name: str = Field(..., description="Collection name or requirements", min_length=1)
    version: Optional[str] = Field(None, description="Collection version")
    source: CollectionInstallSource = Field(
        CollectionInstallSource.GALAXY, description="Installation source"
    )
    source_url: Optional[str] = Field(
        None, description="Source URL for git/url installs"
    )
    requirements_file: Optional[str] = Field(None, description="Requirements file path")
    force: bool = Field(False, description="Force reinstallation")
    upgrade: bool = Field(False, description="Upgrade to latest version")

    @field_validator("name")
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        # Note: cls access in field_validator is different - for now just do basic validation
        if "." not in v:
            raise ValueError(
                "Galaxy collection name must include namespace (e.g., community.general)"
            )
        return v


class CollectionInfo(BaseAnsibleModel):
    """Collection information model"""

    name: str
    namespace: Optional[str] = None
    version: str
    description: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    install_path: str
    installed_at: datetime
    source: str
    documentation_url: Optional[str] = None


class CollectionListResponse(BaseAnsibleModel):
    """Response model for collection listing"""

    collections: List[CollectionInfo]
    total_count: int


class RoleInfo(BaseAnsibleModel):
    """Role information model"""

    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    source: str
    install_path: str
    installed_at: datetime
    dependencies: List[str] = Field(default_factory=list)


class RoleListResponse(BaseAnsibleModel):
    """Response model for role listing"""

    roles: List[RoleInfo]
    total_count: int


# ============================================================================
# REAL-TIME FEEDBACK MODELS
# ============================================================================


class TaskResult(BaseAnsibleModel):
    """Individual task result model"""

    host: str
    task_name: str
    status: TaskStatus
    changed: bool = False
    failed: bool = False
    skipped: bool = False
    unreachable: bool = False
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class PlaybookProgress(BaseAnsibleModel):
    """Real-time playbook progress model"""

    job_id: str
    play_name: Optional[str] = None
    task_name: Optional[str] = None
    current_host: Optional[str] = None
    total_tasks: Optional[int] = None
    completed_tasks: int = 0
    total_hosts: Optional[int] = None
    progress_percentage: Optional[float] = None
    current_task_result: Optional[TaskResult] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class JobLogEntry(BaseAnsibleModel):
    """Job log entry model"""

    job_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    host: Optional[str] = None
    task: Optional[str] = None
    play: Optional[str] = None
    module: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class JobResponse(BaseAnsibleModel):
    """Generic job response model"""

    job_id: str
    status: JobStatus
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_duration: Optional[int] = None
    progress_url: Optional[str] = None
    logs_url: Optional[str] = None
    cancel_url: Optional[str] = None


class HealthResponse(BaseAnsibleModel):
    """Health check response model"""

    healthy: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    ansible_version: str
    uptime_seconds: float
    checks: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None


class ErrorResponse(BaseAnsibleModel):
    """Error response model"""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suggestions: Optional[List[str]] = None


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================


class AnsibleConfig(BaseAnsibleModel):
    """Ansible configuration model"""

    ansible_config_path: Optional[str] = None
    host_key_checking: bool = False
    timeout: int = 30
    forks: int = 5
    gathering: str = "smart"
    fact_caching: Optional[str] = None
    fact_cache_timeout: int = 3600
    retry_files_enabled: bool = False
    log_path: Optional[str] = None
    private_key_file: Optional[str] = None
    remote_user: Optional[str] = None


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


def validate_host_pattern(pattern: str) -> bool:
    """Validate Ansible host pattern"""
    # Allow basic patterns: hostnames, IPs, wildcards, groups
    if not pattern or len(pattern.strip()) == 0:
        return False

    # Basic validation - more comprehensive validation would be done by Ansible
    invalid_chars = ["<", ">", "|", "&", ";"]
    return not any(char in pattern for char in invalid_chars)


def validate_yaml_syntax(content: str) -> tuple[bool, Optional[str]]:
    """Validate YAML syntax"""
    try:
        import yaml

        yaml.safe_load(content)
        return True, None
    except Exception as e:
        if "yaml" in str(type(e)).lower():
            return False, str(e)
        return False, f"Unexpected error: {str(e)}"


def sanitize_extra_vars(extra_vars: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize extra variables for security"""
    # Remove potentially dangerous keys
    dangerous_keys = [
        "ansible_password",
        "ansible_sudo_password",
        "ansible_become_password",
    ]

    sanitized = {}
    for key, value in extra_vars.items():
        if key not in dangerous_keys:
            sanitized[key] = value

    return sanitized
