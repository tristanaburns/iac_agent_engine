# Hooks System Refactoring Plan

## Principles Applied
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY**: Don't Repeat Yourself - shared logic extracted to common modules
- **KISS**: Keep It Simple, Stupid - one clear purpose per module

## New Directory Structure

```
.claude/hooks/
 hooks/                      # Simple wrapper hooks (entry points)
    post_tool_use.py       # Wrapper for PostToolUse events
    subagent_stop.py       # Wrapper for SubagentStop events
    stop.py                # Wrapper for Stop events

 operations/                 # Core business logic (SOLID)
    quality/               # Quality check operations
       black_formatter.py
       isort_formatter.py
       ruff_linter.py
       mypy_checker.py
       compilation_verifier.py
       quality_analyzer.py
   
    cleanup/               # Cleanup operations
       unicode_cleaner.py
       file_validator.py
       backup_manager.py
       cleanup_orchestrator.py
   
    git/                   # Git operations
       protection_commit.py
       completion_commit.py
       rollback_handler.py
       git_orchestrator.py
   
    logging/               # Logging operations
        file_logger.py
        console_logger.py
        metrics_logger.py
        log_orchestrator.py

 claude_sdk/                # Claude SDK operations
    client/               # SDK client management
       sdk_initializer.py
       session_manager.py
       connection_handler.py
   
    workflows/            # Workflow operations
       quality_workflow.py
       remediation_workflow.py
       analysis_workflow.py
       workflow_orchestrator.py
   
    queries/              # Query operations
        query_builder.py
        query_executor.py
        response_handler.py

 orchestrators/             # High-level orchestration
    quality_orchestrator.py
    cleanup_orchestrator.py
    remediation_orchestrator.py
    main_orchestrator.py

 config/                    # Configuration management
    quality_config.py
    cleanup_config.py
    sdk_config.py
    config_loader.py

 utils/                     # Shared utilities
     path_resolver.py
     file_handler.py
     process_runner.py
     error_handler.py
```

## Module Responsibilities

### Hooks (Simple Wrappers)
- **post_tool_use.py**: Receives event, calls orchestrator
- **subagent_stop.py**: Receives event, calls orchestrator
- **stop.py**: Receives event, calls orchestrator

### Operations (Core Logic)
Each module has a single responsibility:
- **black_formatter.py**: Only runs Black formatter
- **unicode_cleaner.py**: Only cleans Unicode characters
- **protection_commit.py**: Only creates protection commits
- **file_logger.py**: Only logs to files

### Claude SDK Operations
- **sdk_initializer.py**: Initialize Claude SDK client
- **query_executor.py**: Execute queries through SDK
- **workflow_orchestrator.py**: Coordinate workflow execution

### Orchestrators
- Coordinate multiple operations
- Handle dependencies between operations
- Manage execution flow

## Implementation Order
1. Create directory structure
2. Extract logging operations
3. Extract quality check operations
4. Extract cleanup operations
5. Extract git operations
6. Create Claude SDK modules
7. Create orchestrators
8. Refactor hooks to wrappers
9. Test the refactored system

## Benefits
1. **Clear Separation**: Each file has one clear purpose
2. **Testability**: Each module can be tested independently
3. **Maintainability**: Changes to one operation don't affect others
4. **Reusability**: Operations can be reused in different contexts
5. **Extensibility**: New operations can be added without modifying existing code