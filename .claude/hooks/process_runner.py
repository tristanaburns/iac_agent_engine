"""Process execution utilities following SOLID principles.

DEPRECATED: This module is deprecated. Please use utils.process_runner instead.
This file now redirects to the canonical implementation in utils.process_runner.
"""

# Import from the canonical location in utils
from utils.process_runner import ProcessRunner

# Maintain backward compatibility
__all__ = ["ProcessRunner"]
