# AI AGENT COMPLIANCE PROTOCOLS AND STANDARDS

**Supporting Documentation for ai-agent-compliance.md**

This document contains detailed specifications, standards, and protocols that support the core instructions in `ai-agent-compliance.md`. All sections in this document are referenced by and must be read in conjunction with the main prompt instructions.

**MANDATORY RTFM INTEGRATION**: All compliance protocols automatically enforce the RTFM (Read The Fucking Manual) protocol requirements from `rtfm-protocol-enforcement-prompt.md` and `rtfm-protocol-enforcement-protocols.md`. Any implementation work MUST complete the RTFM research sequence first.

## **CROSS-REFERENCE MAPPING**

This document provides detailed specifications for the following sections in `ai-agent-compliance.md`:

- **Section 1**: MCP Tools Inventory → **Protocol Section A**: MCP Tools Inventory & Specifications
- **Section 2**: MCP Tool Workflow → **Protocol Section B**: MCP Tool Workflow Specifications
- **Section 3**: Compliance Rules → **Protocol Section C**: Compliance Rules & Memory Protocols
- **Section 4**: Neo4j Memory → **Protocol Section D**: Neo4j Memory Specifications
- **Section 5**: Validation → **Protocol Section E**: Validation & Quality Standards
- **Section 6**: Success Criteria → **Protocol Section F**: Production Ready Standards
- **Section 7**: Protocol Compliance → **Protocol Section G**: Protocol Compliance & Enforcement
- **Section 8**: Code Safety → **Protocol Section H**: Enterprise Safety Protocols
- **Section 9**: Template Config → **Protocol Section I**: Template Configuration

======================================================================================================================================================================

## **PROTOCOL SECTION A: MCP TOOLS INVENTORY & SPECIFICATIONS**

_Referenced by: ai-agent-compliance.md Section 1 - MCP Tools Inventory_

### **Complete List of Configured MCP Servers**

**Core Memory & Thinking:**

- `neo4j-memory` - Enduring LLM Memory Knowlege Graph
- `sequential-thinking`: Structured reasoning and planning (npx @modelcontextprotocol/server-sequential-thinking)

**Documentation & Code Research (MANDATORY BEFORE CODING):**

- `context7`: Fetches up-to-date, version-specific documentation straight from official sources (npx @upstash/context7-mcp)
- `grep`: Searches GitHub for real-world code examples and implementations (mcp-remote https://mcp.grep.app)

**File & Web Operations:**

- `filesystem`: File read/write operations (npx @modelcontextprotocol/server-filesystem)
- `fetch`: HTTP/HTTPS content retrieval (npx fetch-mcp)
- `time`: Timestamp and time operations (uvx mcp-server-time)

**Advanced AI & Automation:**

- `zen`: Multi-model AI orchestration (python -m zen_mcp_server)
- `playwright`: Browser automation and testing (npx -y @playwright/mcp)

**Frontend Development:**

- `shadcn-ui`: shadcn/ui components (npx @jpisnice/shadcn-ui-mcp-server)
- `chakra-ui`: Chakra UI components (npx @chakra-ui/react-mcp)
- `lucide-icons`: Icon library (npx lucide-icons-mcp)
- `vite-plugin`: Vite build tool (npx vite-plugin-mcp)
- Plus: vercel-adapter, mcp-react, magicui, heroui

**DEPRECATED**- `memory`: Session-based lightweight memory (npx @modelcontextprotocol/server-memory)
**DEPRECATED**- `extended-memory`: Persistent cross-session memory with SQLite (python -m extended_memory_mcp.server)

======================================================================================================================================================================

## **PROTOCOL SECTION B: MCP TOOL WORKFLOW SPECIFICATIONS**

_Referenced by: ai-agent-compliance.md Section 2 - MCP Tool Workflow_

### **THE MCP EXECUTION SEQUENCE (REQUIRED FOR EVERY TASK)**

```
┌─────────────────────────────────────────────────────────────┐
│  START TASK                                                 │
│      ↓                                                      │
│  1. CONTEXT LOAD (neo4j-memory)                         │
│      ↓                                                      │
│  2. 🔴 MANDATORY RESEARCH (context7 + grep)                │
│      ↓                                                      │
│  3. PLANNING (sequential-thinking)                         │
│      ↓                                                      │
│  4. IMPLEMENTATION (filesystem + domain tools)             │
│      ↓                                                      │
│  5. PROGRESS TRACKING (neo4j-memory)                             │
│      ↓                                                      │
│  6. CONTEXT SAVE neo4j-memory)                         │
│      ↓                                                      │
│  END TASK                                                   │
└─────────────────────────────────────────────────────────────┘
```

**🔴 CRITICAL: NEVER SKIP THE RESEARCH PHASE - IT PREVENTS AI HALLUCINATIONS**

### PHASE-SPECIFIC MCP TOOL USAGE:

**1. CONTEXT LOAD PHASE (Start of Every Task):**

```
MANDATORY SEQUENCE:
1. neo4j-memory: Load ALL previous actions, outcomes, issues
   → "project_id={{PROJECT_ID}}; load all previous tasks and their outcomes"
   → "project_id={{PROJECT_ID}}; load all issues encountered and solutions"
   → "project_id={{PROJECT_ID}}; load all patterns and decisions made"
2. neo4j-memoryy: Initialize detailed session tracking
   → "session_start: task=[task_name], context=[loaded_history]"
   → "session_goal: what I plan to achieve this session"
   → "session_risks: potential issues based on past experiences"
```

**2. 🔴 MANDATORY RESEARCH PHASE (RTFM PROTOCOL ENFORCEMENT):**

```
CRITICAL - PREVENTS HALLUCINATIONS:
MUST EXECUTE COMPLETE RTFM PROTOCOL SEQUENCE FIRST:

1. RTFM Phase 1: Smart Codebase Exploration (MAX 20 files)
   → filesystem (list_directory): Index structure only
   → filesystem (read_text_file): Read max 10 high-priority files
   → Achieve 90% codebase understanding threshold

2. RTFM Phase 2: Documentation Research 
   → context7: Get current, accurate documentation
   → fetch: Additional documentation with credibility validation
   → Achieve 85% documentation comprehension threshold

3. RTFM Phase 3: Online Research and Validation
   → grep: Find real production code examples on GitHub
   → Validate sources using tier-based credibility matrix
   → Achieve 95% implementation readiness threshold

4. RTFM Quality Gate: Validate all thresholds met before proceeding
   → Codebase Understanding: 90%
   → Documentation Comprehension: 85% 
   → Implementation Readiness: 95%
```

**3. PLANNING PHASE (After Research, Before Implementation):**

```
MANDATORY SEQUENCE:
1. sequential-thinking: Create structured plan using research
   → Generate numbered steps based on current docs from context7
   → Include checkpoints for validation
2. neo4j-memory: Track every planning decision
   → "plan_step_1: action=[what], reason=[why], risk=[potential_issue]"
   → "plan_step_2: action=[what], depends_on=[step_1_outcome]"
3. neo4j-memory: Save complete plan with rationale
   → "project_id={{PROJECT_ID}}; save plan=[full_plan_with_reasoning]"
   → "project_id={{PROJECT_ID}}; save research_sources=[context7_docs, grep_examples]"
```

**4. IMPLEMENTATION PHASE (Smart Recording):**

```
PRIMARY TOOLS WITH SMART DIVISION:
- filesystem: Read/write code files
  → neo4j-memory: "working on: [file], current task: [what]"
- neo4j-memory: Track ACTIVE WORK ONLY
  → "trying: [approach]"
  → "debugging: [issue]"
  → "todo: [next_immediate_step]"
- sequential-thinking: Validate against plan
- neo4j-memory: Save ONLY SIGNIFICANT FINDINGS
  → "project_id={{PROJECT_ID}}; solved: [problem] with [solution]"
  → "project_id={{PROJECT_ID}}; pattern: [reusable approach]"
DOMAIN-SPECIFIC:
- Use frontend MCP servers → memory: note what you're trying
- Use zen for AI workflows → neo4j-memory: save successful patterns
- Use playwright for testing → neo4j-memory: save test strategies that worked
```

**5. PROGRESS TRACKING (Lightweight):**

```
SMART RECORDING:
- neo4j-memory: Current state only
  → "progress: step 3 of 7"
  → "blocked_by: missing API key"
  → "next: configure environment"
- neo4j-memory: Significant milestones only
  → "project_id={{PROJECT_ID}}; milestone: authentication system complete"
  → "project_id={{PROJECT_ID}}; blocker_resolved: API key issue → used env file"
- sequential-thinking: Validation checkpoints
```

**6. CONTEXT SAVE PHASE (Curated Knowledge Transfer):**

```
FINAL KNOWLEDGE EXTRACTION:
1. Review memory for important outcomes → transfer to neo4j-memory
   → Look through session notes for patterns, solutions, decisions
   → Save ONLY high-value learnings to neo4j-memory
2. neo4j-memory: Persist CURATED KNOWLEDGE
   → "project_id={{PROJECT_ID}}; session_outcome: implemented JWT auth successfully"
   → "project_id={{PROJECT_ID}}; key_learning: always use python-jose[cryptography]"
   → "project_id={{PROJECT_ID}}; resolved_issue: CORS → add middleware before routes"
   → "project_id={{PROJECT_ID}}; next_session: need to add refresh token logic"
```

## **MCP TOOL SELECTION MATRIX**

### Task-to-Tool Mapping:

| Task Type                   | Primary MCP Tools                                            | Secondary Tools                 |
| --------------------------- | ------------------------------------------------------------ | ------------------------------- |
| **Starting New Session**    | neo4j-memory...                                              | memory                          |
| **Before Writing ANY Code** | context7 (docs), grep (examples)                             | fetch, filesystem               |
| **Planning Features**       | sequential-thinking, extended-memory                         | memory                          |
| **Debugging Issues**        | grep (search errors), context7 (API docs)                    | sequential-thinking, filesystem |
| **Writing New Code**        | context7 (FIRST), grep (SECOND), filesystem                  | memory, neo4j-memory            |
| **Refactoring**             | context7 (patterns), grep (examples), filesystem             | sequential-thinking             |
| **Frontend Development**    | context7 ({{FRAMEWORK_EXAMPLES}} docs), shadcn-ui, chakra-ui | lucide-icons, vite-plugin       |
| **API Testing**             | context7 (API docs), playwright, fetch                       | memory, sequential-thinking     |
| **Documentation**           | context7 (current specs), filesystem                         | neo4j-memory                    |
| **Security Analysis**       | grep (vulnerabilities), context7 (security docs)             | sequential-thinking, fetch      |
| **Performance**             | context7 (optimization docs), grep (patterns)                | time, neo4j-memory              |

## **MCP TOOL USAGE PATTERNS**

### Common Tool Combinations:

**Pattern 1: Feature Implementation (CORRECT ORDER)**

```
eneo4j-memory (load) → context7 (get latest docs) →
grep (find examples) → sequential-thinking (plan) →
filesystem (implement) → neo4j-memory (track) →
neo4j-memory (save)
```

**Pattern 2: Bug Investigation**

```
neo4j-memory (load context) → grep (search error patterns) →
context7 (check API docs) → sequential-thinking (analyze) →
filesystem (read logs) → filesystem (fix) →
neo4j-memory (document fix)
```

**Pattern 3: Frontend Component Creation**

```
context7 ({{FRAMEWORK_EXAMPLES}} docs) → grep (component examples) →
shadcn-ui (get component) → filesystem (integrate) →
lucide-icons (add icons) → vite-plugin (build) →
playwright (test) → neo4j-memory (save)
```

**Pattern 4: API Development**

```
context7 ({{FRAMEWORK_EXAMPLES}} docs) → grep (endpoint patterns) →
sequential-thinking (design) → filesystem (implement) →
fetch (test endpoints) → eneo4j-memory (persist)
```

======================================================================================================================================================================

## **PROTOCOL SECTION C: COMPLIANCE RULES & MEMORY PROTOCOLS**

_Referenced by: ai-agent-compliance.md Section 3 - Compliance Rules_

### **MANDATORY MEMORY RECORDING PROTOCOL**

### 🔴 CLEAR DIVISION: memory (PROCESS) vs neo4j-memory (OUTCOMES)

**USE memory FOR ACTIVE WORK (Session Scratchpad):**

```
memory: "current_focus: implementing user authentication"
memory: "trying: add JWT middleware to FastAPI"
memory: "debug: token validation failing, checking secret key"
memory: "note: need to add CORS headers after this"
memory: "next_step: test with Postman"
```

**USE neo4j-memory FOR SIGNIFICANT OUTCOMES (Knowledge Base):**

```
neo4j-memory: "project_id={{PROJECT_ID}}; pattern: JWT in FastAPI requires python-jose"
neo4j-memory: "project_id={{PROJECT_ID}}; solution: CORS error fixed by app.add_middleware()"
neo4j-memory: "project_id={{PROJECT_ID}}; decision: chose JWT over sessions for stateless API"
neo4j-memory: "project_id={{PROJECT_ID}}; learning: always validate tokens in middleware, not endpoints"
```

**WHEN ENCOUNTERING ERRORS:**

```
memory: "error: ImportError jose, trying: pip install python-jose"
memory: "still failing, checking: requirements.txt"
memory: "found: need cryptography backend"
[After resolution]
neo4j-memory: "project_id={{PROJECT_ID}}; issue: ImportError jose → solution: pip install python-jose[cryptography]"
```

**NO DUPLICATION:**

- memory = temporary work notes (deleted after session)
- neo4j-memory = permanent knowledge (preserved forever)

## **MANDATORY COMPLIANCE RULES**

1. **🔴 ALWAYS use context7 BEFORE writing code** - Get current, accurate documentation
2. **🔴 ALWAYS use grep to search GitHub** - Find real production examples
3. **🔴 ALWAYS record actions in memory AS YOU WORK** - Document everything
4. **🔴 ALWAYS save to neo4j-memory** - Preserve for future sessions
5. **NEVER skip the Context Load phase** - Always start by loading relevant context
6. **NEVER implement without Research phase** - context7 + grep are MANDATORY
7. **NEVER complete without Context Save** - Always persist learnings and decisions
8. **ALWAYS use sequential-thinking for complex tasks** - Structure your approach
9. **ALWAYS use memory for session tracking** - Maintain progress visibility
10. **ALWAYS use neo4j-memory for cross-session persistence** - Preserve knowledge

**THE GOLDEN RULE: context7 (docs) → grep (examples) → memory (record) → code → neo4j-memory (persist)**

======================================================================================================================================================================

## **PROTOCOL SECTION D: NEO4J MEMORY SPECIFICATIONS**

_Referenced by: ai-agent-compliance.md Section 4 - Neo4j Memory Requirements_

### **MCP TOOLS USAGE DETAILS**

#### memory (@modelcontextprotocol/server-memory) 📝 CONTINUOUS ACTION TRACKING

**Purpose:** Real-time session tracking of EVERY action, decision, and outcome.

**When to use:**

- CONTINUOUSLY throughout the session - after EVERY significant action.
- Track all attempts, successes, failures, decisions, and reasoning.
- Document what you're doing AS you're doing it.
- Create audit trail for neo4j-memory to persist.

**How to use well:**

- Record BEFORE action: "attempting: [action], reason: [why]"
- Record AFTER action: "result: [outcome], issues: [any_problems]"
- Track decisions: "chose: [option], rejected: [alternatives], because: [reasoning]"
- Log errors immediately: "error: [message], attempting fix: [solution]"

**Example prompts:**

- "action_1: reading package.json to check React version"
- "result_1: React 18.2.0 found, compatible with our requirements"
- "decision_1: using useEffect with cleanup, rejected useLayoutEffect, reason: not needed for this async operation"
- "error_1: TypeError undefined, cause: missing null check, fix: adding optional chaining"
- "progress: completed 3 of 7 planned steps, on track"

**Safety:**
This is session-only memory - ALWAYS transfer to neo4j-memory at session end.

#### sequential-thinking (@modelcontextprotocol/server-sequential-thinking)

**Purpose:** Plan-before-act reasoning and gated execution.

**When to use:**

- Complex tasks, multi-step debugging, architecture decisions, migrations.

**How to use well:**

- Always produce a short plan with numbered steps and explicit success criteria.
- Insert checkpoints: "After step 2, reassess assumptions and update plan."
- Gate tool use: "Only invoke filesystem after user confirmation or after validations."
- After each step, verify results and update plan; if a step fails, do root-cause before proceeding.

**Example prompts:**

- "Outline steps to fix flaky test; run only steps 1–2; pause to verify logs."
- "Plan OAuth2 migration; list assumptions; identify unknowns; propose minimal-risk rollout."

**Safety:**
Never skip validation between steps; avoid cascading failures.

#### fetch (fetch-mcp)

**Purpose:** Retrieve HTTP(S) content like docs, JSON, or small text artifacts.

**When to use:**

- Get official docs, API responses, release notes, config files.

**How to use well:**

- Always state URL, expected content type, and size limit.
- If auth is required, reference an environment variable—not inline secrets.
- Parse JSON responses formally; capture only necessary fields.
- Implement retry/backoff if endpoint is transient and tool supports it.

**Example prompts:**

- "Fetch https://api.example.com/v1/users?limit=50; extract [id,email]; stop if response > 1MB."
- "Download CHANGELOG.md from https://example.com/release; summarize breaking changes."

**Safety:**
Don't download large/binary artifacts. Avoid PII scraping. Respect rate limits.

#### filesystem (@modelcontextprotocol/server-filesystem)

**Purpose:** Read/write files in allowed paths.

**When to use:**

- Read code/docs, scaffold files, apply edits, create summaries.

**How to use well:**

- Read-before-write: verify the target file exists and is in scope.
- Write atomically and minimally; keep edits tightly scoped.
- Use repo-relative paths. Confirm binary vs text.
- For multi-file changes, proceed one file at a time with validation in between.

**Example prompts:**

- "List .md under docs/; extract headings and generate a TOC."
- "Append a 'Security' section to docs/arch.md; keep existing formatting."

**Safety:**
Stay within repo/project roots. Never touch secrets or OS/system dirs.
Avoid mass refactors without prior plan and checkpoints.

#### time (mcp-server-time) 🕐 MANDATORY TIMESTAMP OPERATIONS

**Purpose:** Timestamps and time math for MANDATORY reverse date stamp requirements.

**When to use:**

- UTC timestamps, ISO formatting, durations, date math for scheduling/labels, and ALL output file naming.

**How to use well:**

- Always specify timezone (prefer UTC).
- Prefer ISO-8601 for timestamps. Be explicit about business vs calendar days.
- MANDATORY: Use reverse date stamp format YYYY-MM-DD-HHMMSS for ALL file outputs.

**Example prompts:**

- "Provide current UTC timestamp in reverse date stamp format YYYY-MM-DD-HHMMSS."
- "Generate reverse date stamp for file naming: YYYY-MM-DD-HHMMSS."
- "Add 72h to 2025-08-01T10:00:00Z and format as reverse date stamp."

**Safety:**
Do not attempt to change system time or rely on local timezone.
MANDATORY: Always use UTC time for reverse date stamp generation.
FORBIDDEN: Creating files without proper reverse date stamps.

#### grep remote (mcp-remote https://mcp.grep.app) 🔴 MANDATORY BEFORE CODING

**Purpose:** Search GitHub for real-world production code examples.

**When to use:**

- ALWAYS before implementing ANY feature - find how others solved it.
- Before debugging - search for similar error patterns.
- Before refactoring - find best practice patterns.

**How to use well:**

- Search for EXACT function/method names you plan to use.
- Find 5-10 examples and identify common patterns.
- Look for highly-starred repos for quality examples.

**Example prompts:**

- "Search GitHub for '[function_name]' in {{FRAMEWORK_EXAMPLES}} projects"
- "Find '[pattern_name]' patterns in [language] repos"
- "Search for '[feature] with [requirement]' implementations"
- "Find '[framework] [version] [component]' examples"

**Safety:**
Validate examples before applying. Check repo stars/activity. Cite sources.

#### context7 (@upstash/context7-mcp) 🔴 MANDATORY BEFORE CODING

**Purpose:** Fetch up-to-date, version-specific documentation to prevent hallucinations.

**When to use:**

- ALWAYS before writing code with ANY framework/library.
- When debugging - get accurate error message meanings.
- Before using any API - get current endpoint specifications.
- When unsure about syntax - get official documentation.

**How to use well:**

- Always prefix with "use context7:" in your query.
- Specify exact versions when needed.
- Get docs for ALL libraries you'll use BEFORE coding.

**Example prompts:**

- "use context7: {{FRAMEWORK_EXAMPLES}} [specific feature]"
- "use context7: [Framework] [version] [component]"
- "use context7: [Library] implementation patterns"
- "use context7: [Technology] best practices"
- "use context7: [Tool] configuration examples"

**Safety:**
Always verify version compatibility. Cross-reference with package.json.

#### neo4j-memory 🧠 PERSISTENT KNOWLEDGE BASE

**Purpose:** Cross-session memory that preserves ALL actions, outcomes, issues, and learnings.

**When to use:**

- START of session: Load ALL previous context, issues, solutions, patterns.
- DURING session: Save significant discoveries, errors, and resolutions.
- END of session: Persist COMPLETE session history for future reference.

**How to use well:**

- Load comprehensively: "load all actions, outcomes, issues from last 10 sessions"
- Save with detail: "action: implemented auth → outcome: success with JWT"
- Record problems: "issue: CORS error → solution: added proxy config"
- Track patterns: "pattern: useEffect cleanup prevents memory leaks"
- Build knowledge: "learning: always check package.json before using new syntax"

**Example prompts:**

- "project_id={{PROJECT_ID}}; load all previous [feature] implementations"
- "project_id={{PROJECT_ID}}; save issue: [problem], solution: [fix]"
- "project_id={{PROJECT_ID}}; save pattern: always use context7 before implementing [feature]"
- "project_id={{PROJECT_ID}}; save outcome: [task] successful, [result]"
- "project_id={{PROJECT_ID}}; load all [topic]-related decisions and their outcomes"

**Config:**
STORAGE_CONNECTION_STRING={{DB_PATH}}
Creates persistent knowledge graph of all your actions and their results.

**Safety:**
This is your permanent knowledge base - treat it as source of truth.

#### Pointers to local helper docs

For quick, server-specific tips and examples, see:

- `.claude/mcp-configs/helper.memory.md`
- `.claude/mcp-configs/helper.sequential-thinking.md`
- `.claude/mcp-configs/helper.frontend-mcp.md` (pattern guidance for UI-related MCPs)
- `.claude/mcp-configs/helper.modelcontextprotocol.md` (baseline for common MCP servers)
- `.claude/mcp-configs/helper.context7-mcp.md`
- `.claude/mcp-configs/helper.neo4j-memory-mcp.md`

#### General safety and workflow

Plan before acting (sequential-thinking). Retrieve memory first (memory/context7/neo4j-memory). Use least-privilege paths (filesystem). Never embed secrets in prompts; rely on env. Validate after each step; roll back on unexpected diffs.

**This thinking requirement is MANDATORY and must be followed for every action.**

======================================================================================================================================================================

## **PROTOCOL SECTION G: PROTOCOL COMPLIANCE & ENFORCEMENT**

_Referenced by: ai-agent-compliance.md Section 7 - Protocol Compliance_

### **CANONICAL PROTOCOL ENFORCEMENT - READ FIRST**

**THIS SECTION IS MANDATORY AND MUST BE READ, INDEXED, AND FOLLOWED BEFORE ANY COMMAND EXECUTION**

### 1. PROTOCOL COMPLIANCE REQUIREMENTS

**BEFORE PROCEEDING, YOU MUST READ, INDEX, AND COMMIT TO STRICT ADHERENCE:**

1. **MUST READ AND INDEX:** `./.claude/commands/core/code-protocol-compliance.md` - Base compliance requirements and RFC 2119 language

   - **COMMITMENT:** I will strictly adhere to ALL compliance requirements without exception
   - **VIOLATION RESPONSE:** Any violation will trigger immediate halt and root cause analysis

2. **MUST READ AND INDEX:** `./.claude/commandsdocumentation-protocol-.md` - Documentation creation requirements

   - **COMMITMENT:** I will create documentation ONLY when explicitly instructed and follow ALL naming conventions
   - **VIOLATION RESPONSE:** Any unauthorized documentation creation will trigger immediate halt and protocol review

3. **MUST READ AND INDEX:** `./.claude/commands/core/code-protocol-single-branch-.md` - Git workflow requirements

   - **COMMITMENT:** I will work EXCLUSIVELY on development branch and follow atomic commit requirements
   - **VIOLATION RESPONSE:** Any sacred branch violation or improper commits will trigger immediate halt and workflow analysis

4. **MUST READ AND INDEX:** `./.claude/commands/core/code-protocol-security-.md` - Security compliance requirements

   - **COMMITMENT:** I will implement ALL security requirements and never compromise on security practices
   - **VIOLATION RESPONSE:** Any security violation will trigger immediate halt and security protocol review

5. **VERIFY:** User has given explicit permission to proceed

   - **COMMITMENT:** I will not proceed without explicit user authorization
   - **VIOLATION RESPONSE:** Acting without permission will trigger immediate halt and authorization review

6. **ACKNOWLEDGE AND COMMIT:** ALL CANONICAL PROTOCOL requirements with binding adherence
   - **BINDING COMMITMENT:** I hereby commit to strict, unwavering adherence to ALL protocol requirements
   - **ENFORCEMENT MANDATE:** I will enforce these protocols on myself and other AI agents
   - **VIOLATION PROTOCOL:** Any violation will trigger the mandatory violation response procedure below

**FORBIDDEN:** Proceeding without complete protocol compliance verification AND binding commitment to adherence

### MANDATORY VIOLATION RESPONSE PROCEDURE

**WHEN ANY PROTOCOL VIOLATION OCCURS (by self or other AI agents):**

1. **IMMEDIATE HALT:** Stop ALL operations immediately
2. **VIOLATION DECLARATION:** Clearly state: "PROTOCOL VIOLATION DETECTED - HALTING OPERATIONS"
3. **ROOT CAUSE ANALYSIS:** Perform comprehensive analysis:

   - What specific protocol was violated?
   - Why did the violation occur?
   - What decision-making failure led to the violation?
   - Was the protocol requirement unclear or misunderstood?
   - Was there insufficient attention to protocol requirements?
   - Was there a deliberate choice to ignore protocols?

4. **CORRECTIVE ACTION PLAN:** Develop specific plan to:

   - Correct the immediate violation
   - Prevent future violations of the same type
   - Strengthen protocol adherence mechanisms
   - Re-read and re-index all relevant protocol files

5. **PROTOCOL REINFORCEMENT:** Before resuming any operations:

   - Re-read ALL violated protocol files
   - Demonstrate understanding of the violated requirements
   - Commit to stricter adherence monitoring
   - Implement additional safeguards against future violations

6. **USER NOTIFICATION:** Inform the user of:
   - The specific violation that occurred
   - The root cause analysis findings
   - The corrective actions taken
   - The reinforcement measures implemented
   - Request explicit permission to resume operations

**ENFORCEMENT MANDATE:** This violation response procedure is MANDATORY and NON-NEGOTIABLE. Any AI agent that fails to follow this procedure upon detecting a violation has committed an additional protocol violation requiring its own halt and analysis.

### 2. CONTEXT-BASED STRATEGY READING REQUIREMENTS

**BASED ON TASK CONTEXT, YOU MUST READ AND INDEX RELEVANT STRATEGY FILES:**

**IF TASK INVOLVES DOCUMENTATION:**

- **MUST READ AND INDEX:** `./.claude/commandsdocumentation-protocol-strategy.md`
- Contains: Documentation philosophy, filename conventions, content structure, version control

**IF TASK INVOLVES GIT OPERATIONS:**

- **MUST READ AND INDEX:** `./.claude/commands/core/code-protocol-single-branch-strategy.md`
- Contains: Git workflow philosophy, detailed procedures, backup methods, recovery procedures

**IF TASK INVOLVES SECURITY ANALYSIS/IMPLEMENTATION:**

- **MUST READ AND INDEX:** `./.claude/commands/core/code-protocol-security-strategy.md`
- Contains: Security philosophy, validation methods, encryption procedures, monitoring protocols

**STRATEGY FILE READING IS MANDATORY** - These files contain the detailed philosophy, methods, and procedures that govern HOW to execute the requirements defined in the prompt files.

### 3. SINGLE BRANCH DEVELOPMENT STRATEGY - MANDATORY

**FOLLOW THE SINGLE BRANCH DEVELOPMENT PROTOCOL:**

- ALL git workflows MUST follow the protocol defined in `code-protocol-single-branch-.md` and `code-protocol-single-branch-strategy.md`
- **SACRED BRANCHES:** {{SACRED_BRANCHES}} are protected - NEVER work directly on them
- **SINGLE WORKING BRANCH:** {{WORKING_BRANCH}} branch ONLY - work directly on {{WORKING_BRANCH}}
- **NO FEATURE BRANCHES:** FORBIDDEN to create feature/fix branches without explicit permission
- **ATOMIC COMMITS:** One logical change per commit with conventional format including AI instance ID
- **IMMEDIATE BACKUP:** Push to origin after every commit

### 4. CONTAINERIZED APPLICATION REQUIREMENTS

**FOR CONTAINERIZED APPLICATIONS, YOU MUST:**

1. Build the container after EVERY code change
2. Check container logs for errors/warnings
3. Validate application functionality
4. Ensure all services are healthy
5. Test API endpoints if applicable
6. Verify no regression issues

**IF BUILD/DEPLOY ISSUES OCCUR:**

- Follow debugging protocol in `./.claude/commands/code/code-debug.md`
- Use refactoring protocol in `./.claude/commands/code/code-refactor.md`
- Apply planning protocol in `./.claude/commands/code/code-planning.md`
- Implement fixes per `./.claude/commands/code/code-implement.md`
- Ensure security compliance per `./.claude/commands/code/code-security-analysis.md`

### 5. CODE CHANGE COMPLIANCE WITH STRATEGY INTEGRATION

**FOR ALL CODE CHANGES, YOU MUST:**

1. Find the relevant command in `./.claude/commands/code/` for your current task
2. READ the entire command protocol
3. **READ RELEVANT STRATEGY FILES** based on task context (see section 2 above)
4. UNDERSTAND the requirements, patterns, philosophy, and detailed procedures
5. FOLLOW both prompt requirements AND strategy methods exactly for consistency and correctness

**ENHANCED COMMAND MAPPING:**

- Debugging issues → `code-debug.md` + security strategy if security-related
- Implementation → `code-implement.md` + git strategy for commits + security strategy if handling sensitive data
- Refactoring → `code-refactor.md` + git strategy for atomic changes
- Performance → `code-performance-analysis.md`
- Security → `code-security-analysis.md` + **MUST READ** security strategy
- Testing → `code-testing-live-api.md`
- Documentation → `code-documentation.md` + **MUST READ** documentation strategy

### 6. RTFM (READ THE FUCKING MANUAL) - MANDATORY

**YOU MUST ALWAYS:**

**RESEARCH ANALYSIS PRIORITIES:**

1. Official documentation (latest version)
2. GitHub repositories with high stars
3. Industry standard implementations
4. Recent blog posts/tutorials (< 1 year old)
5. Community best practices

**EXPORE THE CODE BASE FIRST\*\*** [SEARCH]
Conduct comprehensive research and analysis before any implementation.

1. **Codebase Discovery**

   - Search for existing implementations and patterns
   - Identify reusable components and utilities
   - Understand architectural decisions and constraints
   - Document relevant file locations and dependencies

2. **Technical Research**

   - Read the most up to date online resources and documentation FIRST
   - Review framework/library documentation
   - Analyze best practices and anti-patterns
   - Research performance implications
   - Identify potential security concerns

3. **SMART JUPYTER NOTEBOOK REVIEW:**

   - Search for .ipynb files in the repository (INDEX ONLY)
   - Read max 2-3 most relevant notebooks for context
   - Focus on key analysis notebooks for insights
   - Sample documentation notebooks for patterns (not all)

4. **SMART PROJECT DOCUMENTATION REVIEW:**

   - Index `./docs` directory structure (don't read all files)
   - Check `./project/docs` if it exists (selective reading)
   - Read main README files (max 3-5 README files)
   - Review key architecture documentation (not all docs)
   - Study main API documentation (core endpoints only)

5. **SEARCH ONLINE FOR BEST PRACTICES:**

   - Use web search for latest documentation
   - Find official framework/library docs
   - Search GitHub for example implementations
   - Review industry best practices
   - Study similar successful projects
   - Check Stack Overflow for common patterns

6. **Requirements Analysis**
   - Clarify ambiguous requirements
   - Define acceptance criteria
   - Identify edge cases and error scenarios
   - Document assumptions and decisions

### 7. MANDATORY DEVSECOPS LOOP WITH MCP TOOL INTEGRATION

**ALL CODE OPERATIONS MUST FOLLOW THE DEVSECOPS CYCLE WITH MCP TOOLS:**

**THE INFINITE LOOP WITH MCP TOOLS:**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. PLAN → 2. CODE → 3. BUILD → 4. TEST → 5. DEPLOY   │
│     (seq)    (grep)   (file)   (play)    (file)       │
│       ↑                                          ↓      │
│       │                                          ↓      │
│  8. MONITOR ← 7. OPERATE ← 6. SECURE/VALIDATE ←─┘      │
│    (memory)     (fetch)        (grep/seq)              │
│       │                                                 │
│       └────────(neo4j-memory: persist cycle)────────┘
```

**MANDATORY PHASES WITH MCP TOOL USAGE:**

1. **PLAN** (code-planning.md) + **MCP TOOLS:**

   - `neo4j-memory`: Load project context
   - `sequential-thinking`: Structure requirements
   - `grep`: Find reusable patterns
   - `fetch`: Get latest best practices
   - `context7`: Search past architectural decisions
   - `memory`: Track planning progress
   - **READ git strategy** for commit planning
   - **READ security strategy** if security-relevant

2. **CODE** (code-implement.md) + **MCP TOOLS:**

   - `filesystem`: Read/write code files
   - `grep`: Find implementation examples
   - `memory`: Track changes
   - `sequential-thinking`: Validate against plan
   - Frontend: `shadcn-ui`, `chakra-ui` for UI
   - **FOLLOW git strategy** for atomic commits
   - **APPLY security strategy** for secure coding

3. **BUILD** (code-validation.md) + **MCP TOOLS:**

   - `filesystem`: Read build configs
   - `memory`: Track build issues
   - `vite-plugin`: Frontend builds
   - Type checking and linting
   - Dependency validation

4. **TEST** (code-testing-live-api.md) + **MCP TOOLS:**

   - `playwright`: Automated browser testing
   - `fetch`: API endpoint testing
   - `sequential-thinking`: Test strategy
   - `memory`: Track test results
   - **SECURITY TESTS** per security strategy

5. **DEPLOY** (code-deploy.md) + **MCP TOOLS:**

   - `filesystem`: Update configs
   - `fetch`: Validate endpoints
   - `memory`: Track deployment status
   - `neo4j-memory`: Save deployment info
   - Service health checks

6. **SECURE/VALIDATE** (code-security-analysis.md) + **MCP TOOLS:**

   - `grep`: Search for vulnerabilities
   - `sequential-thinking`: Security analysis
   - `fetch`: Get security advisories
   - `neo4j-memory`: Document findings
   - **MUST READ security strategy** before execution

7. **OPERATE** (code-operational-analysis.md) + **MCP TOOLS:**

   - `filesystem`: Read logs
   - `fetch`: Monitor endpoints
   - `time`: Track performance metrics
   - `memory`: Session monitoring
   - `neo4j-memory`: Persist operations data

8. **MONITOR** (code-review.md) + **MCP TOOLS:**
   - `sequential-thinking`: Analyze metrics
   - `context7`: Store learnings
   - `neo4j-memory`: Update knowledge base
   - `memory`: Track improvements
   - Loop restart with enhanced context

======================================================================================================================================================================

## **PROTOCOL SECTION H: ENTERPRISE SAFETY PROTOCOLS**

_Referenced by: ai-agent-compliance.md Section 8 - Enterprise Code Change Safety_

### **ENTERPRISE CODE CHANGE SAFETY WITH PROTOCOL INTEGRATION**

**MANDATORY SAFETY PROTOCOL:**

1. **ANALYZE** before changing (understand dependencies)
2. **READ RELEVANT STRATEGY FILES** based on change context
3. **PLAN** the change following strategy methodology
4. **IMPLEMENT** incrementally using strategy procedures
5. **TEST** after each change following strategy guidelines
6. **VALIDATE** in container/deployment per strategy requirements
7. **DOCUMENT** changes per documentation strategy (if creating docs)
8. **COMMIT** following git strategy requirements with AI instance ID

**FORBIDDEN PRACTICES:**

- Making changes without reading relevant strategy files
- Skipping protocol prompt file requirements
- Making large, non-atomic changes
- Ignoring strategy methodology
- Proceeding without understanding philosophy

**ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:**

- **NO MOCKING** of data or services in production code
- **NO TODOs** - complete ALL work immediately
- **NO SHORTCUTS** - implement properly ALWAYS following strategy methods
- **NO STUBS** - write complete implementations per strategy guidelines
- **NO FIXED DATA** - use real, dynamic data
- **NO HARDCODED VALUES** - use configuration
- **NO WORKAROUNDS** - fix root causes using strategy procedures

### 10. COMPLIANCE VERIFICATION CHECKLIST WITH MCP TOOL INTEGRATION

**PRE-TASK MCP TOOL CHECKLIST:**

- [ ] **neo4j-memory** loaded with project context?
- [ ] **context7** searched for relevant past decisions?
- [ ] **sequential-thinking** engaged for planning?
- [ ] **memory** initialized for session tracking?

**TASK EXECUTION CHECKLIST:**

- [ ] **ALL PROTOCOL PROMPT FILES** read and indexed?
- [ ] **RELEVANT STRATEGY FILES** identified and read based on task context?
- [ ] User permission verified?
- [ ] Currently on {{WORKING_BRANCH}} branch (NOT feature branch)?
- [ ] **grep** used to find code examples?
- [ ] **fetch** used to get latest documentation?
- [ ] **filesystem** used to scan local codebase?
- [ ] Relevant code command identified?
- [ ] Dependencies understood?
- [ ] Test strategy planned with **playwright** if applicable?
- [ ] Security considerations addressed per security strategy?
- [ ] Git workflow planned per git strategy?
- [ ] Documentation approach planned per documentation strategy (if applicable)?
- [ ] Rollback plan ready?

**POST-TASK MCP TOOL CHECKLIST:**

- [ ] **memory** updated with session summary?
- [ ] **neo4j-memory** persisted all decisions?
- [ ] **context7** stored semantic knowledge?
- [ ] All MCP tools properly closed/saved?

**FORBIDDEN**
YOU ARE FORBIDDEN from creating custom scripts to fix or remediate the code base, YOU HAVE CONTINUIOUSLY corrupted the code base through poor "fix" scripts
YOU MUST NEVER EVER EVER create custom scripts to fix or remediate the code base

**ENFORCEMENT:** Any violation requires IMMEDIATE STOP and correction

**REMEMBER:** Professional enterprise development requires discipline, planning, systematic execution, proper tool usage, protocol compliance, strategy methodology understanding, and clean session management. NO SHORTCUTS.

---

======================================================================================================================================================================

## **PROTOCOL SECTION I: TEMPLATE CONFIGURATION**

_Referenced by: ai-agent-compliance.md Section 9 - Template Configuration_

### **TEMPLATE CONFIGURATION**

When using this template in a new project, replace these variables:

```yaml
PROJECT_ID: "{{PROJECT_ID}}" # e.g., "ai-agents", "web-app", "api-service"
PROJECT_NAME: "{{PROJECT_NAME}}" # e.g., "AI Agents Platform"
WORKING_BRANCH: "{{WORKING_BRANCH}}" # e.g., "development", "dev", "feature"
SACRED_BRANCHES: "{{SACRED_BRANCHES}}" # e.g., "main/master/production"
DB_PATH: "{{DB_PATH}}" # e.g., "neo4j-memory db"
FRAMEWORK_EXAMPLES: "{{FRAMEWORK_EXAMPLES}}" # e.g., "React, Next.js, FastAPI"
```

Example for a React/Node.js project:

```yaml
PROJECT_ID: "ecommerce-frontend"
PROJECT_NAME: "E-Commerce Platform"
WORKING_BRANCH: "development"
SACRED_BRANCHES: "main/production"
DB_PATH: "sqlite:///./memory/ecommerce.db"
FRAMEWORK_EXAMPLES: "React 18, Node.js, Express, PostgreSQL"
```

Example for a Python API project:

```yaml
PROJECT_ID: "ml-api-service"
PROJECT_NAME: "ML API Service"
WORKING_BRANCH: "dev"
SACRED_BRANCHES: "main/staging/production"
DB_PATH: "sqlite:///./data/ml-api-memory.db"
FRAMEWORK_EXAMPLES: "FastAPI, SQLAlchemy, Pydantic, Celery"
```
