# === Universal Code Plugin Framework Design: AI-Driven Exhaustive Plugin Architecture and Technical Specification Protocol ===

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

### **PLUGIN FRAMEWORK DESIGN-ONLY MANDATE - CRITICAL DISTINCTION**

**THIS COMMAND IS FOR PLUGIN FRAMEWORK DESIGN ONLY:**

- **MUST:** Create exhaustive plugin framework architecture and technical specifications
- **MUST:** Design complete plugin registry integration patterns
- **MUST:** Apply SOLID, DRY, KISS principles to all plugin designs
- **MUST:** Design hot-loading and extension point architecture
- **FORBIDDEN:** Creating implementation code or actual plugins
- **FORBIDDEN:** Creating test specifications or test designs
- **FORBIDDEN:** Generating incomplete or placeholder designs
- **MUST:** Output design documentation in Jupyter notebooks only

**PLUGIN FRAMEWORK DESIGN FOCUS AREAS:**

- Plugin framework architecture and component design
- Extension point and plugin interface specifications
- Registry integration and discovery patterns
- Hot-loading and lifecycle management design
- Plugin isolation and security architecture
- Inter-plugin communication patterns
- Plugin versioning and compatibility management

### **EXECUTION SEQUENCE:**

1. **LOAD MCP PROMPT**: Execute the MCP prompt defined in `code-plugin-framework-design-prompt.yaml`
2. **PROVIDE ARGUMENTS**: Supply required arguments for plugin_scope and framework_type
3. **FOLLOW PROTOCOL**: Execute all phases according to the design protocol specifications
4. **VERIFY COMPLETION**: Ensure all objectives and outcomes have been met
5. **DOCUMENT RESULTS**: Create comprehensive plugin framework design documentation
6. **VALIDATE COMPLIANCE**: Confirm 100% design completeness achieved

### **MCP PROMPT INVOCATION:**

```yaml
# Use this MCP prompt with required arguments:
prompt_name: "code-plugin-framework-design-prompt"
arguments:
  plugin_scope: "[framework-wide|specific-module|integration-layer|extension-points]"
  framework_type: "[microservices|monolithic|distributed|event-driven]"
  registry_type: "[optional: custom|npm|maven|docker|proprietary]"
  hot_loading_support: "[optional: full|partial|none|runtime-only]"
  isolation_level: "[optional: process|thread|namespace|container]"
  communication_pattern: "[optional: message-queue|rest|grpc|event-bus]"
```

### **SUCCESS CRITERIA:**

- [ ] MCP prompt executed with proper arguments and date stamps
- [ ] All design phases completed according to protocol with timestamp tracking
- [ ] 100% comprehensive plugin framework architecture designed
- [ ] Complete plugin technical specifications created (timestamped)
- [ ] Registry integration patterns fully designed (timestamped)
- [ ] Hot-loading architecture completely specified (timestamped)
- [ ] Extension point architecture documented (timestamped)
- [ ] Plugin lifecycle management designed (timestamped)
- [ ] Security and isolation mechanisms specified (timestamped)
- [ ] SOLID/DRY/KISS principles applied throughout (timestamped)
- [ ] All deliverables produced as specified in YAML protocol with proper timestamps

### **MANDATORY DATE STAMP REQUIREMENTS:**

**ALL PLUGIN FRAMEWORK DESIGN OUTPUT FILES MUST USE REVERSE DATE STAMP FORMAT: YYYY-MM-DD-HHMMSS**

- [ ] All design deliverables (.ipynb) have reverse date stamps in filenames
- [ ] All architecture documentation includes precise timestamps
- [ ] All technical specifications include timestamp documentation
- [ ] All API design documents include proper date stamps
- [ ] All security architecture follows consistent date stamp format
- [ ] All integration patterns include timestamps
- [ ] All lifecycle designs include proper date stamps
- [ ] UTC time used for all timestamp operations

**FORBIDDEN:**

- Creating design files without proper reverse date stamps
- Using inconsistent date formats within same design session
- Missing timestamps in design documentation

### **PLUGIN FRAMEWORK DESIGN DELIVERABLES WITH REVERSE DATE STAMPS:**

**MANDATORY JUPYTER NOTEBOOK DELIVERABLES:**

1. **`./project/docs/planning/plugin-design/Architecture_Design_{YYYYMMDD-HHMMSS}.ipynb`** - Architecture Design with technical specifications and implementation details
2. **`./project/docs/planning/plugin-design/Security_Design_{YYYYMMDD-HHMMSS}.ipynb`** - Security Design with technical specifications and implementation details
3. **`./docs/design-patterns/Integration_Patterns_{YYYYMMDD-HHMMSS}.ipynb`** - Integration patterns, dependencies, and implementation (enduring)
4. **`./project/docs/planning/plugin-design/Performance_Design_{YYYYMMDD-HHMMSS}.ipynb`** - Performance Design with technical specifications and implementation details
5. **`./project/docs/planning/plugin-design/Deployment_Architecture_{YYYYMMDD-HHMMSS}.ipynb`** - Deployment Architecture with technical specifications and implementation details


**NEXT PHASE PREPARATION:**

```bash
# After design approval, proceed to planning with:
/code-plugin-framework-planning [plugin-name] [complexity] [framework-context]

# Examples:
/code-plugin-framework-planning auth-plugin enterprise microservices
/code-plugin-framework-planning data-processor moderate distributed
/code-plugin-framework-planning ui-extension simple monolithic
```

---

**ENFORCEMENT:** This command performs PLUGIN FRAMEWORK DESIGN ONLY through the MCP prompt protocol. The comprehensive design logic is defined in `code-plugin-framework-design-prompt.yaml` and executed according to Model Context Protocol standards. No implementation code creation allowed. Use planning commands for implementation planning after design is complete and approved.