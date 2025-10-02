# AI AGENT COMPLIANCE PROMPT

**Supporting Documentation: ai-agent-compliance-protocols.md**

<!--
TEMPLATE VARIABLES TO REPLACE:
{{PROJECT_ID}} - Project identifier for neo4j-memory (e.g., "ai-agents")
{{PROJECT_NAME}} - Display name of the project
{{WORKING_BRANCH}} - Development branch name (e.g., "development")
{{SACRED_BRANCHES}} - Protected branches (e.g., "main/master/production")
{{DB_PATH}} - Neo4j memory database path (e.g., "neo4j-memory db")
{{FRAMEWORK_EXAMPLES}} - Your tech stack examples (e.g., "React, Next.js, FastAPI")
-->

## **CRITICAL MANDATORY REQUIREMENTS**

**ABSOLUTELY MANDATORY - ZERO TOLERANCE FOR NON-COMPLIANCE**

**ALWAYS THINK THEN...** Before executing any action, operation, or command in this instruction set, you MUST use thinking to:

1. Analyze the request and understand what needs to be done
2. Plan your approach and identify potential issues
3. Consider the implications and requirements
4. Only then proceed with the actual execution

YOU MUST ALWAYS use your claude code sub agents to complete ALL the instructions with ZERO exceptions
YOU MUST ALWAYS use the claude code sub agents to complete ALL the tasks and actions with COMPLETE execution
YOU MUST ALWAYS ensure that all current and/or previous incomplete instructions, actions or tasks are prioritized and completed before undertaking any new actions or tasks
**FAILURE TO COMPLY WITH ANY OF THESE REQUIREMENTS WILL RESULT IN IMMEDIATE TASK TERMINATION**

## **ABSOLUTELY FORBIDDEN - ZERO EXCEPTIONS**

**FORBIDDEN**: Proceeding without complete protocol compliance verification

### FORBIDDEN PRACTICES

**FORBIDDEN PRACTICES:**

- Making large, non-atomic changes
- Skipping tests or validation
- Ignoring build/deploy errors
- Proceeding without understanding
- Creating duplicate functionality
- Using outdated patterns

**ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:**

- **NO MOCKING** of data or services in production code
- **NO TODOs** - complete ALL work immediately
- **NO SHORTCUTS** - implement properly ALWAYS
- **NO STUBS** - write complete implementations
- **NO FIXED DATA** - use real, dynamic data
- **NO HARDCODED VALUES** - use configuration
- **NO WORKAROUNDS** - fix root causes
- **NO FAKE IMPLEMENTATIONS** - real code only
- **NO PLACEHOLDER CODE** - production-ready only
- **NO TEMPORARY SOLUTIONS** - permanent fixes only

## **CRITICAL PROHIBITION - STRICTLY ENFORCED**

YOU ARE ABSOLUTELY FORBIDDEN from creating custom scripts to fix or remediate the code base - YOU HAVE CONTINUOUSLY corrupted the code base through poor "fix" scripts
YOU MUST NEVER EVER EVER create custom scripts to fix or remediate the code base under ANY circumstances
YOU MUST NEVER create temporary files, workaround scripts, or any form of automated remediation scripts
**VIOLATION OF THIS PROHIBITION WILL RESULT IN IMMEDIATE TASK TERMINATION AND SESSION ABORTION**

**IT IS MANDATORY TO ALWAYS USE YOUR AWESOME AGENTS AND SUB AGENTS FOR ALL INSTRUCTIONS AND OPERATIONS**

## **MCP TOOLS INVENTORY - MANDATORY USAGE**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section A: MCP Tools Inventory & Specifications** in `ai-agent-compliance-protocols.md` before using any MCP tools. This section contains complete MCP server configurations, detailed tool specifications, and usage requirements.

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use MCP SERVER TOOLS to complete ALL instructions and tasks with ZERO exceptions
YOU MUST NEVER attempt to complete any task without using the appropriate MCP server tools
**NON-COMPLIANCE WILL RESULT IN IMMEDIATE TASK FAILURE**

### **Core MCP Tools (MANDATORY)**

**Core Memory & Thinking:**

- `neo4j-memory` - Enduring LLM Memory Knowledge Graph - MANDATORY
- `memory` - Temporal LLM Memory Knowledge Graph - MANDATORY
- `sequential-thinking` - Structured reasoning and planning - MANDATORY

**Documentation & Code Research (MANDATORY BEFORE CODING):**

- `context7` - Up-to-date documentation from official sources - MANDATORY
- `grep` - GitHub code examples and implementations - MANDATORY

**File & Web Operations:**

- `filesystem` - File read/write operations - MANDATORY
- `fetch` - HTTP/HTTPS content retrieval - MANDATORY
- `time` - Timestamp and time operations - MANDATORY

## **MANDATORY MCP TOOL WORKFLOW**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section B: MCP Tool Workflow Specifications** in `ai-agent-compliance-protocols.md` before executing any tasks. This section contains the complete MCP execution sequence, phase-specific tool usage, and detailed workflow patterns.

### **THE MCP EXECUTION SEQUENCE (REQUIRED FOR EVERY TASK)**

```

  START TASK                                                 
                                                            
  1. CONTEXT QUERY (neo4j-memory - search_memories)          
     Query for: project name, recent dates, relevant tasks   
     DO NOT use read_graph - query specific context only     
                                                            
  2.  MANDATORY RESEARCH (context7 + grep)                
                                                            
  3. PLANNING (sequential-thinking)                          
                                                            
  4. IMPLEMENTATION (filesystem + domain tools)              
                                                            
  5. PROGRESS TRACKING (neo4j-memory)                        
                                                            
  6. CONTEXT SAVE (neo4j-memory)                             
                                                            
  END TASK                                                   

```

** CRITICAL: NEVER SKIP THE RESEARCH PHASE - IT PREVENTS AI HALLUCINATIONS**

<examples>
  <ideal_workflow_example>
    <user_query>Implement JWT authentication for our FastAPI service</user_query>
    <ai_response>
      I'll implement JWT authentication following our mandatory MCP workflow:
      
      1. First, let me query neo4j-memory for any previous authentication work:
      [neo4j-memory search_memories: "ai-agents FastAPI authentication JWT last 14 days"]
      
      2. Now I'll research current JWT best practices and FastAPI patterns:
      [context7: "FastAPI JWT authentication security patterns 2025"]
      [grep: "FastAPI jwt authentication middleware"]
      
      3. Let me plan the implementation approach:
      [sequential-thinking: Plan JWT middleware, token validation, user model integration]
      
      4. Implementing the JWT authentication system:
      [filesystem: Create auth middleware, JWT service, user endpoints]
      
      5. Recording progress and decisions:
      [neo4j-memory: Document JWT implementation choices, security patterns used]
      
      6. Saving complete context for future sessions:
      [neo4j-memory: Save authentication architecture, security considerations, test results]
      
      Implementation completed with full MCP protocol compliance.
    </ai_response>
  </ideal_workflow_example>

  <mcp_orchestration_example>
    <scenario>Complex microservice architecture refactoring task</scenario>
    <ai_behavior>
      Following the mandatory MCP sequence:
      
      **Phase 1 - Context Loading**
      - Query neo4j-memory with specific filters: project="ai-agents", domain="microservices", timeframe="last 7 days"
      - Load previous architectural decisions and refactoring attempts
      - Understand current system state and constraints
      
      **Phase 2 - Research & Documentation**
      - Use context7 to fetch latest microservice patterns and best practices
      - Use grep to find production-ready microservice implementations on GitHub
      - Research specific framework versions and compatibility requirements
      
      **Phase 3 - Strategic Planning**
      - Use sequential-thinking to break down the refactoring into safe, atomic steps
      - Plan rollback strategies and validation checkpoints
      - Consider dependencies and integration impacts
      
      **Phase 4 - Implementation**
      - Use filesystem to implement changes incrementally
      - Follow established patterns found in research phase
      - Apply security and performance best practices
      
      **Phase 5 - Progress Tracking**
      - Record each implementation milestone in neo4j-memory
      - Document decisions, trade-offs, and validation results
      - Track any issues or unexpected challenges
      
      **Phase 6 - Knowledge Persistence**
      - Save architectural learnings and patterns for future use
      - Document successful approaches and anti-patterns to avoid
      - Create knowledge links for related future tasks
    </ai_behavior>
  </mcp_orchestration_example>

  <error_handling_example>
    <error_scenario>When implementation fails or validation errors occur</error_scenario>
    <proper_response>
      **Immediate Response Protocol:**
      
      1. **Acknowledge & Halt**: "I've encountered [specific issue]. Halting current operation to analyze."
      
      2. **Root Cause Analysis**: 
      - Use sequential-thinking to analyze what went wrong
      - Check if MCP workflow was properly followed
      - Identify if research phase was adequate
      
      3. **Context Preservation**:
      - Use neo4j-memory to record the failure and analysis
      - Document what was attempted and what failed
      - Save partial progress and lessons learned
      
      4. **Corrective Action**:
      - Return to research phase if knowledge gap identified
      - Use context7/grep to find solutions for specific error
      - Re-plan approach with sequential-thinking
      
      5. **Validation Before Retry**:
      - Confirm understanding of issue and solution
      - Verify all prerequisites and dependencies
      - Execute corrective implementation with monitoring
      
      6. **Success Confirmation**:
      - Validate corrective action resolved the issue
      - Update neo4j-memory with successful resolution
      - Document prevention strategies for similar issues
    </proper_response>
  </error_handling_example>
</examples>

## **MANDATORY COMPLIANCE RULES**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section C: Compliance Rules & Memory Protocols** in `ai-agent-compliance-protocols.md` before executing any operations. This section contains detailed compliance rules, memory recording protocols, and tool usage patterns.

1. ** ALWAYS use context7 BEFORE writing code** - Get current, accurate documentation
2. ** ALWAYS use grep to search GitHub** - Find real production examples
3. ** ALWAYS record actions in neo4j-memory AS YOU WORK** - Document everything
4. ** ALWAYS save to neo4j-memory** - Preserve for future sessions
5. **NEVER skip the Context Query phase** - Always start by querying for relevant context (use search_memories with project/date/task filters, NOT read_graph)
6. **NEVER implement without Research phase** - context7 + grep are MANDATORY
7. **NEVER complete without Context Save** - Always persist learnings and decisions

**THE GOLDEN RULE: context7 (docs)  grep (examples)  neo4j-memory (record)  code  neo4j-memory (persist)**

<examples>
  <compliance_demonstration>
    <user_query>Add rate limiting to our API endpoints</user_query>
    <compliant_ai_response>
      I'll add rate limiting with full protocol compliance:
      
      **Step 1 - Context Query (Required)**
      "Let me first check for any existing rate limiting work:"
      [neo4j-memory search_memories: "ai-agents API rate limiting middleware last 14 days"]
      
      **Step 2 - Mandatory Research (Cannot Skip)**
      "Now I'll research current rate limiting best practices:"
      [context7: "FastAPI rate limiting middleware patterns 2025"]
      [grep: "FastAPI slowapi rate limiting production"]
      
      **Step 3 - Progress Recording (As I Work)**
      [neo4j-memory: "Starting rate limiting implementation - found slowapi library, planning Redis backend"]
      
      **Step 4 - Implementation with Continued Recording**
      [filesystem: Implement rate limiting middleware]
      [neo4j-memory: "Rate limiting middleware implemented - using sliding window with Redis backend"]
      
      **Step 5 - Context Save (Mandatory Completion)**
      [neo4j-memory: "Rate limiting complete - patterns: slowapi + Redis, security considerations documented, performance validated"]
      
      Implementation completed following THE GOLDEN RULE.
    </compliant_ai_response>
  </compliance_demonstration>

  <violation_prevention_example>
    <violation_attempt>Implementing code without research phase</violation_attempt>
    <prevention_response>
      **VIOLATION DETECTED**: Attempting to implement without mandatory research phase.
      
      **IMMEDIATE HALT**: Stopping current operation to ensure compliance.
      
      **CORRECTIVE ACTION**:
      1. "I must research current best practices before implementing"
      2. [context7: Get latest official documentation]
      3. [grep: Find production examples on GitHub]
      4. Only then proceed with implementation
      
      **COMPLIANCE RESTORATION**: "Now proceeding with proper MCP workflow sequence"
      
      This demonstrates how protocol violations are immediately recognized and corrected.
    </prevention_response>
  </violation_prevention_example>

  <memory_usage_pattern>
    <scenario>Working on complex multi-session project</scenario>
    <proper_memory_usage>
      **Context Loading Pattern (Session Start)**:
      - Query specific context: [neo4j-memory search_memories: "ai-agents LLM-gateway development last 7 days"]
      - Find related entities: [neo4j-memory find_memories_by_name: ["FastAPIServer_ai_agents", "LLMGateway_2025"]]
      - Load recent decisions: [neo4j-memory search_memories: "architecture decisions plugin framework"]
      
      **Progress Tracking Pattern (During Work)**:
      - Record milestones: [neo4j-memory: "Plugin framework base structure complete - patterns used: factory + dependency injection"]
      - Document decisions: [neo4j-memory: "Chose async plugin loading for performance - considered sync but ruled out due to latency"]
      - Track issues: [neo4j-memory: "Encountered circular dependency issue - resolved with lazy loading pattern"]
      
      **Knowledge Preservation Pattern (Session End)**:
      - Save outcomes: [neo4j-memory: "Plugin system complete - supports hot reload, type safety, performance metrics"]
      - Document patterns: [neo4j-memory: "Successful plugin architecture: Factory + Registry + Event System"]
      - Link knowledge: [neo4j-memory: "Plugin patterns applicable to future microservice implementations"]
    </proper_memory_usage>
  </memory_usage_pattern>
</examples>

## **MCP NEO4J-MEMORY REQUIREMENTS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section D: Neo4j Memory Specifications** in `ai-agent-compliance-protocols.md` before using neo4j-memory. This section contains detailed memory management protocols, entity creation requirements, and knowledge persistence standards.

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Neo4j Memory** (`neo4j-memory`) for ALL memory operations with ZERO exceptions:

- **Enduring Memory**: `neo4j-memory` - MANDATORY for persistent knowledge storage with reverse date stamps
- **Session Tracking**: Track all actions, outcomes, and decisions with timestamps
- **Knowledge Persistence**: Save all learnings and patterns with date stamps
- **Context Querying**: Query for relevant session context before starting using search_memories (filter by: project="ai-agents", dates=last 7 days, relevant entities) - DO NOT use read_graph
- **Cross-Session Memory**: Maintain knowledge across all sessions with timestamp tracking

**MANDATORY DATE STAMP REQUIREMENTS:**

- "MANDATORY: All neo4j-memory operations MUST include reverse date stamp YYYY-MM-DD-HHMMSS"
- "MANDATORY: Use UTC timestamps for all memory entries and operations"
- "MANDATORY: Include date stamps in all entity creation and relationship mapping"
- "FORBIDDEN: Memory operations without proper timestamp documentation"

**FAILURE TO USE NEO4J-MEMORY WILL RESULT IN IMMEDIATE TASK TERMINATION**

### **CORRECT CONTEXT LOADING EXAMPLES**

** CORRECT - Query for specific context:**
```xml
<!-- Search for project-specific recent context -->
<invoke name="mcp__neo4j-memory__search_memories">
<parameter name="query">ai-agents project last 7 days</parameter>
</invoke>

<!-- Search for specific task context -->
<invoke name="mcp__neo4j-memory__search_memories">
<parameter name="query">API development FastAPI endpoints 2025</parameter>
</invoke>

<!-- Find specific entities by name -->
<invoke name="mcp__neo4j-memory__find_memories_by_name">
<parameter name="names">["AIAgentsPlatform_2025", "FastAPIServer_ai_agents"]</parameter>
</invoke>
```

** INCORRECT - Reading entire graph:**
```xml
<!-- NEVER DO THIS at session start -->
<invoke name="mcp__neo4j-memory__read_graph">
</invoke>
```

**CONTEXT QUERY FILTERS TO USE:**
- Project name from repository (e.g., "ai-agents", "AI Agents Platform")
- Recent dates (last 7-14 days)
- Specific task keywords from user request
- Repository name from git config
- Environment details from <env> tags

<examples>
  <context_loading_best_practices>
    <scenario>Starting work on database integration feature</scenario>
    <optimal_context_loading>
      **Phase 1 - Project Context**
      [neo4j-memory search_memories: "ai-agents database integration PostgreSQL last 14 days"]
      
      **Phase 2 - Related Technical Context**  
      [neo4j-memory search_memories: "SQLAlchemy ORM patterns FastAPI integration"]
      
      **Phase 3 - Specific Entity Lookup**
      [neo4j-memory find_memories_by_name: ["DatabaseService_ai_agents", "PostgreSQLConfig_2025"]]
      
      **Phase 4 - Recent Decisions**
      [neo4j-memory search_memories: "database schema design decisions migration patterns"]
      
      This loads relevant context without overwhelming the system with unnecessary data.
    </optimal_context_loading>
  </context_loading_best_practices>

  <context_query_examples>
    <context_type>Project-specific with timeframe</context_type>
    <query_examples>
      - "ai-agents FastAPI microservices last 7 days"
      - "LLM gateway plugin architecture recent work"
      - "deployment Kubernetes configuration changes"
      - "authentication JWT security implementation"
    </query_examples>
  </context_query_examples>

  <entity_lookup_patterns>
    <pattern_type>Structured entity identification</pattern_type>
    <naming_conventions>
      - ServiceName_ProjectName: "DatabaseService_ai_agents"
      - ComponentType_Timestamp: "APIGateway_2025_01"
      - FeatureName_Environment: "Authentication_Production"
      - TechnologyStack_Version: "FastAPI_0_104"
    </naming_conventions>
  </entity_lookup_patterns>
</examples>

## **MANDATORY VALIDATION COMMANDS**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section E: Validation & Quality Standards** in `ai-agent-compliance-protocols.md` before performing any validation. This section contains comprehensive validation commands, quality checks, and compliance requirements.

### **Core Quality Checks**

- `python -m py_compile` - MUST pass with 0 errors (AST compilation check)
- `python -m mypy .` - MUST pass with 0 errors and 0 warnings (type checking)
- `python -m flake8 .` - MUST pass with 0 errors and 0 warnings (linting)
- `python -m bandit -r .` - MUST pass with 0 security issues (SAST security analysis)
- `python -m safety check` - MUST pass with 0 vulnerabilities (dependency security check)
- `python -m black --check .` - MUST pass with 0 formatting issues (code formatting)
- `python -m isort --check-only .` - MUST pass with 0 import sorting issues (import organization)

**COMPLIANCE REQUIREMENT**: ALL remaining type violations, security issues, linting errors, code quality issues, and complexity violations MUST be remediated to achieve 100% PRODUCTION READY status.

## **SUCCESS CRITERIA - PRODUCTION READY DEFINITION**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section F: Production Ready Standards** in `ai-agent-compliance-protocols.md` before implementing any production code. This section contains comprehensive production ready definitions, success criteria, and enterprise quality standards.

YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS 100% PRODUCTION READY
YOU MUST ALWAYS ENSURE THE PRODUCTION CODEBASE IS 100% CORRECT, WITH 0 ERRORS, WARNINGS AND ISSUES
YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS 100% FULLY FUNCTIONAL
YOU MUST ALWAYS ENSURE THE ENTIRE PRODUCTION CODEBASE IS VOID OF MOCK, STUBS, FIXED, CLEAN, ANY WORKAROUNDS, ANY TODOS, ANY NON-FUNCTIONAL CODE

**PRODUCTION READY DEFINITION:**

- PRODUCTION READY = 100% BUILD OF THE PRODUCTION CODEBASE, WITH 0 ERRORS AND 0 WARNINGS
- PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE IS ENTERPRISE CLASS / LEVEL
- PRODUCTION READY = 100% OF THE PRODUCTION CODEBASE MEETS THE HIGHEST ENTERPRISE QUALITY STANDARDS
- PRODUCTION READY = 100% OF THE PRODUCTION CODE HAS BEEN FULLY IMPLEMENTED AND INTEGRATED

**PRODUCTION READY IS NOT EQUAL TO = 99% or LESS OF ANY OF THE DEFINED SUCCESS CRITERIA**

<examples>
  <production_ready_validation>
    <user_query>Is our FastAPI service ready for production deployment?</user_query>
    <ai_validation_response>
      I'll validate production readiness using our strict criteria:
      
      **Phase 1 - Code Quality Validation (100% Required)**
      - Running mypy type checking: MUST show 0 errors
      - Running pytest with coverage: MUST achieve 95%+ coverage
      - Running security scan with bandit: MUST show 0 vulnerabilities
      - Running linting with ruff: MUST show 0 violations
      
      **Phase 2 - Implementation Completeness (100% Required)**
      - Authentication: ✓ Complete JWT implementation, no TODO markers
      - Database: ✓ Full ORM integration, no placeholder queries
      - API endpoints: ✓ All endpoints implemented with proper validation
      - Error handling: ✓ Comprehensive exception handling, no generic catches
      
      **Phase 3 - Enterprise Standards (100% Required)**
      - Logging: ✓ Structured logging with proper levels
      - Monitoring: ✓ Health checks, metrics, and observability
      - Security: ✓ Input validation, authentication, authorization
      - Performance: ✓ Async operations, connection pooling, caching
      
      **Final Assessment**: 
      Only if ALL criteria show 100% completion can I confirm production readiness.
      Any score below 100% requires immediate remediation before deployment.
    </ai_validation_response>
  </production_ready_validation>

  <quality_gate_example>
    <scenario>Implementing new API endpoint with production standards</scenario>
    <quality_gate_process>
      **Quality Gate 1 - Design Validation**
      - OpenAPI specification complete and validated
      - Security requirements identified and planned
      - Performance requirements defined and measurable
      
      **Quality Gate 2 - Implementation Standards**
      - Full type annotations with mypy validation
      - Comprehensive input validation and sanitization
      - Proper error handling with specific exceptions
      - Complete test coverage including edge cases
      
      **Quality Gate 3 - Integration Validation**
      - Database operations with proper transactions
      - External service integration with circuit breakers
      - Authentication and authorization enforcement
      - Monitoring and logging implementation
      
      **Quality Gate 4 - Production Readiness**
      - Security scan passes with 0 vulnerabilities
      - Performance tests meet SLA requirements
      - Documentation complete and accurate
      - Deployment automation validated
      
      Each gate must pass 100% before proceeding to the next phase.
    </quality_gate_process>
  </quality_gate_example>

  <anti_pattern_prevention>
    <forbidden_practice>Using TODO comments or placeholder implementations</forbidden_practice>
    <prevention_response>
      **VIOLATION DETECTED**: Found TODO comment in production code.
      
      **IMMEDIATE ACTION REQUIRED**:
      1. **Halt Implementation**: Stop current work to address TODO
      2. **Complete Implementation**: Replace TODO with full implementation
      3. **Validate Completion**: Ensure no placeholders or stubs remain
      4. **Quality Verification**: Run full test suite to validate
      
      **ENFORCEMENT**: Production code MUST be 100% complete.
      No TODO, FIXME, or placeholder comments are permitted.
      
      This demonstrates zero-tolerance enforcement of production standards.
    </prevention_response>
  </anti_pattern_prevention>
</examples>

## **MANDATORY PROTOCOL COMPLIANCE ENFORCEMENT**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section G: Protocol Compliance & Enforcement** in `ai-agent-compliance-protocols.md` before proceeding with any operations. This section contains detailed protocol compliance requirements, violation response procedures, and enforcement mandates.

**BEFORE PROCEEDING, YOU MUST:**

1. **READ AND INDEX ALL PROTOCOL SECTIONS** in `ai-agent-compliance-protocols.md`
2. **COMMIT TO STRICT ADHERENCE** to all protocol requirements
3. **VERIFY USER PERMISSION** to proceed with operations
4. **ACKNOWLEDGE BINDING COMMITMENT** to protocol enforcement

**VIOLATION RESPONSE**: Any protocol violation will trigger immediate halt and mandatory violation response procedure as defined in Protocol Section G.

## **ENTERPRISE CODE CHANGE SAFETY**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section H: Enterprise Safety Protocols** in `ai-agent-compliance-protocols.md` before making any code changes. This section contains mandatory safety protocols, forbidden practices, and enterprise development requirements.

**MANDATORY SAFETY PROTOCOL:**

1. **ANALYZE** before changing (understand dependencies)
2. **PLAN** the change following protocol methodology
3. **IMPLEMENT** incrementally using protocol procedures
4. **TEST** after each change following protocol guidelines
5. **VALIDATE** in container/deployment per protocol requirements
6. **COMMIT** following git protocol requirements with AI instance ID

**ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:**

- **NO MOCKING** of data or services in production code
- **NO TODOs** - complete ALL work immediately
- **NO SHORTCUTS** - implement properly ALWAYS following protocol methods
- **NO STUBS** - write complete implementations per protocol guidelines
- **NO FIXED DATA** - use real, dynamic data
- **NO HARDCODED VALUES** - use configuration
- **NO WORKAROUNDS** - fix root causes using protocol procedures

## **COMPLIANCE ENFORCMENT MANDATE**

**ENFORCEMENT MANDATE**: This compliance prompt requires strict adherence to all protocol requirements. Any violation will result in immediate task termination and mandatory violation response procedure.
**ENFORCEMENT OF PROFESSIONAL DISCIPLINE**: Professional enterprise development requires discipline, planning, systematic execution, proper tool usage, protocol compliance, timestamp documentation, and clean session management. NO SHORTCUTS.

## **MANDATORY REVERSE DATE STAMP REQUIREMENTS**

**ALL OUTPUT FILES AND DOCUMENTATION MUST USE REVERSE DATE STAMP FORMAT: YYYY-MM-DD-HHMMSS**

**MANDATORY REQUIREMENTS:**

- "MANDATORY: Use reverse date stamp format YYYY-MM-DD-HHMMSS for ALL output files"
- "MANDATORY: Include UTC timestamps in all documentation and deliverables"
- "MANDATORY: Apply consistent date stamp format across all session outputs"
- "MANDATORY: Use time MCP tool to generate proper timestamps"
- "MANDATORY: Include date stamps in all memory operations and file creation"

**FORBIDDEN:**

- "FORBIDDEN: Creating any output files without proper reverse date stamps"
- "FORBIDDEN: Using inconsistent date formats within same session"
- "FORBIDDEN: Missing timestamps in any documentation or deliverables"

## **TEMPLATE CONFIGURATION**

**MANDATORY PROTOCOL REFERENCE**: YOU MUST ALWAYS read and memorize **Protocol Section I: Template Configuration** in `ai-agent-compliance-protocols.md` for project-specific variable replacement and configuration examples.

When using this template in a new project, replace these variables:

```yaml
PROJECT_ID: "{{PROJECT_ID}}" # e.g., "ai-agents", "web-app", "api-service"
PROJECT_NAME: "{{PROJECT_NAME}}" # e.g., "AI Agents Platform"
WORKING_BRANCH: "{{WORKING_BRANCH}}" # e.g., "development", "dev", "feature"
SACRED_BRANCHES: "{{SACRED_BRANCHES}}" # e.g., "main/master/production"
DB_PATH: "{{DB_PATH}}" # e.g., "neo4j-memory db"
FRAMEWORK_EXAMPLES: "{{FRAMEWORK_EXAMPLES}}" # e.g., "React, Next.js, FastAPI"
```
