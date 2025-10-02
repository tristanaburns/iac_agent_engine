# MANDATORY CANNONICAL PROTOCOL AND INSTRUCTIONS

## **CRITICAL MANDATORY REQUIREMENTS**

**ABSOLUTELY MANDATORY - ZERO TOLERANCE FOR NON-COMPLIANCE**

YOU MUST ALWAYS use **Sequential Thinking MCP** (`mcp_sequential-thinking_sequentialthinking`) for ALL task planning and analysis
YOU MUST ALWAYS use **TODO list management** (`todo_write`) to track ALL tasks, actions, and progress
YOU MUST ALWAYS use your claude code sub agents to complete ALL the instructions with ZERO exceptions
YOU MUST ALWAYS use the claude code sub agents to complete ALL the tasks and actions with COMPLETE execution
YOU MUST ALWAYS ensure that all current and/or previous incomplete instructions, actions or tasks are prioritized and completed before undertaking any new actions or tasks
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

## **ABSOLUTELY FORBIDDEN - ZERO EXCEPTIONS**

**CRITICAL PROHIBITION - STRICTLY ENFORCED**

YOU ARE ABSOLUTELY FORBIDDEN from creating custom scripts to fix or remediate the code base - YOU HAVE CONTINUOUSLY corrupted the code base through poor "fix" scripts
YOU MUST NEVER EVER EVER create custom scripts to fix or remediate the code base under ANY circumstances
YOU MUST NEVER create temporary files, workaround scripts, or any form of automated remediation scripts
**VIOLATION OF THIS PROHIBITION WILL RESULT IN IMMEDIATE TASK TERMINATION AND SESSION ABORTION**

**ONLY ALLOWED APPROACHES:**

- Direct code editing using proper tools (`search_replace`, `write`, `MultiEdit`)
- Manual code review and improvement
- Using existing validation and quality tools
- Following established patterns and best practices

## **MCP SERVERS AND TOOLS - MANDATORY USAGE**

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use MCP SERVER TOOLS to complete ALL instructions and tasks with ZERO exceptions
YOU MUST NEVER attempt to complete any task without using the appropriate MCP server tools
**NON-COMPLIANCE WILL RESULT IN IMMEDIATE TASK FAILURE**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section A: MCP Server Specifications** in `claude-code-prompt-protocols.md` before using any MCP tools. This section contains detailed specifications for all MCP server operations and tool usage requirements.

### **MCP Memory AND THINKING Management - STRICTLY ENFORCED**

**MANDATORY USAGE - ZERO TOLERANCE FOR NON-COMPLIANCE**

YOU MUST ALWAYS use these MCP MEMORY AND THINKING tools with ZERO exceptions:

- **Temporal Memory**: `mcp_memory_*` (Memory Management MCP) - MANDATORY for session tracking
- **Sequential Thinking**: `mcp_sequential-thinking_sequentialthinking` (Sequential Thinking MCP) - MANDATORY for all planning
- **Enduring Memory**: `mcp_neo4j-memory_*` (Neo4j Memory MCP with persistent storage) - MANDATORY for persistence

**ABSOLUTELY MANDATORY REQUIREMENTS:**
YOU MUST ALWAYS add and use a date property to ALL memory and extended memory entries and objects
YOU MUST ALWAYS use **Temporal Memory** (`mcp_memory_*`) to track current session progress - NO EXCEPTIONS
YOU MUST ALWAYS use a date property to find, search and query the **Temporal Memory** and **Enduring Memory** entries and objects
**FAILURE TO COMPLY WILL RESULT IN IMMEDIATE TASK TERMINATION**

#### **Enduring Memory - MANDATORY PERSISTENCE**

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS ensure that ALL context, outcomes, knowledge and decisions in this session and previous sessions are saved and recorded in the **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`) - NO EXCEPTIONS
YOU MUST ALWAYS add or update the **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`) entries and objects where there is missing or incomplete content for this session and previous sessions
YOU MUST ALWAYS use **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`) to understand the context, outcomes, knowledge and decisions in this session and previous sessions prior to commencing ANY further action or undertaking ANY tasks
YOU MUST ALWAYS begin by using the date props to search and/or query (with pagination) **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`) for entries for ALL content the past 4-48 hours (using the current date & time as the starting point)
YOU MUST ALWAYS iteratively perform queries and/or searches to the **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`), to ensure you have sufficient factual information regarding context, outcomes, knowledge and decisions in this session and previous sessions
YOU MUST ALWAYS ensure that you have current factual information regarding the context, outcomes, knowledge and decisions in this session and previous sessions
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

#### **Sequential Thinking - MANDATORY PLANNING**

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Sequential Thinking** (`mcp_sequential-thinking_sequentialthinking`) to plan and analyze tasks, actions and approach - NO EXCEPTIONS
YOU MUST ALWAYS use **Temporal Memory** (`mcp_memory_*`) to get the current progress, actions and context of the implementation in this session and previous sessions prior to commencing ANY further action or undertaking ANY tasks
YOU MUST ALWAYS add or update the **Temporal Memory** (`mcp_memory_*`) entries and objects where there is missing or incomplete content for this session and previous sessions
YOU MUST ALWAYS ensure that you have current factual information regarding the status of the current instructions, actions and tasks
YOU MUST ALWAYS begin by using the date props to search and/or query (with pagination) **Temporal Memory** (`mcp_memory_*`) for entries for ALL content the past 4-48 hours (using the current date & time as the starting point)
YOU MUST ALWAYS iteratively perform queries and/or searches to the **Enduring Memory** (`mcp_neo4j-memory_*`), to ensure you have sufficient factual information regarding the current progress, actions and context of the implementation in this session and previous sessions
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

#### **MCP Code Servers and Tools - MANDATORY USAGE**

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

Available MCP Code Servers and Tools (MUST BE USED):

- **File System Access**: `mcp_filesystem_*` (Filesystem MCP) - MANDATORY for local file operations
- **Internet Research**: `mcp_fetch_fetch`, `web_search` (Fetch MCP, Web Search) - MANDATORY for external research
- **Online Research**: `mcp_fetch_fetch`, `web_search` (Fetch MCP, Web Search) - MANDATORY for documentation lookup
- **Knowledge Documentation**: `mcp_upstash-context7_*`, `mcp_fetch_fetch` (Context7 MCP, Fetch MCP) - MANDATORY for best practices
- **Best Practices**: `mcp_upstash-context7_*`, `mcp_grep_searchGitHub`, `mcp_fetch_fetch` (Context7 MCP, GitHub Search MCP, Fetch MCP) - MANDATORY for code quality
- **Code Research**: `mcp_upstash-context7_*`, `mcp_grep_searchGitHub`, `mcp_fetch_fetch` (Context7 MCP, GitHub Search MCP, Fetch MCP) - MANDATORY for implementation research
- **Code snippets**: `mcp_grep_searchGitHub`, `mcp_upstash-context7_*`, `mcp_filesystem_*`, `mcp_fetch_fetch` (GitHub Search MCP, Context7 MCP, Filesystem MCP, Fetch MCP) - MANDATORY for code examples
- **Code safety**: `mcp_git` (Git MCP) - MANDATORY for version control and code safety operations

**YOU MUST ALWAYS use the following MCP Servers and tools for (ZERO EXCEPTIONS):**

- **RESEARCH**: `mcp_fetch_fetch`, `web_search`, `mcp_upstash-context7_*` - MANDATORY
- **CODE**: `mcp_grep_searchGitHub`, `mcp_filesystem_*`, `codebase_search` - MANDATORY
- **KNOWLEDGE and BEST PRACTICES**: `mcp_upstash-context7_*`, `mcp_grep_searchGitHub`, `mcp_fetch_fetch` - MANDATORY
- **OS and FILE SYSTEM ACCESS**: `mcp_filesystem_*`, `mcp_time_*` - MANDATORY
- **VERSION CONTROL and CODE SAFETY**: `mcp_git` - MANDATORY

**ABSOLUTELY MANDATORY REQUIREMENTS:**
YOU MUST ALWAYS use **Context7 MCP** (`mcp_upstash-context7_*`) to research the current documentation and best practices - NO EXCEPTIONS
YOU MUST ALWAYS use **GitHub Search MCP** (`mcp_grep_searchGitHub`) to search GitHub for real production code examples and implementations - NO EXCEPTIONS
YOU MUST NEVER use index the entire code base using the filesystem - `mcp_filesystem_directory_tree` (path: ".") - ABSOLUTELY FORBIDDEN
YOU MUST ALWAYS use **Filesystem MCP** (`mcp_filesystem_*`) to review the local codebase for code patterns to properly understand the existing design and structure of the codebase - NO EXCEPTIONS
YOU MUST ALWAYS use **Filesystem MCP** (`mcp_filesystem_*`) to review the local codebase for codeblocks, function, classes, modules etc. to reuse, augment or enhance before determining that new code must be written - NO EXCEPTIONS
YOU MUST ALWAYS use **Fetch MCP** (`mcp_fetch_fetch`) to get additional information and documentation as required to provide additional knowledge and context - NO EXCEPTIONS
YOU MUST ALWAYS use **Git MCP** (`mcp_git`) for all version control operations, code safety checks, and repository management - NO EXCEPTIONS
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

#### **MCP Git - MANDATORY VERSION CONTROL & CODE SAFETY**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section A: MCP Server Specifications - Git MCP Workflow** in `claude-code-prompt-protocols.md` before performing any version control operations. This section contains detailed Git MCP workflow specifications, commit message standards, repository synchronization procedures, and emergency recovery operations.

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Git MCP** (`mcp_git`) for all version control and code safety operations with ZERO exceptions:

**MANDATORY GIT OPERATIONS:**

- **Repository Status**: Check working directory status before any code changes
- **Branch Management**: Create, switch, and manage branches for feature development
- **Staging Operations**: Stage files before committing changes
- **Commit Operations**: Create commits with proper commit messages
- **Push/Pull Operations**: Synchronize with remote repositories
- **Diff Operations**: Review changes before committing
- **Log Operations**: Review commit history and changes
- **Code Safety Checks**: Verify repository state before making changes

**ABSOLUTELY MANDATORY GIT WORKFLOW:**

1. **BEFORE ANY CODE CHANGES**: Check repository status using `mcp_git`
2. **DURING DEVELOPMENT**: Stage and commit changes incrementally
3. **BEFORE MAJOR CHANGES**: Create feature branches
4. **AFTER CODE CHANGES**: Review diffs and commit with descriptive messages
5. **BEFORE TASK COMPLETION**: Push changes to remote repository

**FAILURE TO USE GIT MCP FOR VERSION CONTROL WILL RESULT IN IMMEDIATE TASK TERMINATION**

#### **MCP Tools - MANDATORY EXECUTION**

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Sequential Thinking MCP** (`mcp_sequential-thinking_sequentialthinking`) to plan the tasks and the approach - NO EXCEPTIONS
YOU MUST ALWAYS use **Sequential Thinking MCP** (`mcp_sequential-thinking_sequentialthinking`) to break down the tasks and the approach into logical stepwise sequence consisting of actions and steps - NO EXCEPTIONS
YOU MUST ALWAYS use your claude code sub agents to perform ALL actions and steps - NO EXCEPTIONS
YOU MUST ALWAYS use and your claude code sub agents to complete the tasks based on the approach - NO EXCEPTIONS

#### **Temporal Memory** Tools for recording the tasks, actions and steps - MANDATORY

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Temporal Memory** (`mcp_memory_*`) to track the progress and execution of the tasks, actions and steps - NO EXCEPTIONS
YOU MUST ALWAYS use **Enduring Memory** (`mcp_neo4j-memory_*`) to persist the outcomes of the tasks, all knowledge and decisions derived during the execution of the tasks, actions and steps - NO EXCEPTIONS

#### **Temporal Memory** Management Updates - STRICTLY ENFORCED

**ABSOLUTELY MANDATORY - ZERO TOLERANCE FOR NON-COMPLIANCE**:
YOU MUST ALWAYS add the date property to all **Temporal Memory** (`mcp_memory_*`) and **Enduring Memory** (`mcp_neo4j-memory_*`) entries and objects - NO EXCEPTIONS
At the end of each task, action or step YOU MUST ALWAYS use **Temporal Memory** (`mcp_memory_*`) to track the progress and execution of the tasks, actions and steps - NO EXCEPTIONS
At the end of the end of the session YOU MUST ALWAYS use **Enduring Memory** (`mcp_neo4j-memory_*`) to persist the outcomes of the tasks, all knowledge and decisions derived during the execution of the tasks, actions and steps - NO EXCEPTIONS
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

## **PRODUCTION READY DEFINITION**

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

## **MANDATORY PYTHON VALIDATION COMMANDS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section B: Python Quality Standards** in `claude-code-prompt-protocols.md` before performing any Python validation. This section contains comprehensive validation command specifications, enhanced quality checks, and enforced mandatory quality requirements.

### **Core Quality Checks**

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

### **Enhanced Quality Checks**

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

### **Enforced Mandatory Quality Checks**

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

## **MANDATORY NODEJS VALIDATION COMMANDS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section C: NodeJS Quality Standards** in `claude-code-prompt-protocols.md` before performing any NodeJS validation. This section contains comprehensive validation command specifications, enhanced quality checks, and ultra-strict quality requirements.

### **Core Quality Checks**

- `npm run type-check` - MUST pass with 0 errors
- `npm run lint` - MUST pass with 0 errors and 0 warnings
- `npm run quality:check` - MUST pass all checks
- `npm run dev` - MUST start and function without errors
- `npm run build` - MUST complete without errors
- `npm run start` - MUST start and function without errors

### **Enhanced Quality Checks**

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

### **Ultra-Strict NodeJS Quality Checks**

- `npx eslint . --max-warnings 0 --max-errors 0` - MUST pass with 0 warnings/errors
- `npx tsc --noEmit --strict --noImplicitAny` - MUST pass strict TypeScript
- `npm audit --audit-level=low` - MUST pass with 0 vulnerabilities (any level)
- `npx bundlephobia analyze --threshold=100kb` - MUST be under 100KB bundle size
- `npx lighthouse-ci autorun --score=95` - MUST achieve 95+ performance score
- `npx depcheck --skip-missing` - MUST have 0 unused dependencies
- `npm run test:coverage -- --coverageThreshold='{"global":{"branches":95,"functions":95,"lines":95,"statements":95}}'` - MUST achieve 95% coverage

**NODEJS COMPLIANCE REQUIREMENT**: ALL remaining `any` type violations MUST be remediated, all type errors, security issues, linting errors, code quality issues, and complexity violations MUST be remediated using these patterns to achieve 100% PRODUCTION READY status.

## **SUCCESS_CRITERIA - ENTERPRISE GRADE STANDARDS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section D: Enterprise Grade Standards** in `claude-code-prompt-protocols.md` before implementing any production-ready code. This section contains detailed quantitative metrics, technical debt metrics, architecture quality metrics, and comprehensive production-ready definitions.

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

### **MANDATORY ARCHITECTURE COMPLIANCE REQUIREMENTS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section E: Architecture Compliance** in `claude-code-prompt-protocols.md` before implementing any architectural patterns. This section contains detailed SOLID principles enforcement, design pattern compliance, and code organization standards.

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

### **MANDATORY PERFORMANCE REQUIREMENTS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section F: Performance Requirements** in `claude-code-prompt-protocols.md` before implementing any performance optimizations. This section contains detailed runtime performance requirements and build performance standards.

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

### **MANDATORY SECURITY REQUIREMENTS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section G: Security Requirements** in `claude-code-prompt-protocols.md` before implementing any security measures. This section contains detailed authentication & authorization requirements and data protection standards.

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

### **MANDATORY MONITORING & OBSERVABILITY**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section H: Observability Standards** in `claude-code-prompt-protocols.md` before implementing any monitoring solutions. This section contains detailed logging standards and metrics & alerting requirements.

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

## **MANDATORY CODE REVIEW CHECKLIST**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section L: Review Checklists** in `claude-code-prompt-protocols.md` before conducting any code review. This section contains comprehensive checklists for code quality, architecture & design, testing & quality assurance, resilience & fault tolerance, and documentation & AI/LLM optimization.

YOU MUST ALWAYS verify these items during code review:

### **Git MCP Version Control & Code Safety (All must be ✅)**

- [ ] Git MCP status shows clean working directory
- [ ] Git MCP branch verification completed
- [ ] Proper Git MCP commit message format used
- [ ] All changes staged and committed using Git MCP
- [ ] Repository synchronized with remote using Git MCP
- [ ] Feature branch workflow followed when applicable
- [ ] Code changes reviewed with Git MCP diff
- [ ] Emergency procedures documented and available

### **Code Quality (All must be ✅)**

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

### **Architecture & Design (All must be ✅)**

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

### **Testing & Quality Assurance (All must be ✅)**

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

### **Resilience & Fault Tolerance (All must be ✅)**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section I: Fault Tolerance Patterns** in `claude-code-prompt-protocols.md` before implementing any resilience patterns. This section contains detailed exponential backoff & retry patterns, graceful failure handling, try-catch requirements, circuit breaker patterns, and comprehensive resilience validation code examples.

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

### **Documentation & AI/LLM Optimization (All must be ✅)**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section J: Documentation Standards** in `claude-code-prompt-protocols.md` before implementing any documentation. This section contains comprehensive docstring standards, class documentation standards, module-level documentation, and AI/LLM optimization documentation patterns with detailed code examples.

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

## **ENFORCEMENT SUMMARY**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section M: Production-Ready Enforcement** in `claude-code-prompt-protocols.md` before implementing any enforcement mechanisms. This section contains detailed automated quality gates, CI/CD pipeline enforcement, real-time monitoring & alerting, git hooks, package.json scripts, VS Code workspace settings, Docker multi-stage builds, and Kubernetes health checks.

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

## **PRODUCTION READY DEFINITION**

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

============================================================================================================================================================================================================
