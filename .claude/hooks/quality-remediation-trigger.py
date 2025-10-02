#!/usr/bin/env python3
"""
Quality Remediation Trigger Hook.

Monitors quality check results and triggers Claude SDK remediation workflow.
"""

import ast
import datetime
import glob
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def log_message(message, level="INFO"):
    """Log a message with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] [{level}] {message}"


def debug_print(message: str) -> None:
    """Print debug message to stderr if debug mode is enabled."""
    if os.environ.get("DEBUG", "").lower() in ("1", "true", "yes"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%")[:-3]
        print(f"[{timestamp}] DEBUG: {message}", file=sys.stderr)


# ========================================================================
# WORKFLOW STATE MANAGEMENT SYSTEM
# ========================================================================


class WorkflowState(Enum):
    """
    Enumeration of all possible workflow states with clear state transitions.

    Ensures atomic state management and prevents inconsistent state transitions.
    """

    INITIALIZING = auto()  # Setting up context and session
    PARSING_CONTEXT = auto()  # Parsing execution context
    DISCOVERING_RESULTS = auto()  # Finding quality results files
    ANALYZING_RESULTS = auto()  # Analyzing quality results
    EVALUATING_THRESHOLD = auto()  # Determining if remediation is needed
    EXECUTING_WORKFLOW = auto()  # Triggering remediation workflow
    LOGGING_RESULTS = auto()  # Logging trigger events
    COMPLETED = auto()  # Successful completion
    SKIPPED = auto()  # Workflow skipped (below threshold)
    FAILED = auto()  # Failed state requiring rollback
    ROLLED_BACK = auto()  # State after rollback operations


@dataclass
class StateTransition:
    """
    Tracks a single state transition with comprehensive metadata.

    Used for state validation, rollback operations, and audit trails.
    """

    from_state: WorkflowState
    to_state: WorkflowState
    timestamp: datetime.datetime
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    rollback_data: Dict[str, Any] = field(default_factory=dict)


class WorkflowStateManager:
    """
    Manages atomic workflow state transitions with rollback capabilities.

    Ensures that workflow state is always consistent and provides recovery
    mechanisms for partial failures. Implements comprehensive state validation
    and transaction-like behavior for state changes.

    Key Features:
    - Atomic state transitions (all-or-nothing)
    - Automatic rollback on partial failures
    - Comprehensive state validation
    - Complete audit trail of state changes
    - Recovery mechanisms for inconsistent states
    """

    # Valid state transitions mapping
    VALID_TRANSITIONS = {
        WorkflowState.INITIALIZING: [
            WorkflowState.PARSING_CONTEXT,
            WorkflowState.FAILED,
        ],
        WorkflowState.PARSING_CONTEXT: [
            WorkflowState.DISCOVERING_RESULTS,
            WorkflowState.FAILED,
        ],
        WorkflowState.DISCOVERING_RESULTS: [
            WorkflowState.ANALYZING_RESULTS,
            WorkflowState.SKIPPED,
            WorkflowState.FAILED,
        ],
        WorkflowState.ANALYZING_RESULTS: [
            WorkflowState.EVALUATING_THRESHOLD,
            WorkflowState.FAILED,
        ],
        WorkflowState.EVALUATING_THRESHOLD: [
            WorkflowState.EXECUTING_WORKFLOW,
            WorkflowState.SKIPPED,
            WorkflowState.FAILED,
        ],
        WorkflowState.EXECUTING_WORKFLOW: [
            WorkflowState.LOGGING_RESULTS,
            WorkflowState.FAILED,
        ],
        WorkflowState.LOGGING_RESULTS: [WorkflowState.COMPLETED, WorkflowState.FAILED],
        WorkflowState.COMPLETED: [],  # Terminal state
        WorkflowState.SKIPPED: [],  # Terminal state
        WorkflowState.FAILED: [WorkflowState.ROLLED_BACK],
        WorkflowState.ROLLED_BACK: [],  # Terminal state
    }

    def __init__(self, session_id: str):
        """
        Initialize workflow state manager with session tracking.

        Args:
            session_id: Unique session identifier for audit trail
        """
        self.session_id = session_id
        self.current_state = WorkflowState.INITIALIZING
        self.state_history: List[StateTransition] = []
        self.workflow_data: Dict[str, Any] = {}
        self.rollback_stack: List[Dict[str, Any]] = []

        debug_print(f"WorkflowStateManager initialized for session {session_id}")
        print(
            log_message(
                f"Workflow state manager initialized - Session: {session_id[:8]}"
            )
        )

    def transition_to(
        self,
        new_state: WorkflowState,
        data: Optional[Dict[str, Any]] = None,
        rollback_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Perform atomic state transition with validation and rollback support.

        Args:
            new_state: Target state to transition to
            data: Optional data associated with this transition
            rollback_data: Optional data needed for rollback operations

        Returns:
            True if transition was successful, False otherwise

        Raises:
            ValueError: If transition is not allowed from current state
        """
        # Validate transition is allowed
        if new_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            error_msg = (
                f"Invalid state transition from {self.current_state} to {new_state}"
            )
            debug_print(f"State transition validation failed: {error_msg}")
            print(log_message(error_msg, "ERROR"))
            raise ValueError(error_msg)

        # Create transition record
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=datetime.datetime.now(),
            success=False,
            data=data or {},
            rollback_data=rollback_data or {},
        )

        try:
            # Store current state for potential rollback
            if rollback_data:
                self.rollback_stack.append(
                    {
                        "state": self.current_state,
                        "data": rollback_data,
                        "timestamp": transition.timestamp,
                    }
                )

            # Perform atomic state transition
            previous_state = self.current_state
            self.current_state = new_state

            # Update workflow data
            if data:
                self.workflow_data.update(data)

            # Mark transition as successful
            transition.success = True
            self.state_history.append(transition)

            debug_print(f"State transition successful: {previous_state} -> {new_state}")
            print(
                log_message(
                    f"Workflow state: {previous_state.name} -> {new_state.name}"
                )
            )

            return True

        except Exception as e:
            # Mark transition as failed and add to history
            transition.error = str(e)
            self.state_history.append(transition)

            error_msg = (
                f"State transition failed: {previous_state} -> {new_state}: {str(e)}"
            )
            debug_print(f"State transition error: {error_msg}")
            print(log_message(error_msg, "ERROR"))

            return False

    def rollback_to_last_stable_state(self) -> bool:
        """
        Rollback to the last stable state using rollback stack.

        Returns:
            True if rollback was successful, False otherwise
        """
        if not self.rollback_stack:
            debug_print("No rollback data available - cannot rollback")
            print(log_message("No rollback data available for recovery", "ERROR"))
            return False

        try:
            # Get last stable state data
            rollback_info = self.rollback_stack.pop()
            stable_state = rollback_info["state"]
            rollback_data = rollback_info["data"]

            debug_print(f"Rolling back from {self.current_state} to {stable_state}")
            print(log_message(f"Rolling back workflow state to {stable_state.name}"))

            # Perform rollback operations
            self._execute_rollback_operations(rollback_data)

            # Transition to ROLLED_BACK state
            self.current_state = WorkflowState.ROLLED_BACK

            # Record rollback transition
            rollback_transition = StateTransition(
                from_state=WorkflowState.FAILED,
                to_state=WorkflowState.ROLLED_BACK,
                timestamp=datetime.datetime.now(),
                success=True,
                data={"rollback_target": stable_state.name},
                rollback_data=rollback_data,
            )
            self.state_history.append(rollback_transition)

            debug_print(f"Rollback completed successfully to {stable_state}")
            print(log_message("Workflow state rolled back successfully"))

            return True

        except Exception as e:
            error_msg = f"Rollback operation failed: {str(e)}"
            debug_print(f"Rollback error: {error_msg}")
            print(log_message(error_msg, "ERROR"))
            return False

    def _execute_rollback_operations(self, rollback_data: Dict[str, Any]) -> None:
        """
        Execute rollback operations based on rollback data.

        Args:
            rollback_data: Data needed to perform rollback operations
        """
        debug_print("Executing rollback operations")

        # Clean up temporary files if any
        if "temp_files" in rollback_data:
            for temp_file in rollback_data["temp_files"]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        debug_print(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    debug_print(f"Failed to clean up temp file {temp_file}: {e}")

        # Reset workflow data to known state
        if "workflow_data_backup" in rollback_data:
            self.workflow_data = rollback_data["workflow_data_backup"].copy()
            debug_print("Restored workflow data from backup")

        # Additional rollback operations can be added here
        debug_print("Rollback operations completed")

    def get_current_state(self) -> WorkflowState:
        """Get current workflow state."""
        return self.current_state

    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (workflow ended)."""
        return self.current_state in [
            WorkflowState.COMPLETED,
            WorkflowState.SKIPPED,
            WorkflowState.ROLLED_BACK,
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of workflow state and history.

        Returns:
            Dictionary containing state summary and transition history
        """
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.name,
            "is_terminal": self.is_terminal_state(),
            "total_transitions": len(self.state_history),
            "successful_transitions": len([t for t in self.state_history if t.success]),
            "failed_transitions": len([t for t in self.state_history if not t.success]),
            "rollback_stack_size": len(self.rollback_stack),
            "workflow_data_keys": list(self.workflow_data.keys()),
            "state_history": [
                {
                    "from": t.from_state.name,
                    "to": t.to_state.name,
                    "timestamp": t.timestamp.isoformat(),
                    "success": t.success,
                    "error": t.error,
                }
                for t in self.state_history
            ],
        }


def _get_files_to_check(project_dir: Path) -> list[Path]:
    """
    Get list of Python files to check for compilation.

    Attempts to get modified files from git first, falls back to all Python files.

    Args:
        project_dir: Path to the project directory

    Returns:
        List of Python file paths to check for compilation
    """
    import subprocess

    print(log_message("Starting file discovery for compilation check", "DEBUG"))

    try:
        # Try to get modified files from git
        git_cmd = ["git", "dif", "--name-only", "HEAD"]
        print(log_message(f"Running git command: {' '.join(git_cmd)}", "DEBUG"))

        result = subprocess.run(
            git_cmd, cwd=project_dir, capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            print(
                log_message(
                    f"Git command failed with code {result.returncode}: {result.stderr}",
                    "WARN",
                )
            )
            print(log_message("Falling back to checking all Python files", "INFO"))
            python_files = list(project_dir.rglob("*.py"))
            print(
                log_message(
                    f"Found {len(python_files)} Python files in fallback scan", "DEBUG"
                )
            )
            return python_files

        # Process git output for Python files
        modified_files = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )
        print(log_message(f"Git found {len(modified_files)} modified files", "DEBUG"))

        python_files = []
        for file in modified_files:
            if file.endswith(".py"):
                file_path = Path(project_dir) / file
                if file_path.exists():
                    python_files.append(file_path)
                    print(log_message(f"Added Python file: {file_path}", "DEBUG"))
                else:
                    print(
                        log_message(f"Skipping non-existent file: {file_path}", "DEBUG")
                    )

        print(
            log_message(
                f"Selected {len(python_files)} Python files for compilation check",
                "INFO",
            )
        )
        return python_files

    except Exception as e:
        print(log_message(f"Error during file discovery: {str(e)}", "ERROR"))
        print(log_message("Falling back to checking all Python files", "INFO"))
        python_files = list(project_dir.rglob("*.py"))
        print(
            log_message(
                f"Found {len(python_files)} Python files in exception fallback", "DEBUG"
            )
        )
        return python_files


def _should_skip_file(file_path: Path) -> bool:
    """
    Determine if a file should be skipped during compilation check.

    Args:
        file_path: Path to the file to check

    Returns:
        True if file should be skipped, False otherwise
    """
    skip_directories = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".mypy_cache",
        "site-packages",
        ".tox",
    ]

    file_str = str(file_path)
    for skip_dir in skip_directories:
        if skip_dir in file_str:
            print(
                log_message(
                    f"Skipping file due to '{skip_dir}' directory: {file_path}", "DEBUG"
                )
            )
            return True

    print(log_message(f"File will be checked: {file_path}", "DEBUG"))
    return False


def _validate_file_reading(file_path: Path) -> tuple[str | None, dict | None]:
    """Layer 1: File Reading and Encoding Validation."""
    print(log_message(f"Layer 1: Reading file content: {file_path}", "DEBUG"))

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        print(log_message(f"Successfully read {len(source_code)} characters", "DEBUG"))
        return source_code, None
    except UnicodeDecodeError as e:
        error_info = {
            "file": str(file_path),
            "error": f"Unicode decode error: {str(e)}",
            "layer": "file_reading",
            "line": getattr(e, "start", "unknown"),
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 1): {file_path} - Unicode error", "ERROR"
            )
        )
        return None, error_info
    except Exception as e:
        error_info = {
            "file": str(file_path),
            "error": f"File reading error: {str(e)}",
            "layer": "file_reading",
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 1): {file_path} - File error", "ERROR"
            )
        )
        return None, error_info


def _validate_ast_parsing(
    source_code: str, file_path: Path
) -> tuple[ast.AST | None, dict | None]:
    """Layer 2: AST Parsing and Syntax Tree Validation."""
    print(log_message(f"Layer 2: AST parsing and validation: {file_path}", "DEBUG"))

    try:
        # Parse the source code into an Abstract Syntax Tree
        ast_tree = ast.parse(source_code, filename=str(file_path))
        print(
            log_message(
                f"AST parsing successful - {len(ast_tree.body)} top-level nodes",
                "DEBUG",
            )
        )

        # Basic AST structure validation
        _validate_ast_structure(ast_tree, file_path)
        print(log_message("AST structure validation passed", "DEBUG"))
        return ast_tree, None

    except SyntaxError as e:
        error_info = {
            "file": str(file_path),
            "error": f"Syntax error: {e.msg}",
            "layer": "ast_parsing",
            "line": e.lineno or "unknown",
            "column": e.offset or "unknown",
            "context": _get_error_context(source_code, e.lineno) if e.lineno else None,
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 2): {file_path} - Syntax error at line {e.lineno}",
                "ERROR",
            )
        )
        return None, error_info
    except Exception as e:
        error_info = {
            "file": str(file_path),
            "error": f"AST parsing error: {str(e)}",
            "layer": "ast_parsing",
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 2): {file_path} - AST error", "ERROR"
            )
        )
        return None, error_info


def _validate_builtin_compilation(source_code: str, file_path: Path) -> dict | None:
    """Layer 3: Python Compilation Verification (Built-in compile function)."""
    print(
        log_message(f"Layer 3: Built-in compilation verification: {file_path}", "DEBUG")
    )

    try:
        # Compile the source code to bytecode
        compile(source_code, str(file_path), "exec", dont_inherit=True)
        print(log_message("Built-in compilation successful", "DEBUG"))
        return None
    except SyntaxError as e:
        error_info = {
            "file": str(file_path),
            "error": f"Compilation syntax error: {e.msg}",
            "layer": "builtin_compilation",
            "line": e.lineno or "unknown",
            "column": e.offset or "unknown",
            "context": _get_error_context(source_code, e.lineno) if e.lineno else None,
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 3): {file_path} - Compilation syntax error",
                "ERROR",
            )
        )
        return error_info
    except Exception as e:
        error_info = {
            "file": str(file_path),
            "error": f"Built-in compilation error: {str(e)}",
            "layer": "builtin_compilation",
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 3): {file_path} - Compilation error", "ERROR"
            )
        )
        return error_info


def _validate_py_compile(file_path: Path) -> dict | None:
    """Layer 4: py_compile Module Verification."""
    print(log_message(f"Layer 4: py_compile module verification: {file_path}", "DEBUG"))

    try:
        # Use py_compile for additional verification
        with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as tmp_file:
            py_compile.compile(str(file_path), tmp_file.name, doraise=True)
        print(log_message("py_compile verification successful", "DEBUG"))
        return None
    except py_compile.PyCompileError as e:
        error_info = {
            "file": str(file_path),
            "error": f"py_compile error: {str(e)}",
            "layer": "py_compile_verification",
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 4): {file_path} - py_compile error", "ERROR"
            )
        )
        return error_info
    except Exception as e:
        error_info = {
            "file": str(file_path),
            "error": f"py_compile verification error: {str(e)}",
            "layer": "py_compile_verification",
        }
        print(
            log_message(
                f"VALIDATION FAILED (Layer 4): {file_path} - py_compile error", "ERROR"
            )
        )
        return error_info


def _validate_import_statements(ast_tree: ast.AST, file_path: Path) -> dict | None:
    """Layer 5: Import Statement Validation."""
    print(log_message(f"Layer 5: Import statement validation: {file_path}", "DEBUG"))

    try:
        import_errors = _validate_imports(ast_tree, file_path)
        if import_errors:
            error_info = {
                "file": str(file_path),
                "error": f"Import validation errors: {'; '.join(import_errors)}",
                "layer": "import_validation",
            }
            print(
                log_message(
                    f"VALIDATION FAILED (Layer 5): {file_path} - Import errors", "ERROR"
                )
            )
            return error_info
        print(log_message("Import validation successful", "DEBUG"))
        return None
    except Exception as e:
        print(log_message(f"Import validation warning: {str(e)}", "WARN"))
        # Don't fail on import validation errors - they may be environment-specific
        return None


def _compile_single_file(file_path: Path, project_dir: Path) -> dict[str, str] | None:
    """
    Comprehensive Python file validation with multi-layer verification.

    Implements comprehensive AST validation, syntax checking, and compilation verification
    to ensure code integrity after automated fixes. Includes multiple validation layers:
    1. File reading and encoding validation
    2. AST parsing and syntax tree validation
    3. Python compilation verification (py_compile + compile)
    4. Code structure and import validation
    5. Comprehensive error reporting with line numbers and context

    Args:
        file_path: Path to the Python file to validate
        project_dir: Path to the project directory

    Returns:
        Dictionary with detailed error information if validation fails, None if successful
    """
    print(log_message(f"Starting comprehensive validation for: {file_path}", "DEBUG"))

    try:
        return _execute_validation_layers(file_path, project_dir)
    except Exception as e:
        return _handle_unexpected_validation_error(file_path, e)


def _execute_validation_layers(
    file_path: Path, project_dir: Path
) -> dict[str, str] | None:
    """Execute all validation layers in sequence.

    Args:
        file_path: Path to the Python file to validate
        project_dir: Path to the project directory

    Returns:
        Dictionary with error information if validation fails, None if successful
    """
    # Layer 1: File Reading and Encoding Validation
    source_code, error = _validate_file_reading(file_path)
    if error:
        return error

    # Skip empty files
    if _is_empty_file(source_code, file_path):
        return None

    # Ensure source_code is not None for type checking
    assert source_code is not None

    # Layer 2: AST Parsing and Syntax Tree Validation
    ast_tree, error = _validate_ast_parsing(source_code, file_path)
    if error:
        return error

    # Layer 3: Python Compilation Verification
    error = _validate_builtin_compilation(source_code, file_path)
    if error:
        return error

    # Layer 4: py_compile Module Verification
    error = _validate_py_compile(file_path)
    if error:
        return error

    # Layer 5: Import Statement Validation
    error = _validate_imports_layer(ast_tree, file_path)
    if error:
        return error

    # All validation layers passed
    _log_validation_success(file_path)
    return None


def _is_empty_file(source_code: str | None, file_path: Path) -> bool:
    """Check if the file is empty and should be skipped.

    Args:
        source_code: Source code content or None
        file_path: Path to the file being checked

    Returns:
        True if file is empty and should be skipped
    """
    if not source_code or not source_code.strip():
        print(log_message(f"Skipping empty file: {file_path}", "DEBUG"))
        return True
    return False


def _validate_imports_layer(
    ast_tree: ast.AST | None, file_path: Path
) -> dict[str, str] | None:
    """Validate import statements in the AST.

    Args:
        ast_tree: AST tree to validate
        file_path: Path to the file being validated

    Returns:
        Dictionary with error information if validation fails, None if successful
    """
    if ast_tree is not None:
        return _validate_import_statements(ast_tree, file_path)
    else:
        return _create_ast_none_error(file_path)


def _create_ast_none_error(file_path: Path) -> dict[str, str]:
    """Create error dictionary for None AST tree.

    Args:
        file_path: Path to the file with the error

    Returns:
        Error dictionary
    """
    return {
        "type": "ast_error",
        "message": "AST tree is None, cannot validate import statements",
        "file": str(file_path),
        "severity": "ERROR",
    }


def _log_validation_success(file_path: Path) -> None:
    """Log successful completion of all validation layers.

    Args:
        file_path: Path to the successfully validated file
    """
    print(log_message(f"ALL VALIDATION LAYERS PASSED: {file_path}", "DEBUG"))


def _handle_unexpected_validation_error(
    file_path: Path, error: Exception
) -> dict[str, str]:
    """Handle unexpected errors during validation.

    Args:
        file_path: Path to the file being validated
        error: The unexpected exception

    Returns:
        Error information dictionary
    """
    error_info = {
        "file": str(file_path),
        "error": f"Unexpected validation error: {str(error)}",
        "layer": "general_exception",
    }
    print(
        log_message(
            f"VALIDATION FAILED (Exception): {file_path} - {str(error)}", "ERROR"
        )
    )
    return error_info


def _validate_ast_structure(ast_tree: ast.AST, file_path: Path) -> None:
    """
    Validate the basic structure of the AST to ensure code integrity.

    Args:
        ast_tree: The parsed AST tree
        file_path: Path to the file being validated

    Raises:
        ValueError: If AST structure validation fails
    """
    print(log_message(f"Validating AST structure for: {file_path}", "DEBUG"))

    try:
        # Count different types of nodes
        node_counts = {"functions": 0, "classes": 0, "imports": 0, "assignments": 0}

        # Walk through all nodes in the AST
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                node_counts["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                node_counts["classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                node_counts["imports"] += 1
            elif isinstance(node, ast.Assign):
                node_counts["assignments"] += 1

        print(
            log_message(
                f"AST structure: {node_counts['functions']} functions, "
                f"{node_counts['classes']} classes, {node_counts['imports']} imports, "
                f"{node_counts['assignments']} assignments",
                "DEBUG",
            )
        )

        # Basic sanity checks
        if hasattr(ast_tree, "body") and not ast_tree.body:
            print(log_message(f"Warning: Empty AST body for {file_path}", "WARN"))

    except Exception as e:
        raise ValueError(f"AST structure validation failed: {str(e)}")


def _validate_regular_import(node: ast.Import) -> list[str]:
    """Validate a regular import statement."""
    errors = []
    for alias in node.names:
        if not alias.name:
            errors.append(f"Empty import name at line {node.lineno}")
        elif alias.name.startswith("."):
            errors.append(
                f"Invalid relative import '{alias.name}' at line {node.lineno}"
            )
    return errors


def _validate_from_import(node: ast.ImportFrom) -> list[str]:
    """Validate a from-import statement."""
    errors = []
    if node.module and node.module.startswith("."):
        # Relative imports are okay in certain contexts
        pass
    if not node.names:
        errors.append(f"Empty from-import at line {node.lineno}")
    return errors


def _validate_imports(ast_tree: ast.AST, file_path: Path) -> list[str]:
    """
    Validate import statements in the AST.

    Args:
        ast_tree: The parsed AST tree
        file_path: Path to the file being validated

    Returns:
        List of import validation error messages
    """
    print(log_message(f"Validating imports for: {file_path}", "DEBUG"))

    errors = []

    try:
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import):
                errors.extend(_validate_regular_import(node))
            elif isinstance(node, ast.ImportFrom):
                errors.extend(_validate_from_import(node))

        if errors:
            print(log_message(f"Found {len(errors)} import validation errors", "WARN"))
        else:
            print(log_message("Import validation successful", "DEBUG"))

    except Exception as e:
        errors.append(f"Import validation exception: {str(e)}")

    return errors


def _get_error_context(
    source_code: str, line_number: int | None, context_lines: int = 2
) -> str | None:
    """
    Get error context around a specific line number.

    Args:
        source_code: The source code content
        line_number: Line number where error occurred
        context_lines: Number of lines to show before and after error line

    Returns:
        String containing error context with line numbers, or None if unavailable
    """
    if not line_number or not source_code:
        return None

    try:
        lines = source_code.splitlines()
        if line_number > len(lines) or line_number < 1:
            return None

        start_line = max(1, line_number - context_lines)
        end_line = min(len(lines), line_number + context_lines)

        context_lines_list = []
        for i in range(start_line, end_line + 1):
            line_content = lines[i - 1] if i <= len(lines) else ""
            marker = " >>> " if i == line_number else "     "
            context_lines_list.append(f"{i:4d}{marker}{line_content}")

        return "\n".join(context_lines_list)

    except Exception:
        return None


def _group_failures_by_layer(
    compilation_failures: list[dict[str, str]],
) -> dict[str, list[dict]]:
    """Group failures by validation layer for analysis."""
    failures_by_layer: dict[str, list[dict]] = {}
    for failure in compilation_failures:
        layer = failure.get("layer", "unknown")
        if layer not in failures_by_layer:
            failures_by_layer[layer] = []
        failures_by_layer[layer].append(failure)
    return failures_by_layer


def _report_layer_statistics(failures_by_layer: dict[str, list[dict]]) -> None:
    """Report layer-specific statistics."""
    print(log_message("Validation failures by layer:", "ERROR"))
    layer_name_map = {
        "file_reading": "File Reading & Encoding",
        "ast_parsing": "AST Parsing & Syntax Tree",
        "builtin_compilation": "Built-in Compilation",
        "py_compile_verification": "py_compile Verification",
        "import_validation": "Import Statement Validation",
        "general_exception": "General Exception Handling",
        "unknown": "Unknown Layer",
    }

    for layer, layer_failures in failures_by_layer.items():
        count = len(layer_failures)
        layer_name = layer_name_map.get(layer, layer.title())
        print(log_message(f"  - {layer_name}: {count} failures", "ERROR"))


def _report_failure_details(failure: dict, failure_num: int) -> None:
    """Report detailed information for a single failure."""
    print(log_message(f"\n--- Failure #{failure_num} ---", "ERROR"))
    print(log_message(f"File: {failure['file']}", "ERROR"))
    print(log_message(f"Layer: {failure.get('layer', 'unknown')}", "ERROR"))
    print(log_message(f"Error: {failure['error']}", "ERROR"))

    # Add line and column information if available
    if "line" in failure and failure["line"] != "unknown":
        line_info = f"Line: {failure['line']}"
        if "column" in failure and failure["column"] != "unknown":
            line_info += f", Column: {failure['column']}"
        print(log_message(line_info, "ERROR"))

    # Add error context if available
    if "context" in failure and failure["context"]:
        print(log_message("Error Context:", "ERROR"))
        for context_line in failure["context"].split("\n"):
            print(log_message(f"  {context_line}", "ERROR"))


def _report_compilation_results(compilation_failures: list[dict[str, str]]) -> bool:
    """
    Report comprehensive validation results with detailed error analysis.

    Provides detailed reporting of validation failures across all validation layers,
    including layer-specific analysis, error context, and line number information.

    Args:
        compilation_failures: List of dictionaries containing detailed failure information

    Returns:
        True if no failures, False if there were validation failures
    """
    # Guard clause: No failures
    if not compilation_failures:
        print(
            log_message("All modified files passed comprehensive validation!", "INFO")
        )
        print(
            log_message(
                "Comprehensive validation PASSED - code safety and integrity maintained",
                "INFO",
            )
        )
        return True

    # Report critical validation failures
    print(
        log_message(
            f"CRITICAL: {len(compilation_failures)} files failed comprehensive validation!",
            "ERROR",
        )
    )

    # Group failures and report statistics
    failures_by_layer = _group_failures_by_layer(compilation_failures)
    _report_layer_statistics(failures_by_layer)

    # Report detailed failure information
    print(log_message("\n=== DETAILED VALIDATION FAILURE REPORTS ===", "ERROR"))
    for i, failure in enumerate(compilation_failures, 1):
        _report_failure_details(failure, i)

    # Provide remediation guidance and final summary
    print(log_message("\n=== REMEDIATION GUIDANCE ===", "ERROR"))
    _provide_remediation_guidance(failures_by_layer)

    print(
        log_message(
            "\nComprehensive validation FAILED - code safety compromised", "ERROR"
        )
    )
    print(
        log_message(
            "Automated fixes may have introduced syntax errors or code integrity issues",
            "ERROR",
        )
    )
    return False


def _provide_remediation_guidance(failures_by_layer: dict[str, list[dict]]) -> None:
    """
    Provide specific remediation guidance based on validation layer failures.

    Args:
        failures_by_layer: Dictionary mapping layer names to failure lists
    """
    guidance_map = {
        "file_reading": [
            "Check file encoding - ensure files are saved as UTF-8",
            "Verify file permissions and accessibility",
            "Check for binary files that were incorrectly processed",
        ],
        "ast_parsing": [
            "Review syntax errors - check for incomplete statements",
            "Verify proper indentation and bracket matching",
            "Check for invalid character sequences or encoding issues",
            "Ensure Python version compatibility",
        ],
        "builtin_compilation": [
            "Review bytecode compilation errors",
            "Check for advanced syntax errors not caught by AST parsing",
            "Verify import dependencies and module availability",
        ],
        "py_compile_verification": [
            "Review py_compile specific errors",
            "Check for module-level compilation issues",
            "Verify Python path and environment setup",
        ],
        "import_validation": [
            "Review import statement structure",
            "Check for circular imports or missing modules",
            "Verify relative import paths and package structure",
        ],
        "general_exception": [
            "Review unexpected errors in validation process",
            "Check system resources and environment",
            "Consider filing a bug report if errors persist",
        ],
    }

    for layer, failures in failures_by_layer.items():
        if layer in guidance_map:
            print(
                log_message(
                    f"{layer.title()} failures ({len(failures)} files):", "ERROR"
                )
            )
            for guidance in guidance_map[layer]:
                print(log_message(f"   {guidance}", "ERROR"))
            print()

    # General remediation steps
    print(log_message("General remediation steps:", "ERROR"))
    print(log_message("  1. Review all failed files manually", "ERROR"))
    print(
        log_message(
            "  2. Run validation on individual files for detailed debugging", "ERROR"
        )
    )
    print(
        log_message(
            "  3. Consider reverting automated changes if errors persist", "ERROR"
        )
    )
    print(
        log_message(
            "  4. Ensure development environment is properly configured", "ERROR"
        )
    )


def verify_files_compile_after_fixes(project_dir: Path) -> bool:
    """
    Verify that all Python files in the project still compile after automated fixes.

    This is critical to ensure that black, isort, and other auto-fixers didn't break the code.
    Uses git to identify modified files and tests compilation on those files.

    Args:
        project_dir: Path to the project directory

    Returns:
        True if all modified files compile successfully, False otherwise
    """
    print(
        log_message("Starting compilation verification for safety validation", "INFO")
    )

    try:
        # Get files to check using helper function
        python_files = _get_files_to_check(project_dir)

        if not python_files:
            print(log_message("No Python files to check for compilation", "INFO"))
            return True

        print(
            log_message(
                f"Checking compilation of {len(python_files)} Python files...", "INFO"
            )
        )

        # Compile each file and collect failures
        compilation_failures = []
        files_checked = 0
        files_skipped = 0

        for python_file in python_files:
            # Skip files that shouldn't be checked
            if _should_skip_file(python_file):
                files_skipped += 1
                continue

            files_checked += 1

            # Compile the file and collect any errors
            error_info = _compile_single_file(python_file, project_dir)
            if error_info:
                compilation_failures.append(error_info)

        print(
            log_message(
                f"Comprehensive validation summary: {files_checked} checked, {files_skipped} skipped",
                "INFO",
            )
        )

        # Report results using helper function
        return _report_compilation_results(compilation_failures)

    except Exception as e:
        print(log_message(f"Error during compilation verification: {str(e)}", "ERROR"))
        print(log_message("Compilation verification FAILED due to exception", "ERROR"))
        return False


def find_latest_quality_results(project_dir, specific_file=None):
    """Find the most recent quality check results file."""
    # Use project directory for quality-checks results
    quality_dir = Path(project_dir) / ".claude" / "hooks" / "quality-checks"

    if not quality_dir.exists():
        return None

    # If a specific file is provided, use it
    if specific_file and Path(specific_file).exists():
        return specific_file

    # Find all quality result files (both session-end and post-response)
    patterns = [
        str(quality_dir / "session-end-quality-*.json"),
        str(quality_dir / "post-response-quality-*.json"),
    ]

    result_files = []
    for pattern in patterns:
        result_files.extend(glob.glob(pattern))

    if not result_files:
        return None

    # Return the most recent file
    latest_file = max(result_files, key=os.path.getmtime)
    return latest_file


def _initialize_analysis_structure():
    """Initialize the analysis structure with default values."""
    print(
        log_message(
            "DEBUG: Initializing analysis structure for quality decision engine"
        )
    )

    analysis = {
        "needs_remediation": False,
        "critical_issues": 0,
        "security_issues": 0,
        "quality_issues": 0,
        "total_issues": 0,
        "issue_summary": "",
        "remediation_priority": "none",
    }

    print(log_message(f"DEBUG: Analysis structure initialized: {analysis}"))
    return analysis


def _validate_formatting_inputs(results, analysis):
    """
    Validate input parameters for formatting analysis.

    Args:
        results: Quality check results dictionary
        analysis: Analysis structure to update

    Returns:
        bool: True if validation passes

    Raises:
        ValueError: On critical validation failures
        TypeError: On invalid input types
    """
    print(log_message("DEBUG: Starting formatting inputs validation"))

    if results is None:
        raise ValueError("Results parameter cannot be None")
    if not isinstance(results, dict):
        raise TypeError(f"Results must be a dictionary, got {type(results)}")
    if analysis is None:
        raise ValueError("Analysis parameter cannot be None")
    if not isinstance(analysis, dict):
        raise TypeError(f"Analysis must be a dictionary, got {type(analysis)}")

    print(log_message("DEBUG: Input parameter validation passed"))
    return True


def _validate_formatting_structure(results):
    """
    Validate the structure of formatting results.

    Args:
        results: Quality check results dictionary

    Returns:
        dict: The formatting section from results

    Raises:
        ValueError: On structure validation failures
    """
    print(log_message("DEBUG: Starting formatting structure validation"))

    validation_errors = []

    # Validate quality_checks exists
    if "quality_checks" not in results:
        validation_errors.append("Missing 'quality_checks' key in results")
    elif not isinstance(results["quality_checks"], dict):
        validation_errors.append(
            f"'quality_checks' must be a dictionary, got {type(results['quality_checks'])}"
        )

    # Validate formatting section exists
    quality_checks = results.get("quality_checks", {})
    if "formatting" not in quality_checks:
        validation_errors.append("Missing 'formatting' key in quality_checks")
    elif not isinstance(quality_checks["formatting"], dict):
        validation_errors.append(
            f"'formatting' must be a dictionary, got {type(quality_checks['formatting'])}"
        )

    if validation_errors:
        error_summary = "; ".join(validation_errors)
        print(
            log_message(
                f"ERROR: Result structure validation failed: {error_summary}", "ERROR"
            )
        )
        raise ValueError(error_summary)

    print(log_message("DEBUG: Result structure validation passed"))
    return quality_checks["formatting"]


def _validate_formatting_data_types(formatting):
    """
    Validate data types in formatting section.

    Args:
        formatting: Formatting section from quality results

    Returns:
        tuple: (files_formatted, formatting_errors, validation_warnings)
    """
    print(log_message("DEBUG: Starting formatting data type validation"))

    validation_warnings = []

    # Validate files_formatted
    files_formatted_raw = formatting.get("files_formatted", [])
    if not isinstance(files_formatted_raw, list):
        validation_warnings.append(
            f"'files_formatted' must be a list, got {type(files_formatted_raw)}"
        )
        files_formatted = []
    else:
        files_formatted = files_formatted_raw

    # Validate formatting_errors
    formatting_errors_raw = formatting.get("errors", [])
    if not isinstance(formatting_errors_raw, list):
        validation_warnings.append(
            f"'errors' must be a list, got {type(formatting_errors_raw)}"
        )
        formatting_errors = []
    else:
        formatting_errors = formatting_errors_raw

    if validation_warnings:
        warning_summary = "; ".join(validation_warnings)
        print(
            log_message(f"WARN: Data type validation issues: {warning_summary}", "WARN")
        )

    print(log_message("DEBUG: Data type validation completed"))
    print(log_message(f"DEBUG: Found {len(files_formatted)} formatted files"))
    print(log_message(f"DEBUG: Found {len(formatting_errors)} formatting errors"))

    return files_formatted, formatting_errors, validation_warnings


def _process_formatting_data(files_formatted, formatting_errors, analysis):
    """
    Process formatting data and update analysis structure.

    Args:
        files_formatted: List of formatted files
        formatting_errors: List of formatting errors
        analysis: Analysis structure to update

    Returns:
        tuple: (updated_analysis, issues_processed)
    """
    print(log_message("DEBUG: Starting formatting data processing"))

    issues_processed = 0

    # Process formatted files
    if files_formatted:
        try:
            formatted_count = len(files_formatted)
            analysis["quality_issues"] = (
                analysis.get("quality_issues", 0) + formatted_count
            )
            analysis["needs_remediation"] = True
            issues_processed += formatted_count
            print(
                log_message(
                    f"DEBUG: Added {formatted_count} quality issues from formatted files"
                )
            )
        except Exception as e:
            error_msg = f"Error processing formatted files: {str(e)}"
            print(log_message(error_msg, "ERROR"))
            analysis["analysis_failures"] = analysis.get("analysis_failures", [])
            analysis["analysis_failures"].append(
                {
                    "function": "_analyze_formatting_issues",
                    "stage": "files_formatted_processing",
                    "error": error_msg,
                    "critical": False,
                }
            )

    # Process formatting errors
    if formatting_errors:
        try:
            error_count = len(formatting_errors)
            analysis["critical_issues"] = (
                analysis.get("critical_issues", 0) + error_count
            )
            analysis["needs_remediation"] = True
            issues_processed += error_count
            print(
                log_message(
                    f"DEBUG: Added {error_count} critical issues from formatting errors"
                )
            )
        except Exception as e:
            error_msg = f"Error processing formatting errors: {str(e)}"
            print(log_message(error_msg, "ERROR"))
            analysis["analysis_failures"] = analysis.get("analysis_failures", [])
            analysis["analysis_failures"].append(
                {
                    "function": "_analyze_formatting_issues",
                    "stage": "formatting_errors_processing",
                    "error": error_msg,
                    "critical": False,
                }
            )

    print(
        log_message(
            f"DEBUG: Analysis operations completed successfully - {issues_processed} total issues processed"
        )
    )
    return analysis, issues_processed


def _verify_formatting_output(
    analysis,
    initial_quality_issues,
    initial_critical_issues,
    files_formatted,
    formatting_errors,
    issues_processed,
    validation_warnings,
):
    """
    Verify formatting analysis output and add completion markers.

    Args:
        analysis: Analysis structure to verify
        initial_quality_issues: Initial count of quality issues
        initial_critical_issues: Initial count of critical issues
        files_formatted: List of formatted files
        formatting_errors: List of formatting errors
        issues_processed: Number of issues processed
        validation_warnings: List of validation warnings

    Returns:
        dict: Updated analysis with completion metadata
    """
    print(log_message("DEBUG: Starting formatting output verification"))

    try:
        # Verify analysis was actually performed
        final_quality_issues = analysis.get("quality_issues", 0)
        final_critical_issues = analysis.get("critical_issues", 0)

        expected_quality_increase = len(files_formatted) if files_formatted else 0
        expected_critical_increase = len(formatting_errors) if formatting_errors else 0

        actual_quality_increase = final_quality_issues - initial_quality_issues
        actual_critical_increase = final_critical_issues - initial_critical_issues

        if actual_quality_increase != expected_quality_increase:
            print(
                log_message(
                    f"WARN: Quality issues count mismatch - expected increase: {expected_quality_increase}, actual: {actual_quality_increase}",
                    "WARN",
                )
            )

        if actual_critical_increase != expected_critical_increase:
            print(
                log_message(
                    f"WARN: Critical issues count mismatch - expected increase: {expected_critical_increase}, actual: {actual_critical_increase}",
                    "WARN",
                )
            )

        # Add analysis completion marker
        analysis["analysis_completion"] = analysis.get("analysis_completion", {})
        analysis["analysis_completion"]["_analyze_formatting_issues"] = {
            "completed": True,
            "issues_processed": issues_processed,
            "quality_issues_added": actual_quality_increase,
            "critical_issues_added": actual_critical_increase,
            "validation_errors": len(validation_warnings),
        }

        print(log_message("DEBUG: Output verification completed successfully"))

    except Exception as e:
        error_msg = f"Error during output verification: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        analysis["analysis_failures"] = analysis.get("analysis_failures", [])
        analysis["analysis_failures"].append(
            {
                "function": "_analyze_formatting_issues",
                "stage": "output_verification",
                "error": error_msg,
                "critical": False,
            }
        )

    return analysis


def _execute_formatting_analysis_pipeline(results, analysis):
    """
    Execute the complete formatting analysis pipeline with consolidated error handling.

    Args:
        results: Quality check results dictionary
        analysis: Analysis structure to update

    Returns:
        tuple: (success, updated_analysis, error_details)
    """
    # Step 1: Input validation
    try:
        _validate_formatting_inputs(results, analysis)
    except (ValueError, TypeError) as e:
        error_msg = (
            f"CRITICAL: Input validation failed in _analyze_formatting_issues: {str(e)}"
        )
        print(log_message(error_msg, "ERROR"))
        return False, analysis, ("input_validation", str(e), True)

    # Step 2: Structure validation
    try:
        formatting = _validate_formatting_structure(results)
    except ValueError as e:
        error_summary = str(e)
        print(
            log_message(
                f"ERROR: Result structure validation failed: {error_summary}", "ERROR"
            )
        )
        return False, analysis, ("structure_validation", error_summary, True)
    except Exception as e:
        error_msg = f"Unexpected error during structure validation: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, analysis, ("structure_validation", error_msg, True)

    # Step 3: Data type validation
    try:
        files_formatted, formatting_errors, validation_warnings = (
            _validate_formatting_data_types(formatting)
        )
        if validation_warnings:
            warning_summary = "; ".join(validation_warnings)
            analysis["analysis_warnings"] = analysis.get("analysis_warnings", [])
            analysis["analysis_warnings"].append(
                {
                    "function": "_analyze_formatting_issues",
                    "stage": "data_validation",
                    "warning": warning_summary,
                }
            )
    except Exception as e:
        error_msg = f"Unexpected error during data validation: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, analysis, ("data_validation", error_msg, True)

    # Step 4: Process data
    try:
        initial_quality_issues = analysis.get("quality_issues", 0)
        initial_critical_issues = analysis.get("critical_issues", 0)
        analysis, issues_processed = _process_formatting_data(
            files_formatted, formatting_errors, analysis
        )
    except Exception as e:
        error_msg = f"Unexpected error during analysis operations: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, analysis, ("analysis_operations", error_msg, True)

    # Step 5: Verify output
    analysis = _verify_formatting_output(
        analysis,
        initial_quality_issues,
        initial_critical_issues,
        files_formatted,
        formatting_errors,
        issues_processed,
        validation_warnings,
    )

    return True, analysis, None


def _analyze_formatting_issues(results, analysis):
    """
    Analyze formatting issues from quality check results with comprehensive validation.

    Implements robust validation and failure detection to prevent misinterpretation
    of analysis failures as "no issues found".

    Args:
        results: Quality check results dictionary
        analysis: Analysis structure to update

    Returns:
        Updated analysis structure with validation metadata

    Raises:
        ValueError: On critical validation failures
        TypeError: On invalid input types
    """
    print(
        log_message(
            "DEBUG: Starting formatting issues analysis with comprehensive validation"
        )
    )

    success, updated_analysis, error_details = _execute_formatting_analysis_pipeline(
        results, analysis
    )

    if not success:
        stage, error_msg, is_critical = error_details
        if stage == "input_validation" and is_critical:
            # Add failure marker to analysis
            updated_analysis["analysis_failures"] = updated_analysis.get(
                "analysis_failures", []
            )
            updated_analysis["analysis_failures"].append(
                {
                    "function": "_analyze_formatting_issues",
                    "stage": stage,
                    "error": error_msg,
                    "critical": is_critical,
                }
            )
            raise ValueError(
                f"CRITICAL: Input validation failed in _analyze_formatting_issues: {error_msg}"
            )
        else:
            # Add failure marker for other errors
            updated_analysis["analysis_failures"] = updated_analysis.get(
                "analysis_failures", []
            )
            updated_analysis["analysis_failures"].append(
                {
                    "function": "_analyze_formatting_issues",
                    "stage": stage,
                    "error": error_msg,
                    "critical": is_critical,
                }
            )
            return updated_analysis

    print(
        log_message(
            f"DEBUG: Formatting analysis complete - needs_remediation: {updated_analysis.get('needs_remediation', False)}"
        )
    )
    return updated_analysis


def _calculate_total_issues(analysis):
    """Calculate total issues across all categories."""
    print(log_message("DEBUG: Calculating total issues across all categories"))

    total = (
        analysis["critical_issues"]
        + analysis["security_issues"]
        + analysis["quality_issues"]
    )

    analysis["total_issues"] = total
    print(
        log_message(
            f"DEBUG: Total issues calculated: {total} (critical: {analysis['critical_issues']}, security: {analysis['security_issues']}, quality: {analysis['quality_issues']})"
        )
    )

    return analysis


def _determine_remediation_priority(analysis):
    """Determine the priority level for remediation based on issue counts."""
    print(
        log_message("DEBUG: Determining remediation priority based on issue analysis")
    )

    if analysis["critical_issues"] > 0:
        priority = "critical"
        print(
            log_message(
                f"DEBUG: Set priority to 'critical' due to {analysis['critical_issues']} critical issues"
            )
        )
    elif analysis["security_issues"] > 0:
        priority = "high"
        print(
            log_message(
                f"DEBUG: Set priority to 'high' due to {analysis['security_issues']} security issues"
            )
        )
    elif analysis["quality_issues"] > 5:
        priority = "medium"
        print(
            log_message(
                f"DEBUG: Set priority to 'medium' due to {analysis['quality_issues']} quality issues (>5)"
            )
        )
    elif analysis["quality_issues"] > 0:
        priority = "low"
        print(
            log_message(
                f"DEBUG: Set priority to 'low' due to {analysis['quality_issues']} quality issues"
            )
        )
    else:
        priority = "none"
        print(log_message("DEBUG: Set priority to 'none' - no issues found"))

    analysis["remediation_priority"] = priority
    print(log_message(f"DEBUG: Final remediation priority: {priority}"))

    return analysis


def _create_issue_summary(analysis):
    """Create a human-readable summary of issues found."""
    print(log_message("DEBUG: Creating issue summary for analysis results"))

    summary_parts = []

    if analysis["critical_issues"]:
        part = f"{analysis['critical_issues']} critical"
        summary_parts.append(part)
        print(log_message(f"DEBUG: Added to summary: {part}"))

    if analysis["security_issues"]:
        part = f"{analysis['security_issues']} security"
        summary_parts.append(part)
        print(log_message(f"DEBUG: Added to summary: {part}"))

    if analysis["quality_issues"]:
        part = f"{analysis['quality_issues']} quality"
        summary_parts.append(part)
        print(log_message(f"DEBUG: Added to summary: {part}"))

    summary = ", ".join(summary_parts) if summary_parts else "no issues"
    analysis["issue_summary"] = summary

    print(log_message(f"DEBUG: Issue summary created: '{summary}'"))
    return analysis


def _validate_input_file(results_file):
    """
    Validate input file path and existence.

    Args:
        results_file: Path to the quality results file

    Returns:
        bool: True if validation passes, False otherwise

    Raises:
        ValueError: On critical validation failures
    """
    if not results_file:
        raise ValueError("Results file path cannot be empty or None")
    if not os.path.exists(results_file):
        raise ValueError(f"Results file does not exist: {results_file}")

    print(log_message("DEBUG: Input validation passed"))
    return True


def _load_and_validate_json(results_file):
    """
    Load and validate JSON structure from results file.

    Args:
        results_file: Path to the quality results file

    Returns:
        dict: Loaded results dictionary, or None on failure

    Raises:
        ValueError: On JSON loading or validation failures
    """
    print(log_message("DEBUG: Loading quality results from file"))

    try:
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        if results is None:
            raise ValueError("Loaded results is None")
        if not isinstance(results, dict):
            raise TypeError(f"Results must be a dictionary, got {type(results)}")

        print(log_message("DEBUG: Quality results loaded and validated successfully"))
        return results

    except (json.JSONDecodeError, ValueError, TypeError, IOError) as e:
        error_msg = f"CRITICAL: Failed to load or validate results file: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        raise ValueError(error_msg)


def _execute_analysis_functions(results, analysis):
    """
    Execute all analysis functions and track completion status.

    Args:
        results: Quality check results dictionary
        analysis: Analysis structure to update

    Returns:
        tuple: (updated_analysis, completed_functions, failed_functions)
    """
    analysis_functions = [
        ("_analyze_formatting_issues", _analyze_formatting_issues),
        ("_calculate_total_issues", _calculate_total_issues),
        ("_determine_remediation_priority", _determine_remediation_priority),
        ("_create_issue_summary", _create_issue_summary),
    ]

    completed_functions = []
    failed_functions = []

    for func_name, func in analysis_functions:
        try:
            print(log_message(f"DEBUG: Executing {func_name}"))

            if func_name == "_analyze_formatting_issues":
                # This function takes results parameter
                updated_analysis = func(results, analysis)
            else:
                # Other functions only take analysis parameter
                updated_analysis = func(analysis)

            if updated_analysis is None:
                raise ValueError(f"{func_name} returned None")
            if not isinstance(updated_analysis, dict):
                raise TypeError(
                    f"{func_name} returned invalid type: {type(updated_analysis)}"
                )

            analysis = updated_analysis
            completed_functions.append(func_name)
            print(log_message(f"DEBUG: {func_name} completed successfully"))

        except Exception as e:
            error_msg = f"CRITICAL: {func_name} failed: {str(e)}"
            print(log_message(error_msg, "ERROR"))
            failed_functions.append(
                {"function": func_name, "error": str(e), "critical": True}
            )

            # Add failure to analysis if possible
            if analysis and isinstance(analysis, dict):
                analysis["analysis_failures"] = analysis.get("analysis_failures", [])
                analysis["analysis_failures"].append(
                    {
                        "function": func_name,
                        "stage": "function_execution",
                        "error": str(e),
                        "critical": True,
                    }
                )

    return analysis, completed_functions, failed_functions


def _validate_analysis_completion(analysis, completed_functions, failed_functions):
    """
    Validate analysis completion and add validation metadata.

    Args:
        analysis: Analysis structure to validate
        completed_functions: List of successfully completed functions
        failed_functions: List of failed functions with error details

    Returns:
        dict: Updated analysis with validation metadata
    """
    # Check for critical analysis failures
    critical_failures = []
    if "analysis_failures" in analysis:
        critical_failures = [
            f for f in analysis["analysis_failures"] if f.get("critical", False)
        ]

    total_functions = 4  # Known number of analysis functions
    completed_count = len(completed_functions)
    failed_count = len(failed_functions)

    print(
        log_message(
            f"DEBUG: Analysis execution summary - Completed: {completed_count}/{total_functions}, Failed: {failed_count}"
        )
    )

    # Determine if analysis is valid
    analysis_valid = True
    validation_issues = []

    # Check function completion rate
    if failed_count > 0:
        analysis_valid = False
        validation_issues.append(f"{failed_count} analysis functions failed")

    # Check for critical failures
    if critical_failures:
        analysis_valid = False
        validation_issues.append(f"{len(critical_failures)} critical analysis failures")

    # Check for missing core analysis components
    required_keys = [
        "total_issues",
        "needs_remediation",
        "remediation_priority",
        "issue_summary",
    ]
    missing_keys = [key for key in required_keys if key not in analysis]
    if missing_keys:
        analysis_valid = False
        validation_issues.append(f"Missing required analysis keys: {missing_keys}")

    # Add validation metadata
    analysis["analysis_validation"] = {
        "valid": analysis_valid,
        "completed_functions": completed_functions,
        "failed_functions": failed_functions,
        "completion_rate": f"{completed_count}/{total_functions}",
        "validation_issues": validation_issues,
        "critical_failures_count": len(critical_failures),
    }

    # Handle invalid analysis
    if not analysis_valid:
        error_summary = "; ".join(validation_issues)
        print(
            log_message(f"ERROR: Analysis validation failed: {error_summary}", "ERROR")
        )

        # Return the analysis with failure information rather than None
        # This allows calling code to distinguish between file loading failures
        # and analysis processing failures
        analysis["analysis_failed"] = True
        analysis["failure_reason"] = error_summary

        print(
            log_message(
                "DEBUG: Returning failed analysis with detailed failure information"
            )
        )
        return analysis

    print(
        log_message(
            "DEBUG: Analysis validation passed - all functions completed successfully"
        )
    )
    return analysis


def _execute_complete_analysis_pipeline(results_file):
    """
    Execute the complete analysis pipeline with consolidated error handling.

    Args:
        results_file: Path to the quality results JSON file

    Returns:
        tuple: (success, results_or_analysis, error_message)
    """
    # Step 1: Validate input file
    try:
        _validate_input_file(results_file)
    except (ValueError, OSError) as e:
        error_msg = (
            f"CRITICAL: Input validation failed in analyze_quality_results: {str(e)}"
        )
        print(log_message(error_msg, "ERROR"))
        return False, None, error_msg

    # Step 2: Load and validate JSON
    try:
        results = _load_and_validate_json(results_file)
    except ValueError:
        return False, None, "JSON loading failed"

    # Step 3: Initialize analysis structure
    try:
        analysis = _initialize_analysis_structure()
        if not analysis or not isinstance(analysis, dict):
            raise ValueError("Failed to initialize analysis structure")
        print(log_message("DEBUG: Analysis structure initialized successfully"))
    except Exception as e:
        error_msg = f"CRITICAL: Failed to initialize analysis structure: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, None, error_msg

    # Step 4: Execute analysis functions
    try:
        analysis, completed_functions, failed_functions = _execute_analysis_functions(
            results, analysis
        )
    except Exception as e:
        error_msg = f"CRITICAL: Analysis functions execution failed: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, None, error_msg

    # Step 5: Validate completion
    try:
        analysis = _validate_analysis_completion(
            analysis, completed_functions, failed_functions
        )
        return True, analysis, None
    except Exception as e:
        error_msg = f"CRITICAL: Analysis validation failed: {str(e)}"
        print(log_message(error_msg, "ERROR"))
        return False, analysis, error_msg


def analyze_quality_results(results_file):
    """
    Analyze quality results to determine if remediation is needed.

    Implements comprehensive analysis failure detection to distinguish between
    "no issues found" and "analysis failed".

    Args:
        results_file: Path to the quality results JSON file

    Returns:
        Analysis dictionary with validation metadata, or None on critical failure

    Raises:
        ValueError: On critical analysis failures that should halt processing
    """
    print(
        log_message(
            f"DEBUG: Starting quality results analysis for file: {results_file}"
        )
    )

    success, analysis, error_msg = _execute_complete_analysis_pipeline(results_file)

    if not success:
        if analysis and isinstance(analysis, dict):
            analysis["analysis_failed"] = True
            analysis["failure_reason"] = f"Validation error: {error_msg}"
            return analysis
        return None

    print(log_message(f"DEBUG: Quality analysis complete - Final analysis: {analysis}"))
    return analysis


def _validate_analysis_input(analysis) -> bool:
    """Validation Layer 1: Input Validation."""
    if not analysis:
        print(log_message("DEBUG: No analysis provided - not triggering remediation"))
        return False

    if not isinstance(analysis, dict):
        print(
            log_message(
                f"ERROR: Invalid analysis type: {type(analysis)} - not triggering remediation"
            )
        )
        return False

    return True


def _check_analysis_failures(analysis) -> bool:
    """Validation Layer 2: Analysis Failure Detection."""
    analysis_failed = analysis.get("analysis_failed", False)
    if analysis_failed:
        failure_reason = analysis.get("failure_reason", "Unknown failure")
        print(
            log_message(
                f"CRITICAL: Analysis failed - {failure_reason} - TRIGGERING REMEDIATION for investigation",
                "ERROR",
            )
        )
        return True

    analysis_validation = analysis.get("analysis_validation", {})
    analysis_valid = analysis_validation.get("valid", True)
    if not analysis_valid:
        validation_issues = analysis_validation.get("validation_issues", [])
        issues_summary = (
            "; ".join(validation_issues)
            if validation_issues
            else "Unknown validation issues"
        )
        print(
            log_message(
                f"ERROR: Analysis validation failed - {issues_summary} - TRIGGERING REMEDIATION for investigation",
                "ERROR",
            )
        )
        return True

    # Check for critical analysis failures that don't necessarily invalidate the entire analysis
    analysis_failures = analysis.get("analysis_failures", [])
    critical_failures = [f for f in analysis_failures if f.get("critical", False)]
    if critical_failures:
        failure_count = len(critical_failures)
        print(
            log_message(
                f"WARN: {failure_count} critical analysis failures detected - TRIGGERING REMEDIATION for investigation",
                "WARN",
            )
        )
        return True

    return False


def _check_priority_based_decision(analysis, min_priority: str) -> bool:
    """Validation Layer 3: Standard Priority-Based Decision."""
    needs_remediation = analysis.get("needs_remediation", False)
    if not needs_remediation:
        print(log_message("DEBUG: Analysis successful - no remediation needed"))
        return False

    # Check priority levels
    priority_order = ["none", "low", "medium", "high", "critical"]
    current_priority = analysis.get("remediation_priority", "none")

    try:
        current_index = priority_order.index(current_priority)
        min_index = priority_order.index(min_priority)
        should_trigger = current_index >= min_index

        if should_trigger:
            print(
                log_message(
                    f"DEBUG: Priority check passed - current: {current_priority} (index {current_index}) >= min: {min_priority} (index {min_index}) - TRIGGERING REMEDIATION"
                )
            )
        else:
            print(
                log_message(
                    f"DEBUG: Priority check failed - current: {current_priority} (index {current_index}) < min: {min_priority} (index {min_index}) - not triggering remediation"
                )
            )

        return should_trigger

    except ValueError as e:
        print(
            log_message(
                f"ERROR: Invalid priority value - current: '{current_priority}', min: '{min_priority}' - {str(e)}",
                "ERROR",
            )
        )
        return False


def should_trigger_remediation(analysis, min_priority="medium"):
    """
    Determine if remediation workflow should be triggered.

    Handles analysis failures separately from successful analysis with no issues.
    Analysis failures may trigger remediation for investigation purposes.

    Args:
        analysis: Analysis dictionary from analyze_quality_results
        min_priority: Minimum priority level to trigger remediation

    Returns:
        bool: True if remediation should be triggered, False otherwise
    """
    print(
        log_message(
            f"DEBUG: Evaluating remediation trigger - min_priority: {min_priority}"
        )
    )

    # Validation Layer 1: Input Validation
    if not _validate_analysis_input(analysis):
        return False

    # Validation Layer 2: Analysis Failure Detection
    if _check_analysis_failures(analysis):
        return True

    # Validation Layer 3: Standard Priority-Based Decision
    return _check_priority_based_decision(analysis, min_priority)


def _setup_git_protection(project_dir, analysis):
    """Set up git protection manager and create protection commit."""
    print(log_message("DEBUG: Starting git protection setup"))

    # Import git protection manager
    import sys
    from pathlib import Path

    print(log_message("DEBUG: Setting up git protection manager imports"))

    # Get the directory where this hook script is located
    hook_script_dir = Path(__file__).parent.resolve()
    tools_dir = hook_script_dir / "tools"
    sys.path.insert(0, str(tools_dir))

    print(log_message(f"DEBUG: Added tools directory to path: {tools_dir}"))

    try:
        from git_protection_manager import GitProtectionManager  # type: ignore

        print(log_message("DEBUG: Successfully imported GitProtectionManager"))
    except ImportError:
        print(
            log_message(
                "Git protection manager not available - proceeding without protection",
                "WARN",
            )
        )
        print(log_message("DEBUG: GitProtectionManager import failed, returning None"))
        return None, None

    # Initialize git protection if available
    print(log_message("DEBUG: Initializing git protection manager"))
    git_manager = GitProtectionManager(Path(project_dir))
    protection_commit_hash = None

    print(log_message("DEBUG: Creating protection commit before automation"))

    # Create protection commit BEFORE automation
    print(log_message("Creating git protection commit before automation..."))
    issue_summary = analysis.get("issue_summary", "unknown issues")
    operation_description = f"Python quality improvements - {issue_summary}"

    print(log_message(f"DEBUG: Protection commit description: {operation_description}"))

    protection_result = git_manager.create_protection_commit(
        operation_description=operation_description,
        target_files=None,  # Will protect entire codebase
    )

    if protection_result["success"]:
        protection_commit_hash = protection_result["commit_hash"]
        print(log_message(f"Protection commit created: {protection_commit_hash}"))
        print(
            log_message(
                f"DEBUG: Protection commit successful: {protection_commit_hash}"
            )
        )
    else:
        print(
            log_message(
                f"Protection commit failed: {protection_result['errors']}",
                "WARN",
            )
        )
        print(
            log_message(
                f"DEBUG: Protection commit failed with errors: {protection_result['errors']}"
            )
        )

    print(log_message("DEBUG: Git protection setup complete"))
    return git_manager, protection_commit_hash


def _get_quality_commands():
    """Get the list of quality remediation commands to execute."""
    print(log_message("DEBUG: Setting up quality commands"))
    quality_commands = [
        ["python", "-m", "black", "--line-length", "88", "."],
        ["python", "-m", "isort", "--profile", "black", "."],
    ]
    print(log_message(f"DEBUG: Will execute {len(quality_commands)} quality commands"))
    return quality_commands


class SubprocessResourceManager:
    """
    Comprehensive subprocess resource management with proper timeout handling and cleanup.

    Implements enterprise-grade subprocess lifecycle management to prevent resource leaks,
    zombie processes, and ensure proper cleanup of all subprocess resources including:
    - Process termination and forced killing
    - File descriptor cleanup
    - Memory resource management
    - Process monitoring and status tracking
    - Comprehensive error handling and logging
    """

    def __init__(self, cmd: list[str], cwd: str, timeout: int = 60):
        """
        Initialize subprocess resource manager.

        Args:
            cmd: Command and arguments to execute
            cwd: Working directory for process execution
            timeout: Maximum execution time in seconds
        """
        self.cmd = cmd
        self.cwd = cwd
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.execution_duration: Optional[float] = None
        self.termination_attempts = 0
        self.kill_attempts = 0
        self.resource_cleanup_completed = False
        self.process_status = "not_started"

        # Process monitoring
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_active = False
        self.status_updates: list[Tuple[float, str]] = []

        debug_print(f"SubprocessResourceManager initialized for cmd: {' '.join(cmd)}")
        debug_print(f"Working directory: {cwd}, Timeout: {timeout}s")

    def __enter__(self):
        """Enter context manager - start process with monitoring."""
        debug_print(
            f"Entering SubprocessResourceManager context for: {' '.join(self.cmd)}"
        )
        self._start_process()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - ensure complete resource cleanup."""
        debug_print("Exiting SubprocessResourceManager context")
        debug_print(f"Exception info: type={exc_type}, value={exc_val}")

        try:
            self._ensure_process_termination()
            self._cleanup_resources()
            self._finalize_monitoring()
        except Exception as e:
            debug_print(f"Error during resource cleanup: {str(e)}")
            # Don't suppress exceptions from cleanup

        debug_print("SubprocessResourceManager context exit completed")
        debug_print(f"Final process status: {self.process_status}")
        debug_print(f"Resource cleanup completed: {self.resource_cleanup_completed}")

    def _start_process(self) -> None:
        """Start the subprocess with comprehensive monitoring."""
        try:
            debug_print(f"Starting subprocess: {' '.join(self.cmd)}")
            self.start_time = time.time()
            self.process_status = "starting"
            self._add_status_update("process_creation_initiated")

            # Create subprocess with proper resource management
            self.process = subprocess.Popen(
                self.cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                # Ensure process group creation for better process management
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
                # Close file descriptors on Windows
                close_fds=True if os.name != "nt" else False,
            )

            self.process_status = "running"
            self._add_status_update(f"process_started_pid_{self.process.pid}")
            debug_print(f"Process started successfully with PID: {self.process.pid}")

            # Start process monitoring
            self._start_monitoring()

        except Exception as e:
            self.process_status = "failed_to_start"
            self._add_status_update(f"process_creation_failed: {str(e)}")
            debug_print(f"Failed to start subprocess: {str(e)}")
            raise RuntimeError(f"Failed to start subprocess: {str(e)}")

    def _start_monitoring(self) -> None:
        """Start background monitoring thread for process lifecycle."""
        if not self.process:
            debug_print("Cannot start monitoring: process is None")
            return

        self.monitor_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_process_lifecycle,
            name=f"ProcessMonitor-{self.process.pid}",
            daemon=True,
        )
        self.monitor_thread.start()
        debug_print(f"Process monitoring thread started for PID: {self.process.pid}")

    def _monitor_process_lifecycle(self) -> None:
        """Monitor process lifecycle and resource usage."""
        try:
            while self.monitor_active and self.process:
                # Check if process is still running
                poll_result = self.process.poll()

                if poll_result is not None:
                    # Process has terminated
                    self.process_status = f"terminated_code_{poll_result}"
                    self._add_status_update(
                        f"process_terminated_naturally_code_{poll_result}"
                    )
                    debug_print(
                        f"Process {self.process.pid} terminated naturally with code {poll_result}"
                    )
                    break

                # Check for timeout
                if self.start_time and (time.time() - self.start_time) > self.timeout:
                    self.process_status = "timed_out"
                    self._add_status_update("process_execution_timeout_detected")
                    debug_print(
                        f"Process {self.process.pid} execution timeout detected"
                    )
                    break

                # Monitor at 100ms intervals
                time.sleep(0.1)

        except Exception as e:
            debug_print(f"Error in process monitoring: {str(e)}")
            self._add_status_update(f"monitoring_error: {str(e)}")

    def execute(self) -> Tuple[bool, subprocess.CompletedProcess]:
        """
        Execute subprocess with comprehensive resource management and timeout handling.

        Returns:
            Tuple of (success, CompletedProcess-like object)
        """
        if not self.process:
            raise RuntimeError("Process not started - call within context manager")

        debug_print(f"Executing subprocess with timeout {self.timeout}s")

        try:
            # Attempt to communicate with timeout
            stdout, stderr = self.process.communicate(timeout=self.timeout)

            self.end_time = time.time()
            if self.start_time is not None:
                self.execution_duration = self.end_time - self.start_time

            # Create CompletedProcess-like result
            result = type(
                "CompletedProcess",
                (),
                {
                    "args": self.cmd,
                    "returncode": self.process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                },
            )()

            success = self.process.returncode == 0
            self.process_status = f"completed_code_{self.process.returncode}"
            self._add_status_update(f"execution_completed_success_{success}")

            debug_print(
                f"Process execution completed in {self.execution_duration:.2f}s"
            )
            debug_print(f"Return code: {self.process.returncode}, Success: {success}")

            return success, result

        except subprocess.TimeoutExpired as e:
            debug_print(f"Process {self.process.pid} timed out after {self.timeout}s")
            self.process_status = "timed_out_expired"
            self._add_status_update("timeout_expired_exception_caught")

            # Handle timeout with proper cleanup
            success, result = self._handle_timeout_cleanup(e)
            return success, result

        except Exception as e:
            debug_print(f"Unexpected error during process execution: {str(e)}")
            self.process_status = "execution_error"
            self._add_status_update(f"execution_error: {str(e)}")

            # Create error result
            result = type(
                "CompletedProcess",
                (),
                {"args": self.cmd, "returncode": -1, "stdout": "", "stderr": str(e)},
            )()

            return False, result

    def _handle_timeout_cleanup(
        self, timeout_exception: subprocess.TimeoutExpired
    ) -> Tuple[bool, subprocess.CompletedProcess]:
        """
        Handle timeout with comprehensive process cleanup and resource management.

        Implements the proper timeout handling pattern:
        1. Attempt graceful termination
        2. Wait for graceful shutdown
        3. Force kill if necessary
        4. Ensure resource cleanup
        5. Collect any available output
        """
        if not self.process:
            debug_print("Cannot handle timeout cleanup: process is None")
            # Create error result for None process case
            result = type(
                "CompletedProcess",
                (),
                {
                    "args": self.cmd,
                    "returncode": -1,
                    "stdout": getattr(timeout_exception, "stdout", "") or "",
                    "stderr": getattr(timeout_exception, "stderr", "")
                    or "Process is None",
                },
            )()
            return False, result

        debug_print(f"Handling timeout cleanup for PID {self.process.pid}")

        # Attempt graceful termination first
        try:
            debug_print(f"Attempting graceful termination of PID {self.process.pid}")
            self.process.terminate()
            self.termination_attempts += 1
            self._add_status_update("graceful_termination_sent")

            # Give process time to terminate gracefully (5 seconds)
            try:
                stdout, stderr = self.process.communicate(timeout=5.0)
                debug_print(f"Process {self.process.pid} terminated gracefully")
                self.process_status = "terminated_gracefully"
                self._add_status_update("graceful_termination_successful")

            except subprocess.TimeoutExpired:
                # Process didn't terminate gracefully, force kill
                debug_print(
                    f"Process {self.process.pid} didn't terminate gracefully, forcing kill"
                )
                self.process.kill()
                self.kill_attempts += 1
                self._add_status_update("forced_kill_sent")

                # Final communication to clean up
                stdout, stderr = self.process.communicate()
                debug_print(f"Process {self.process.pid} killed forcefully")
                self.process_status = "killed_forcefully"
                self._add_status_update("forced_kill_successful")

        except Exception as e:
            debug_print(f"Error during timeout cleanup: {str(e)}")
            self._add_status_update(f"timeout_cleanup_error: {str(e)}")
            stdout, stderr = "", str(e)

        # Record execution metrics
        self.end_time = time.time()
        if self.start_time is not None:
            self.execution_duration = self.end_time - self.start_time

        # Create result object with timeout information
        result = type(
            "CompletedProcess",
            (),
            {
                "args": self.cmd,
                "returncode": -1,  # Timeout return code
                "stdout": getattr(timeout_exception, "stdout", "") or stdout,
                "stderr": getattr(timeout_exception, "stderr", "") or stderr,
            },
        )()

        debug_print(f"Timeout cleanup completed for PID {self.process.pid}")
        debug_print(
            f"Termination attempts: {self.termination_attempts}, Kill attempts: {self.kill_attempts}"
        )

        return False, result

    def _ensure_process_termination(self) -> None:
        """Ensure process is completely terminated and resources are freed."""
        if not self.process:
            debug_print("No process to terminate")
            return

        debug_print(f"Ensuring termination of PID {self.process.pid}")

        # Check if process is already terminated
        if self.process.poll() is not None:
            debug_print(f"Process {self.process.pid} already terminated")
            self._add_status_update("process_already_terminated")
            return

        # Attempt graceful termination
        try:
            debug_print(f"Sending termination signal to PID {self.process.pid}")
            self.process.terminate()
            self.termination_attempts += 1

            # Wait up to 3 seconds for graceful termination
            try:
                self.process.wait(timeout=3.0)
                debug_print(f"Process {self.process.pid} terminated gracefully")
                self._add_status_update("context_exit_graceful_termination")
                return
            except subprocess.TimeoutExpired:
                pass
        except Exception as e:
            debug_print(f"Error during graceful termination: {str(e)}")

        # Force kill if graceful termination failed
        try:
            debug_print(f"Force killing PID {self.process.pid}")
            self.process.kill()
            self.kill_attempts += 1

            # Final wait to ensure process is dead
            self.process.wait(timeout=2.0)
            debug_print(f"Process {self.process.pid} killed successfully")
            self._add_status_update("context_exit_forced_kill")

        except Exception as e:
            debug_print(f"Error during force kill: {str(e)}")
            self._add_status_update(f"termination_error: {str(e)}")

    def _cleanup_resources(self) -> None:
        """Clean up all subprocess resources including file descriptors."""
        debug_print("Cleaning up subprocess resources")

        try:
            if self.process:
                # Close all pipes to free file descriptors
                if self.process.stdin:
                    self.process.stdin.close()
                    debug_print("Closed stdin pipe")

                if self.process.stdout:
                    self.process.stdout.close()
                    debug_print("Closed stdout pipe")

                if self.process.stderr:
                    self.process.stderr.close()
                    debug_print("Closed stderr pipe")

                # Additional cleanup for the process object
                self.process = None
                debug_print("Process object cleared")

            self.resource_cleanup_completed = True
            self._add_status_update("resource_cleanup_completed")
            debug_print("All subprocess resources cleaned up successfully")

        except Exception as e:
            debug_print(f"Error during resource cleanup: {str(e)}")
            self._add_status_update(f"resource_cleanup_error: {str(e)}")

    def _finalize_monitoring(self) -> None:
        """Finalize process monitoring and collect final statistics."""
        debug_print("Finalizing process monitoring")

        try:
            # Stop monitoring
            self.monitor_active = False

            # Wait for monitoring thread to finish
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1.0)
                debug_print("Monitoring thread stopped")

            # Record final metrics
            if self.start_time and not self.end_time:
                self.end_time = time.time()
                self.execution_duration = self.end_time - self.start_time

            self._add_status_update("monitoring_finalized")
            debug_print("Process monitoring finalized")
            debug_print(f"Total status updates: {len(self.status_updates)}")

        except Exception as e:
            debug_print(f"Error finalizing monitoring: {str(e)}")

    def _add_status_update(self, status: str) -> None:
        """Add timestamped status update for process lifecycle tracking."""
        timestamp = time.time()
        self.status_updates.append((timestamp, status))
        debug_print(f"Status update: {status} at {timestamp}")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics and process lifecycle data."""
        return {
            "command": " ".join(self.cmd),
            "working_directory": self.cwd,
            "timeout_configured": self.timeout,
            "process_status": self.process_status,
            "execution_duration": self.execution_duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "termination_attempts": self.termination_attempts,
            "kill_attempts": self.kill_attempts,
            "resource_cleanup_completed": self.resource_cleanup_completed,
            "status_updates_count": len(self.status_updates),
            "status_timeline": self.status_updates,
        }


def _execute_single_quality_command(cmd, project_dir):
    """
    Execute a single quality command with comprehensive resource management and timeout handling.

    This function has been completely rewritten to address CRITICAL subprocess resource leak
    defects and implements enterprise-grade process lifecycle management:

    FIXES IMPLEMENTED:
    1. **Subprocess Resource Management**: Uses context manager for automatic cleanup
    2. **Timeout Handling**: Proper timeout with graceful termination and forced killing
    3. **Process Lifecycle Management**: Comprehensive monitoring and status tracking
    4. **Resource Cleanup**: File descriptor cleanup and memory management
    5. **Zombie Prevention**: Proper process termination and reaping
    6. **Error Recovery**: Robust error handling with resource cleanup
    7. **Comprehensive Logging**: Detailed debug logging for all process operations

    Args:
        cmd: Command and arguments to execute
        project_dir: Working directory for command execution

    Returns:
        bool: True if command executed successfully, False otherwise
    """
    tool_name = cmd[2] if len(cmd) > 2 else cmd[0]

    print(
        log_message(
            f"[SUBPROCESS] Starting resource-managed execution of {tool_name}", "INFO"
        )
    )
    debug_print(f"Executing command with SubprocessResourceManager: {' '.join(cmd)}")
    debug_print(f"Working directory: {project_dir}")

    execution_stats = None

    try:
        # Use SubprocessResourceManager for comprehensive resource management
        with SubprocessResourceManager(cmd, project_dir, timeout=60) as process_manager:
            debug_print(f"SubprocessResourceManager context entered for {tool_name}")

            # Execute the command with full resource management
            success, result = process_manager.execute()

            # Get execution statistics for detailed logging
            execution_stats = process_manager.get_execution_stats()

            # Log execution details
            print(log_message(f"[SUBPROCESS] {tool_name} execution completed", "INFO"))
            debug_print(f"Process execution statistics: {execution_stats}")
            debug_print(f"Command success: {success}")
            debug_print(
                f"Process status: {execution_stats.get('process_status', 'unknown')}"
            )
            debug_print(
                f"Execution duration: {execution_stats.get('execution_duration', 'unknown')}s"
            )
            debug_print(
                f"Resource cleanup: {execution_stats.get('resource_cleanup_completed', False)}"
            )

            # Process the result using existing result processing logic
            return _process_command_result(tool_name, result)

    except RuntimeError as e:
        # Handle process creation failures
        print(
            log_message(
                f"[PROCESS_ERROR] Failed to start {tool_name}: {str(e)}", "ERROR"
            )
        )
        debug_print(f"Process creation failed: {str(e)}")

        if execution_stats:
            debug_print(f"Failed process statistics: {execution_stats}")

        return False

    except Exception as e:
        # Handle unexpected errors with comprehensive logging
        print(
            log_message(
                f"[CRITICAL_ERROR] Unexpected error executing {tool_name}: {str(e)}",
                "ERROR",
            )
        )
        debug_print(
            f"Unexpected exception in _execute_single_quality_command: {str(e)}"
        )
        debug_print(f"Exception type: {type(e).__name__}")

        if execution_stats:
            debug_print(f"Error context - execution statistics: {execution_stats}")
            print(
                log_message(
                    f"[PROCESS_STATS] {tool_name} - Duration: {execution_stats.get('execution_duration', 'N/A')}s, "
                    f"Status: {execution_stats.get('process_status', 'unknown')}, "
                    f"Cleanup: {execution_stats.get('resource_cleanup_completed', False)}",
                    "INFO",
                )
            )

        return False

    finally:
        # Final logging of process execution results
        if execution_stats:
            print(
                log_message(
                    f"[EXECUTION_SUMMARY] {tool_name} - "
                    f"Status: {execution_stats.get('process_status', 'unknown')}, "
                    f"Duration: {execution_stats.get('execution_duration', 'N/A')}s, "
                    f"Terminations: {execution_stats.get('termination_attempts', 0)}, "
                    f"Kills: {execution_stats.get('kill_attempts', 0)}, "
                    f"Cleanup: {execution_stats.get('resource_cleanup_completed', False)}",
                    "INFO",
                )
            )

            debug_print(f"Final process lifecycle summary for {tool_name}:")
            debug_print(
                f"  - Total status updates: {execution_stats.get('status_updates_count', 0)}"
            )
            debug_print("  - Resource management completed successfully")

        debug_print(f"_execute_single_quality_command completed for {tool_name}")


def _process_command_result(tool_name, result):
    """Process the result of a quality command execution."""
    if result.returncode == 0:
        print(log_message(f"[OK] {tool_name} completed successfully"))
        if result.stdout.strip():
            print(log_message(f"Output: {result.stdout.strip()}"))
            print(log_message(f"DEBUG: {tool_name} output logged"))
        return True
    else:
        print(log_message(f"[FAIL] {tool_name} failed: {result.stderr}", "WARN"))
        print(log_message(f"DEBUG: {tool_name} failed with stderr: {result.stderr}"))
        return False


def _log_execution_summary(all_success):
    """Log the final execution summary for quality commands."""
    result_status = "successful" if all_success else "with failures"
    print(log_message(f"DEBUG: Quality command execution complete: {result_status}"))

    if all_success:
        print(log_message("Quality remediation completed successfully"))
    else:
        print(log_message("Some quality remediation steps failed", "WARN"))


def _execute_quality_commands(project_dir, analysis):
    """Execute quality remediation commands with comprehensive logging and error handling."""
    print(log_message("DEBUG: Starting quality command execution"))

    if analysis.get("quality_issues", 0) <= 0:
        print(log_message("DEBUG: No quality issues found, skipping command execution"))
        return True, []

    quality_commands = _get_quality_commands()
    all_success = True
    tools_executed = []

    for cmd in quality_commands:
        tool_name = cmd[2]
        tools_executed.append(tool_name)

        command_success = _execute_single_quality_command(cmd, project_dir)
        if not command_success:
            all_success = False

    _log_execution_summary(all_success)
    return all_success, tools_executed


def _verify_and_handle_compilation(project_dir, git_manager, protection_commit_hash):
    """Verify compilation after automated fixes and handle rollback if needed."""
    print(log_message("DEBUG: Starting compilation verification"))

    # CRITICAL: Verify all modified files still compile after automated fixes
    print(log_message("Verifying files still compile after automated fixes..."))
    compilation_check_passed = verify_files_compile_after_fixes(project_dir)

    print(log_message(f"DEBUG: Compilation check result: {compilation_check_passed}"))

    if not compilation_check_passed:
        print(
            log_message(
                "CRITICAL: Files do not compile after automated fixes!",
                "ERROR",
            )
        )
        print(log_message("Rolling back to protection commit...", "WARN"))
        print(log_message("DEBUG: Starting rollback process"))

        if git_manager and protection_commit_hash:
            print(
                log_message(
                    f"DEBUG: Attempting rollback to commit: {protection_commit_hash}"
                )
            )
            rollback_result = git_manager.rollback_to_protection_commit(
                protection_commit_hash
            )
            if rollback_result["success"]:
                print(log_message("Successfully rolled back to protection commit"))
                print(log_message("DEBUG: Rollback completed successfully"))
            else:
                print(
                    log_message(
                        f"Rollback failed: {rollback_result['errors']}",
                        "ERROR",
                    )
                )
                print(
                    log_message(
                        f"DEBUG: Rollback failed with errors: {rollback_result['errors']}"
                    )
                )
        else:
            print(
                log_message(
                    "DEBUG: No git manager or protection commit available for rollback"
                )
            )

        print(log_message("DEBUG: Returning compilation failure result"))
        return {
            "continue": False,
            "result": {
                "triggered": True,
                "success": False,
                "workflow_executed": True,
                "error": "Files do not compile after automated fixes - rolled back",
            },
        }

    print(log_message("All files compile successfully after automated fixes"))
    print(
        log_message("DEBUG: Compilation verification successful, continuing workflow")
    )

    return {"continue": True, "result": None}


def _handle_completion_workflow(
    git_manager,
    analysis,
    tools_executed,
    files_modified,
    all_success,
    protection_commit_hash,
):
    """Handle completion workflow with comprehensive logging."""
    print(log_message("DEBUG: Starting completion workflow"))

    if all_success:
        print(log_message("DEBUG: Processing successful automation completion"))

        # Create completion commit AFTER automation
        if git_manager:
            print(log_message("DEBUG: Creating completion commit"))
            print(log_message("Creating git completion commit after automation..."))

            operation_description = f"Python quality improvements - {analysis.get('issue_summary', 'unknown issues')}"
            print(
                log_message(
                    f"DEBUG: Completion commit description: {operation_description}"
                )
            )

            execution_summary = {
                "total_issues": analysis.get("total_issues", 0),
                "quality_issues": analysis.get("quality_issues", 0),
                "tools_executed": len(tools_executed),
                "remediation_priority": analysis.get("remediation_priority", "unknown"),
            }
            print(log_message(f"DEBUG: Execution summary: {execution_summary}"))

            completion_result = git_manager.create_completion_commit(
                operation_description=operation_description,
                tools_executed=tools_executed,
                files_modified=files_modified,  # Git manager will detect modified files
                execution_summary=execution_summary,
            )

            if completion_result["success"]:
                completion_commit_hash = completion_result["commit_hash"]
                print(
                    log_message(f"Completion commit created: {completion_commit_hash}")
                )
                print(
                    log_message(
                        f"DEBUG: Completion commit successful: {completion_commit_hash}"
                    )
                )
            else:
                print(
                    log_message(
                        f"Completion commit failed: {completion_result['errors']}",
                        "WARN",
                    )
                )
                print(
                    log_message(
                        f"DEBUG: Completion commit failed with errors: {completion_result['errors']}"
                    )
                )

        print(log_message("DEBUG: Successful automation workflow complete"))
        return True
    else:
        print(log_message("Some quality remediation steps failed", "WARN"))
        print(log_message("DEBUG: Processing failed automation completion"))

        # If automation failed and we have a protection commit, offer rollback info
        if protection_commit_hash:
            rollback_command = f"git reset --hard {protection_commit_hash}"
            print(
                log_message(
                    f"To rollback failed automation: {rollback_command}",
                    "INFO",
                )
            )
            print(log_message(f"DEBUG: Rollback command provided: {rollback_command}"))

        print(log_message("DEBUG: Failed automation workflow complete"))
        return False


def trigger_remediation_workflow(project_dir, results_file, analysis):
    """Trigger quality remediation workflow with git protection."""
    try:
        print(log_message("Triggering quality remediation workflow..."))

        # Setup git protection using extracted function
        git_manager, protection_commit_hash = _setup_git_protection(
            project_dir, analysis
        )

        # Create remediation instructions based on analysis
        remediation_plan = create_remediation_plan(analysis)

        # Write remediation plan to file for future reference
        plan_file = write_remediation_plan(project_dir, remediation_plan, analysis)

        # Execute quality remediation using extracted function
        print(log_message("Executing quality remediation directly..."))
        all_success, tools_executed = _execute_quality_commands(project_dir, analysis)
        files_modified = []  # We'll get this from git status

        if all_success:
            # Verify compilation and handle rollback if needed using extracted function
            compilation_result = _verify_and_handle_compilation(
                project_dir, git_manager, protection_commit_hash
            )

            if not compilation_result["continue"]:
                return compilation_result["result"]

        # Handle completion workflow using extracted function
        return _handle_completion_workflow(
            git_manager,
            analysis,
            tools_executed,
            files_modified,
            all_success,
            protection_commit_hash,
        )

        print(
            log_message(
                f"Remediation plan created: {len(remediation_plan)} steps identified"
            )
        )
        print(log_message(f"Plan saved to: {plan_file}"))
        return True

    except Exception as e:
        print(log_message(f"Error creating remediation workflow: {e}", "ERROR"))
        return False


def create_remediation_plan(analysis):
    """Create a structured remediation plan based on quality analysis."""
    plan = []

    if analysis.get("critical_issues", 0) > 0:
        plan.append(
            {
                "action": "Fix critical compilation and syntax errors",
                "priority": "critical",
                "command_file": "quality/quality-fix-critical.md",
                "estimated_time": "15-30 minutes",
                "description": f"Address {analysis['critical_issues']} critical issues blocking compilation",
            }
        )

    if analysis.get("security_issues", 0) > 0:
        plan.append(
            {
                "action": "Remediate security vulnerabilities",
                "priority": "high",
                "command_file": "quality/quality-fix-security.md",
                "estimated_time": "30-60 minutes",
                "description": f"Fix {analysis['security_issues']} security vulnerabilities",
            }
        )

    if analysis.get("quality_issues", 0) > 0:
        plan.append(
            {
                "action": "Improve code quality and formatting",
                "priority": "medium",
                "command_file": "quality/quality-fix-simple.md",
                "estimated_time": "5-10 minutes",
                "description": f"Address {analysis['quality_issues']} code quality issues",
            }
        )

        plan.append(
            {
                "action": "Update and secure dependencies",
                "priority": "medium",
                "command_file": "quality/quality-fix-dependencies.md",
                "estimated_time": "15-30 minutes",
                "description": "Update packages and resolve dependency conflicts",
            }
        )

    # Always include validation and reporting
    plan.append(
        {
            "action": "Validate all remediation work",
            "priority": "high",
            "command_file": "quality/quality-validate-fixes.md",
            "estimated_time": "10-20 minutes",
            "description": "Run comprehensive validation tests",
        }
    )

    plan.append(
        {
            "action": "Generate comprehensive remediation report",
            "priority": "low",
            "command_file": "quality/quality-generate-report.md",
            "estimated_time": "5-10 minutes",
            "description": "Create detailed report of all improvements",
        }
    )

    return plan


def write_remediation_plan(project_dir, plan, analysis):
    """Write remediation plan to file for future execution."""
    # Use project directory for quality-checks results
    plan_dir = (
        Path(project_dir) / ".claude" / "hooks" / "quality-checks" / "remediation-plans"
    )
    plan_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = plan_dir / f"remediation-plan-{timestamp}.json"

    plan_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "analysis": analysis,
        "total_steps": len(plan),
        "estimated_total_time": "1-3 hours",
        "remediation_plan": plan,
        "execution_instructions": [
            "Review each step in the remediation plan",
            "Execute command files in priority order (critical  high  medium  low)",
            "Validate changes after each major step",
            "Run final validation before considering complete",
        ],
        "next_actions": [
            "Execute .claude/commands/quality/quality-fix-critical.md (if critical issues exist)",
            "Execute .claude/commands/quality/quality-fix-security.md (if security issues exist)",
            "Execute .claude/commands/quality/quality-improve-code.md (if quality issues exist)",
            "Execute .claude/commands/quality/quality-validate-fixes.md (always)",
            "Execute .claude/commands/quality/quality-generate-report.md (always)",
        ],
    }

    try:
        with open(plan_file, "w") as f:
            json.dump(plan_data, f, indent=2)
        return str(plan_file)
    except Exception as e:
        print(log_message(f"Failed to write remediation plan: {e}", "ERROR"))
        return None


def write_trigger_log(project_dir, trigger_data):
    """Write trigger event log."""
    # Use project directory for quality-checks results
    log_dir = Path(project_dir) / ".claude" / "hooks" / "quality-checks" / "triggers"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"remediation-trigger-{timestamp}.json"

    try:
        with open(log_file, "w") as f:
            json.dump(trigger_data, f, indent=2)
        return str(log_file)
    except Exception as e:
        print(log_message(f"Failed to write trigger log: {e}", "ERROR"))
        return None


def _parse_execution_context(
    state_manager: WorkflowStateManager,
) -> Optional[Dict[str, Any]]:
    """Parse execution context from stdin or standalone mode with state management.

    Args:
        state_manager: Workflow state manager for atomic transitions

    Returns:
        Dict containing session_id, project_dir, specific_results_file, and input_data
        or None if parsing failed

    State Transitions:
        PARSING_CONTEXT -> DISCOVERING_RESULTS (success)
        PARSING_CONTEXT -> FAILED (failure)
    """
    debug_print("Starting execution context parsing with state management")

    try:
        if not sys.stdin.isatty():
            # Hook mode - read from stdin
            debug_print("Detected hook mode - reading from stdin")
            input_data = json.load(sys.stdin)
            session_id = input_data.get("session_id", "unknown")
            project_dir = input_data.get("cwd", os.getcwd())
            specific_results_file = input_data.get("results_file")
            debug_print(
                f"Hook mode parsed - session: {session_id[:8]}, dir: {project_dir}"
            )
        else:
            # Standalone mode - use current directory
            debug_print("Detected standalone mode - using current directory")
            session_id = "standalone"
            project_dir = os.getcwd()
            specific_results_file = None
            input_data = {"session_id": session_id, "cwd": project_dir}
            debug_print(f"Standalone mode configured - dir: {project_dir}")

        context = {
            "session_id": session_id,
            "project_dir": project_dir,
            "specific_results_file": specific_results_file,
            "input_data": input_data,
        }
        debug_print(f"Execution context successfully parsed: {len(str(context))} chars")

        # Atomic state transition to next phase
        transition_success = state_manager.transition_to(
            WorkflowState.DISCOVERING_RESULTS,
            data={"context": context},
            rollback_data={
                "temp_files": [],
                "workflow_data_backup": state_manager.workflow_data.copy(),
            },
        )

        if not transition_success:
            debug_print("Failed to transition to DISCOVERING_RESULTS state")
            return None

        return context

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON input: {e}"
        print(log_message(error_msg, "ERROR"), file=sys.stderr)
        debug_print(f"JSON decode error: {e}")

        # Transition to failed state instead of sys.exit
        state_manager.transition_to(
            WorkflowState.FAILED, data={"error": error_msg, "stage": "context_parsing"}
        )
        return None

    except Exception as e:
        error_msg = f"Unexpected error during context parsing: {e}"
        print(log_message(error_msg, "ERROR"), file=sys.stderr)
        debug_print(f"Unexpected error: {e}")

        # Transition to failed state for any unexpected errors
        state_manager.transition_to(
            WorkflowState.FAILED, data={"error": error_msg, "stage": "context_parsing"}
        )
        return None


def _log_skip_decision(
    project_dir: str, session_id: str, results_file: str, analysis: Dict[str, Any]
) -> None:
    """Log the decision to skip remediation workflow.

    Args:
        project_dir: Project directory path
        session_id: Current session identifier
        results_file: Quality results file path
        analysis: Quality analysis results
    """
    debug_print("Logging skip decision for remediation workflow")

    trigger_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "results_file": results_file,
        "analysis": analysis,
        "decision": "skipped",
        "reason": "Below remediation threshold",
    }

    log_file = write_trigger_log(project_dir, trigger_data)
    if log_file:
        debug_print(f"Skip decision logged to: {log_file}")
    else:
        debug_print("Failed to log skip decision")


def _process_quality_workflow(
    context: Dict[str, Any], state_manager: WorkflowStateManager
) -> Optional[Dict[str, Any]]:
    """Process the core quality workflow: discovery, analysis, and decision with state management.

    Args:
        context: Execution context from _parse_execution_context()
        state_manager: Workflow state manager for atomic transitions

    Returns:
        Dict with analysis and workflow decision, or None if workflow should exit

    State Transitions:
        DISCOVERING_RESULTS -> ANALYZING_RESULTS (results found)
        DISCOVERING_RESULTS -> SKIPPED (no results found)
        ANALYZING_RESULTS -> EVALUATING_THRESHOLD (analysis successful)
        ANALYZING_RESULTS -> FAILED (analysis failed)
        EVALUATING_THRESHOLD -> EXECUTING_WORKFLOW (threshold met)
        EVALUATING_THRESHOLD -> SKIPPED (below threshold)
    """
    session_id = context["session_id"]
    project_dir = context["project_dir"]
    specific_results_file = context["specific_results_file"]

    debug_print("Starting quality workflow processing with state management")
    print(log_message(f"Quality remediation trigger - Session: {session_id[:8]}"))
    print(log_message(f"Scanning for quality results in: {project_dir}"))

    # Find latest quality results - state already transitioned to DISCOVERING_RESULTS
    debug_print("Searching for quality results files")
    results_file = find_latest_quality_results(project_dir, specific_results_file)

    if not results_file:
        print(log_message("No quality check results found - skipping remediation"))
        debug_print("No quality results found - transitioning to SKIPPED state")

        # Atomic transition to SKIPPED state
        state_manager.transition_to(
            WorkflowState.SKIPPED,
            data={"reason": "no_results_found", "project_dir": project_dir},
        )
        return None

    print(log_message(f"Found quality results: {results_file}"))
    debug_print(f"Quality results file located: {results_file}")

    # Transition to analyzing results state
    transition_success = state_manager.transition_to(
        WorkflowState.ANALYZING_RESULTS,
        data={"results_file": results_file},
        rollback_data={
            "temp_files": [],
            "workflow_data_backup": state_manager.workflow_data.copy(),
        },
    )

    if not transition_success:
        debug_print("Failed to transition to ANALYZING_RESULTS state")
        return None

    # Analyze quality results
    debug_print("Analyzing quality results")
    analysis = analyze_quality_results(results_file)

    if not analysis:
        print(log_message("Failed to analyze quality results", "ERROR"))
        debug_print("Quality analysis failed - transitioning to FAILED state")

        # Transition to failed state instead of sys.exit
        state_manager.transition_to(
            WorkflowState.FAILED,
            data={
                "error": "analysis_failed",
                "stage": "quality_analysis",
                "results_file": results_file,
            },
        )
        return None

    print(
        log_message(
            f"Quality analysis: {analysis['issue_summary']} ({analysis['remediation_priority']} priority)"
        )
    )
    debug_print(
        f"Analysis completed - {analysis['total_issues']} issues, {analysis['remediation_priority']} priority"
    )

    # Transition to threshold evaluation state
    transition_success = state_manager.transition_to(
        WorkflowState.EVALUATING_THRESHOLD,
        data={"analysis": analysis},
        rollback_data={
            "temp_files": [],
            "workflow_data_backup": state_manager.workflow_data.copy(),
        },
    )

    if not transition_success:
        debug_print("Failed to transition to EVALUATING_THRESHOLD state")
        return None

    # Determine if remediation is needed
    debug_print("Evaluating remediation threshold")
    if not should_trigger_remediation(analysis, min_priority="medium"):
        print(
            log_message(
                "Quality issues below remediation threshold - skipping workflow"
            )
        )
        debug_print(
            "Issues below threshold - logging skip decision and transitioning to SKIPPED"
        )

        _log_skip_decision(project_dir, session_id, results_file, analysis)

        # Atomic transition to SKIPPED state
        state_manager.transition_to(
            WorkflowState.SKIPPED,
            data={"reason": "below_threshold", "analysis": analysis},
        )
        return None

    debug_print(
        f"Remediation threshold met - proceeding with workflow for {analysis['total_issues']} issues"
    )

    # Transition to execution state
    transition_success = state_manager.transition_to(
        WorkflowState.EXECUTING_WORKFLOW,
        data={
            "analysis": analysis,
            "results_file": results_file,
            "should_proceed": True,
        },
        rollback_data={
            "temp_files": [],
            "workflow_data_backup": state_manager.workflow_data.copy(),
        },
    )

    if not transition_success:
        debug_print("Failed to transition to EXECUTING_WORKFLOW state")
        return None

    return {"analysis": analysis, "results_file": results_file, "should_proceed": True}


def _handle_workflow_result(
    context: Dict[str, Any],
    workflow_result: Dict[str, Any],
    state_manager: WorkflowStateManager,
) -> bool:
    """Handle workflow execution result, logging, and status output with state management.

    Args:
        context: Execution context
        workflow_result: Result from _process_quality_workflow()
        state_manager: Workflow state manager for atomic transitions

    Returns:
        True if workflow completed successfully, False otherwise

    State Transitions:
        EXECUTING_WORKFLOW -> LOGGING_RESULTS (workflow execution completed)
        LOGGING_RESULTS -> COMPLETED (success)
        LOGGING_RESULTS -> FAILED (failure)
    """
    session_id = context["session_id"]
    project_dir = context["project_dir"]
    analysis = workflow_result["analysis"]
    results_file = workflow_result["results_file"]

    debug_print("Handling workflow execution and result logging with state management")
    print(
        log_message(
            f"Triggering remediation workflow for {analysis['total_issues']} issues"
        )
    )

    # Trigger remediation workflow - state is already EXECUTING_WORKFLOW
    debug_print("Executing remediation workflow trigger")
    success = trigger_remediation_workflow(project_dir, results_file, analysis)
    debug_print(f"Workflow trigger result: {success}")

    # Transition to logging results state
    transition_success = state_manager.transition_to(
        WorkflowState.LOGGING_RESULTS,
        data={
            "workflow_success": success,
            "analysis": analysis,
            "results_file": results_file,
        },
        rollback_data={
            "temp_files": [],
            "workflow_data_backup": state_manager.workflow_data.copy(),
        },
    )

    if not transition_success:
        debug_print("Failed to transition to LOGGING_RESULTS state")
        return False

    # Log the trigger event
    debug_print("Logging trigger event")
    trigger_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "results_file": results_file,
        "analysis": analysis,
        "decision": "triggered" if success else "failed",
        "workflow_success": success,
    }

    log_file = write_trigger_log(project_dir, trigger_data)
    if log_file:
        print(log_message(f"Trigger event logged: {log_file}"))
        debug_print(f"Trigger event logged to: {log_file}")

    # Handle success/failure outcomes with atomic state transitions
    if success:
        print(
            log_message(
                "Quality remediation workflow preparation completed successfully"
            )
        )
        print(
            log_message(
                "Review the generated remediation plan and execute the recommended command files"
            )
        )
        debug_print(
            "Workflow completed successfully - transitioning to COMPLETED state"
        )

        # Atomic transition to COMPLETED state
        final_transition = state_manager.transition_to(
            WorkflowState.COMPLETED,
            data={"final_status": "success", "log_file": log_file},
        )

        if final_transition:
            debug_print("Workflow completed successfully with atomic state management")
            return True
        else:
            debug_print("Final state transition failed")
            return False

    else:
        print(log_message("Failed to create quality remediation workflow", "ERROR"))
        debug_print("Workflow failed - transitioning to FAILED state")

        # Transition to failed state instead of sys.exit
        state_manager.transition_to(
            WorkflowState.FAILED,
            data={
                "error": "workflow_execution_failed",
                "stage": "remediation_trigger",
                "log_file": log_file,
            },
        )
        return False


def main() -> None:
    """
    Execute main hook with atomic workflow state management and comprehensive error handling.

    Implements a state machine-based approach to ensure atomic state transitions,
    comprehensive rollback capabilities, and consistent state management throughout
    the workflow execution. Replaces direct sys.exit() calls with proper state
    transitions and recovery mechanisms.

    Key Features:
    - Atomic state transitions with validation
    - Comprehensive rollback on partial failures
    - State consistency verification
    - Complete audit trail of all operations
    - Recovery mechanisms for inconsistent states

    State Flow:
    INITIALIZING -> PARSING_CONTEXT -> DISCOVERING_RESULTS -> ANALYZING_RESULTS ->
    EVALUATING_THRESHOLD -> EXECUTING_WORKFLOW -> LOGGING_RESULTS -> COMPLETED/SKIPPED/FAILED

    Exit Codes:
    - 0: Successful completion or workflow skipped
    - 1: Workflow failed with rollback attempted
    - 2: Critical state management failure
    """
    # Generate unique session ID for this workflow execution
    session_id = (
        f"quality-remediation-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )

    debug_print(
        f"Starting main orchestrator with atomic state management - Session: {session_id}"
    )
    print(
        log_message(
            f"Quality remediation workflow starting - Session: {session_id[:16]}"
        )
    )

    # Initialize workflow state manager
    state_manager = WorkflowStateManager(session_id)

    try:
        # =================================================================
        # PHASE 1: CONTEXT PARSING WITH ATOMIC STATE TRANSITION
        # =================================================================
        debug_print("Phase 1: Atomic context parsing with state management")

        # Transition to context parsing state
        if not state_manager.transition_to(WorkflowState.PARSING_CONTEXT):
            print(log_message("Failed to initialize context parsing state", "ERROR"))
            sys.exit(2)  # Critical state management failure

        # Parse execution context with state management
        context = _parse_execution_context(state_manager)

        if context is None:
            debug_print("Context parsing failed - checking state for recovery")
            return _handle_workflow_failure(state_manager, "context_parsing_failed")

        debug_print(
            f"Context parsing completed successfully - Session: {context['session_id'][:8]}"
        )

        # =================================================================
        # PHASE 2: QUALITY WORKFLOW PROCESSING WITH STATE TRANSITIONS
        # =================================================================
        debug_print("Phase 2: Quality workflow processing with atomic state management")

        # Process quality workflow with comprehensive state management
        workflow_result = _process_quality_workflow(context, state_manager)

        # Check for early termination (skipped or failed states)
        current_state = state_manager.get_current_state()
        if current_state in [WorkflowState.SKIPPED, WorkflowState.FAILED]:
            debug_print(f"Workflow terminated in {current_state.name} state")
            return _handle_workflow_termination(state_manager, context)

        if workflow_result is None:
            debug_print("Quality workflow returned None - checking state consistency")
            if current_state != WorkflowState.SKIPPED:
                debug_print(
                    "Inconsistent state detected - workflow returned None but state is not SKIPPED"
                )
                state_manager.transition_to(
                    WorkflowState.FAILED,
                    data={
                        "error": "inconsistent_state",
                        "expected": "SKIPPED",
                        "actual": current_state.name,
                    },
                )
            return _handle_workflow_termination(state_manager, context)

        debug_print(
            "Quality workflow processing completed - proceeding to execution phase"
        )

        # =================================================================
        # PHASE 3: WORKFLOW RESULT HANDLING WITH ATOMIC COMPLETION
        # =================================================================
        debug_print("Phase 3: Workflow result handling with atomic state transitions")

        # Handle workflow result with comprehensive state management
        success = _handle_workflow_result(context, workflow_result, state_manager)

        if not success:
            debug_print("Workflow result handling failed")
            return _handle_workflow_failure(state_manager, "result_handling_failed")

        # =================================================================
        # PHASE 4: WORKFLOW COMPLETION AND STATE VALIDATION
        # =================================================================
        debug_print("Phase 4: Workflow completion validation and cleanup")

        # Validate final state consistency
        final_state = state_manager.get_current_state()
        if final_state != WorkflowState.COMPLETED:
            error_msg = f"Workflow completed but final state is {final_state.name}, expected COMPLETED"
            debug_print(error_msg)
            print(log_message(error_msg, "ERROR"))
            return _handle_workflow_failure(state_manager, "final_state_inconsistent")

        # Generate comprehensive state summary
        state_summary = state_manager.get_state_summary()
        debug_print(
            f"Workflow completed successfully - {state_summary['total_transitions']} state transitions"
        )
        print(log_message("Quality remediation workflow completed successfully"))
        print(
            log_message(
                f"State transitions: {state_summary['successful_transitions']}/{state_summary['total_transitions']} successful"
            )
        )

        # Clean exit with success
        debug_print(
            "Main orchestrator function completed successfully with atomic state management"
        )
        sys.exit(0)

    except Exception as e:
        # Handle any unexpected exceptions with proper state management
        error_msg = f"Unexpected error in main workflow: {str(e)}"
        debug_print(f"Critical error in main function: {error_msg}")
        print(log_message(error_msg, "ERROR"))

        # Attempt to transition to failed state
        try:
            state_manager.transition_to(
                WorkflowState.FAILED,
                data={
                    "error": error_msg,
                    "stage": "main_function",
                    "exception_type": type(e).__name__,
                },
            )
            return _handle_workflow_failure(state_manager, "unexpected_exception")
        except Exception as state_error:
            # Critical state management failure
            debug_print(
                f"Critical: State management failed during error handling: {state_error}"
            )
            print(
                log_message(
                    f"Critical state management failure: {state_error}", "ERROR"
                )
            )
            sys.exit(2)


def _handle_workflow_termination(
    state_manager: WorkflowStateManager, context: Optional[Dict[str, Any]]
) -> None:
    """
    Handle workflow termination for SKIPPED or FAILED states with proper cleanup.

    Args:
        state_manager: Workflow state manager
        context: Execution context (may be None for early failures)
    """
    current_state = state_manager.get_current_state()
    debug_print(f"Handling workflow termination in {current_state.name} state")

    if current_state == WorkflowState.SKIPPED:
        # Clean termination - workflow was skipped
        state_summary = state_manager.get_state_summary()
        print(log_message("Quality remediation workflow skipped"))
        debug_print(
            f"Workflow skipped cleanly - {state_summary['total_transitions']} state transitions"
        )
        sys.exit(0)

    elif current_state == WorkflowState.FAILED:
        # Failed state - attempt rollback
        return _handle_workflow_failure(state_manager, "workflow_failed")

    else:
        # Unexpected state for termination
        error_msg = f"Unexpected termination state: {current_state.name}"
        debug_print(error_msg)
        print(log_message(error_msg, "ERROR"))
        state_manager.transition_to(WorkflowState.FAILED, data={"error": error_msg})
        return _handle_workflow_failure(state_manager, "unexpected_termination_state")


def _handle_workflow_failure(
    state_manager: WorkflowStateManager, failure_reason: str
) -> None:
    """
    Handle workflow failure with comprehensive rollback and state recovery.

    Args:
        state_manager: Workflow state manager
        failure_reason: Reason for workflow failure
    """
    debug_print(f"Handling workflow failure: {failure_reason}")
    print(
        log_message(f"Quality remediation workflow failed: {failure_reason}", "ERROR")
    )

    # Attempt rollback to last stable state
    rollback_success = state_manager.rollback_to_last_stable_state()

    if rollback_success:
        debug_print("Rollback completed successfully")
        print(log_message("Workflow state rolled back to last stable point"))
    else:
        debug_print("Rollback failed or no rollback data available")
        print(
            log_message(
                "Warning: Rollback failed or no recovery data available", "WARN"
            )
        )

    # Generate comprehensive failure report
    state_summary = state_manager.get_state_summary()
    failure_report = {
        "session_id": state_manager.session_id,
        "failure_reason": failure_reason,
        "final_state": state_summary["current_state"],
        "total_transitions": state_summary["total_transitions"],
        "successful_transitions": state_summary["successful_transitions"],
        "failed_transitions": state_summary["failed_transitions"],
        "rollback_attempted": rollback_success,
        "state_history": state_summary["state_history"],
    }

    debug_print(f"Failure report: {failure_report}")
    print(
        log_message(
            f"Failure report logged - {failure_report['failed_transitions']} failed transitions"
        )
    )

    # Exit with failure code
    sys.exit(1)


if __name__ == "__main__":
    main()
