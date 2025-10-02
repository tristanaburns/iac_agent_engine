# === Plugin Architecture Quality Analysis: Comprehensive Plugin System Assessment Protocol ===

**ALWAYS THINK THEN...** Before executing any action, operation, or command in this instruction set, you MUST use thinking to:

1. Analyze the request and understand what needs to be done
2. Plan your approach and identify potential issues
3. Consider the implications and requirements
4. Only then proceed with the actual execution

**This thinking requirement is MANDATORY and must be followed for every action.**

## CANONICAL PROTOCOL ENFORCEMENT - READ FIRST

**THIS SECTION IS MANDATORY AND MUST BE READ, INDEXED, AND FOLLOWED BEFORE ANY COMMAND EXECUTION**

**BEFORE PROCEEDING, YOU MUST ALWAYS:**

1. **READ AND EXECUTE**: `.claude/commands/ai-agent-compliance-prompt.md`
2. **VERIFY**: User has given explicit permission to proceed
3. **ACKNOWLEDGE**: ALL CANONICAL PROTOCOL requirements

**BINDING COMMITMENT**: I hereby commit to strict, unwavering adherence to ALL ai-agent-compliance-prompt.md requirements and will halt operations immediately upon any protocol violation to perform mandatory root cause analysis and corrective action.

**FORBIDDEN**: Proceeding without complete protocol compliance verification

## FORBIDDEN PRACTICES

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

---

## **MCP PROMPT EXECUTION INSTRUCTIONS**

**MANDATORY PROTOCOL COMPLIANCE**: This is an MCP-compliant prompt that must be executed according to Model Context Protocol standards.

### **PLUGIN QUALITY ANALYSIS-ONLY MANDATE - CRITICAL DISTINCTION**

**THIS COMMAND IS FOR PLUGIN ARCHITECTURE QUALITY ANALYSIS ONLY:**

- **MUST:** Perform comprehensive plugin system quality assessment
- **MUST:** Analyze plugin architecture principles and patterns
- **MUST:** Evaluate plugin security and isolation mechanisms
- **MUST:** Assess plugin lifecycle and hot-loading capabilities
- **FORBIDDEN:** Implementing fixes during analysis
- **FORBIDDEN:** Creating test code
- **MUST:** Generate comprehensive quality metrics and reports

**PLUGIN QUALITY ANALYSIS FOCUS AREAS:**

- Plugin component inventory and dependency mapping
- Plugin interface segregation and contract analysis
- Plugin design pattern usage and anti-pattern detection
- Plugin security boundary and isolation assessment
- Plugin performance and scalability metrics
- Plugin maintainability and extensibility evaluation
- Plugin registry and discovery mechanism quality

### **EXECUTION SEQUENCE:**

1. **LOAD MCP PROMPT**: Execute the MCP prompt defined in `code-plugin-quality-analysis-prompt.yaml`
2. **PROVIDE ARGUMENTS**: Supply optional arguments for analysis scope and depth
3. **FOLLOW PROTOCOL**: Execute all phases according to the quality analysis protocol specifications
4. **VERIFY COMPLETION**: Ensure all quality metrics have been collected
5. **DOCUMENT RESULTS**: Create comprehensive quality assessment documentation
6. **VALIDATE COMPLIANCE**: Confirm 100% analysis coverage achieved

### **MCP PROMPT INVOCATION:**

```yaml
# Use this MCP prompt with optional arguments:
prompt_name: "code-plugin-quality-analysis-prompt"
arguments:
  analysis_scope: "[optional: entire-codebase|specific-plugins|core-framework]"
  quality_focus: "[optional: architecture|security|performance|maintainability|all]"
  metrics_depth: "[optional: basic|comprehensive|exhaustive]"
  pattern_analysis: "[optional: enabled|disabled]"
  anti_pattern_detection: "[optional: strict|moderate|lenient]"
```

### **SUCCESS CRITERIA:**

- [ ] MCP prompt executed with proper arguments and date stamps
- [ ] All phases completed according to protocol with timestamp tracking
- [ ] Complete plugin component inventory documented (timestamped)
- [ ] Plugin architecture principles analyzed (timestamped)
- [ ] Design patterns and anti-patterns identified (timestamped)
- [ ] Security and isolation mechanisms assessed (timestamped)
- [ ] Performance metrics collected (timestamped)
- [ ] Maintainability scores calculated (timestamped)
- [ ] Quality recommendations generated (timestamped)
- [ ] All deliverables produced as specified in YAML protocol with proper timestamps

### **MANDATORY DATE STAMP REQUIREMENTS:**

**ALL PLUGIN QUALITY ANALYSIS OUTPUT FILES MUST USE REVERSE DATE STAMP FORMAT: YYYY-MM-DD-HHMMSS**

- [ ] All quality reports (.ipynb) have reverse date stamps in filenames
- [ ] All metric collections include precise timestamps
- [ ] All pattern analysis documentation includes timestamp documentation
- [ ] All security assessments include proper date stamps
- [ ] All performance analyses follow consistent date stamp format
- [ ] All recommendation reports include timestamps
- [ ] UTC time used for all timestamp operations

**FORBIDDEN:**

- Creating quality analysis files without proper reverse date stamps
- Using inconsistent date formats within same analysis session
- Missing timestamps in quality documentation

### **PLUGIN QUALITY ANALYSIS DELIVERABLES WITH REVERSE DATE STAMPS:**

**MANDATORY JUPYTER NOTEBOOK DELIVERABLES:**

1. **`./project/docs/analysis/plugin/Analysis_Report_{YYYYMMDD-HHMMSS}.ipynb`** - Comprehensive analysis report and findings
2. **`./project/docs/analysis/plugin/Findings_Recommendations_{YYYYMMDD-HHMMSS}.ipynb`** - Findings Recommendations
3. **`./project/docs/analysis/plugin/Action_Plan_{YYYYMMDD-HHMMSS}.ipynb`** - Action Plan with detailed breakdown and timeline


**NEXT PHASE PREPARATION:**

```bash
# After quality analysis completion, proceed to improvements with:
/code-plugin-refactor [target-area] [quality-focus]

# Examples:
/code-plugin-refactor ./src/plugins architecture
/code-plugin-refactor ./lib/extensions security
/code-plugin-refactor ./modules/registry performance
```

---

**ENFORCEMENT:** This command performs PLUGIN QUALITY ANALYSIS ONLY through the MCP prompt protocol. The comprehensive quality analysis logic is defined in `code-plugin-quality-analysis-prompt.yaml` and executed according to Model Context Protocol standards. No implementation changes allowed. Use refactoring commands for quality improvements.