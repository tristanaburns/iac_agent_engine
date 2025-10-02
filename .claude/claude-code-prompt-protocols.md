======================================================================================================================================================================

# CLAUDE CODE PROTOCOLS AND STANDARDS

**Supporting Documentation for claude-code-prompt.md**

This document contains detailed specifications, standards, and protocols that support the core instructions in `claude-code-prompt.md`. All sections in this document are referenced by and must be read in conjunction with the main prompt instructions.

## **CROSS-REFERENCE MAPPING**

This document provides detailed specifications for the following sections in `claude-code-prompt.md`:

- **Section 1**: MCP Servers and Tools → **Protocol Section A**: MCP Server Specifications (includes Git MCP)
- **Section 2**: Python Validation → **Protocol Section B**: Python Quality Standards
- **Section 3**: NodeJS Validation → **Protocol Section C**: NodeJS Quality Standards
- **Section 4**: Production Ready → **Protocol Section D**: Enterprise Grade Standards
- **Section 5**: Architecture → **Protocol Section E**: Architecture Compliance
- **Section 6**: Performance → **Protocol Section F**: Performance Requirements
- **Section 7**: Security → **Protocol Section G**: Security Requirements
- **Section 8**: Monitoring → **Protocol Section H**: Observability Standards
- **Section 9**: Resilience → **Protocol Section I**: Fault Tolerance Patterns
- **Section 10**: Documentation → **Protocol Section J**: Documentation Standards
- **Section 11**: Pre-commit → **Protocol Section K**: Validation Sequences
- **Section 12**: Code Review → **Protocol Section L**: Review Checklists
- **Section 13**: Enforcement → **Protocol Section M**: Production-Ready Enforcement

======================================================================================================================================================================

## **PROTOCOL SECTION A: MCP SERVER SPECIFICATIONS**

_Referenced by: claude-code-prompt.md Section 1 - MCP Servers and Tools_

### **Detailed MCP Server Tool Specifications**

#### **Memory Management Protocols**

**Temporal Memory Operations** (`mcp_memory_*`):

- `mcp_memory_create_entities`: Create session entities with date properties
- `mcp_memory_create_relations`: Create relationships between entities
- `mcp_memory_add_observations`: Add observations with timestamps
- `mcp_memory_search_nodes`: Search with date-based queries
- `mcp_memory_open_nodes`: Retrieve specific entities

**Enduring Memory Operations** (`mcp_neo4j-memory_*`):

- `mcp_neo4j-memory_create_entities`: Create persistent entities
- `mcp_neo4j-memory_create_relations`: Create persistent relationships
- `mcp_neo4j-memory_add_observations`: Add persistent observations
- `mcp_neo4j-memory_search_nodes`: Search persistent knowledge
- `mcp_neo4j-memory_open_nodes`: Retrieve persistent entities

#### **Code Server Tool Specifications**

**Filesystem Operations** (`mcp_filesystem_*`):

- `mcp_filesystem_read_text_file`: Read source files
- `mcp_filesystem_list_directory`: List directory contents
- `mcp_filesystem_search_files`: Search for files by pattern
- `mcp_filesystem_directory_tree`: Get directory structure (FORBIDDEN for root)

**Research Operations**:

- `mcp_fetch_fetch`: Fetch external documentation
- `web_search`: Search for current information
- `mcp_upstash-context7_*`: Access library documentation
- `mcp_grep_searchGitHub`: Search GitHub code examples

#### **Version Control & Code Safety Specifications**

**Git Operations** (`mcp_git`):

- `mcp_git status`: Check repository working directory status
- `mcp_git branch`: List, create, or switch branches
- `mcp_git checkout`: Switch branches or restore files
- `mcp_git add`: Stage files for commit
- `mcp_git commit`: Create commits with messages
- `mcp_git push`: Push changes to remote repository
- `mcp_git pull`: Pull changes from remote repository
- `mcp_git diff`: Show differences between commits/files
- `mcp_git log`: Show commit history
- `mcp_git stash`: Temporarily save changes
- `mcp_git merge`: Merge branches
- `mcp_git reset`: Reset repository state
- `mcp_git clean`: Clean untracked files

### **MANDATORY GIT MCP WORKFLOW SPECIFICATIONS**

#### **Pre-Development Safety Checks**

```bash
# MANDATORY: Always check repository status before any changes
mcp_git status
mcp_git branch  # Verify current branch
mcp_git log --oneline -5  # Check recent commits
```

#### **Feature Development Workflow**

```bash
# MANDATORY: Create feature branch for significant changes
mcp_git checkout -b feature/task-description
mcp_git status  # Verify clean working directory

# During development - stage and commit incrementally
mcp_git add specific-file.py
mcp_git commit -m "feat: implement specific functionality

- Add function X with proper error handling
- Include comprehensive docstrings
- Add unit tests with 95% coverage
- Follow SOLID principles"

# MANDATORY: Review changes before committing
mcp_git diff --cached  # Review staged changes
mcp_git diff  # Review unstaged changes
```

#### **Code Safety and Quality Checks**

```bash
# MANDATORY: Pre-commit safety verification
mcp_git status  # Ensure no untracked files
mcp_git diff --name-only  # List modified files
mcp_git log --oneline -3  # Verify commit history

# MANDATORY: Staging verification
mcp_git add .  # Stage all changes
mcp_git status  # Verify staged files
mcp_git diff --cached --stat  # Review staged changes summary
```

#### **Commit Message Standards**

**MANDATORY COMMIT MESSAGE FORMAT:**

```
<type>: <description>

<body>
<footer>
```

**Required Types:**

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**

```bash
mcp_git commit -m "feat: implement exponential backoff retry pattern

- Add ExponentialBackoff decorator class
- Include configurable retry parameters
- Add comprehensive error handling
- Include unit tests with 100% coverage
- Follow circuit breaker pattern integration

Resolves: #123
Breaking-change: None"
```

#### **Repository Synchronization**

```bash
# MANDATORY: Before pushing changes
mcp_git pull origin main  # Sync with remote
mcp_git status  # Verify clean state
mcp_git push origin feature/task-description  # Push feature branch

# MANDATORY: After task completion
mcp_git checkout main
mcp_git pull origin main
mcp_git merge feature/task-description
mcp_git push origin main
```

#### **Emergency Procedures**

```bash
# MANDATORY: If changes need to be stashed
mcp_git stash push -m "WIP: description of changes"
mcp_git stash list  # Verify stash created

# MANDATORY: If commit needs to be amended
mcp_git add missed-file.py
mcp_git commit --amend --no-edit

# MANDATORY: If reset is needed (CAUTION)
mcp_git reset --soft HEAD~1  # Undo last commit, keep changes
mcp_git reset --hard HEAD~1  # DANGER: Undo last commit, lose changes
```

======================================================================================================================================================================

## **PROTOCOL SECTION B: PYTHON QUALITY STANDARDS**

_Referenced by: claude-code-prompt.md Section 2 - Python Validation_

### **Comprehensive Python Validation Command Specifications**

#### **Core Quality Checks**

- `python -m py_compile` - MUST pass with 0 errors (AST compilation check)
- `python -m mypy .` - MUST pass with 0 errors and 0 warnings (type checking)
- `python -m flake8 .` - MUST pass with 0 errors and 0 warnings (linting)
- `python -m bandit -r .` - MUST pass with 0 security issues (SAST security analysis)
- `python -m safety check` - MUST pass with 0 vulnerabilities (dependency security check)
- `python -m black --check .` - MUST pass with 0 formatting issues (code formatting)
- `python -m isort --check-only .` - MUST pass with 0 import sorting issues (import organization)
- `python -m radon cc . -a` - MUST pass with 0 complexity issues (cyclomatic complexity analysis)
- `python -m radon mi . -a` - MUST pass with 0 maintainability issues (maintainability index)
- `python -m xenon . --max-absolute B --max-modules A --max-average A` - MUST pass with 0 complexity violations

#### **Enhanced Quality Checks**

- `python -m pylint --errors-only --disable=all --enable=E` - MUST pass with 0 errors (strict error checking)
- `python -m vulture . --min-confidence 80` - MUST pass with 0 dead code issues (dead code detection)
- `python -m dodgy .` - MUST pass with 0 hardcoded secrets (secret detection)
- `python -m semgrep --config=auto .` - MUST pass with 0 security vulnerabilities (advanced SAST)
- `python -m docstr-coverage . --fail-under 90` - MUST pass with 90%+ docstring coverage (documentation quality)
- `python -m interrogate . --fail-under 90 --ignore-init-method` - MUST pass with 90%+ docstring coverage (alternative)
- `python -m darglint .` - MUST pass with 0 docstring style violations (docstring validation)
- `python -m perflint .` - MUST pass with 0 performance anti-patterns (performance linting)
- `python -m autoflake --check --recursive .` - MUST pass with 0 unused imports/variables (code cleanup)
- `python -m unimport --check .` - MUST pass with 0 unused imports (import optimization)
- `python -m pydocstyle . --convention=google` - MUST pass with 0 docstring style issues (docstring standards)
- `python -m mccabe --min 10 .` - MUST pass with 0 complexity violations (complexity analysis)
- `python -m pycodestyle .` - MUST pass with 0 style violations (PEP 8 compliance)
- `python -m pydiatra .` - MUST pass with 0 dependency issues (dependency analysis)

#### **Enforced Mandatory Quality Checks**

- `python -m pylint --score=y --fail-under=10` - MUST achieve 10/10 score
- `python -m vulture . --min-confidence 95` - MUST pass with 95%+ confidence
- `python -m dodgy . --severity-level=low` - MUST pass with 0 hardcoded secrets
- `python -m semgrep --config=security .` - MUST pass with 0 security findings
- `python -m docstr-coverage . --fail-under 95` - MUST achieve 95%+ coverage
- `python -m perflint . --strict` - MUST pass with 0 performance issues
- `python -m xenon . --max-absolute A --max-modules A+ --max-average A+` - MUST achieve A+ grade
- `python -m radon cc . --min B --max A` - MUST achieve A grade complexity
- `python -m radon mi . --min A` - MUST achieve A grade maintainability
- `python -m mccabe --min 5 .` - MUST have complexity ≤ 5 (enhanced from ≤ 10)

**PYTHON COMPLIANCE REQUIREMENT**: ALL remaining type violations, security issues, linting errors, code quality issues, and complexity violations MUST be remediated using these patterns to achieve 100% PRODUCTION READY status.

### **MANDATORY NODEJS VALIDATION COMMANDS**

#### **Core Quality Checks**

- `npm run type-check` - MUST pass with 0 errors
- `npm run lint` - MUST pass with 0 errors and 0 warnings
- `npm run quality:check` - MUST pass all checks
- `npm run dev` - MUST start and function without errors
- `npm run build` - MUST complete without errors
- `npm run start` - MUST start and function without errors

#### **Enhanced Quality Checks**

- `npm audit --audit-level=moderate` - MUST pass with 0 vulnerabilities (security audit)
- `npm run test:coverage` - MUST pass with 90%+ code coverage (test coverage)
- `npm run test:unit` - MUST pass with 0 test failures (unit tests)
- `npm run test:integration` - MUST pass with 0 integration test failures
- `npm run test:e2e` - MUST pass with 0 end-to-end test failures
- `npx eslint . --max-warnings 0` - MUST pass with 0 ESLint warnings (strict linting)
- `npx tsc --noEmit --strict` - MUST pass with 0 TypeScript strict mode errors
- `npx prettier --check .` - MUST pass with 0 formatting issues (code formatting)
- `npx depcheck` - MUST pass with 0 unused dependencies (dependency optimization)
- `npx npm-check-updates --doctor` - MUST pass with 0 outdated dependencies (dependency freshness)
- `npx bundlephobia analyze` - MUST pass bundle size checks (performance optimization)
- `npx lighthouse-ci autorun` - MUST pass with 90%+ performance scores (web performance)
- `npx cspell "**/*.{js,ts,json,md}"` - MUST pass with 0 spelling errors (documentation quality)
- `npx license-checker --failOn GPL` - MUST pass with 0 GPL license violations (license compliance)
- `npx audit-ci --config audit-ci.json` - MUST pass with 0 security vulnerabilities (CI security)

#### **Ultra-Strict NodeJS Quality Checks**

- `npx eslint . --max-warnings 0 --max-errors 0` - MUST pass with 0 warnings/errors
- `npx tsc --noEmit --strict --noImplicitAny` - MUST pass strict TypeScript
- `npm audit --audit-level=low` - MUST pass with 0 vulnerabilities (any level)
- `npx bundlephobia analyze --threshold=100kb` - MUST be under 100KB bundle size
- `npx lighthouse-ci autorun --score=95` - MUST achieve 95+ performance score
- `npx depcheck --skip-missing` - MUST have 0 unused dependencies
- `npm run test:coverage -- --coverageThreshold='{"global":{"branches":95,"functions":95,"lines":95,"statements":95}}'` - MUST achieve 95% coverage

**NODEJS COMPLIANCE REQUIREMENT**: ALL remaining `any` type violations MUST be remediated, all type errors, security issues, linting errors, code quality issues, and complexity violations MUST be remediated using these patterns to achieve 100% PRODUCTION READY status.

======================================================================================================================================================================

## **PROTOCOL SECTION C: NODEJS QUALITY STANDARDS**

_Referenced by: claude-code-prompt.md Section 3 - NodeJS Validation_

[Content preserved from original - NodeJS validation commands and requirements]

======================================================================================================================================================================

## **PROTOCOL SECTION D: ENTERPRISE GRADE STANDARDS**

_Referenced by: claude-code-prompt.md Section 4 - Production Ready Definition_

### **MANDATORY QUANTITATIVE METRICS (ALL MUST BE 100%)**

#### **Code Quality Metrics**

- **Lint Errors**: 0 errors, 0 warnings (flake8, eslint)
- **Type Check Errors**: 0 errors, 0 warnings (mypy, tsc)
- **Security Vulnerabilities**: 0 high/critical, 0 medium/low (bandit, safety, npm audit)
- **Code Complexity**: ≤ 8 cyclomatic complexity (enhanced from ≤ 15)
- **Maintainability Index**: ≥ A+ (enhanced from ≥ A)
- **Test Coverage**: ≥ 95% (enhanced from 90%)
- **Documentation Coverage**: ≥ 95% (enhanced from 90%)
- **Code Duplication**: ≤ 5% (enhanced from ≤ 20%)
- **Performance Score**: ≥ 95/100 (Lighthouse, bundle size)

#### **Technical Debt Metrics**

- **Dead Code**: 0 lines (vulture, depcheck)
- **Unused Imports**: 0 imports (autoflake, unimport)
- **TODO Comments**: 0 TODO/FIXME/HACK/STUB comments
- **Hardcoded Values**: 0 hardcoded secrets/credentials
- **Deprecated APIs**: 0 deprecated function calls
- **Memory Leaks**: 0 potential memory leaks (static analysis)

#### **Architecture Quality Metrics**

- **Coupling**: ≤ 3 dependencies per module
- **Cohesion**: ≥ 0.8 cohesion score
- **SOLID Principles**: 100% compliance
- **Design Patterns**: Appropriate pattern usage
- **API Design**: RESTful/GraphQL compliance
- **Error Handling**: 100% exception coverage

### **PRODUCTION READY DEFINITION**

YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS 100% PRODUCTION READY
YOU MUST ALWAYS ENSURE THE PRODUCTION CODEBASE IS 100% CORRECT, WITH 0 ERRORS, WARNINGS AND ISSUES
YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS 100% FULLY FUNCTIONAL
YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS VOID OF MOCK, STUBS, FIXED, CLEAN, ANY WORKROUNDS, ANY TODOS, ANY NON-FUNCTIONAL CODE

PRODUCTION READY = 100% BUILD OF THE PRODUCTION CODEBASE, WITH 0 ERRORS AND 0 WARNINGS
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE IS ENTERPRISE CLASS / LEVEL
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE MEETS THE HIGHEST ENTERPRISE QUALITY STANDARDS
PRODUCTION READY = 100% OF THE PRODUCTION CODE HAS BEEN FULLY IMPLEMENTED AND INTEGRATED

PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS LINT ERRORS AND WARNING = 0
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS TYPECHECK ERRORS AND WARNINGS = 0
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS SECURITY ISSUES = 0
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS ALL THE CODE CYCLOMATIC COMPLEXITY <= 15
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS MAINTAINABILITY INDEX >= A
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS XENON COMPLEXITY VIOLATIONS = 0
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE WITH THE CODE DEDUPLICATION TOTAL <= 5%
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS AST COMPILATION ERRORS = 0
PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE HAS FORMATTING ISSUES = 0

PRODUCTION READY IS NOT EQUAL TO = 99% or LESS OF ANY OF THE DEFINED SUCCESS CRITERIA
PRODUCTION READY IS NOT EQUAL TO = 99% BUILD OF THE PRODUCTION CODEBASE, WITH => 1 ERRORS AND => 1 WARNINGS
PRODUCTION READY IS NOT EQUAL TO = THE PRODUCTION CODEBASE WITH 1 CODEBLOCK AND/ OR 1 FILE WITH CODE COMPLEXITY >= 15
PRODUCTION READY IS NOT EQUAL TO = THE PRODUCTION CODEBASE WITH THE CODE DEDUPLICATION TOTAL >= 5%

**IMPORTANT**
PRODUCTION READY criteria does not apply to any submodules or any other directories and content which is not actually part of the application
This specificially applies to any directory and its contents that is set as git submodules e.g ./submodules/\*

**FORBIDDEN**
YOU ARE FORBIDDEN from creating custom scripts to fix or remediate the code base, YOU HAVE CONTINUIOUSLY corrupted the code base through poor "fix" scripts
YOU MUST NEVER EVER EVER create custom scripts to fix or remediate the code base

======================================================================================================================================================================

## **PROTOCOL SECTION E: ARCHITECTURE COMPLIANCE**

_Referenced by: claude-code-prompt.md Section 5 - Architecture Requirements_

### **MANDATORY ARCHITECTURE COMPLIANCE REQUIREMENTS**

YOU MUST ALWAYS ensure these architectural standards are met:

#### **SOLID Principles Enforcement**

- **Single Responsibility**: Each class/function has exactly one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes must be substitutable for base classes
- **Interface Segregation**: No client should depend on unused methods
- **Dependency Inversion**: Depend on abstractions, not concretions

#### **Design Pattern Compliance**

- **Factory Pattern**: For object creation
- **Strategy Pattern**: For algorithm selection
- **Observer Pattern**: For event handling
- **Repository Pattern**: For data access
- **Service Layer Pattern**: For business logic

#### **Code Organization Standards**

- **Module Structure**: Clear separation of concerns
- **File Naming**: Consistent naming conventions
- **Directory Structure**: Logical organization
- **Import Organization**: Clean import statements
- **Export Strategy**: Clear module exports

======================================================================================================================================================================

## **PROTOCOL SECTION F: PERFORMANCE REQUIREMENTS**

_Referenced by: claude-code-prompt.md Section 6 - Performance Standards_

### **MANDATORY PERFORMANCE REQUIREMENTS**

YOU MUST ALWAYS ensure these performance standards are met:

#### **Runtime Performance**

- **Response Time**: ≤ 100ms for API endpoints
- **Memory Usage**: ≤ 512MB per process
- **CPU Usage**: ≤ 50% under normal load
- **Database Queries**: ≤ 10ms average query time
- **Cache Hit Rate**: ≥ 95% for frequently accessed data

#### **Build Performance**

- **Compilation Time**: ≤ 30 seconds for full build
- **Bundle Size**: ≤ 100KB for web applications
- **Dependency Count**: ≤ 50 direct dependencies
- **Build Artifacts**: Minimal and optimized

======================================================================================================================================================================

## **PROTOCOL SECTION G: SECURITY REQUIREMENTS**

_Referenced by: claude-code-prompt.md Section 7 - Security Standards_

### **MANDATORY SECURITY REQUIREMENTS**

YOU MUST ALWAYS ensure these security standards are met:

#### **Authentication & Authorization**

- **JWT Tokens**: Secure token handling
- **Password Hashing**: bcrypt with salt rounds ≥ 12
- **Session Management**: Secure session handling
- **Role-Based Access**: Proper RBAC implementation
- **API Security**: Rate limiting and input validation

#### **Data Protection**

- **Encryption**: AES-256 for sensitive data
- **SQL Injection**: Parameterized queries only
- **XSS Prevention**: Input sanitization
- **CSRF Protection**: Token-based protection
- **Secrets Management**: No hardcoded credentials

======================================================================================================================================================================

## **PROTOCOL SECTION H: OBSERVABILITY STANDARDS**

_Referenced by: claude-code-prompt.md Section 8 - Monitoring & Observability_

### **MANDATORY MONITORING & OBSERVABILITY**

YOU MUST ALWAYS ensure these observability standards are met:

#### **Logging Standards**

- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: Appropriate level usage
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time logging
- **Audit Trails**: Security event logging

#### **Metrics & Alerting**

- **Health Checks**: Comprehensive health endpoints
- **Performance Metrics**: Response time, throughput
- **Error Rates**: < 0.1% error rate
- **Availability**: 99.9% uptime target
- **Alerting**: Proactive issue detection

======================================================================================================================================================================

## **PROTOCOL SECTION I: FAULT TOLERANCE PATTERNS**

_Referenced by: claude-code-prompt.md Section 9 - Resilience & Fault Tolerance_

### **MANDATORY RESILIENCE & FAULT TOLERANCE REQUIREMENTS**

YOU MUST ALWAYS ensure these resilience and fault tolerance standards are met:

#### **Exponential Backoff & Retry Patterns**

```python
# MANDATORY: All external service calls MUST implement exponential backoff
import time
import random
from typing import Callable, Any, Optional
from functools import wraps

def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """MANDATORY: Exponential backoff decorator for all external calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)

                    time.sleep(delay)

            raise last_exception
        return wrapper
    return decorator

# MANDATORY: Usage example
@exponential_backoff(max_retries=5, base_delay=1.0)
def external_api_call(url: str) -> dict:
    """All external API calls MUST use exponential backoff"""
    # Implementation here
    pass
```

#### **Graceful Failure Handling**

```python
# MANDATORY: All functions MUST handle failures gracefully
from typing import Optional, Union, Any
import logging
from enum import Enum

class FailureMode(Enum):
    """MANDATORY: Define failure modes for graceful degradation"""
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    COMPLETE_FAILURE = "complete_failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

class GracefulFailure:
    """MANDATORY: Base class for graceful failure handling"""

    def __init__(self, fallback_value: Any = None, log_errors: bool = True):
        self.fallback_value = fallback_value
        self.log_errors = log_errors

    def handle_failure(self, error: Exception, context: str = "") -> Any:
        """MANDATORY: Handle failures gracefully with fallback"""
        if self.log_errors:
            logging.error(f"Graceful failure in {context}: {error}")

        return self.fallback_value

# MANDATORY: All functions MUST implement graceful failure
def process_data_with_graceful_failure(data: list) -> Union[list, FailureMode]:
    """MANDATORY: Example of graceful failure handling"""
    failure_handler = GracefulFailure(fallback_value=[], log_errors=True)

    try:
        # Process data
        processed_data = []
        for item in data:
            try:
                result = process_item(item)
                processed_data.append(result)
            except Exception as e:
                logging.warning(f"Failed to process item {item}: {e}")
                # Continue processing other items
                continue

        if not processed_data:
            return FailureMode.COMPLETE_FAILURE

        return processed_data if len(processed_data) == len(data) else FailureMode.PARTIAL_FAILURE

    except Exception as e:
        return failure_handler.handle_failure(e, "process_data_with_graceful_failure")
```

#### **Try-Catch Requirements for All Code Blocks**

```python
# MANDATORY: ALL code blocks MUST have try-catch with specific error handling

# ❌ FORBIDDEN: Code without try-catch
def bad_function():
    result = risky_operation()  # NO TRY-CATCH - FORBIDDEN
    return result

# ✅ MANDATORY: All functions with comprehensive error handling
def good_function() -> Union[Any, FailureMode]:
    """MANDATORY: All functions MUST have try-catch blocks"""
    try:
        # Primary operation
        result = risky_operation()

        # Validate result
        if not validate_result(result):
            logging.warning("Result validation failed")
            return FailureMode.PARTIAL_FAILURE

        return result

    except SpecificException as e:
        # Handle specific exceptions
        logging.error(f"Specific error occurred: {e}")
        return handle_specific_error(e)

    except TimeoutError as e:
        # Handle timeouts
        logging.error(f"Operation timed out: {e}")
        return FailureMode.TIMEOUT

    except RateLimitError as e:
        # Handle rate limiting
        logging.error(f"Rate limited: {e}")
        return FailureMode.RATE_LIMITED

    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return FailureMode.COMPLETE_FAILURE

    finally:
        # MANDATORY: Cleanup operations
        cleanup_resources()

# MANDATORY: Class-level error handling
class ResilientService:
    """MANDATORY: All classes MUST implement comprehensive error handling"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.retry_handler = ExponentialBackoffRetry()

    def process_request(self, request: dict) -> Union[dict, FailureMode]:
        """MANDATORY: All methods MUST have try-catch blocks"""
        try:
            # Validate input
            if not self.validate_request(request):
                return FailureMode.COMPLETE_FAILURE

            # Check circuit breaker
            if not self.circuit_breaker.can_execute():
                return FailureMode.RATE_LIMITED

            # Execute with retry
            result = self.retry_handler.execute(
                lambda: self.execute_request(request)
            )

            # Update circuit breaker
            self.circuit_breaker.record_success()
            return result

        except ValidationError as e:
            logging.error(f"Validation error: {e}")
            return FailureMode.COMPLETE_FAILURE

        except CircuitBreakerOpenError as e:
            logging.warning(f"Circuit breaker open: {e}")
            return FailureMode.RATE_LIMITED

        except Exception as e:
            logging.error(f"Service error: {e}", exc_info=True)
            self.circuit_breaker.record_failure()
            return FailureMode.COMPLETE_FAILURE
```

#### **Circuit Breaker Patterns**

```python
# MANDATORY: Circuit breaker implementation for all external dependencies
from enum import Enum
import time
import logging
from typing import Callable, Any
from functools import wraps

class CircuitState(Enum):
    """MANDATORY: Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """MANDATORY: Circuit breaker for fault tolerance"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:
        """MANDATORY: Check if circuit breaker allows execution"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # HALF_OPEN state
        return True

    def record_success(self) -> None:
        """MANDATORY: Record successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logging.info("Circuit breaker: Success recorded, state = CLOSED")

    def record_failure(self) -> None:
        """MANDATORY: Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logging.error(f"Circuit breaker: OPENED after {self.failure_count} failures")
        else:
            logging.warning(f"Circuit breaker: {self.failure_count}/{self.failure_threshold} failures")

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: type = Exception
):
    """MANDATORY: Circuit breaker decorator for all external calls"""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not breaker.can_execute():
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except breaker.expected_exception as e:
                breaker.record_failure()
                raise e

        return wrapper
    return decorator

# MANDATORY: Usage example
@circuit_breaker(failure_threshold=3, recovery_timeout=30.0)
def external_service_call(data: dict) -> dict:
    """MANDATORY: All external service calls MUST use circuit breaker"""
    # Implementation here
    pass
```

#### **Comprehensive Resilience Validation**

```python
# MANDATORY: Validation tools for resilience patterns
import ast
import re
from typing import List, Dict, Any

class ResilienceValidator:
    """MANDATORY: Validator for resilience pattern compliance"""

    def validate_try_catch_coverage(self, file_path: str) -> Dict[str, Any]:
        """MANDATORY: Ensure all functions have try-catch blocks"""
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())

        violations = []
        functions_without_try_catch = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_try_catch = self._function_has_try_catch(node)
                if not has_try_catch:
                    functions_without_try_catch.append(node.name)

        return {
            'try_catch_coverage': len(functions_without_try_catch) == 0,
            'violations': functions_without_try_catch,
            'coverage_percentage': self._calculate_coverage(tree)
        }

    def validate_retry_patterns(self, file_path: str) -> Dict[str, Any]:
        """MANDATORY: Ensure exponential backoff is implemented"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for retry patterns
        retry_patterns = [
            r'exponential_backoff',
            r'@retry',
            r'tenacity',
            r'backoff'
        ]

        has_retry_patterns = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in retry_patterns
        )

        return {
            'has_retry_patterns': has_retry_patterns,
            'retry_coverage': self._check_external_calls_have_retry(content)
        }

    def validate_circuit_breaker(self, file_path: str) -> Dict[str, Any]:
        """MANDATORY: Ensure circuit breaker patterns are implemented"""
        with open(file_path, 'r') as f:
            content = f.read()

        circuit_breaker_patterns = [
            r'circuit_breaker',
            r'CircuitBreaker',
            r'@circuit_breaker'
        ]

        has_circuit_breaker = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in circuit_breaker_patterns
        )

        return {
            'has_circuit_breaker': has_circuit_breaker,
            'external_calls_protected': self._check_external_calls_protected(content)
        }
```

======================================================================================================================================================================

## **PROTOCOL SECTION J: DOCUMENTATION STANDARDS**

_Referenced by: claude-code-prompt.md Section 10 - Documentation Requirements_

### **MANDATORY DOCUMENTATION REQUIREMENTS FOR AI/LLM OPTIMIZATION**

YOU MUST ALWAYS ensure comprehensive documentation standards are met for enhanced AI/LLM understanding and developer experience:

#### **Comprehensive Docstring Standards**

```python
# MANDATORY: All functions, classes, and modules MUST have comprehensive docstrings

def process_user_data(
    user_id: int,
    data: Dict[str, Any],
    options: Optional[ProcessingOptions] = None,
    validate: bool = True
) -> Union[ProcessingResult, FailureMode]:
    """
    Process user data with comprehensive validation and error handling.

    This function performs the core business logic for user data processing,
    including validation, transformation, and persistence operations. It implements
    exponential backoff retry logic and circuit breaker patterns for external
    service calls.

    Args:
        user_id (int): Unique identifier for the user. Must be positive integer.
        data (Dict[str, Any]): User data dictionary containing:
            - 'profile': User profile information (required)
            - 'preferences': User preferences (optional)
            - 'metadata': Additional metadata (optional)
        options (Optional[ProcessingOptions]): Processing configuration options.
            If None, default options will be used.
        validate (bool): Whether to validate input data. Defaults to True.
            Set to False only for trusted internal calls.

    Returns:
        Union[ProcessingResult, FailureMode]: Processing result containing:
            - ProcessingResult: Success with processed data and metadata
            - FailureMode: Failure mode indicating type of failure

    Raises:
        ValidationError: If input validation fails and validate=True
        AuthenticationError: If user authentication fails
        RateLimitError: If rate limit is exceeded (handled gracefully)
        TimeoutError: If operation times out (handled gracefully)
        ExternalServiceError: If external service fails (handled with retry)

    Examples:
        Basic usage:
        >>> result = process_user_data(123, {'profile': {'name': 'John'}})
        >>> if isinstance(result, ProcessingResult):
        ...     print(f"Processed: {result.data}")

        With custom options:
        >>> options = ProcessingOptions(enable_caching=True, timeout=30)
        >>> result = process_user_data(123, data, options)

        Error handling:
        >>> try:
        ...     result = process_user_data(-1, {})  # Invalid user_id
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")

    Notes:
        - This function implements exponential backoff for external API calls
        - Circuit breaker pattern is used for fault tolerance
        - All operations are logged for audit purposes
        - Resource cleanup is performed automatically in finally blocks
        - Partial failures are handled gracefully with fallback values

    Performance:
        - Average execution time: 150ms
        - Memory usage: ~2MB per request
        - External API calls: 1-3 calls with retry logic
        - Database operations: 2-4 queries with connection pooling

    Security:
        - Input sanitization is performed on all string fields
        - SQL injection protection via parameterized queries
        - Rate limiting prevents abuse
        - Audit logging for all operations

    Dependencies:
        - External services: UserService, DataService, CacheService
        - Database: PostgreSQL with connection pooling
        - Cache: Redis for session management
        - Monitoring: Prometheus metrics collection

    Related:
        - See also: validate_user_data(), transform_user_data()
        - Part of: UserDataProcessingService class
        - Used by: UserRegistrationWorkflow, DataMigrationService

    Version:
        - Added in: v2.1.0
        - Last modified: v2.3.0 (added circuit breaker pattern)
        - Breaking changes: None
        - Deprecated: None

    Todo:
        - [ ] Add support for batch processing
        - [ ] Implement data compression for large datasets
        - [ ] Add metrics for processing time distribution

    Warning:
        - Do not call with validate=False unless you trust the input completely
        - Large datasets (>10MB) may cause memory issues
        - External service downtime will result in FailureMode.RATE_LIMITED
    """
    # Implementation here
    pass
```

#### **Class Documentation Standards**

```python
class UserDataProcessingService:
    """
    Service class for processing user data with comprehensive error handling.

    This service provides a complete solution for user data processing operations,
    including validation, transformation, persistence, and monitoring. It implements
    enterprise-grade patterns for fault tolerance, retry logic, and circuit breaking.

    The service is designed to handle high-throughput scenarios with graceful
    degradation and comprehensive error recovery mechanisms.

    Attributes:
        circuit_breaker (CircuitBreaker): Circuit breaker for external service calls
        retry_handler (ExponentialBackoffRetry): Retry handler with backoff logic
        validator (DataValidator): Input validation service
        transformer (DataTransformer): Data transformation service
        persistence (DataPersistence): Data persistence service
        monitor (ServiceMonitor): Service monitoring and metrics collection

    Configuration:
        The service can be configured via environment variables or configuration files:
        - MAX_RETRIES: Maximum number of retry attempts (default: 3)
        - CIRCUIT_BREAKER_THRESHOLD: Failure threshold for circuit breaker (default: 5)
        - PROCESSING_TIMEOUT: Timeout for processing operations (default: 30s)
        - ENABLE_CACHING: Whether to enable result caching (default: True)
        - LOG_LEVEL: Logging level (default: INFO)

    Examples:
        Basic usage:
        >>> service = UserDataProcessingService()
        >>> result = service.process_user_data(123, user_data)

        With custom configuration:
        >>> config = ProcessingConfig(max_retries=5, timeout=60)
        >>> service = UserDataProcessingService(config=config)

        Batch processing:
        >>> results = service.process_batch(user_data_list)
        >>> successful = [r for r in results if isinstance(r, ProcessingResult)]

    Performance Characteristics:
        - Throughput: 1000+ requests per second
        - Latency: 95th percentile < 200ms
        - Memory usage: ~50MB base + 2MB per concurrent request
        - CPU usage: Moderate, scales linearly with load
        - External dependencies: 3 services with circuit breaker protection

    Error Handling:
        - All external calls use exponential backoff retry
        - Circuit breaker prevents cascading failures
        - Graceful degradation with fallback values
        - Comprehensive logging and monitoring
        - Automatic resource cleanup

    Thread Safety:
        This class is thread-safe and can be used in multi-threaded environments.
        All shared state is protected by appropriate synchronization mechanisms.

        Note: Circuit breaker state is shared across all threads. This is intentional
        for coordinated failure handling across the application.

    Dependencies:
        External Services:
            - UserService: User authentication and authorization
            - DataService: Core data operations and validation
            - CacheService: Caching and session management

        Internal Components:
            - CircuitBreaker: Fault tolerance pattern implementation
            - ExponentialBackoffRetry: Retry logic with backoff
            - DataValidator: Input validation and sanitization
            - DataTransformer: Data transformation and normalization
            - DataPersistence: Database operations with connection pooling
            - ServiceMonitor: Metrics collection and health monitoring

    Monitoring and Observability:
        The service exposes comprehensive metrics:
        - Processing time (histogram)
        - Success/failure rates (counter)
        - Circuit breaker state (gauge)
        - Retry attempts (counter)
        - External service latency (histogram)
        - Memory usage (gauge)
        - Active connections (gauge)

        Health checks are available at /health/processing-service

    Security Considerations:
        - Input validation prevents injection attacks
        - Rate limiting prevents abuse
        - Audit logging for compliance
        - Secure handling of sensitive data
        - Token-based authentication for external services

    Version History:
        - v1.0.0: Initial implementation
        - v1.1.0: Added circuit breaker pattern
        - v1.2.0: Added comprehensive monitoring
        - v2.0.0: Major refactor with improved error handling
        - v2.1.0: Added batch processing support
        - v2.2.0: Performance optimizations

    Future Enhancements:
        - [ ] Add support for streaming data processing
        - [ ] Implement machine learning-based validation
        - [ ] Add support for real-time data processing
        - [ ] Implement distributed processing capabilities

    See Also:
        - ProcessingResult: Result object for successful operations
        - FailureMode: Enumeration of failure modes
        - ProcessingOptions: Configuration options for processing
        - UserDataValidator: Input validation utilities
        - DataTransformationService: Data transformation utilities
    """

    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Initialize the UserDataProcessingService.

        Args:
            config (Optional[ProcessingConfig]): Service configuration.
                If None, default configuration will be used.

        Raises:
            ConfigurationError: If configuration is invalid
            ServiceInitializationError: If service fails to initialize
        """
        pass

    def process_user_data(self, user_id: int, data: Dict[str, Any]) -> Union[ProcessingResult, FailureMode]:
        """
        Process user data with comprehensive error handling.

        See class-level documentation for detailed information about this method.
        """
        pass
```

#### **Module-Level Documentation**

```python
"""
User Data Processing Module

This module provides comprehensive user data processing capabilities with enterprise-grade
fault tolerance, monitoring, and security features.

The module implements the following key patterns:
- Circuit Breaker: Prevents cascading failures from external services
- Exponential Backoff: Intelligent retry logic with jitter
- Graceful Failure Handling: Comprehensive error recovery and fallback strategies
- Comprehensive Monitoring: Metrics collection and health monitoring
- Security Best Practices: Input validation, rate limiting, and audit logging

Key Components:
- UserDataProcessingService: Main service class for data processing
- ProcessingResult: Success result object with metadata
- FailureMode: Enumeration of failure modes for error handling
- ProcessingOptions: Configuration options for processing operations
- CircuitBreaker: Circuit breaker implementation for fault tolerance
- ExponentialBackoffRetry: Retry logic with exponential backoff
- DataValidator: Input validation and sanitization utilities
- DataTransformer: Data transformation and normalization utilities

Usage Example:
    >>> from user_data_processing import UserDataProcessingService, ProcessingOptions
    >>>
    >>> # Initialize service
    >>> service = UserDataProcessingService()
    >>>
    >>> # Process user data
    >>> result = service.process_user_data(123, user_data)
    >>>
    >>> # Handle result
    >>> if isinstance(result, ProcessingResult):
    >>>     print(f"Success: {result.data}")
    >>> else:
    >>>     print(f"Failure: {result}")

Performance Characteristics:
- Throughput: 1000+ requests per second
- Latency: 95th percentile < 200ms
- Memory usage: ~50MB base + 2MB per concurrent request
- External dependencies: 3 services with circuit breaker protection

Error Handling:
All operations implement comprehensive error handling:
- Input validation with detailed error messages
- External service failure handling with retry logic
- Circuit breaker protection against cascading failures
- Graceful degradation with fallback values
- Comprehensive logging and monitoring

Security Features:
- Input sanitization and validation
- SQL injection protection
- Rate limiting and abuse prevention
- Audit logging for compliance
- Secure handling of sensitive data

Dependencies:
- External Services: UserService, DataService, CacheService
- Database: PostgreSQL with connection pooling
- Cache: Redis for session management
- Monitoring: Prometheus metrics collection

Configuration:
The module can be configured via environment variables:
- MAX_RETRIES: Maximum retry attempts (default: 3)
- CIRCUIT_BREAKER_THRESHOLD: Circuit breaker failure threshold (default: 5)
- PROCESSING_TIMEOUT: Operation timeout (default: 30s)
- ENABLE_CACHING: Enable result caching (default: True)
- LOG_LEVEL: Logging level (default: INFO)

Monitoring:
The module exposes comprehensive metrics:
- Processing time distribution
- Success/failure rates
- Circuit breaker state
- Retry attempt counts
- External service latency
- Resource usage metrics

Health Checks:
Health check endpoints are available:
- /health/processing-service: Service health status
- /health/circuit-breakers: Circuit breaker status
- /health/external-services: External service status

Version: 2.2.0
Author: Development Team
License: MIT
Last Updated: 2024-01-15

See Also:
- user_authentication: User authentication and authorization
- data_persistence: Data persistence and database operations
- monitoring: Service monitoring and metrics collection
- security: Security utilities and validation
"""
```

#### **AI/LLM Optimization Documentation Patterns**

```python
# MANDATORY: AI/LLM optimized documentation patterns

def analyze_user_behavior(
    user_id: int,
    time_range: Tuple[datetime, datetime],
    analysis_type: AnalysisType,
    include_metadata: bool = True
) -> UserBehaviorAnalysis:
    """
    AI/LLM OPTIMIZED: Analyze user behavior patterns with comprehensive context.

    CONTEXT FOR AI/LLM:
    This function performs behavioral analysis on user interaction data within a
    specified time range. It's part of the recommendation system that powers
    personalized content delivery and user experience optimization.

    BUSINESS LOGIC:
    The analysis involves multiple stages:
    1. Data collection from user interaction logs
    2. Pattern recognition using machine learning algorithms
    3. Statistical analysis of behavior metrics
    4. Anomaly detection for unusual patterns
    5. Trend analysis for predictive insights

    DATA FLOW:
    Input: user_id → Data Collection → ML Analysis → Statistical Processing → Output
    The function processes data from: clickstream, page views, search queries,
    purchase history, and engagement metrics.

    ALGORITHM DETAILS:
    - Uses collaborative filtering for recommendation generation
    - Implements clustering algorithms for behavior segmentation
    - Applies time series analysis for trend detection
    - Utilizes anomaly detection for fraud prevention

    PERFORMANCE IMPACT:
    - CPU intensive due to ML algorithms
    - Memory usage scales with data volume
    - Database queries optimized with indexes
    - Results cached for 1 hour to reduce computation

    ERROR SCENARIOS:
    - Insufficient data: Returns partial analysis with confidence scores
    - Data corruption: Logs error and returns cached results if available
    - ML model failure: Falls back to rule-based analysis
    - Database timeout: Returns error with retry suggestion

    INTEGRATION POINTS:
    - Called by: RecommendationEngine, PersonalizationService
    - Calls: UserDataService, MLModelService, CacheService
    - Triggers: UserSegmentationUpdate, RecommendationRefresh

    Args:
        user_id: Unique user identifier (positive integer)
        time_range: Analysis period as (start_date, end_date) tuple
        analysis_type: Type of analysis (BEHAVIOR, PURCHASE, ENGAGEMENT, COMPREHENSIVE)
        include_metadata: Whether to include raw metadata in results

    Returns:
        UserBehaviorAnalysis object containing:
        - behavior_patterns: Dict of identified behavior patterns
        - confidence_scores: Confidence levels for each pattern
        - recommendations: Generated recommendations based on analysis
        - metadata: Optional raw data and processing details

    Raises:
        UserNotFoundError: If user_id doesn't exist
        InsufficientDataError: If insufficient data for analysis
        AnalysisTimeoutError: If analysis exceeds time limit
        ModelServiceError: If ML model service is unavailable

    Example Usage:
        >>> from datetime import datetime, timedelta
        >>> end_date = datetime.now()
        >>> start_date = end_date - timedelta(days=30)
        >>>
        >>> analysis = analyze_user_behavior(
        ...     user_id=12345,
        ...     time_range=(start_date, end_date),
        ...     analysis_type=AnalysisType.COMPREHENSIVE,
        ...     include_metadata=True
        ... )
        >>>
        >>> print(f"Found {len(analysis.behavior_patterns)} patterns")
        >>> print(f"Recommendations: {analysis.recommendations}")

    Performance Notes:
        - Average execution time: 2-5 seconds
        - Memory usage: 50-200MB depending on data volume
        - Database queries: 3-5 optimized queries with indexes
        - ML processing: 1-3 seconds for model inference
        - Caching: Results cached for 1 hour with user-specific keys

    Security Considerations:
        - User data access is logged for audit purposes
        - PII is anonymized in analysis results
        - Results are encrypted before storage
        - Access is restricted to authorized services only

    Monitoring Metrics:
        - Analysis completion time (histogram)
        - Success/failure rates (counter)
        - Data volume processed (histogram)
        - ML model inference time (histogram)
        - Cache hit/miss rates (counter)
        - Error rates by type (counter)

    Related Functions:
        - generate_recommendations(): Uses this analysis for recommendations
        - update_user_segments(): Updates user segmentation based on analysis
        - detect_anomalies(): Performs anomaly detection on behavior data
        - calculate_engagement_score(): Calculates user engagement metrics

    Version History:
        - v1.0: Initial implementation with basic pattern recognition
        - v1.1: Added ML model integration
        - v1.2: Added caching and performance optimizations
        - v2.0: Complete rewrite with advanced ML algorithms
        - v2.1: Added anomaly detection and fraud prevention
        - v2.2: Added comprehensive monitoring and metrics
    """
    # Implementation here
    pass
```

======================================================================================================================================================================

## **PROTOCOL SECTION K: VALIDATION SEQUENCES**

_Referenced by: claude-code-prompt.md Section 11 - Pre-commit Validation_

### **MANDATORY PRE-COMMIT VALIDATION SEQUENCE**

YOU MUST ALWAYS execute validation commands in this exact sequence with these gates:

#### **Phase 1: Security & Dependencies (GATE 1)**

1. `mcp_git status` - MUST verify clean working directory
2. `mcp_git branch` - MUST verify current branch
3. `safety check --json` - MUST pass with 0 vulnerabilities
4. `npm audit --audit-level=low` - MUST pass with 0 vulnerabilities
5. `bandit -r . -f json` - MUST pass with 0 high/critical issues
6. `semgrep --config=security --json` - MUST pass with 0 findings

#### **Phase 2: Code Quality & Complexity (GATE 2)**

7. `python -m py_compile` - MUST pass with 0 errors
8. `python -m mypy . --strict` - MUST pass with 0 errors
9. `python -m flake8 . --max-complexity=8` - MUST pass with 0 errors
10. `python -m radon cc . -a` - MUST achieve A grade
11. `python -m xenon . --max-absolute A` - MUST achieve A grade

#### **Phase 3: Testing & Coverage (GATE 3)**

12. `python -m pytest --cov=. --cov-fail-under=95` - MUST achieve 95% coverage
13. `npm run test:coverage -- --coverageThreshold='{"global":{"branches":95,"functions":95,"lines":95,"statements":95}}'`

#### **Phase 4: Documentation & Standards (GATE 4)**

14. `python -m docstr-coverage . --fail-under 95` - MUST achieve 95% coverage
15. `python -m black --check .` - MUST pass with 0 formatting issues
16. `python -m isort --check-only .` - MUST pass with 0 import issues

#### **Phase 5: Performance & Optimization (GATE 5)**

17. `python -m perflint . --strict` - MUST pass with 0 performance issues
18. `npx bundlephobia analyze --threshold=100kb` - MUST be under 100KB
19. `npx lighthouse-ci autorun --score=95` - MUST achieve 95+ score

#### **Phase 6: Resilience & Fault Tolerance (GATE 6)**

20. `python resilience_validator.py --check-try-catch-coverage` - MUST have 100% try-catch coverage
21. `python resilience_validator.py --check-retry-patterns` - MUST have retry patterns for external calls
22. `python resilience_validator.py --check-circuit-breaker` - MUST have circuit breaker patterns
23. `python resilience_validator.py --check-graceful-failure` - MUST have graceful failure handling
24. `python resilience_validator.py --validate-all` - MUST pass all resilience checks

#### **Phase 7: Documentation & AI/LLM Optimization (GATE 7)**

25. `python -m docstr-coverage . --fail-under 95 --include-private` - MUST achieve 95% docstring coverage
26. `python -m interrogate . --fail-under 95 --ignore-init-method --ignore-module` - MUST achieve 95% coverage
27. `python -m darglint . --verbosity 2` - MUST pass with 0 docstring style violations
28. `python documentation_validator.py --check-ai-llm-optimization` - MUST have AI/LLM optimized docs
29. `python documentation_validator.py --validate-comprehensive-docs` - MUST have comprehensive documentation

#### **Phase 8: Git Version Control & Code Safety (GATE 8)**

30. `mcp_git diff --name-only` - MUST review all modified files
31. `mcp_git status` - MUST verify clean working directory
32. `mcp_git add .` - MUST stage all changes
33. `mcp_git commit -m "type: descriptive message"` - MUST commit with proper format
34. `mcp_git push origin branch-name` - MUST push changes to remote repository

**GATE FAILURE**: If ANY command fails, the entire commit is BLOCKED until all issues are resolved.

### **MANDATORY CI/CD INTEGRATION REQUIREMENTS**

YOU MUST ALWAYS ensure these commands are integrated into CI/CD pipelines:

- **Git MCP validation**: Repository status and branch checks MUST pass
- **Pre-commit hooks**: All validation commands MUST run before any commit
- **Pull request validation**: All commands MUST pass before PR merge
- **Build pipeline**: All commands MUST pass before deployment
- **Quality gates**: 0 errors, 0 warnings, 95%+ coverage required
- **Security scanning**: All security checks MUST pass before production deployment
- **Git safety checks**: Clean working directory and proper commit messages required

======================================================================================================================================================================

## **PROTOCOL SECTION L: REVIEW CHECKLISTS**

_Referenced by: claude-code-prompt.md Section 12 - Code Review Requirements_

### **MANDATORY CODE REVIEW CHECKLIST**

YOU MUST ALWAYS verify these items during code review:

#### **Git MCP Version Control & Code Safety (All must be ✅)**

- [ ] Git MCP status shows clean working directory (`mcp_git status`)
- [ ] Git MCP branch verification completed (`mcp_git branch`)
- [ ] Proper Git MCP commit message format used (type: description)
- [ ] All changes staged and committed using Git MCP (`mcp_git add`, `mcp_git commit`)
- [ ] Repository synchronized with remote using Git MCP (`mcp_git push`, `mcp_git pull`)
- [ ] Feature branch workflow followed when applicable (`mcp_git checkout -b feature/name`)
- [ ] Code changes reviewed with Git MCP diff (`mcp_git diff`, `mcp_git diff --cached`)
- [ ] Emergency procedures documented and available (`mcp_git stash`, `mcp_git reset`)
- [ ] Commit history is clean and informative (`mcp_git log --oneline`)
- [ ] No untracked files in working directory (`mcp_git status`)
- [ ] All modified files are intentionally included (`mcp_git diff --name-only`)

#### **Code Quality (All must be ✅)**

- [ ] All validation commands pass with 0 errors/warnings
- [ ] Code complexity ≤ 15 (cyclomatic complexity)
- [ ] Test coverage ≥ 95%
- [ ] Documentation coverage ≥ 95%
- [ ] No dead code or unused imports
- [ ] No TODO/FIXME/HACK comments
- [ ] No hardcoded secrets or credentials
- [ ] No security vulnerabilities
- [ ] No performance anti-patterns
- [ ] No license violations
- [ ] No spelling errors in documentation

#### **Architecture & Design (All must be ✅)**

- [ ] SOLID principles compliance
- [ ] Appropriate design patterns used
- [ ] Clean separation of concerns
- [ ] Proper error handling
- [ ] Input validation implemented
- [ ] Security best practices followed
- [ ] Performance optimizations applied
- [ ] Logging and monitoring in place
- [ ] API design follows REST/GraphQL standards
- [ ] Database queries are optimized

#### **Testing & Quality Assurance (All must be ✅)**

- [ ] Unit tests cover all business logic
- [ ] Integration tests cover API endpoints
- [ ] End-to-end tests cover user workflows
- [ ] Performance tests validate response times
- [ ] Security tests validate authentication/authorization
- [ ] Error scenarios are tested
- [ ] Edge cases are covered
- [ ] Mock objects are properly implemented
- [ ] Test data is realistic and comprehensive
- [ ] Test cleanup is properly handled

#### **Resilience & Fault Tolerance (All must be ✅)**

- [ ] All functions have try-catch blocks with specific error handling
- [ ] Exponential backoff implemented for all external service calls
- [ ] Circuit breaker patterns implemented for external dependencies
- [ ] Graceful failure handling with fallback values
- [ ] Timeout handling for all network operations
- [ ] Rate limiting protection implemented
- [ ] Retry mechanisms with jitter and max retry limits
- [ ] Comprehensive logging for all failure scenarios
- [ ] Resource cleanup in finally blocks
- [ ] Failure mode enumeration and proper handling
- [ ] Partial failure scenarios handled gracefully
- [ ] Health checks validate circuit breaker status
- [ ] Monitoring and alerting for resilience metrics

#### **Documentation & AI/LLM Optimization (All must be ✅)**

- [ ] All functions have comprehensive docstrings with Args, Returns, Raises, Examples
- [ ] All classes have detailed class-level documentation with Attributes, Configuration, Examples
- [ ] All modules have module-level documentation with Usage Examples, Performance Characteristics
- [ ] AI/LLM optimized documentation with CONTEXT, BUSINESS LOGIC, DATA FLOW sections
- [ ] Performance characteristics documented (execution time, memory usage, database queries)
- [ ] Security considerations documented (input validation, rate limiting, audit logging)
- [ ] Dependencies and integration points clearly documented
- [ ] Error scenarios and handling strategies documented
- [ ] Monitoring metrics and health check endpoints documented
- [ ] Version history and breaking changes documented
- [ ] Related functions and cross-references documented
- [ ] Configuration options and environment variables documented
- [ ] Thread safety and concurrency considerations documented

======================================================================================================================================================================

## **PROTOCOL SECTION M: PRODUCTION-READY ENFORCEMENT**

_Referenced by: claude-code-prompt.md Section 13 - Enforcement Mechanisms_

### **MANDATORY PRODUCTION-READY ENFORCEMENT MECHANISMS**

YOU MUST ALWAYS implement these enforcement mechanisms to guarantee production-ready status:

#### **Automated Quality Gates (BLOCKING)**

```bash
# Pre-commit Hook Enforcement
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 ENFORCING PRODUCTION-READY STANDARDS..."

# Gate 0: Git MCP Safety Check
mcp_git status | grep -q "working tree clean" || {
    echo "❌ GIT SAFETY GATE FAILED: Working directory not clean"
    exit 1
}

# Gate 1: Security & Dependencies
safety check --json | jq '.vulnerabilities | length' | grep -q "^0$" || {
    echo "❌ SECURITY GATE FAILED: Vulnerabilities detected"
    exit 1
}

# Gate 2: Code Quality
python -m radon cc . -a | grep -E "(F|D|C)" && {
    echo "❌ COMPLEXITY GATE FAILED: Complexity > 15 detected"
    exit 1
}

python -m xenon . --max-absolute B --max-modules A --max-average A || {
    echo "❌ MAINTAINABILITY GATE FAILED: Maintainability < A"
    exit 1
}

# Gate 3: Testing
coverage run -m pytest && coverage report --fail-under=95 || {
    echo "❌ TESTING GATE FAILED: Coverage < 95%"
    exit 1
}

# Gate 4: Resilience & Fault Tolerance
python resilience_validator.py --validate-all || {
    echo "❌ RESILIENCE GATE FAILED: Fault tolerance patterns not implemented"
    exit 1
}

echo "✅ ALL PRODUCTION-READY GATES PASSED"
```

#### **CI/CD Pipeline Enforcement**

```yaml
# .github/workflows/production-ready.yml
name: Production Ready Enforcement
on: [push, pull_request]

jobs:
  production-ready-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: 🔒 Git Safety Gate
        run: |
          mcp_git status
          mcp_git branch
          mcp_git log --oneline -3

      - name: 🔒 Security Gate
        run: |
          safety check --json
          bandit -r . -f json
          semgrep --config=security --json

      - name: 📊 Quality Gate
        run: |
          python -m radon cc . -a
          python -m xenon . --max-absolute B --max-modules A --max-average A
          python -m mypy . --strict

      - name: 🧪 Testing Gate
        run: |
          python -m pytest --cov=. --cov-fail-under=95
          npm run test:coverage -- --coverageThreshold='{"global":{"branches":95,"functions":95,"lines":95,"statements":95}}'

      - name: 🛡️ Resilience Gate
        run: |
          python resilience_validator.py --validate-all

      - name: 📚 Documentation Gate
        run: |
          python -m docstr-coverage . --fail-under 95 --include-private
          python -m interrogate . --fail-under 95 --ignore-init-method --ignore-module
          python -m darglint . --verbosity 2
          python documentation_validator.py --validate-comprehensive-docs

      - name: 🚫 BLOCK DEPLOYMENT IF FAILED
        if: failure()
        run: |
          echo "❌ PRODUCTION-READY STANDARDS NOT MET"
          echo "🚫 DEPLOYMENT BLOCKED"
          exit 1
```

#### **Real-time Monitoring & Alerting**

```python
# production_ready_monitor.py
import subprocess
import json
import time
from typing import Dict, Any

class ProductionReadyMonitor:
    def __init__(self):
        self.thresholds = {
            'git_working_directory_clean': True,
            'git_branch_valid': True,
            'git_commit_format_valid': True,
            'complexity': 15,
            'maintainability': 'A',
            'coverage': 95,
            'security_vulnerabilities': 0,
            'lint_errors': 0,
            'type_errors': 0,
            'try_catch_coverage': 100,
            'retry_patterns': True,
            'circuit_breaker_patterns': True,
            'graceful_failure_handling': True,
            'docstring_coverage': 95,
            'ai_llm_optimized_docs': True,
            'comprehensive_documentation': True
        }

    def check_git_working_directory_clean(self) -> bool:
        """Check Git working directory is clean"""
        result = subprocess.run(['mcp_git', 'status', '--porcelain'],
                              capture_output=True, text=True)
        return result.stdout.strip() == ""

    def check_git_branch_valid(self) -> bool:
        """Check Git branch is valid (not detached HEAD)"""
        result = subprocess.run(['mcp_git', 'branch', '--show-current'],
                              capture_output=True, text=True)
        return result.stdout.strip() != ""

    def check_git_commit_format_valid(self) -> bool:
        """Check last Git commit message follows format"""
        result = subprocess.run(['mcp_git', 'log', '--format=%s', '-1'],
                              capture_output=True, text=True)
        commit_msg = result.stdout.strip()
        # Check if commit message starts with valid type
        valid_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
        return any(commit_msg.startswith(f"{t}:") for t in valid_types)

    def check_complexity(self) -> bool:
        """Check cyclomatic complexity <= 15"""
        result = subprocess.run(['python', '-m', 'radon', 'cc', '.', '-a'],
                              capture_output=True, text=True)
        # Parse output for complexity violations > 15
        return self._parse_complexity_output(result.stdout)

    def check_maintainability(self) -> bool:
        """Check maintainability index >= A"""
        result = subprocess.run(['python', '-m', 'xenon', '.', '--max-absolute', 'B'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_coverage(self) -> bool:
        """Check test coverage >= 95%"""
        result = subprocess.run(['coverage', 'report', '--format=json'],
                              capture_output=True, text=True)
        coverage_data = json.loads(result.stdout)
        return coverage_data['totals']['percent_covered'] >= 95

    def check_try_catch_coverage(self) -> bool:
        """Check try-catch coverage = 100%"""
        result = subprocess.run(['python', 'resilience_validator.py', '--check-try-catch-coverage'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_retry_patterns(self) -> bool:
        """Check retry patterns implemented"""
        result = subprocess.run(['python', 'resilience_validator.py', '--check-retry-patterns'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_circuit_breaker_patterns(self) -> bool:
        """Check circuit breaker patterns implemented"""
        result = subprocess.run(['python', 'resilience_validator.py', '--check-circuit-breaker'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_graceful_failure_handling(self) -> bool:
        """Check graceful failure handling implemented"""
        result = subprocess.run(['python', 'resilience_validator.py', '--check-graceful-failure'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_docstring_coverage(self) -> bool:
        """Check docstring coverage >= 95%"""
        result = subprocess.run(['python', '-m', 'docstr-coverage', '.', '--fail-under=95', '--include-private'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_ai_llm_optimized_docs(self) -> bool:
        """Check AI/LLM optimized documentation"""
        result = subprocess.run(['python', 'documentation_validator.py', '--check-ai-llm-optimization'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def check_comprehensive_documentation(self) -> bool:
        """Check comprehensive documentation standards"""
        result = subprocess.run(['python', 'documentation_validator.py', '--validate-comprehensive-docs'],
                              capture_output=True, text=True)
        return result.returncode == 0

    def enforce_production_ready(self) -> Dict[str, Any]:
        """Enforce all production-ready criteria"""
        checks = {
            'git_working_directory_clean': self.check_git_working_directory_clean(),
            'git_branch_valid': self.check_git_branch_valid(),
            'git_commit_format_valid': self.check_git_commit_format_valid(),
            'complexity': self.check_complexity(),
            'maintainability': self.check_maintainability(),
            'coverage': self.check_coverage(),
            'security': self.check_security(),
            'linting': self.check_linting(),
            'typing': self.check_typing(),
            'try_catch_coverage': self.check_try_catch_coverage(),
            'retry_patterns': self.check_retry_patterns(),
            'circuit_breaker_patterns': self.check_circuit_breaker_patterns(),
            'graceful_failure_handling': self.check_graceful_failure_handling(),
            'docstring_coverage': self.check_docstring_coverage(),
            'ai_llm_optimized_docs': self.check_ai_llm_optimized_docs(),
            'comprehensive_documentation': self.check_comprehensive_documentation()
        }

        all_passed = all(checks.values())

        if not all_passed:
            self._trigger_alert(checks)
            self._block_deployment()

        return {
            'production_ready': all_passed,
            'checks': checks,
            'timestamp': time.time()
        }

    def _trigger_alert(self, failed_checks: Dict[str, bool]) -> None:
        """Trigger alert for failed production-ready checks"""
        failed = [check for check, passed in failed_checks.items() if not passed]
        print(f"🚨 PRODUCTION-READY ALERT: Failed checks: {failed}")
        # Send to monitoring system (DataDog, New Relic, etc.)

    def _block_deployment(self) -> None:
        """Block deployment if production-ready standards not met"""
        print("🚫 DEPLOYMENT BLOCKED: Production-ready standards not met")
        # Update deployment status in CI/CD system
```

#### **Git Hooks for Enforcement**

```bash
# .git/hooks/pre-push
#!/bin/bash
echo "🔍 PRE-PUSH: Enforcing Production-Ready Standards..."

# Run comprehensive production-ready check
python production_ready_monitor.py --enforce

if [ $? -ne 0 ]; then
    echo "❌ PUSH BLOCKED: Production-ready standards not met"
    echo "📋 Required actions:"
    echo "   - Ensure Git working directory is clean"
    echo "   - Verify Git branch is valid (not detached HEAD)"
    echo "   - Use proper Git commit message format (type: description)"
    echo "   - Fix complexity violations (≤ 15)"
    echo "   - Improve maintainability (≥ A)"
    echo "   - Increase test coverage (≥ 95%)"
    echo "   - Resolve security vulnerabilities (0)"
    echo "   - Fix linting errors (0)"
    echo "   - Resolve type errors (0)"
    echo "   - Add try-catch blocks to all functions (100%)"
    echo "   - Implement exponential backoff for external calls"
    echo "   - Add circuit breaker patterns"
    echo "   - Implement graceful failure handling"
    echo "   - Add comprehensive docstrings to all functions (95% coverage)"
    echo "   - Add AI/LLM optimized documentation"
    echo "   - Add comprehensive documentation standards"
    exit 1
fi

echo "✅ PUSH ALLOWED: All production-ready standards met"
```

#### **Package.json Scripts for Enforcement**

```json
{
  "scripts": {
    "prod-ready:check": "node scripts/production-ready-check.js",
    "prod-ready:enforce": "npm run prod-ready:check && echo '✅ Production Ready' || (echo '❌ Not Production Ready' && exit 1)",
    "precommit": "npm run prod-ready:enforce",
    "prebuild": "npm run prod-ready:enforce",
    "predeploy": "npm run prod-ready:enforce"
  }
}
```

#### **VS Code Workspace Settings for Enforcement**

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-complexity=15"],
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": ["--strict"],
  "python.testing.pytestEnabled": true,
  "python.testing.coverageEnabled": true,
  "python.testing.coverageThreshold": 95,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true
  }
}
```

#### **Docker Multi-stage Build Enforcement**

```dockerfile
# Dockerfile with production-ready enforcement
FROM python:3.11-slim as quality-check

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Enforce production-ready standards
RUN python -m radon cc . -a | grep -E "(F|D|C)" && exit 1 || true
RUN python -m xenon . --max-absolute B --max-modules A --max-average A
RUN python -m pytest --cov=. --cov-fail-under=95
RUN python -m mypy . --strict
RUN python -m flake8 . --max-complexity=15

# Only proceed if all checks pass
FROM python:3.11-slim as production

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
```

#### **Kubernetes Health Checks with Production-Ready Validation**

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-ready-app
spec:
  template:
    spec:
      containers:
        - name: app
          image: production-ready-app:latest
          livenessProbe:
            httpGet:
              path: /health/production-ready
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/production-ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

```python
# health_check_endpoint.py
from fastapi import FastAPI, HTTPException
from production_ready_monitor import ProductionReadyMonitor

app = FastAPI()
monitor = ProductionReadyMonitor()

@app.get("/health/production-ready")
async def production_ready_health():
    """Health check endpoint that validates production-ready status"""
    status = monitor.enforce_production_ready()

    if not status['production_ready']:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Service not production-ready",
                "failed_checks": [k for k, v in status['checks'].items() if not v]
            }
        )

    return {"status": "production-ready", "checks": status['checks']}
```

### **ENFORCEMENT SUMMARY**

These mechanisms provide **multiple layers of enforcement**:

1. **Git MCP Safety**: Mandatory version control and code safety checks
2. **Pre-commit Hooks**: Block commits that don't meet standards
3. **CI/CD Pipelines**: Block deployments that don't meet standards
4. **Real-time Monitoring**: Continuous validation with alerts
5. **Git Hooks**: Block pushes that don't meet standards
6. **Package Scripts**: Automated checks before build/deploy
7. **VS Code Settings**: IDE-level enforcement
8. **Docker Builds**: Multi-stage validation
9. **Kubernetes Health Checks**: Runtime validation

**Result**: It MUST NEVER BE POSSIBLE to deploy code that doesn't meet these production-ready standards!

======================================================================================================================================================================
