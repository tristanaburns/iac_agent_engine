"""
State Management Service
Production-ready centralized Terraform state management with MinIO backend
"""

try:
    from .app import app
    from .config import config, load_config
    from .exceptions import StateManagementError
    from .models import (
        BackendCreateRequest,
        BackendResponse,
        StateResponse,
        StateUpdateRequest,
        StateUpdateResponse,
    )
except ImportError:
    # Handle running as __main__ module
    from app import app  # type: ignore[no-redef]
    from config import config, load_config  # type: ignore[no-redef]
    from exceptions import StateManagementError  # type: ignore[no-redef]
    from models import (  # type: ignore[no-redef]
        BackendCreateRequest,
        BackendResponse,
        StateResponse,
        StateUpdateRequest,
        StateUpdateResponse,
    )

__version__ = "1.0.0"
__all__ = [
    "app",
    "config",
    "load_config",
    "StateManagementError",
    "BackendCreateRequest",
    "BackendResponse",
    "StateResponse",
    "StateUpdateRequest",
    "StateUpdateResponse",
]
