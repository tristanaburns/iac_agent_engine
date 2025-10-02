# AI Agent Compliance Protocols v2.0
## MCP Neo4j Memory Server - Complete Protocol Framework
### Generated: 2025-09-23-044431 UTC

---

## PROJECT METADATA
- **PROJECT_ID**: neo4j-memory
- **PROJECT_NAME**: MCP Neo4j Memory Server
- **WORKING_BRANCH**: development
- **SACRED_BRANCHES**: main/master
- **DB_PATH**: neo4j://localhost:7687
- **FRAMEWORK_EXAMPLES**: FastMCP, Neo4j, Python
- **PROTOCOL_VERSION**: 2.0.0
- **LAST_UPDATED**: 2025-09-23-044431

---

## PROTOCOL SECTION A: MCP TOOLS INVENTORY & SPECIFICATIONS

### A.1 MCP Server Configuration
```yaml
mcp_servers:
  neo4j_memory:
    type: "graph_database_memory"
    transport: ["stdio", "http", "sse"]
    default_transport: "stdio"
    database:
      type: "neo4j"
      default_url: "neo4j://localhost:7687"
      default_username: "neo4j"
      default_database: "neo4j"
    security:
      cors_enabled: true
      trusted_hosts_enabled: true
      dns_rebinding_protection: true
```

### A.2 Core MCP Tools Specification

#### A.2.1 Query Operations
```yaml
read_graph:
  description: "Read the entire knowledge graph"
  parameters: {}
  returns: "Complete graph structure with all nodes and relationships"
  mandatory_usage: "MUST be called before any graph modifications"

search_memories:
  description: "Search for memories based on query containing search terms"
  parameters:
    query:
      type: "string"
      required: true
      validation: "Non-empty string, minimum 2 characters"
  returns: "List of matching Memory nodes with relevance scores"

find_memories_by_name:
  description: "Find specific memories by exact name match"
  parameters:
    names:
      type: "array[string]"
      required: true
      validation: "At least one name required"
  returns: "Memory nodes matching provided names"
```

#### A.2.2 Entity Management Operations
```yaml
create_entities:
  description: "Create multiple new entities in the knowledge graph"
  parameters:
    entities:
      type: "array[Entity]"
      schema:
        name: "string (required, unique)"
        type: "string (required)"
        observations: "array[string] (required, min 1)"
  validation_rules:
    - "Names must be unique within graph"
    - "Type must be non-empty string"
    - "At least one observation required"

delete_entities:
  description: "Delete multiple entities and their associated relations"
  parameters:
    entityNames:
      type: "array[string]"
      required: true
  cascade_behavior: "Automatically removes all connected relationships"
```

#### A.2.3 Relation Management Operations
```yaml
create_relations:
  description: "Create multiple new relations between entities"
  parameters:
    relations:
      type: "array[Relation]"
      schema:
        source: "string (entity name, must exist)"
        target: "string (entity name, must exist)"
        relationType: "string (required, active voice)"
  validation_rules:
    - "Source and target entities must exist"
    - "Relation type must be in active voice"
    - "No duplicate relations allowed"

delete_relations:
  description: "Delete multiple relations from the graph"
  parameters:
    relations:
      type: "array[Relation]"
      required: true
  validation: "Exact match required for deletion"
```

#### A.2.4 Observation Management Operations
```yaml
add_observations:
  description: "Add new observations to existing entities"
  parameters:
    observations:
      type: "array[ObservationAddition]"
      schema:
        entityName: "string (must exist)"
        observations: "array[string] (min 1)"
  validation: "Entity must exist before adding observations"

delete_observations:
  description: "Delete specific observations from entities"
  parameters:
    deletions:
      type: "array[ObservationDeletion]"
      schema:
        entityName: "string"
        observations: "array[string]"
  behavior: "Exact match required for deletion"
```

### A.3 Supplementary MCP Tools

#### A.3.1 File System Operations
```yaml
mcp__filesystem:
  tools:
    - read_text_file
    - read_media_file
    - read_multiple_files
    - write_file
    - edit_file
    - create_directory
    - list_directory
    - list_directory_with_sizes
    - directory_tree
    - move_file
    - search_files
    - get_file_info
    - list_allowed_directories
```

#### A.3.2 Sequential Thinking Tool
```yaml
mcp__sequential_thinking:
  purpose: "Structured problem-solving and analysis"
  mandatory_use_cases:
    - "Complex multi-step operations"
    - "Protocol violation analysis"
    - "Root cause analysis"
    - "Compliance verification"
  parameters:
    thought: "Current thinking step"
    nextThoughtNeeded: "boolean"
    thoughtNumber: "integer"
    totalThoughts: "integer"
    isRevision: "boolean (optional)"
    revisesThought: "integer (optional)"
```

---

## PROTOCOL SECTION B: MCP TOOL WORKFLOW SPECIFICATIONS

### B.1 Standard Workflow Sequence

#### B.1.1 Initialization Workflow
```yaml
initialization_sequence:
  1_verify_connection:
    tool: "read_graph"
    purpose: "Verify Neo4j connection and graph accessibility"
    error_handling: "Retry 3 times with exponential backoff"

  2_record_session:
    tool: "create_entities"
    entity:
      name: "Session_2025-09-23-044431"
      type: "AI_Agent_Session"
      observations:
        - "Session initiated at 2025-09-23-044431"
        - "Project: neo4j-memory"
        - "Branch: development"
        - "Protocol version: 2.0.0"

  3_establish_context:
    tool: "search_memories"
    query: "PROJECT:neo4j-memory"
    purpose: "Load existing project context"
```

#### B.1.2 Operation Workflow Pattern
```yaml
standard_operation_pattern:
  pre_operation:
    - Validate prerequisites using read_graph
    - Check entity existence with find_memories_by_name
    - Record operation intent as observation

  operation_execution:
    - Execute primary operation
    - Capture operation result
    - Log execution timestamp

  post_operation:
    - Verify operation success
    - Record outcome as observation
    - Update related entities
    - Create audit trail relation
```

### B.2 Complex Operation Workflows

#### B.2.1 Entity Creation Workflow
```yaml
entity_creation_workflow:
  1_pre_validation:
    - Check name uniqueness: find_memories_by_name
    - Validate type against schema
    - Ensure observations non-empty

  2_creation:
    - Execute create_entities
    - Capture creation timestamp

  3_relationship_establishment:
    - Link to parent entities if applicable
    - Create default relations
    - Establish audit relations

  4_verification:
    - Query created entity: find_memories_by_name
    - Validate all properties
    - Confirm relationships
```

#### B.2.2 Deletion Workflow
```yaml
safe_deletion_workflow:
  1_impact_analysis:
    - Identify all relationships
    - Find dependent entities
    - Calculate cascade impact

  2_backup_creation:
    - Record deletion intent
    - Create backup observations
    - Store relationship snapshot

  3_execution:
    - Delete relations first
    - Remove entity
    - Log deletion timestamp

  4_cleanup:
    - Verify complete removal
    - Update affected entities
    - Record deletion audit
```

### B.3 Error Recovery Workflows

#### B.3.1 Connection Recovery
```yaml
connection_recovery:
  detection:
    - Monitor all Neo4j operations
    - Detect connection failures

  recovery_steps:
    1: "Wait 1 second"
    2: "Retry operation"
    3: "Wait 5 seconds"
    4: "Test with read_graph"
    5: "Escalate if still failing"

  fallback:
    - Switch to local memory cache
    - Queue operations for replay
    - Alert user of degraded state
```

---

## PROTOCOL SECTION C: COMPLIANCE RULES & MEMORY PROTOCOLS

### C.1 Mandatory Compliance Rules

#### C.1.1 Universal Rules
```yaml
universal_compliance:
  RULE_001:
    id: "NEVER_DELETE_WITHOUT_BACKUP"
    severity: "CRITICAL"
    description: "Never delete entities without creating backup observations"
    enforcement: "Automatic backup before any deletion"

  RULE_002:
    id: "ALWAYS_VERIFY_OPERATIONS"
    severity: "HIGH"
    description: "All operations must be verified post-execution"
    enforcement: "Mandatory verification step in all workflows"

  RULE_003:
    id: "TIMESTAMP_ALL_OPERATIONS"
    severity: "HIGH"
    description: "Every operation must include timestamp in format YYYY-MM-DD-HHMMSS"
    enforcement: "Automatic timestamp injection"

  RULE_004:
    id: "MAINTAIN_AUDIT_TRAIL"
    severity: "CRITICAL"
    description: "All operations must create audit trail entities"
    enforcement: "Automatic audit entity creation"
```

#### C.1.2 Memory Recording Rules
```yaml
memory_recording_rules:
  MEMORY_001:
    rule: "Record all AI agent decisions"
    implementation:
      - Create Decision entity for each choice
      - Link to context entities
      - Include reasoning as observations

  MEMORY_002:
    rule: "Track all protocol violations"
    implementation:
      - Create Violation entity immediately
      - Include full context
      - Link to remediation actions

  MEMORY_003:
    rule: "Document all user interactions"
    implementation:
      - Create Interaction entity per exchange
      - Record request and response
      - Link to affected entities
```

### C.2 Memory Protocol Specifications

#### C.2.1 Entity Naming Conventions
```yaml
naming_conventions:
  sessions:
    pattern: "Session_{YYYY-MM-DD-HHMMSS}"
    example: "Session_2025-09-23-044431"

  operations:
    pattern: "Operation_{TYPE}_{YYYY-MM-DD-HHMMSS}"
    example: "Operation_CREATE_2025-09-23-044431"

  violations:
    pattern: "Violation_{RULE}_{YYYY-MM-DD-HHMMSS}"
    example: "Violation_RULE_001_2025-09-23-044431"

  audits:
    pattern: "Audit_{ACTION}_{YYYY-MM-DD-HHMMSS}"
    example: "Audit_DELETE_2025-09-23-044431"
```

#### C.2.2 Observation Format Standards
```yaml
observation_formats:
  standard_observation:
    template: "[{TIMESTAMP}] {ACTION}: {DETAILS}"
    example: "[2025-09-23-044431] CREATED: Entity 'User_Profile' with 3 observations"

  error_observation:
    template: "[{TIMESTAMP}] ERROR: {CODE} - {MESSAGE} | Context: {CONTEXT}"
    example: "[2025-09-23-044431] ERROR: NEO4J_001 - Connection failed | Context: Initial connection"

  audit_observation:
    template: "[{TIMESTAMP}] AUDIT: {USER} performed {ACTION} on {TARGET} | Result: {RESULT}"
    example: "[2025-09-23-044431] AUDIT: AI_Agent performed DELETE on Entity_123 | Result: SUCCESS"
```

### C.3 Compliance Verification Protocols

#### C.3.1 Pre-Operation Checks
```yaml
pre_operation_verification:
  mandatory_checks:
    - Protocol version compatibility
    - User authorization status
    - Resource availability
    - Prerequisite completion

  validation_sequence:
    1: "Check protocol compliance state"
    2: "Verify all required parameters"
    3: "Validate against schema"
    4: "Confirm no active violations"
```

#### C.3.2 Post-Operation Verification
```yaml
post_operation_verification:
  success_criteria:
    - Operation completed without errors
    - All entities properly created/updated
    - Relationships correctly established
    - Audit trail complete

  failure_handling:
    - Create failure entity
    - Record error details
    - Initiate rollback if possible
    - Alert user with remediation steps
```

---

## PROTOCOL SECTION D: NEO4J MEMORY SPECIFICATIONS

### D.1 Graph Schema Specifications

#### D.1.1 Core Node Types
```yaml
memory_node:
  label: "Memory"
  properties:
    name:
      type: "string"
      constraints: ["UNIQUE", "NOT NULL"]
    type:
      type: "string"
      constraints: ["NOT NULL"]
    observations:
      type: "array[string]"
      constraints: ["NOT NULL", "MIN_LENGTH: 1"]
    created_at:
      type: "datetime"
      constraints: ["NOT NULL", "IMMUTABLE"]
    updated_at:
      type: "datetime"
      constraints: ["NOT NULL"]
  indexes:
    - "CREATE INDEX memory_name_idx ON :Memory(name)"
    - "CREATE INDEX memory_type_idx ON :Memory(type)"
    - "CREATE FULLTEXT INDEX memory_search_idx ON :Memory(name, type, observations)"
```

#### D.1.2 Relationship Types
```yaml
relationship_types:
  RELATES_TO:
    properties:
      relationType: "string"
      created_at: "datetime"
      strength: "float (0.0-1.0)"

  CREATED_BY:
    properties:
      timestamp: "datetime"
      session_id: "string"

  AUDIT_TRAIL:
    properties:
      action: "string"
      timestamp: "datetime"
      details: "string"

  DEPENDS_ON:
    properties:
      dependency_type: "string"
      required: "boolean"
```

### D.2 Memory Management Protocols

#### D.2.1 Entity Lifecycle Management
```yaml
entity_lifecycle:
  creation:
    required_fields:
      - name (unique)
      - type (non-empty)
      - observations (at least one)
    auto_generated:
      - created_at (current timestamp)
      - updated_at (current timestamp)
    post_creation:
      - Create audit relationship
      - Link to session entity

  modification:
    allowed_operations:
      - Add observations
      - Update type
      - Add relationships
    prohibited:
      - Changing name (immutable)
      - Deleting all observations
      - Modifying created_at
    tracking:
      - Update updated_at timestamp
      - Create modification audit

  deletion:
    pre_deletion:
      - Create deletion record
      - Backup all properties
      - Store relationship snapshot
    cascade_rules:
      - Delete all outgoing relationships
      - Delete all incoming relationships
      - Preserve audit trail
```

#### D.2.2 Relationship Management
```yaml
relationship_management:
  creation_rules:
    - Both nodes must exist
    - Relationship type required
    - No duplicate relationships
    - Must use active voice

  validation:
    - Check node existence
    - Verify relationship uniqueness
    - Validate type format

  deletion:
    - Exact match required
    - Create deletion audit
    - Update connected nodes
```

### D.3 Query Optimization Specifications

#### D.3.1 Index Usage Guidelines
```yaml
index_optimization:
  fulltext_search:
    index: "memory_search_idx"
    usage: "For search_memories operations"
    query_pattern: "CALL db.index.fulltext.queryNodes('memory_search_idx', $query)"

  exact_match:
    index: "memory_name_idx"
    usage: "For find_memories_by_name operations"
    query_pattern: "MATCH (m:Memory {name: $name})"

  type_filtering:
    index: "memory_type_idx"
    usage: "For filtering by entity type"
    query_pattern: "MATCH (m:Memory {type: $type})"
```

#### D.3.2 Query Performance Standards
```yaml
performance_standards:
  response_times:
    read_graph: "< 5 seconds for graphs under 10,000 nodes"
    search_memories: "< 1 second for standard searches"
    create_entities: "< 500ms per entity"

  batch_operations:
    max_batch_size: 1000
    chunking_strategy: "Split large batches into 100-item chunks"

  connection_pooling:
    min_connections: 1
    max_connections: 10
    connection_timeout: 30
```

---

## PROTOCOL SECTION E: VALIDATION & QUALITY STANDARDS

### E.1 Validation Commands

#### E.1.1 Pre-Deployment Validation
```yaml
pre_deployment_validation:
  unit_tests:
    command: "uv run pytest tests/unit/ -v"
    required_coverage: 80%
    failure_action: "BLOCK deployment"

  integration_tests:
    command: "uv run pytest tests/integration/ -v"
    required_pass_rate: 100%
    failure_action: "BLOCK deployment"

  type_checking:
    command: "uv run pyright"
    allowed_errors: 0
    failure_action: "BLOCK deployment"

  security_scan:
    command: "uv run bandit -r src/"
    severity_threshold: "MEDIUM"
    failure_action: "MANUAL review required"
```

#### E.1.2 Runtime Validation
```yaml
runtime_validation:
  health_checks:
    neo4j_connection:
      interval: 30
      timeout: 5
      retry: 3

    memory_availability:
      threshold: "80%"
      action: "Alert and gc.collect()"

    response_time:
      threshold: 5000
      action: "Log warning and optimize"

  data_validation:
    entity_names:
      pattern: "^[A-Za-z0-9_-]+$"
      max_length: 255

    observations:
      max_length: 5000
      encoding: "UTF-8"

    relationships:
      max_per_node: 1000
      type_pattern: "^[A-Z][A-Z_]*$"
```

### E.2 Quality Standards

#### E.2.1 Code Quality Metrics
```yaml
code_quality_metrics:
  complexity:
    cyclomatic_complexity: "< 10 per function"
    cognitive_complexity: "< 15 per function"

  maintainability:
    maintainability_index: "> 70"
    technical_debt_ratio: "< 5%"

  documentation:
    docstring_coverage: 100%
    inline_comment_ratio: "> 15%"

  testing:
    test_coverage: "> 80%"
    test_ratio: "2:1 (test:code)"
    mutation_score: "> 75%"
```

#### E.2.2 Documentation Standards
```yaml
documentation_standards:
  docstrings:
    style: "Google"
    required_sections:
      - Description
      - Args
      - Returns
      - Raises
      - Examples (for public APIs)

  inline_comments:
    complex_logic: "Required for logic with complexity > 5"
    business_rules: "Required for all business logic"
    workarounds: "Required with issue reference"

  external_docs:
    api_documentation: "OpenAPI 3.0 specification"
    user_guide: "Markdown with examples"
    architecture: "C4 model diagrams"
```

### E.3 Quality Assurance Protocols

#### E.3.1 Automated Quality Checks
```yaml
automated_qa:
  pre_commit_hooks:
    - black (code formatting)
    - isort (import sorting)
    - mypy (type checking)
    - pylint (linting)
    - pytest (unit tests)

  ci_pipeline:
    stages:
      - lint
      - type_check
      - unit_test
      - integration_test
      - security_scan
      - coverage_report

  quality_gates:
    coverage: "> 80%"
    duplication: "< 3%"
    vulnerabilities: 0
    code_smells: "< 10"
```

#### E.3.2 Manual Review Standards
```yaml
manual_review:
  code_review:
    required_approvals: 2
    checklist:
      - Functionality correct
      - Tests comprehensive
      - Documentation complete
      - Performance acceptable
      - Security validated

  architecture_review:
    frequency: "Every 10 PRs"
    reviewers: "Senior architects"
    focus_areas:
      - Design patterns
      - Scalability
      - Maintainability

  security_review:
    triggers:
      - Authentication changes
      - Authorization changes
      - Cryptography usage
      - External integrations
```

---

## PROTOCOL SECTION F: PRODUCTION READY STANDARDS

### F.1 Success Criteria

#### F.1.1 Functional Success Criteria
```yaml
functional_criteria:
  core_functionality:
    - All 9 MCP tools operational
    - Neo4j connection stable
    - Graph operations performant
    - Error handling comprehensive

  integration:
    - Claude Desktop compatible
    - HTTP/SSE transport working
    - Docker deployment successful
    - Kubernetes ready

  reliability:
    uptime_target: "99.9%"
    error_rate: "< 0.1%"
    recovery_time: "< 1 minute"
```

#### F.1.2 Performance Success Criteria
```yaml
performance_criteria:
  response_times:
    p50: "< 100ms"
    p95: "< 500ms"
    p99: "< 1000ms"

  throughput:
    reads: "> 1000 ops/sec"
    writes: "> 100 ops/sec"
    searches: "> 500 ops/sec"

  resource_usage:
    cpu: "< 50% average"
    memory: "< 1GB"
    disk_io: "< 100 IOPS"
```

### F.2 Enterprise Standards

#### F.2.1 Security Standards
```yaml
security_standards:
  authentication:
    methods: ["API Key", "JWT", "OAuth2"]
    mfa_required: true
    session_timeout: 3600

  authorization:
    model: "RBAC"
    granularity: "Operation level"
    audit_logging: "All operations"

  encryption:
    data_at_rest: "AES-256"
    data_in_transit: "TLS 1.3"
    key_management: "HSM backed"

  compliance:
    standards: ["SOC2", "ISO 27001", "GDPR"]
    audit_frequency: "Quarterly"
    penetration_testing: "Annual"
```

#### F.2.2 Operational Standards
```yaml
operational_standards:
  monitoring:
    metrics:
      - Response time
      - Error rate
      - Throughput
      - Resource usage
    tools:
      - Prometheus
      - Grafana
      - ELK Stack

  alerting:
    severity_levels:
      - P1: "Service down"
      - P2: "Degraded performance"
      - P3: "Warning threshold"
    notification_channels:
      - PagerDuty
      - Slack
      - Email

  backup:
    frequency: "Every 6 hours"
    retention: "30 days"
    testing: "Weekly restore test"
```

### F.3 Deployment Standards

#### F.3.1 Container Standards
```yaml
container_standards:
  docker:
    base_image: "python:3.11-slim"
    multi_stage: true
    security_scanning: "Trivy"
    size_limit: "< 500MB"

  kubernetes:
    resources:
      requests:
        cpu: "100m"
        memory: "256Mi"
      limits:
        cpu: "1000m"
        memory: "1Gi"
    probes:
      liveness: "/health"
      readiness: "/ready"
    scaling:
      min_replicas: 2
      max_replicas: 10
      target_cpu: 70
```

#### F.3.2 CI/CD Standards
```yaml
cicd_standards:
  pipeline_stages:
    - validate
    - build
    - test
    - scan
    - package
    - deploy

  environments:
    development:
      auto_deploy: true
      approval: "Not required"

    staging:
      auto_deploy: true
      approval: "Not required"
      smoke_tests: "Required"

    production:
      auto_deploy: false
      approval: "2 approvers"
      canary_deployment: true
      rollback_ready: true
```

---

## PROTOCOL SECTION G: PROTOCOL COMPLIANCE & ENFORCEMENT

### G.1 Violation Response Procedures

#### G.1.1 Violation Detection
```yaml
violation_detection:
  automated_detection:
    monitors:
      - Protocol version mismatch
      - Unauthorized operations
      - Schema violations
      - Performance degradation
    response_time: "< 1 second"

  manual_detection:
    sources:
      - Code review findings
      - User reports
      - Audit logs
    response_time: "< 1 hour"
```

#### G.1.2 Violation Classification
```yaml
violation_severity:
  CRITICAL:
    description: "Immediate system integrity threat"
    examples:
      - Data corruption
      - Security breach
      - Protocol bypass
    response:
      - Immediate system halt
      - Emergency notification
      - Incident response team activation

  HIGH:
    description: "Significant compliance deviation"
    examples:
      - Missing audit trail
      - Validation skip
      - Unauthorized access attempt
    response:
      - Operation blocked
      - Supervisor notification
      - Remediation required

  MEDIUM:
    description: "Standard compliance issue"
    examples:
      - Documentation missing
      - Performance threshold exceeded
      - Non-critical validation failure
    response:
      - Warning logged
      - Remediation scheduled
      - Monthly review

  LOW:
    description: "Minor deviation"
    examples:
      - Formatting issues
      - Optional field missing
      - Style guide violation
    response:
      - Logged for review
      - Batch remediation
      - Quarterly cleanup
```

#### G.1.3 Remediation Procedures
```yaml
remediation_procedures:
  immediate_actions:
    1: "Isolate affected components"
    2: "Capture full context"
    3: "Create violation entity"
    4: "Notify stakeholders"

  root_cause_analysis:
    methodology: "5 Whys"
    documentation: "RCA document required"
    timeline: "Within 24 hours"
    participants:
      - Incident owner
      - Technical lead
      - Security officer

  corrective_actions:
    implementation:
      - Fix immediate issue
      - Update protocols
      - Add preventive measures
      - Update monitoring
    verification:
      - Test remediation
      - Validate compliance
      - Update documentation
      - Train team

  post_incident:
    review_meeting: "Within 48 hours"
    lessons_learned: "Document and share"
    protocol_updates: "If needed"
    monitoring_enhancement: "Required"
```

### G.2 Enforcement Mechanisms

#### G.2.1 Automated Enforcement
```yaml
automated_enforcement:
  pre_execution_gates:
    - Protocol version check
    - Authorization validation
    - Resource availability
    - Compliance state verification

  runtime_enforcement:
    - Parameter validation
    - Schema compliance
    - Rate limiting
    - Audit logging

  post_execution_verification:
    - Operation success validation
    - State consistency check
    - Audit trail completion
    - Performance threshold check
```

#### G.2.2 Manual Enforcement
```yaml
manual_enforcement:
  code_review:
    mandatory_checks:
      - Protocol compliance
      - Security standards
      - Documentation completeness
      - Test coverage
    blocking_issues:
      - Protocol violations
      - Security vulnerabilities
      - Missing tests
      - Incomplete documentation

  audit_reviews:
    frequency: "Monthly"
    scope:
      - Operation logs
      - Violation records
      - Performance metrics
      - Compliance reports
    outcomes:
      - Compliance score
      - Remediation items
      - Process improvements
      - Training needs
```

### G.3 Compliance Monitoring

#### G.3.1 Real-time Monitoring
```yaml
realtime_monitoring:
  metrics:
    compliance_score:
      calculation: "(compliant_ops / total_ops) * 100"
      threshold: "> 99%"

    violation_rate:
      calculation: "violations_per_hour"
      threshold: "< 1"

    mean_time_to_remediation:
      calculation: "avg(remediation_time)"
      threshold: "< 4 hours"

  dashboards:
    compliance_overview:
      - Current compliance score
      - Active violations
      - Remediation queue
      - Trend analysis

    violation_tracker:
      - Recent violations
      - Severity distribution
      - Root cause analysis
      - Remediation status
```

#### G.3.2 Periodic Assessments
```yaml
periodic_assessments:
  weekly:
    - Violation summary
    - Remediation progress
    - Compliance trends

  monthly:
    - Full compliance audit
    - Protocol effectiveness review
    - Training needs assessment

  quarterly:
    - Protocol revision review
    - Enterprise compliance report
    - Strategic improvements

  annual:
    - Complete protocol overhaul
    - Enterprise security audit
    - Compliance certification
```

---

## PROTOCOL SECTION H: ENTERPRISE SAFETY PROTOCOLS

### H.1 Safety Mechanisms

#### H.1.1 Data Safety
```yaml
data_safety:
  backup_protocols:
    frequency: "Every 6 hours"
    retention: "30 days"
    encryption: "AES-256"
    verification: "Daily restore test"

  data_validation:
    input_sanitization:
      - SQL injection prevention
      - NoSQL injection prevention
      - XSS prevention
      - Command injection prevention

    output_validation:
      - Schema compliance
      - Size limits
      - Encoding verification

  data_integrity:
    checksums: "SHA-256"
    versioning: "Enabled"
    audit_trail: "Immutable"
    recovery_point: "< 1 hour RPO"
```

#### H.1.2 Operational Safety
```yaml
operational_safety:
  circuit_breakers:
    failure_threshold: 5
    timeout: 30
    reset_timeout: 60

  rate_limiting:
    requests_per_second: 100
    burst_size: 200
    per_user_limit: 10

  resource_limits:
    cpu_limit: "80%"
    memory_limit: "1GB"
    disk_quota: "10GB"
    connection_pool: 100

  graceful_degradation:
    fallback_modes:
      - Read-only mode
      - Cached responses
      - Queue for later
      - Service unavailable
```

### H.2 Forbidden Practices

#### H.2.1 Code Practices
```yaml
forbidden_code_practices:
  FORBIDDEN_001:
    practice: "Direct database manipulation"
    reason: "Bypasses validation and audit"
    alternative: "Use repository pattern"

  FORBIDDEN_002:
    practice: "Hardcoded credentials"
    reason: "Security vulnerability"
    alternative: "Use secure credential management"

  FORBIDDEN_003:
    practice: "Synchronous blocking operations"
    reason: "Performance degradation"
    alternative: "Use async/await pattern"

  FORBIDDEN_004:
    practice: "Unvalidated user input"
    reason: "Security vulnerability"
    alternative: "Validate all inputs"

  FORBIDDEN_005:
    practice: "Global mutable state"
    reason: "Thread safety issues"
    alternative: "Use immutable patterns"
```

#### H.2.2 Operational Practices
```yaml
forbidden_operational_practices:
  FORBIDDEN_OP_001:
    practice: "Production debugging"
    reason: "Performance and security risk"
    alternative: "Use staging environment"

  FORBIDDEN_OP_002:
    practice: "Manual database changes"
    reason: "Audit trail bypass"
    alternative: "Use migration scripts"

  FORBIDDEN_OP_003:
    practice: "Unannounced deployments"
    reason: "User disruption"
    alternative: "Follow deployment schedule"

  FORBIDDEN_OP_004:
    practice: "Skipping tests"
    reason: "Quality risk"
    alternative: "Fix failing tests"

  FORBIDDEN_OP_005:
    practice: "Ignoring alerts"
    reason: "Incident escalation"
    alternative: "Investigate all alerts"
```

### H.3 Emergency Procedures

#### H.3.1 Emergency Response
```yaml
emergency_response:
  incident_levels:
    P1_CRITICAL:
      description: "Service down or data loss"
      response_time: "< 5 minutes"
      escalation: "Immediate"
      team: "On-call + Leadership"

    P2_HIGH:
      description: "Degraded service"
      response_time: "< 30 minutes"
      escalation: "After 1 hour"
      team: "On-call"

    P3_MEDIUM:
      description: "Feature impaired"
      response_time: "< 2 hours"
      escalation: "After 4 hours"
      team: "Primary support"

  emergency_contacts:
    on_call: "+1-XXX-XXX-XXXX"
    escalation: "+1-YYY-YYY-YYYY"
    leadership: "+1-ZZZ-ZZZ-ZZZZ"
```

#### H.3.2 Disaster Recovery
```yaml
disaster_recovery:
  rpo_target: "1 hour"
  rto_target: "4 hours"

  recovery_procedures:
    data_corruption:
      1: "Isolate affected system"
      2: "Identify corruption extent"
      3: "Restore from backup"
      4: "Validate data integrity"
      5: "Resume operations"

    complete_failure:
      1: "Activate DR site"
      2: "Restore from backup"
      3: "Validate functionality"
      4: "Update DNS"
      5: "Monitor closely"

  testing:
    frequency: "Quarterly"
    scenarios:
      - Database failure
      - Network partition
      - Data center loss
      - Cyber attack
```

---

## PROTOCOL SECTION I: TEMPLATE CONFIGURATION

### I.1 Project-Specific Variables

#### I.1.1 Core Configuration
```yaml
project_configuration:
  identifiers:
    PROJECT_ID: "neo4j-memory"
    PROJECT_NAME: "MCP Neo4j Memory Server"
    PROJECT_VERSION: "1.0.0"
    PROTOCOL_VERSION: "2.0.0"

  environment:
    WORKING_BRANCH: "development"
    SACRED_BRANCHES: ["main", "master"]
    PROTECTED_PATHS:
      - "/.github/"
      - "/deployments/production/"
      - "/security/"

  database:
    DB_TYPE: "neo4j"
    DB_PATH: "neo4j://localhost:7687"
    DB_USERNAME: "neo4j"
    DB_NAME: "neo4j"
    DB_VERSION: "5.x"

  frameworks:
    PRIMARY: "FastMCP"
    DATABASE: "Neo4j"
    LANGUAGE: "Python"
    RUNTIME: "Python 3.11+"
    PACKAGE_MANAGER: "uv"
```

#### I.1.2 Deployment Configuration
```yaml
deployment_configuration:
  docker:
    IMAGE_NAME: "mcp/neo4j-memory"
    BASE_IMAGE: "python:3.11-slim"
    REGISTRY: "docker.io"

  kubernetes:
    NAMESPACE: "mcp-services"
    SERVICE_NAME: "neo4j-memory"
    REPLICAS: 3

  transport:
    MODES: ["stdio", "http", "sse"]
    DEFAULT: "stdio"
    HTTP_PORT: 8000
    HTTP_PATH: "/mcp/"
```

### I.2 Variable Replacement Rules

#### I.2.1 Timestamp Variables
```yaml
timestamp_replacements:
  YYYY-MM-DD-HHMMSS:
    format: "2025-09-23-044431"
    timezone: "UTC"
    usage: "All timestamps"

  YYYY-MM-DD:
    format: "2025-09-23"
    timezone: "UTC"
    usage: "Date only references"

  HHMMSS:
    format: "044431"
    timezone: "UTC"
    usage: "Time only references"
```

#### I.2.2 Dynamic Variables
```yaml
dynamic_replacements:
  SESSION_ID:
    pattern: "Session_{YYYY-MM-DD-HHMMSS}"
    scope: "Per AI agent session"

  OPERATION_ID:
    pattern: "Op_{UUID}"
    scope: "Per operation"

  USER_ID:
    source: "Authentication context"
    scope: "Per user session"

  TRACE_ID:
    pattern: "Trace_{UUID}"
    scope: "Per request chain"
```

### I.3 Protocol Activation

#### I.3.1 Initialization Sequence
```yaml
protocol_initialization:
  step_1_validation:
    - Verify protocol version
    - Check configuration completeness
    - Validate environment

  step_2_connection:
    - Connect to Neo4j
    - Verify graph accessibility
    - Create session entity

  step_3_context:
    - Load project context
    - Initialize monitoring
    - Start audit logging

  step_4_ready:
    - Set compliance state ACTIVE
    - Enable all protocols
    - Begin normal operations
```

#### I.3.2 Deactivation Sequence
```yaml
protocol_deactivation:
  step_1_preparation:
    - Set compliance state DEACTIVATING
    - Stop accepting new operations
    - Complete active operations

  step_2_cleanup:
    - Flush audit logs
    - Close database connections
    - Save session summary

  step_3_shutdown:
    - Create shutdown entity
    - Final compliance check
    - Set compliance state INACTIVE
```

---

## APPENDIX A: QUICK REFERENCE

### MCP Tool Commands
```bash
# Query Operations
read_graph()
search_memories(query="search_term")
find_memories_by_name(names=["name1", "name2"])

# Entity Operations
create_entities(entities=[{name, type, observations}])
delete_entities(entityNames=["name1", "name2"])

# Relation Operations
create_relations(relations=[{source, target, relationType}])
delete_relations(relations=[{source, target, relationType}])

# Observation Operations
add_observations(observations=[{entityName, observations}])
delete_observations(deletions=[{entityName, observations}])
```

### Validation Commands
```bash
# Testing
uv run pytest tests/ -v
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# Type Checking
uv run pyright
uv run mypy src/

# Linting
uv run pylint src/
uv run black --check src/
```

### Deployment Commands
```bash
# Local Development
uv run python -m mcp_neo4j_memory --db-url neo4j://localhost:7687

# Docker
docker build -t mcp/neo4j-memory:latest .
docker run -e NEO4J_URL=neo4j://localhost:7687 mcp/neo4j-memory:latest

# Kubernetes
kubectl apply -f deployments/kubernetes/
kubectl get pods -n mcp-services
```

---

## APPENDIX B: COMPLIANCE CHECKLIST

### Pre-Operation Checklist
- [ ] Protocol version verified
- [ ] Configuration validated
- [ ] Neo4j connection confirmed
- [ ] Session entity created
- [ ] Audit logging enabled
- [ ] Monitoring active
- [ ] Compliance state ACTIVE

### Post-Operation Checklist
- [ ] Operation completed successfully
- [ ] Audit trail created
- [ ] Observations recorded
- [ ] Relationships established
- [ ] Verification completed
- [ ] Metrics updated
- [ ] No violations detected

### Daily Compliance Tasks
- [ ] Review violation logs
- [ ] Check compliance score
- [ ] Verify backup completion
- [ ] Review performance metrics
- [ ] Update documentation
- [ ] Clear remediation queue

---

## DOCUMENT METADATA

- **Document Version**: 2.0.0
- **Created**: 2025-09-23-044431
- **Last Updated**: 2025-09-23-044431
- **Status**: ACTIVE
- **Review Cycle**: Quarterly
- **Next Review**: 2025-12-23
- **Owner**: AI Agent Compliance Team
- **Classification**: MANDATORY COMPLIANCE

---

END OF PROTOCOL DOCUMENT