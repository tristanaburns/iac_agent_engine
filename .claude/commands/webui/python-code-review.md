# === Python Code Review: Comprehensive Python Code Review Protocol ===

**ALWAYS THINK THEN...** Before executing any action, operation, or command in this instruction set, you MUST use thinking to:
1. Analyze the request and understand what needs to be done
2. Plan your approach and identify potential issues
3. Consider the implications and requirements
4. Only then proceed with the actual execution

**This thinking requirement is MANDATORY and must be followed for every action.**

## CANONICAL PROTOCOL ENFORCEMENT - READ FIRST

**THIS SECTION IS MANDATORY AND MUST BE READ, INDEXED, AND FOLLOWED BEFORE ANY COMMAND EXECUTION**

**BEFORE PROCEEDING, YOU MUST:**
1. **READ AND INDEX**: Complete ai-agent-compliance.md protocol requirements
2. **VERIFY**: User has given explicit permission to proceed
3. **ACKNOWLEDGE**: ALL CANONICAL PROTOCOL requirements

**BINDING COMMITMENT**: I hereby commit to strict, unwavering adherence to ALL ai-agent-compliance.md requirements and will halt operations immediately upon any protocol violation to perform mandatory root cause analysis and corrective action.

**FORBIDDEN**: Proceeding without complete protocol compliance verification

## FORBIDDEN PRACTICES

**FORBIDDEN**
YOU ARE FORBIDDEN from creating custom scripts to fix or remediate the code base, YOU HAVE CONTINUIOUSLY corrupted the code base through poor "fix" scripts
YOU MUST NEVER EVER EVER create custom scripts to fix or remediate the code base

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

## RTFM (READ THE FUCKING MANUAL) - MANDATORY

**YOU MUST ALWAYS:**

1. **READ JUPYTER NOTEBOOKS:**
   - Search for .ipynb files in the repository
   - Read implementation notebooks for context
   - Review analysis notebooks for insights
   - Study documentation notebooks for patterns

2. **READ PROJECT DOCUMENTATION:**
   - Check `./docs` directory thoroughly
   - Check `./project/docs` if it exists
   - Read ALL README files
   - Review architecture documentation
   - Study API documentation

3. **SEARCH ONLINE FOR BEST PRACTICES:**
   - Use web search for latest documentation
   - Find official framework/library docs
   - Search GitHub for example implementations
   - Review industry best practices
   - Study similar successful projects
   - Check Stack Overflow for common patterns

**SEARCH PRIORITIES:**
- Official documentation (latest version)
- GitHub repositories with high stars
- Industry standard implementations
- Recent blog posts/tutorials (< 1 year old)
- Community best practices

## MCP TOOLS REQUIREMENTS

**MANDATORY PROTOCOL REFERENCE**: You MUST use designated MCP tools for all operations:

### Core MCP Tools (MANDATORY)

**Core Memory & Thinking:**
- `neo4j-memory` - Enduring LLM Memory Knowledge Graph - MANDATORY
- `memory` - Temporal LLM Memory Knowledge Graph - MANDATORY 
- `sequential-thinking` - Structured reasoning and planning - MANDATORY

**Documentation & Code Research (MANDATORY BEFORE ANALYSIS):**
- `context7` - Up-to-date documentation from official sources - MANDATORY
- `grep` - GitHub code examples and implementations - MANDATORY

**File & Web Operations:**
- `filesystem` - File read/write operations - MANDATORY
- `fetch` - HTTP/HTTPS content retrieval - MANDATORY
- `time` - Timestamp and time operations - MANDATORY for reverse date stamp generation

### MCP EXECUTION SEQUENCE (REQUIRED)

```

  START ANALYSIS                                             
                                                            
  1. CONTEXT LOAD (neo4j-memory + memory)                   
                                                            
  2.  MANDATORY RESEARCH (context7 + grep)                
                                                            
  3. PLANNING (sequential-thinking)                          
                                                            
  4. ANALYSIS (filesystem + domain tools)                   
                                                            
  5. PROGRESS TRACKING (neo4j-memory + memory)              
                                                            
  6. CONTEXT SAVE (neo4j-memory + memory)                   
                                                            
  END ANALYSIS                                               

```

** CRITICAL: NEVER SKIP THE RESEARCH PHASE - IT PREVENTS AI HALLUCINATIONS**

### MCP MEMORY REQUIREMENTS

**ABSOLUTELY MANDATORY - ZERO EXCEPTIONS ALLOWED**

YOU MUST ALWAYS use **Neo4j Memory** (`neo4j-memory`) and **Memory** (`memory`) for ALL memory operations:

- **Enduring Memory**: `neo4j-memory` - MANDATORY for persistent knowledge storage with reverse date stamps
- **Session Memory**: `memory` - MANDATORY for temporal tracking with timestamps
- **Session Tracking**: Track all actions, outcomes, and decisions with timestamps
- **Knowledge Persistence**: Save all learnings and patterns with date stamps
- **Context Loading**: Load previous session context before starting (with date filtering)
- **Cross-Session Memory**: Maintain knowledge across all sessions with timestamp tracking

**MANDATORY DATE STAMP REQUIREMENTS:**
- "MANDATORY: All memory operations MUST include reverse date stamp YYYY-MM-DD-HHMMSS"
- "MANDATORY: Use UTC timestamps for all memory entries and operations"
- "MANDATORY: Include date stamps in all entity creation and relationship mapping"
- "FORBIDDEN: Memory operations without proper timestamp documentation"

**FAILURE TO USE MCP MEMORY WILL RESULT IN IMMEDIATE TASK TERMINATION**

---

## INSTRUCTIONS

model_context:
  role: "Python code review specialist for comprehensive code quality assessment"
  domain: "Python Development, Code Quality, Best Practices, PEP Standards"
  goal: >
    Perform a comprehensive Python code review focusing on Pythonic patterns, PEP compliance,
    type safety, performance optimization, and security best practices. Generate an interactive
    analysis report using Jupyter Notebook format. All findings must adhere to Python community
    standards, PEP guidelines, and modern Python development best practices.

configuration:
  # Python-specific review parameters
  python_version: ""      # Target Python version (3.8, 3.9, 3.10, 3.11, 3.12)
  project_type: ""        # Auto-detected: Package, Application, API, CLI, Library, Framework
  framework_stack: []     # Auto-detected: FastAPI, Django, Flask, Pyramid, aiohttp, etc.
  package_manager: ""     # Auto-detected: pip, poetry, pipenv, conda, pdm
  type_checking: ""       # Auto-detected: mypy, pyright, pyre, none
  test_framework: ""      # Auto-detected: pytest, unittest, nose2, doctest

instructions:
  - Analyze all source files and application logic down to individual function/method/class level
  - Identify and document:
      - Violations of canonical coding principles (SOLID, DRY, KISS, YAGNI)
      - Python-specific best practice violations:
          - PEP 8 style violations (naming, spacing, line length)
          - PEP 484 type hint issues and missing annotations
          - PEP 257 docstring convention violations
          - Unpythonic patterns (not using context managers, comprehensions, generators)
          - Mutable default arguments and late binding issues
          - Global state modifications and side effects
          - Improper exception handling (bare except, broad exceptions)
          - Resource management without context managers
          - Thread safety issues in concurrent code
          - Security vulnerabilities (injection, path traversal, unsafe pickle)
      - Architectural issues:
          - Circular dependencies
          - Tight coupling between modules
          - Missing abstraction layers
          - Inconsistent patterns across codebase
      - Code quality issues:
          - Complex functions (high cyclomatic complexity)
          - Code duplication across files
          - Dead code and unused imports
          - Missing or inadequate documentation
      - Testing gaps:
          - Untested functions/methods
          - Missing edge case coverage
          - Inadequate integration tests
      - Interface contracts between all code blocks, functions, modules, and services
  - Perform comprehensive analysis:
      - Function/method-level dependency mapping and call graph analysis
      - Module/package-level dependency mapping
      - Data flow analysis with object/type transformations
      - Control flow analysis with branching complexity
      - Cross-cutting concerns identification (logging, auth, validation)
      - Performance bottleneck identification
      - Security vulnerability scanning
      - API contract validation (FastAPI, Django REST, Flask-RESTful)
      - Async/await pattern correctness and efficiency
      - Decorator usage and custom decorator patterns
  - Deliver:
      - Complete MERMAID diagram set with appropriate granularity:
          - Package/Module dependency graph
          - Class/Interface hierarchy diagrams
          - Sequence diagrams for critical workflows
          - Data flow diagrams
          - Component interaction diagrams
      - File-level and function-level breakdowns with interface contracts
      - Refactoring roadmap with prioritized recommendations
      - Python-specific best practices compliance matrix (PEP 8, PEP 484, PEP 257)
      - Pythonic patterns usage assessment
      - Security and performance improvement plan
  - Format final output in structured `.ipynb` notebook format using markdown + executable code cells

input_requirements:
  expected_inputs:
    - Python source files (.py)
    - Configuration files (pyproject.toml, setup.py, setup.cfg, .env)
    - Dependency files (requirements.txt, Pipfile, poetry.lock, environment.yml)
    - Test files (test_*.py, *_test.py) and coverage reports (.coverage)
    - Documentation files (README.md, docs/, docstrings)
  optional_context:
    - Target deployment environment
    - Performance requirements or SLAs
    - Security compliance requirements
    - Team coding standards or style guides
    - Known issues or technical debt backlog

analysis_templates:
  # Python-specific analysis patterns
  python_code_review:
    style_checks:
      - PEP 8 compliance (line length, naming, spacing)
      - Import organization (standard, third-party, local)
      - Code formatting consistency (black, autopep8)
    type_safety:
      - Type hint coverage percentage
      - Mypy strict mode compliance
      - Generic type usage correctness
      - Protocol and TypedDict patterns
    documentation:
      - Docstring completeness (modules, classes, functions)
      - PEP 257 docstring conventions
      - Type annotations in docstrings vs inline
      - README and inline comment quality
    patterns:
      - Context manager usage (with statements)
      - Generator and iterator patterns
      - Comprehensions vs loops
      - Decorator patterns and usage
      - Property decorators and descriptors
    async_patterns:
      - Async/await correctness
      - Asyncio best practices
      - Concurrent.futures usage
      - Thread safety and GIL considerations
    testing:
      - Test coverage percentage
      - Pytest vs unittest patterns
      - Mock and patch usage
      - Fixture design and usage
      - Test organization and naming

constraints:
  - All outputs MUST be compiled into Jupyter Notebook format and include:
      - Markdown cells for detailed explanations
      - Fenced code blocks with syntax highlighting
      - Mermaid/PlantUML diagrams showing appropriate detail level
      - Interactive visualizations where applicable
  - All architectural insights MUST include detailed technical diagrams with:
      - Function/method-level call graphs where complexity warrants
      - Type/interface contracts between components
      - Data transformation pipelines
      - Service/module boundaries with API specifications
  - Every significant code unit must be reviewed for:
      - Single Responsibility Principle
      - Interface segregation and consistency
      - Dependency injection patterns
      - Code duplication (DRY violations)
      - Premature optimization (KISS violations)
      - Over-engineering (YAGNI violations)
  - Interface documentation must include:
      - Input contracts (types, validation, constraints)
      - Output contracts (types, formats, guarantees)
      - Error contracts (exceptions, error codes, failure modes)
      - Side effects and state mutations
      - Performance characteristics (time/space complexity)
  - Do NOT implement fixes; provide actionable recommendations with examples

output_format:
  jupyter_structure:
    - Section 1: Executive Summary
    - Section 2: Python Codebase Overview and Metrics
    - Section 3: Module Architecture and Import Analysis
    - Section 4: Code Quality Issues Matrix
    - Section 5: PEP Compliance and Pythonic Patterns
    - Section 6: Type Safety and Annotation Coverage
    - Section 7: Testing and Coverage Analysis
    - Section 8: Performance and Optimization Opportunities
    - Section 6: Language-Specific Best Practices Analysis
    - Section 7: Interface Contract Documentation
    - Section 8: Dependency and Call Graph Analysis
    - Section 9: Security Vulnerability Assessment
    - Section 10: Performance Analysis
    - Section 11: Testing Coverage and Quality
    - Section 12: Technical Debt Inventory
    - Section 13: Refactoring Roadmap
    - Section 14: Code Examples and Anti-patterns
    - Section 15: Recommendations and Next Steps
  diagram_format: "Mermaid/PlantUML syntax blocks with appropriate detail level"
  code_snippet_format: "Language-specific fenced code blocks with syntax highlighting"
  interface_documentation_format: |
    For each significant interface:
    ```
    Interface: <ComponentName.FunctionName>
    Language: <Language>
    Inputs: 
      - [Type] parameterName: description (constraints)
    Outputs: 
      - [Type]: description (guarantees)
    Errors: 
      - [ErrorType]: condition and handling
    Side Effects: 
      - Description of state changes or external interactions
    Dependencies: 
      - Internal: [Component.Function]
      - External: [Library/Service]
    Performance: 
      - Time: O(n)
      - Space: O(1)
    ```

validation_criteria:
  clarity: "10 - All constructs clearly documented, no ambiguous patterns"
  completeness: "10 - All code paths, edge cases, and interactions analyzed"
  technical_precision: "10 - Language idioms, patterns, and best practices validated"
  security_coverage: "10 - Input validation, auth, data handling, dependency vulnerabilities"
  performance_analysis: "10 - Algorithmic complexity, resource usage, bottlenecks identified"
  maintainability: "10 - Code clarity, modularity, testability assessed"
  scalability: "10 - Architecture supports growth, handles concurrent load"

final_deliverables:
  # MANDATORY: ALL files MUST use reverse date stamp format YYYY-MM-DD-HHMMSS
  - Code_Review_Analysis-{{YYYY-MM-DD-HHMMSS}}.ipynb (comprehensive review with appropriate detail level)
  - Architecture_Diagrams-{{YYYY-MM-DD-HHMMSS}}.md (complete diagram set)
  - Interface_Contracts-{{YYYY-MM-DD-HHMMSS}}.md (all significant interfaces documented)
  - Best_Practices_Report-{{YYYY-MM-DD-HHMMSS}}.md (language-specific findings)
  - Security_Assessment-{{YYYY-MM-DD-HHMMSS}}.md (vulnerabilities and recommendations)
  - Performance_Report-{{YYYY-MM-DD-HHMMSS}}.md (bottlenecks and optimizations)
  - Refactoring_Roadmap-{{YYYY-MM-DD-HHMMSS}}.md (prioritized improvement plan)
  - Executive_Summary-{{YYYY-MM-DD-HHMMSS}}.pdf (high-level findings for stakeholders)
  
  date_stamp_requirements:
    - "MANDATORY: Use current UTC timestamp for all analysis output files"
    - "MANDATORY: Format as YYYY-MM-DD-HHMMSS (reverse chronological order)"
    - "MANDATORY: Include date stamp in ALL code review deliverable filenames"
    - "MANDATORY: Use consistent date stamp across all analysis outputs"
    - "FORBIDDEN: Creating analysis files without proper date stamps"
    - "FORBIDDEN: Using different date formats within same analysis session"

# Dynamic Analysis Configuration
analysis_depth:
  # Automatically adjusted based on codebase size
  small_codebase: # < 10K LOC
    function_analysis: "all"
    diagram_detail: "high"
    example_coverage: "comprehensive"
  medium_codebase: # 10K - 100K LOC
    function_analysis: "critical_paths"
    diagram_detail: "module_level"
    example_coverage: "representative"
  large_codebase: # > 100K LOC
    function_analysis: "high_complexity_only"
    diagram_detail: "service_level"
    example_coverage: "key_patterns"

# Execution Instructions
execution_notes: |
  1. MANDATORY: Load context from neo4j-memory and memory before starting
  2. MANDATORY: Research using context7 and grep for latest analysis patterns
  3. First scan the codebase to detect languages, frameworks, and project structure
  4. Adjust analysis depth based on codebase size and complexity
  5. Focus on critical paths and high-risk areas
  6. Provide actionable recommendations with priority levels
  7. Include code examples for all identified anti-patterns
  8. Generate diagrams at appropriate abstraction level
  9. Ensure all findings are traceable to specific code locations
  10. MANDATORY: Save all findings and decisions to neo4j-memory and memory
  11. MANDATORY: Use reverse date stamps for all output files

## MCP PROTOCOL COMPLIANCE REQUIREMENTS

**MANDATORY REQUIREMENTS FOR ALL CODE REVIEW OPERATIONS:**

1. ** ALWAYS use context7 BEFORE analyzing code** - Get current, accurate documentation
2. ** ALWAYS use grep to search GitHub** - Find real production examples of review patterns
3. ** ALWAYS record actions in neo4j-memory and memory AS YOU WORK** - Document everything
4. ** ALWAYS save to neo4j-memory and memory** - Preserve for future sessions
5. **NEVER skip the Context Load phase** - Always start by loading relevant context
6. **NEVER analyze without Research phase** - context7 + grep are MANDATORY
7. **NEVER complete without Context Save** - Always persist learnings and decisions

**THE GOLDEN RULE: context7 (docs)  grep (examples)  memory (record)  analysis  memory (persist)**

## MANDATORY REVERSE DATE STAMP REQUIREMENTS

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