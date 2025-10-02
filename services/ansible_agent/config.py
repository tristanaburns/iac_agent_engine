"""
Ansible Executor Service Configuration
Environment-based configuration with validation
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class AnsibleExecutorConfig:
    """Configuration for Ansible Executor service"""

    def __init__(self) -> None:
        # ============================================================================
        # SERVICE CONFIGURATION
        # ============================================================================

        self.service_name: str = os.getenv("SERVICE_NAME", "ansible-executor")
        self.service_version: str = os.getenv("SERVICE_VERSION", "2.0.0")
        self.host: str = os.getenv("UVICORN_HOST", "127.0.0.1")
        self.port: int = int(os.getenv("UVICORN_PORT", "8081"))
        self.workers: int = int(os.getenv("UVICORN_WORKERS", "1"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.is_development: bool = (
            os.getenv("IS_DEVELOPMENT", "false").lower() == "true"
        )
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

        # ============================================================================
        # ANSIBLE CONFIGURATION
        # ============================================================================

        self.ansible_binary_path: str = os.getenv(
            "ANSIBLE_BINARY_PATH", "ansible-playbook"
        )
        self.ansible_config_path: Optional[str] = os.getenv("ANSIBLE_CONFIG")
        self.ansible_collections_path: Optional[str] = os.getenv(
            "ANSIBLE_COLLECTIONS_PATH"
        )
        self.ansible_roles_path: Optional[str] = os.getenv("ANSIBLE_ROLES_PATH")
        self.ansible_inventory_path: Optional[str] = os.getenv("ANSIBLE_INVENTORY")
        self.ansible_vault_password_file: Optional[str] = os.getenv(
            "ANSIBLE_VAULT_PASSWORD_FILE"
        )

        # Default Ansible settings
        self.default_forks: int = int(os.getenv("ANSIBLE_DEFAULT_FORKS", "5"))
        self.default_timeout: int = int(os.getenv("ANSIBLE_DEFAULT_TIMEOUT", "30"))
        self.default_gather_timeout: int = int(
            os.getenv("ANSIBLE_DEFAULT_GATHER_TIMEOUT", "10")
        )
        self.host_key_checking: bool = (
            os.getenv("ANSIBLE_HOST_KEY_CHECKING", "false").lower() == "true"
        )
        self.retry_files_enabled: bool = (
            os.getenv("ANSIBLE_RETRY_FILES_ENABLED", "false").lower() == "true"
        )
        self.fact_caching: Optional[str] = os.getenv("ANSIBLE_FACT_CACHING")
        self.fact_cache_timeout: int = int(
            os.getenv("ANSIBLE_FACT_CACHE_TIMEOUT", "3600")
        )

        # ============================================================================
        # EXECUTION LIMITS
        # ============================================================================

        self.max_concurrent_jobs: int = int(os.getenv("MAX_CONCURRENT_JOBS", "10"))
        self.max_job_duration: int = int(
            os.getenv("MAX_JOB_DURATION", "3600")
        )  # 1 hour default
        self.max_playbook_size_mb: int = int(os.getenv("MAX_PLAYBOOK_SIZE_MB", "10"))
        self.max_inventory_size_mb: int = int(os.getenv("MAX_INVENTORY_SIZE_MB", "5"))
        self.max_log_size_mb: int = int(os.getenv("MAX_LOG_SIZE_MB", "50"))
        self.cleanup_completed_jobs_hours: int = int(
            os.getenv("CLEANUP_COMPLETED_JOBS_HOURS", "24")
        )

        # ============================================================================
        # STORAGE CONFIGURATION
        # ============================================================================

        # Use OS-specific temp directory for better security
        import tempfile

        default_work_dir = os.path.join(tempfile.gettempdir(), "ansible_agent")
        self.work_directory: str = os.getenv("ANSIBLE_WORK_DIRECTORY", default_work_dir)
        self.playbooks_directory: str = os.getenv("PLAYBOOKS_DIRECTORY", "playbooks")
        self.inventories_directory: str = os.getenv(
            "INVENTORIES_DIRECTORY", "inventories"
        )
        self.collections_directory: str = os.getenv(
            "COLLECTIONS_DIRECTORY", "collections"
        )
        self.roles_directory: str = os.getenv("ROLES_DIRECTORY", "roles")
        self.logs_directory: str = os.getenv("LOGS_DIRECTORY", "logs")
        self.artifacts_directory: str = os.getenv("ARTIFACTS_DIRECTORY", "artifacts")

        # ============================================================================
        # CELERY CONFIGURATION
        # ============================================================================

        self.celery_broker_url: str = os.getenv(
            "CELERY_BROKER_URL", "redis://redis:6379/1"
        )
        self.celery_result_backend: str = os.getenv(
            "CELERY_RESULT_BACKEND", "redis://redis:6379/1"
        )
        self.celery_task_serializer: str = os.getenv("CELERY_TASK_SERIALIZER", "json")
        self.celery_result_serializer: str = os.getenv(
            "CELERY_RESULT_SERIALIZER", "json"
        )
        self.celery_accept_content: List[str] = os.getenv(
            "CELERY_ACCEPT_CONTENT", "json"
        ).split(",")
        self.celery_timezone: str = os.getenv("CELERY_TIMEZONE", "UTC")
        self.celery_enable_utc: bool = (
            os.getenv("CELERY_ENABLE_UTC", "true").lower() == "true"
        )
        self.celery_task_soft_time_limit: int = int(
            os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "1800")
        )  # 30 minutes
        self.celery_task_time_limit: int = int(
            os.getenv("CELERY_TASK_TIME_LIMIT", "3600")
        )  # 1 hour

        # ============================================================================
        # REDIS CONFIGURATION
        # ============================================================================

        self.redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
        self.redis_db: int = int(os.getenv("REDIS_DB", "0"))
        self.redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
        self.redis_socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "30"))

        # ============================================================================
        # VAULT INTEGRATION
        # ============================================================================

        # HashiCorp Vault
        self.vault_enabled: bool = os.getenv("VAULT_ENABLED", "true").lower() == "true"
        self.vault_url: str = os.getenv("VAULT_URL", "http://vault:8200")
        self.vault_token: Optional[str] = os.getenv("VAULT_TOKEN")
        self.vault_role_id: Optional[str] = os.getenv("VAULT_ROLE_ID")
        self.vault_secret_id: Optional[str] = os.getenv("VAULT_SECRET_ID")
        self.vault_mount_point: str = os.getenv("VAULT_MOUNT_POINT", "ansible")
        self.vault_timeout: int = int(os.getenv("VAULT_TIMEOUT", "30"))

        # Ansible Vault
        self.ansible_vault_enabled: bool = (
            os.getenv("ANSIBLE_VAULT_ENABLED", "true").lower() == "true"
        )
        ansible_vault_ids = os.getenv("ANSIBLE_VAULT_IDENTITY_LIST", "")
        self.ansible_vault_identity_list: Optional[List[str]] = (
            ansible_vault_ids.split(",") if ansible_vault_ids else None
        )

        # ============================================================================
        # GIT INTEGRATION
        # ============================================================================

        self.git_enabled: bool = os.getenv("GIT_ENABLED", "true").lower() == "true"
        self.git_timeout: int = int(os.getenv("GIT_TIMEOUT", "300"))  # 5 minutes
        self.git_max_repo_size_mb: int = int(os.getenv("GIT_MAX_REPO_SIZE_MB", "100"))
        allowed_domains = os.getenv(
            "GIT_ALLOWED_DOMAINS", "github.com,gitlab.com,bitbucket.org"
        )
        self.git_allowed_domains: List[str] = allowed_domains.split(",")
        self.git_default_branch: str = os.getenv("GIT_DEFAULT_BRANCH", "main")

        # ============================================================================
        # SECURITY CONFIGURATION
        # ============================================================================

        # Authentication
        self.require_authentication: bool = (
            os.getenv("REQUIRE_AUTHENTICATION", "true").lower() == "true"
        )
        self.jwt_secret_key: Optional[str] = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes: int = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Authorization
        self.enable_rbac: bool = os.getenv("ENABLE_RBAC", "true").lower() == "true"
        admin_users = os.getenv("ADMIN_USERS", "")
        self.admin_users: List[str] = admin_users.split(",") if admin_users else []
        operator_users = os.getenv("OPERATOR_USERS", "")
        self.operator_users: List[str] = (
            operator_users.split(",") if operator_users else []
        )
        readonly_users = os.getenv("READONLY_USERS", "")
        self.readonly_users: List[str] = (
            readonly_users.split(",") if readonly_users else []
        )

        # Security policies
        allowed_modules = os.getenv("ALLOWED_MODULES")
        self.allowed_modules: Optional[List[str]] = (
            allowed_modules.split(",") if allowed_modules else None
        )
        blocked_modules = os.getenv("BLOCKED_MODULES", "shell,command,raw,script")
        self.blocked_modules: List[str] = (
            blocked_modules.split(",") if blocked_modules else []
        )
        self.allow_become: bool = os.getenv("ALLOW_BECOME", "false").lower() == "true"
        allowed_become_users = os.getenv("ALLOWED_BECOME_USERS", "root")
        self.allowed_become_users: List[str] = allowed_become_users.split(",")
        self.max_hosts_per_job: int = int(os.getenv("MAX_HOSTS_PER_JOB", "100"))

        # ============================================================================
        # MONITORING AND OBSERVABILITY
        # ============================================================================

        # Metrics
        self.enable_metrics: bool = (
            os.getenv("ENABLE_METRICS", "true").lower() == "true"
        )
        self.metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))

        # Logging
        self.structured_logging: bool = (
            os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
        )
        self.log_to_file: bool = os.getenv("LOG_TO_FILE", "false").lower() == "true"
        self.log_file_path: Optional[str] = os.getenv("LOG_FILE_PATH")
        self.log_rotation_size_mb: int = int(os.getenv("LOG_ROTATION_SIZE_MB", "100"))
        self.log_retention_days: int = int(os.getenv("LOG_RETENTION_DAYS", "30"))

        # Tracing
        self.enable_tracing: bool = (
            os.getenv("ENABLE_TRACING", "true").lower() == "true"
        )
        self.jaeger_endpoint: Optional[str] = os.getenv("JAEGER_ENDPOINT")
        self.trace_sampling_rate: float = float(os.getenv("TRACE_SAMPLING_RATE", "0.1"))

        # Health checks
        self.health_check_interval: int = int(
            os.getenv("HEALTH_CHECK_INTERVAL", "60")
        )  # seconds
        self.health_check_timeout: int = int(
            os.getenv("HEALTH_CHECK_TIMEOUT", "10")
        )  # seconds

        # ============================================================================
        # API CONFIGURATION
        # ============================================================================

        # CORS
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins: List[str] = cors_origins.split(",")
        self.cors_credentials: bool = (
            os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
        )
        cors_methods = os.getenv("CORS_METHODS", "*")
        self.cors_methods: List[str] = cors_methods.split(",")
        cors_headers = os.getenv("CORS_HEADERS", "*")
        self.cors_headers: List[str] = cors_headers.split(",")

        # Rate limiting
        self.rate_limit_enabled: bool = (
            os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        )
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_period: int = int(
            os.getenv("RATE_LIMIT_PERIOD", "60")
        )  # seconds

        # Request validation
        self.max_request_size_mb: int = int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))
        self.request_timeout: int = int(
            os.getenv("REQUEST_TIMEOUT", "300")
        )  # 5 minutes

        # Validate configuration
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate configuration values"""
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")

        # Ensure work directory is absolute path
        path = Path(self.work_directory)
        if not path.is_absolute():
            self.work_directory = str(path.resolve())

        # Validate ranges
        if not (1 <= self.default_forks <= 50):
            raise ValueError("default_forks must be between 1 and 50")

        if not (1 <= self.max_concurrent_jobs <= 100):
            raise ValueError("max_concurrent_jobs must be between 1 and 100")

        if not (0 <= self.redis_db <= 15):
            raise ValueError("redis_db must be between 0 and 15")

        if not (0.0 <= self.trace_sampling_rate <= 1.0):
            raise ValueError("trace_sampling_rate must be between 0.0 and 1.0")

    # ============================================================================
    # COMPUTED PROPERTIES
    # ============================================================================

    @property
    def full_work_directory(self) -> Path:
        """Get full work directory path"""
        return Path(self.work_directory).resolve()

    @property
    def full_playbooks_path(self) -> Path:
        """Get full playbooks directory path"""
        return self.full_work_directory / self.playbooks_directory

    @property
    def full_inventories_path(self) -> Path:
        """Get full inventories directory path"""
        return self.full_work_directory / self.inventories_directory

    @property
    def full_logs_path(self) -> Path:
        """Get full logs directory path"""
        return self.full_work_directory / self.logs_directory

    @property
    def full_artifacts_path(self) -> Path:
        """Get full artifacts directory path"""
        return self.full_work_directory / self.artifacts_directory

    @property
    def ansible_environment_vars(self) -> Dict[str, str]:
        """Get Ansible environment variables"""
        env_vars = {}

        if self.ansible_config_path:
            env_vars["ANSIBLE_CONFIG"] = self.ansible_config_path

        if self.ansible_collections_path:
            env_vars["ANSIBLE_COLLECTIONS_PATH"] = self.ansible_collections_path

        if self.ansible_roles_path:
            env_vars["ANSIBLE_ROLES_PATH"] = self.ansible_roles_path

        if self.ansible_inventory_path:
            env_vars["ANSIBLE_INVENTORY"] = self.ansible_inventory_path

        if self.ansible_vault_password_file:
            env_vars["ANSIBLE_VAULT_PASSWORD_FILE"] = self.ansible_vault_password_file

        # Security settings
        env_vars["ANSIBLE_HOST_KEY_CHECKING"] = str(self.host_key_checking).lower()
        env_vars["ANSIBLE_RETRY_FILES_ENABLED"] = str(self.retry_files_enabled).lower()

        # Performance settings
        env_vars["ANSIBLE_FORKS"] = str(self.default_forks)
        env_vars["ANSIBLE_TIMEOUT"] = str(self.default_timeout)
        env_vars["ANSIBLE_GATHER_TIMEOUT"] = str(self.default_gather_timeout)

        # Fact caching
        if self.fact_caching:
            env_vars["ANSIBLE_CACHE_PLUGIN"] = self.fact_caching
            env_vars["ANSIBLE_CACHE_PLUGIN_TIMEOUT"] = str(self.fact_cache_timeout)

        return env_vars

    # ============================================================================
    # METHODS
    # ============================================================================

    def create_directories(self) -> None:
        """Create necessary directories"""
        directories = [
            self.full_work_directory,
            self.full_playbooks_path,
            self.full_inventories_path,
            self.full_logs_path,
            self.full_artifacts_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_ansible_installation(self) -> bool:
        """Validate Ansible installation"""
        import subprocess  # nosec B404

        try:
            result = subprocess.run(  # nosec B603
                [self.ansible_binary_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=False,  # Explicitly set shell=False for security
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def is_module_allowed(self, module_name: str) -> bool:
        """Check if module is allowed"""
        if module_name in self.blocked_modules:
            return False

        if self.allowed_modules is None:
            return True

        return module_name in self.allowed_modules

    def is_become_allowed(self, become_user: Optional[str] = None) -> bool:
        """Check if become is allowed"""
        if not self.allow_become:
            return False

        if become_user is None:
            return True

        return become_user in self.allowed_become_users


# Global configuration instance
_config: Optional[AnsibleExecutorConfig] = None


def get_config() -> AnsibleExecutorConfig:
    """Get configuration singleton"""
    global _config
    if _config is None:
        _config = AnsibleExecutorConfig()
    return _config


def validate_environment() -> None:
    """Validate environment configuration"""
    config = get_config()

    # Validate Ansible installation
    if not config.validate_ansible_installation():
        raise RuntimeError(f"Ansible not found at: {config.ansible_binary_path}")

    # Create directories
    config.create_directories()

    # Validate vault configuration if enabled
    if config.vault_enabled:
        if not config.vault_token and not (
            config.vault_role_id and config.vault_secret_id
        ):
            raise ValueError(
                "Vault token or role_id/secret_id must be provided when Vault is "
                "enabled"
            )

    # Validate JWT configuration if authentication is required
    if config.require_authentication and not config.jwt_secret_key:
        raise ValueError(
            "JWT secret key must be provided when authentication is required"
        )


# Configuration for different environments
def get_development_config() -> AnsibleExecutorConfig:
    """Get development configuration"""
    # Set environment variables for development
    os.environ.update(
        {
            "IS_DEVELOPMENT": "true",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "REQUIRE_AUTHENTICATION": "false",
            "ANSIBLE_HOST_KEY_CHECKING": "false",
            "MAX_CONCURRENT_JOBS": "5",
            "RATE_LIMIT_ENABLED": "false",
        }
    )
    return AnsibleExecutorConfig()


def get_production_config() -> AnsibleExecutorConfig:
    """Get production configuration"""
    # Set environment variables for production
    os.environ.update(
        {
            "IS_DEVELOPMENT": "false",
            "DEBUG": "false",
            "LOG_LEVEL": "INFO",
            "REQUIRE_AUTHENTICATION": "true",
            "ANSIBLE_HOST_KEY_CHECKING": "true",
            "STRUCTURED_LOGGING": "true",
            "ENABLE_METRICS": "true",
            "ENABLE_TRACING": "true",
            "RATE_LIMIT_ENABLED": "true",
        }
    )
    return AnsibleExecutorConfig()
