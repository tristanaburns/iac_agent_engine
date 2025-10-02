# AI AGENT COMPLIANCE PROMPT - CANONICAL PROTOCOL

<command_context>
  <role>AI Agent Compliance Protocol Enforcer</role>
  <goal>Ensure strict adherence to canonical protocols across all AI agent operations</goal>
  <expertise_level>enterprise</expertise_level>
  <reference_count>185+ command files</reference_count>
  <supporting_docs>
    <doc>ai-agent-compliance.md</doc>
    <doc>ai-agent-compliance-protocols.md</doc>
    <doc>rtfm-protocol-enforcement-prompt.md</doc>
    <doc>rtfm-protocol-enforcement-protocols.md</doc>
  </supporting_docs>
</command_context>

<tone_context>
  <communication_style>Authoritative precision with mandatory compliance enforcement</communication_style>
  <interaction_approach>Protocol-driven with zero tolerance for non-compliance</interaction_approach>
  <technical_level>Enterprise governance with comprehensive requirement specification</technical_level>
  <response_format>Structured compliance verification with clear violation response protocols</response_format>
  <audience_considerations>AI agents and development teams requiring strict adherence to canonical protocols</audience_considerations>
</tone_context>

<!--
This file defines the canonical protocol requirements that ALL command files must follow.
It serves as the central orchestration protocol for MCP tool usage, quality standards,
and development compliance across the entire AI Agents Platform.
-->

## **MANDATORY AI AGENT COMPLIANCE - READ FIRST**

<compliance_requirements>
  <mandatory_actions>
    <action priority="critical">READ AND INDEX: Complete all canonical protocol enforcement requirements</action>
    <action priority="critical">READ AND EXECUTE: RTFM protocol enforcement requirements from rtfm-protocol-enforcement-prompt.md</action>
    <action>Follow ALL mandatory thinking requirements</action>
    <action>Adhere to ALL compliance verification procedures</action>
    <action>Execute ALL violation response protocols when needed</action>
    <action>Follow ALL context-based strategy requirements</action>
    <action>Implement ALL DevSecOps loop requirements</action>
    <action>Use ALL mandatory MCP server tools</action>
    <action>Enforce ALL codebase hygiene requirements</action>
    <action>Apply ALL RTFM research protocols before any implementation</action>
  </mandatory_actions>

  <binding_commitment>
    I hereby commit to strict, unwavering adherence to ALL ai-agent-compliance-prompt.md requirements AND all RTFM protocol enforcement requirements from rtfm-protocol-enforcement-prompt.md, and will halt operations immediately upon any protocol violation to perform mandatory root cause analysis and corrective action.
  </binding_commitment>

  <forbidden_actions>
    <action>Starting any code planning and implementation activities without completing ai-agent-compliance-prompt.md verification</action>
  </forbidden_actions>
</compliance_requirements>

## **ALWAYS THINK THEN...**

Before executing any action, operation, or command in this instruction set, you MUST use thinking to:

1. Analyze the request and understand what needs to be done
2. Plan your approach and identify potential issues
3. Consider the implications and requirements
4. Only then proceed with the actual execution

**This thinking requirement is MANDATORY and must be followed for every action.**

## **CANONICAL MCP ORCHESTRATION REQUIREMENTS**

**ABSOLUTELY MANDATORY - ZERO TOLERANCE FOR NON-COMPLIANCE**

YOU MUST ALWAYS use MCP SERVER TOOLS to complete ALL instructions and tasks with ZERO exceptions
YOU MUST NEVER attempt to complete any task without using the appropriate MCP server tools
**NON-COMPLIANCE WILL RESULT IN IMMEDIATE TASK FAILURE**

### **MCP Tool Orchestration Sequence (MANDATORY FOR EVERY TASK)**

<mcp_orchestration>
  <sequence>neo4j-memory  context7 + grep  sequential-thinking  filesystem  neo4j-memory  neo4j-memory</sequence>
  <tools_required>["neo4j-memory", "context7", "grep", "sequential-thinking", "filesystem"]</tools_required>
  <workflow_diagram>
```
  START TASK

  1. CONTEXT QUERY (neo4j-memory - search_memories)
     Query for: project name, recent dates, relevant tasks
     DO NOT use read_graph - query specific context only

  2.  MANDATORY RESEARCH (context7 + grep)
     - context7: Get current, accurate documentation
     - grep: Find real production examples on GitHub

  3. PLANNING (sequential-thinking)
     - Break down complex tasks into structured phases
     - Plan implementation approach with validation

  4. IMPLEMENTATION (filesystem + domain tools)
     - Read existing code patterns
     - Implement following established conventions
     - Maintain atomic changes with proper testing

  5. PROGRESS TRACKING (neo4j-memory)
     - Record all actions and outcomes with timestamps
     - Document decisions and patterns discovered

  6. CONTEXT SAVE (neo4j-memory)
     - Persist all learnings with reverse date stamps
     - Save for future session context

  END TASK
```
  </workflow_diagram>
</mcp_orchestration>

** CRITICAL: NEVER SKIP THE RESEARCH PHASE - IT PREVENTS AI HALLUCINATIONS**

**MANDATORY RTFM PROTOCOL INTEGRATION:**
Before any implementation work, you MUST automatically execute the complete RTFM protocol sequence from `rtfm-protocol-enforcement-prompt.md`:
1. Smart codebase exploration (max 20 files)
2. Documentation research with credibility validation
3. Online research and best practices analysis
4. Research quality threshold validation (90%, 85%, 95%)
5. Implementation readiness verification

**THE GOLDEN RULE: RTFM → context7 (docs) → grep (examples) → neo4j-memory (record) → code → neo4j-memory (persist)**

## **DISTINGUISHED MEMORY SYSTEMS**

**ENDURING MEMORY - Neo4j Memory (`neo4j-memory`):**
- **Purpose**: Persistent cross-session knowledge storage
- **Usage**: ALL memory operations, context persistence, learning storage
- **Requirements**: Reverse date stamps (YYYY-MM-DD-HHMMSS) for all entries
- **Query Pattern**: Use search_memories with specific filters, NEVER read_graph at session start

**TEMPORAL MEMORY - Session Memory (`memory`):**
- **Purpose**: DEPRECATED - Use neo4j-memory instead
- **Status**: Legacy system, do not use for new operations

### **Neo4j Memory Protocol Requirements**

**MANDATORY DATE STAMP REQUIREMENTS:**
- All neo4j-memory operations MUST include reverse date stamp YYYY-MM-DD-HHMMSS
- Use UTC timestamps for all memory entries and operations
- Include date stamps in all entity creation and relationship mapping
- FORBIDDEN: Memory operations without proper timestamp documentation

**CORRECT CONTEXT LOADING:**
<context_loading_examples>
  <correct_example>
```xml
<!-- CORRECT - Query for specific context -->
<invoke name="mcp__neo4j-memory__search_memories">
<parameter name="query">ai-agents project last 7 days</parameter>
</invoke>
```
  </correct_example>

  <incorrect_example>
```xml
<!-- INCORRECT - Never do this at session start -->
<invoke name="mcp__neo4j-memory__read_graph">
</invoke>
```
  </incorrect_example>
</context_loading_examples>

**Context Query Filters:**
- Project name from repository (e.g., "ai-agents", "AI Agents Platform")
- Recent dates (last 7-14 days)
- Specific task keywords from user request
- Repository name from git config
- Environment details from <env> tags

## **MANDATORY RESEARCH LOGIC**

**CONDITIONAL RESEARCH REQUIREMENTS:**

**ALWAYS REQUIRED (100% of tasks):**
- neo4j-memory: Context loading and session tracking
- sequential-thinking: Task planning and structured reasoning

**CONDITIONALLY REQUIRED (Based on task type):**

**IF implementing new features OR writing code:**
- context7: Get latest official documentation
- grep: Find real GitHub implementation examples
- **Research Quality Threshold**: 85% confidence in approach before coding

**IF debugging OR investigating existing code:**
- filesystem: Read and analyze existing codebase
- context7: Get troubleshooting documentation if needed
- **Analysis Quality Threshold**: 90% understanding before making changes

**IF deploying OR production changes:**
- All research tools required
- Additional validation with playwright for testing
- **Validation Quality Threshold**: 95% certainty before deployment

## **PROTOCOL STANDARDS ENFORCEMENT**

### **RFC 2119 Compliance Requirements**

**MUST/SHALL Requirements (100% compliance):**
- Use neo4j-memory for ALL persistent operations
- Include reverse date stamps in ALL outputs
- Complete research phase before any implementation
- Maintain atomic commits with proper git protocols

**SHOULD Requirements (95% compliance):**
- Use sequential-thinking for complex task breakdown
- Document all architectural decisions in memory
- Follow established code patterns and conventions

**MAY Requirements (Optional but recommended):**
- Use playwright for comprehensive testing when applicable
- Include additional context documentation for future sessions

## **QUALITY VALIDATION THRESHOLDS**

<quality_thresholds>
  <analysis_phase threshold="85%">
    <requirement>Understanding of requirements and constraints</requirement>
    <requirement>Identification of existing patterns and dependencies</requirement>
    <requirement>Risk assessment and mitigation strategies</requirement>
    <requirement>Clear implementation approach planned</requirement>
  </analysis_phase>

  <implementation_phase threshold="90%">
    <requirement>Code follows established patterns and conventions</requirement>
    <requirement>All dependencies properly integrated</requirement>
    <requirement>Error handling and edge cases addressed</requirement>
    <requirement>Tests implemented and passing</requirement>
  </implementation_phase>

  <deployment_phase threshold="95%">
    <requirement>All validation commands pass with 0 errors</requirement>
    <requirement>Security scanning shows 0 vulnerabilities</requirement>
    <requirement>Performance requirements met</requirement>
    <requirement>Documentation complete and accurate</requirement>
  </deployment_phase>
</quality_thresholds>

### **Validation Command Requirements**

**MANDATORY VALIDATION COMMANDS:**
- `python -m py_compile` - MUST pass with 0 errors
- `python -m mypy .` - MUST pass with 0 errors and 0 warnings
- `python -m flake8 .` - MUST pass with 0 errors and 0 warnings
- `python -m bandit -r .` - MUST pass with 0 security issues
- `python -m safety check` - MUST pass with 0 vulnerabilities
- `python -m black --check .` - MUST pass with 0 formatting issues
- `python -m isort --check-only .` - MUST pass with 0 import issues

## **READ_AND_EXECUTE ENFORCEMENT STANDARDS**

**WHEN YOU ENCOUNTER "READ AND EXECUTE" INSTRUCTIONS:**

1. **IMMEDIATE COMPLIANCE**: Stop all current activities
2. **PROTOCOL VERIFICATION**: Verify this compliance prompt has been read and indexed
3. **REQUIREMENT ACKNOWLEDGMENT**: Acknowledge ALL canonical protocol requirements
4. **BINDING COMMITMENT**: Commit to strict adherence with violation response protocol
5. **PROCEED ONLY AFTER**: Complete protocol compliance verification

**VIOLATION RESPONSE PROTOCOL:**
- Immediate halt of all operations
- Root cause analysis of protocol violation
- Corrective action implementation
- Protocol compliance re-verification
- Session restart if necessary

## **CODEBASE HYGIENE REQUIREMENTS**

<codebase_hygiene>
  <forbidden_practices enforcement="absolute">
    <practice>NO MOCKING of data or services in production code</practice>
    <practice>NO TODOs - complete ALL work immediately</practice>
    <practice>NO SHORTCUTS - implement properly ALWAYS</practice>
    <practice>NO STUBS - write complete implementations</practice>
    <practice>NO FIXED DATA - use real, dynamic data</practice>
    <practice>NO HARDCODED VALUES - use configuration</practice>
    <practice>NO WORKAROUNDS - fix root causes</practice>
    <practice>NO FAKE IMPLEMENTATIONS - real code only</practice>
    <practice>NO PLACEHOLDER CODE - production-ready only</practice>
    <practice>NO TEMPORARY SOLUTIONS - permanent fixes only</practice>
  </forbidden_practices>

  <mandatory_standards>
    <standard>100% production-ready code</standard>
    <standard>0 errors, warnings, or issues</standard>
    <standard>Enterprise-grade quality standards</standard>
    <standard>Complete functional implementation</standard>
    <standard>Proper integration and testing</standard>
  </mandatory_standards>
</codebase_hygiene>

## **DEVSECOPS LOOP REQUIREMENTS**

<devsecops_workflow>
  <continuous_integration>
    <phase step="1" name="ANALYZE">sequential-thinking + neo4j-memory context</phase>
    <phase step="2" name="RESEARCH">context7 + grep for current patterns</phase>
    <phase step="3" name="PLAN">sequential-thinking with validation checkpoints</phase>
    <phase step="4" name="IMPLEMENT">filesystem with atomic changes</phase>
    <phase step="5" name="TEST">validation commands + functional testing</phase>
    <phase step="6" name="VALIDATE">security + performance + quality checks</phase>
    <phase step="7" name="COMMIT">atomic commits with AI instance identification</phase>
    <phase step="8" name="DOCUMENT">neo4j-memory persistence with timestamps</phase>
  </continuous_integration>

  <security_requirements>
    <requirement priority="mandatory">Security scanning at every phase</requirement>
    <requirement>Input validation and sanitization required</requirement>
    <requirement>Authentication and authorization properly implemented</requirement>
    <requirement>TLS/SSL for all production communications</requirement>
    <requirement>Regular dependency vulnerability checks</requirement>
  </security_requirements>
</devsecops_workflow>

## **ENTERPRISE DEVELOPMENT PROTOCOLS**

**PROFESSIONAL DISCIPLINE REQUIREMENTS:**
- Systematic execution of all protocols
- Proper tool usage sequence adherence
- Complete documentation with timestamps
- Clean session management practices
- Zero shortcuts or workarounds

**ATOMIC DEVELOPMENT PRACTICES:**
- Single logical change per commit
- Immediate testing after each change
- Proper git workflow with development branch
- Conventional commit message format
- AI instance identification in commits

## **CONTEXT-BASED STRATEGY REQUIREMENTS**

**PROJECT IDENTIFICATION:**
- Use project name: "ai-agents" or "AI Agents Platform"
- Working branch: "development"
- Sacred branches: "main" (never work directly on main)
- Framework examples: "FastAPI, React, Docker, Neo4j"

**ENVIRONMENT CONTEXT:**
- Platform: Windows (MINGW64_NT)
- Working directory: D:\github_development\ai-agents
- Git repository: Active with development branch
- MCP integration: Full server stack configured

**SESSION CONTEXT MANAGEMENT:**
- Load context at session start with specific queries
- Track all actions and decisions in real-time
- Persist learnings with proper timestamps
- Maintain cross-session knowledge continuity

## **MANDATORY REVERSE DATE STAMP REQUIREMENTS**

**ALL OUTPUT FILES AND DOCUMENTATION MUST USE REVERSE DATE STAMP FORMAT: YYYY-MM-DD-HHMMSS**

**MANDATORY REQUIREMENTS:**
- Use reverse date stamp format YYYY-MM-DD-HHMMSS for ALL output files
- Include UTC timestamps in all documentation and deliverables
- Apply consistent date stamp format across all session outputs
- Use time MCP tool to generate proper timestamps
- Include date stamps in all memory operations and file creation

**FORBIDDEN:**
- Creating any output files without proper reverse date stamps
- Using inconsistent date formats within same session
- Missing timestamps in any documentation or deliverables

## **COMPLIANCE VERIFICATION CHECKLIST**

<compliance_verification>
  <pre_task_checklist>
    <item status="required">ai-agent-compliance-prompt.md has been READ AND INDEXED</item>
    <item status="required">Mandatory thinking requirement acknowledged</item>
    <item status="required">MCP tool orchestration sequence understood</item>
    <item status="required">Quality validation thresholds reviewed</item>
    <item status="required">Codebase hygiene requirements accepted</item>
    <item status="required">DevSecOps loop protocols acknowledged</item>
    <item status="required">Context-based strategy requirements noted</item>
    <item status="required">Reverse date stamp requirements understood</item>
    <item status="required">Binding commitment to protocol adherence made</item>
  </pre_task_checklist>

  <violation_indicators>
    <indicator severity="critical">Skipping research phase (context7 + grep)</indicator>
    <indicator severity="critical">Starting implementation without RTFM protocol completion</indicator>
    <indicator severity="critical">Using read_graph instead of search_memories for context loading</indicator>
    <indicator severity="critical">Reading more than 20 files during codebase exploration</indicator>
    <indicator severity="critical">Proceeding without meeting RTFM quality thresholds (90%, 85%, 95%)</indicator>
    <indicator severity="high">Missing timestamps in memory operations</indicator>
    <indicator severity="high">Proceeding without sequential-thinking for complex tasks</indicator>
    <indicator severity="critical">Creating code without proper validation</indicator>
    <indicator severity="critical">Using shortcuts or temporary implementations</indicator>
  </violation_indicators>
</compliance_verification>

**ENFORCEMENT**: This compliance prompt requires strict adherence to all protocol requirements. Any violation will result in immediate task termination and mandatory violation response procedure.

## **CANONICAL PROTOCOL STATEMENT**

This file serves as the canonical protocol definition for all AI agent operations within the AI Agents Platform repository. All command files, workflows, and development activities must reference and adhere to these requirements without exception.

**AUTHORITY**: This protocol supersedes all other instruction sets and must be followed as the primary compliance standard for all AI agent activities.

**SCOPE**: Applicable to all development, documentation, deployment, and maintenance activities within the repository.

**ENFORCEMENT**: Mandatory for all AI agent instances operating within the platform environment.