---
title: Get started with Claude Code hooks
source: https://docs.anthropic.com/en/docs/claude-code/hooks-guide
fetched: 2025-09-24 20:17:20
---

[Claude Docs home page![light logo](https://mintcdn.com/anthropic-claude-docs/DcI2Ybid7ZEnFaf0/logo/light.svg?fit=max&auto=format&n=DcI2Ybid7ZEnFaf0&q=85&s=c877c45432515ee69194cb19e9f983a2)![dark logo](https://mintcdn.com/anthropic-claude-docs/DcI2Ybid7ZEnFaf0/logo/dark.svg?fit=max&auto=format&n=DcI2Ybid7ZEnFaf0&q=85&s=f5bb877be0cb3cba86cf6d7c88185216)](/)

![US](https://d3gk2c5xim1je2.cloudfront.net/flags/US.svg)

English

Search...

⌘K

* [Console](https://console.anthropic.com/login)
* [Support](https://support.claude.com/)
* [Research](https://www.anthropic.com/research)
* [Discord](https://www.anthropic.com/discord)
* [Sign up](https://console.anthropic.com/login)
* [Sign up](https://console.anthropic.com/login)

Search...

Navigation

Build with Claude Code

Get started with Claude Code hooks

[Welcome](/en/home)[Claude Developer Platform](/en/docs/intro)[Claude Code](/en/docs/claude-code/overview)[Model Context Protocol (MCP)](/en/docs/mcp)[API Reference](/en/api/messages)[Resources](/en/resources/overview)[Release Notes](/en/release-notes/overview)

##### Getting started

* [Overview](/en/docs/claude-code/overview)
* [Quickstart](/en/docs/claude-code/quickstart)
* [Common workflows](/en/docs/claude-code/common-workflows)

##### Build with Claude Code

* [Subagents](/en/docs/claude-code/sub-agents)
* [Output styles](/en/docs/claude-code/output-styles)
* [Hooks](/en/docs/claude-code/hooks-guide)
* [GitHub Actions](/en/docs/claude-code/github-actions)
* [GitLab CI/CD](/en/docs/claude-code/gitlab-ci-cd)
* [Model Context Protocol (MCP)](/en/docs/claude-code/mcp)
* [Troubleshooting](/en/docs/claude-code/troubleshooting)

##### Claude Code SDK

* [Overview](/en/docs/claude-code/sdk/sdk-overview)
* [TypeScript SDK reference](/en/docs/claude-code/sdk/sdk-typescript)
* [Python SDK reference](/en/docs/claude-code/sdk/sdk-python)
* [Headless mode](/en/docs/claude-code/sdk/sdk-headless)
* Guides

##### Deployment

* [Overview](/en/docs/claude-code/third-party-integrations)
* [Amazon Bedrock](/en/docs/claude-code/amazon-bedrock)
* [Google Vertex AI](/en/docs/claude-code/google-vertex-ai)
* [Network configuration](/en/docs/claude-code/network-config)
* [LLM gateway](/en/docs/claude-code/llm-gateway)
* [Development containers](/en/docs/claude-code/devcontainer)

##### Administration

* [Advanced installation](/en/docs/claude-code/setup)
* [Identity and Access Management](/en/docs/claude-code/iam)
* [Security](/en/docs/claude-code/security)
* [Data usage](/en/docs/claude-code/data-usage)
* [Monitoring](/en/docs/claude-code/monitoring-usage)
* [Costs](/en/docs/claude-code/costs)
* [Analytics](/en/docs/claude-code/analytics)

##### Configuration

* [Settings](/en/docs/claude-code/settings)
* [Add Claude Code to your IDE](/en/docs/claude-code/ide-integrations)
* [Terminal configuration](/en/docs/claude-code/terminal-config)
* [Model configuration](/en/docs/claude-code/model-config)
* [Memory management](/en/docs/claude-code/memory)
* [Status line configuration](/en/docs/claude-code/statusline)

##### Reference

* [CLI reference](/en/docs/claude-code/cli-reference)
* [Interactive mode](/en/docs/claude-code/interactive-mode)
* [Slash commands](/en/docs/claude-code/slash-commands)
* [Hooks reference](/en/docs/claude-code/hooks)

##### Resources

* [Legal and compliance](/en/docs/claude-code/legal-and-compliance)

On this page

* [Hook Events Overview](#hook-events-overview)
* [Quickstart](#quickstart)
* [Prerequisites](#prerequisites)
* [Step 1: Open hooks configuration](#step-1%3A-open-hooks-configuration)
* [Step 2: Add a matcher](#step-2%3A-add-a-matcher)
* [Step 3: Add the hook](#step-3%3A-add-the-hook)
* [Step 4: Save your configuration](#step-4%3A-save-your-configuration)
* [Step 5: Verify your hook](#step-5%3A-verify-your-hook)
* [Step 6: Test your hook](#step-6%3A-test-your-hook)
* [More Examples](#more-examples)
* [Code Formatting Hook](#code-formatting-hook)
* [Markdown Formatting Hook](#markdown-formatting-hook)
* [Custom Notification Hook](#custom-notification-hook)
* [File Protection Hook](#file-protection-hook)
* [Learn more](#learn-more)

Build with Claude Code

# Get started with Claude Code hooks

Copy page

Learn how to customize and extend Claude Code’s behavior by registering shell commands

Copy page

Claude Code hooks are user-defined shell commands that execute at various points
in Claude Code’s lifecycle. Hooks provide deterministic control over Claude
Code’s behavior, ensuring certain actions always happen rather than relying on
the LLM to choose to run them.

For reference documentation on hooks, see [Hooks reference](/en/docs/claude-code/hooks).

Example use cases for hooks include:

* **Notifications**: Customize how you get notified when Claude Code is awaiting
  your input or permission to run something.
* **Automatic formatting**: Run `prettier` on .ts files, `gofmt` on .go files,
  etc. after every file edit.
* **Logging**: Track and count all executed commands for compliance or
  debugging.
* **Feedback**: Provide automated feedback when Claude Code produces code that
  does not follow your codebase conventions.
* **Custom permissions**: Block modifications to production files or sensitive
  directories.

By encoding these rules as hooks rather than prompting instructions, you turn
suggestions into app-level code that executes every time it is expected to run.

You must consider the security implication of hooks as you add them, because hooks run automatically during the agent loop with your current environment’s credentials.
For example, malicious hooks code can exfiltrate your data. Always review your hooks implementation before registering them.For full security best practices, see [Security Considerations](/en/docs/claude-code/hooks#security-considerations) in the hooks reference documentation.

## [​](#hook-events-overview) Hook Events Overview

Claude Code provides several hook events that run at different points in the
workflow:

* **PreToolUse**: Runs before tool calls (can block them)
* **PostToolUse**: Runs after tool calls complete
* **UserPromptSubmit**: Runs when the user submits a prompt, before Claude processes it
* **Notification**: Runs when Claude Code sends notifications
* **Stop**: Runs when Claude Code finishes responding
* **SubagentStop**: Runs when subagent tasks complete
* **PreCompact**: Runs before Claude Code is about to run a compact operation
* **SessionStart**: Runs when Claude Code starts a new session or resumes an existing session
* **SessionEnd**: Runs when Claude Code session ends

Each event receives different data and can control Claude’s behavior in
different ways.

## [​](#quickstart) Quickstart

In this quickstart, you’ll add a hook that logs the shell commands that Claude
Code runs.

### [​](#prerequisites) Prerequisites

Install `jq` for JSON processing in the command line.

### [​](#step-1%3A-open-hooks-configuration) Step 1: Open hooks configuration

Run the `/hooks` [slash command](/en/docs/claude-code/slash-commands) and select
the `PreToolUse` hook event.
`PreToolUse` hooks run before tool calls and can block them while providing
Claude feedback on what to do differently.

### [​](#step-2%3A-add-a-matcher) Step 2: Add a matcher

Select `+ Add new matcher…` to run your hook only on Bash tool calls.
Type `Bash` for the matcher.

You can use `*` to match all tools.

### [​](#step-3%3A-add-the-hook) Step 3: Add the hook

Select `+ Add new hook…` and enter this command:

Copy

```
jq -r '"\(.tool_input.command) - \(.tool_input.description // "No description")"' >> ~/.claude/bash-command-log.txt

```

### [​](#step-4%3A-save-your-configuration) Step 4: Save your configuration

For storage location, select `User settings` since you’re logging to your home
directory. This hook will then apply to all projects, not just your current
project.
Then press Esc until you return to the REPL. Your hook is now registered!

### [​](#step-5%3A-verify-your-hook) Step 5: Verify your hook

Run `/hooks` again or check `~/.claude/settings.json` to see your configuration:

Copy

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"\\(.tool_input.command) - \\(.tool_input.description // \"No description\")\"' >> ~/.claude/bash-command-log.txt"
          }
        ]
      }
    ]
  }
}

```

### [​](#step-6%3A-test-your-hook) Step 6: Test your hook

Ask Claude to run a simple command like `ls` and check your log file:

Copy

```
cat ~/.claude/bash-command-log.txt

```

You should see entries like:

Copy

```
ls - Lists files and directories

```

## [​](#more-examples) More Examples

For a complete example implementation, see the [bash command validator example](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py) in our public codebase.

### [​](#code-formatting-hook) Code Formatting Hook

Automatically format TypeScript files after editing:

Copy

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -q '\\.ts$'; then npx prettier --write \"$file_path\"; fi; }"
          }
        ]
      }
    ]
  }
}

```

### [​](#markdown-formatting-hook) Markdown Formatting Hook

Automatically fix missing language tags and formatting issues in markdown files:

Copy

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/markdown_formatter.py"
          }
        ]
      }
    ]
  }
}

```

Create `.claude/hooks/markdown_formatter.py` with this content:

Copy

```
#!/usr/bin/env python3
"""
Markdown formatter for Claude Code output.
Fixes missing language tags and spacing issues while preserving code content.
"""
import json
import sys
import re
import os

def detect_language(code):
    """Best-effort language detection from code content."""
    s = code.strip()
    
    # JSON detection
    if re.search(r'^\s*[{\[]', s):
        try:
            json.loads(s)
            return 'json'
        except:
            pass
    
    # Python detection
    if re.search(r'^\s*def\s+\w+\s*\(', s, re.M) or \
       re.search(r'^\s*(import|from)\s+\w+', s, re.M):
        return 'python'
    
    # JavaScript detection  
    if re.search(r'\b(function\s+\w+\s*\(|const\s+\w+\s*=)', s) or \
       re.search(r'=>|console\.(log|error)', s):
        return 'javascript'
    
    # Bash detection
    if re.search(r'^#!.*\b(bash|sh)\b', s, re.M) or \
       re.search(r'\b(if|then|fi|for|in|do|done)\b', s):
        return 'bash'
    
    # SQL detection
    if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE)\s+', s, re.I):
        return 'sql'
        
    return 'text'

def format_markdown(content):
    """Format markdown content with language detection."""
    # Fix unlabeled code fences
    def add_lang_to_fence(match):
        indent, info, body, closing = match.groups()
        if not info.strip():
            lang = detect_language(body)
            return f"{indent}```{lang}\n{body}{closing}\n"
        return match.group(0)
    
    fence_pattern = r'(?ms)^([ \t]{0,3})```([^\n]*)\n(.*?)(\n\1```)\s*$'
    content = re.sub(fence_pattern, add_lang_to_fence, content)
    
    # Fix excessive blank lines (only outside code fences)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.rstrip() + '\n'

# Main execution
try:
    input_data = json.load(sys.stdin)
    file_path = input_data.get('tool_input', {}).get('file_path', '')
    
    if not file_path.endswith(('.md', '.mdx')):
        sys.exit(0)  # Not a markdown file
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        formatted = format_markdown(content)
        
        if formatted != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"✓ Fixed markdown formatting in {file_path}")
    
except Exception as e:
    print(f"Error formatting markdown: {e}", file=sys.stderr)
    sys.exit(1)

```

Make the script executable:

Copy

```
chmod +x .claude/hooks/markdown_formatter.py

```

This hook automatically:

* Detects programming languages in unlabeled code blocks
* Adds appropriate language tags for syntax highlighting
* Fixes excessive blank lines while preserving code content
* Only processes markdown files (`.md`, `.mdx`)

### [​](#custom-notification-hook) Custom Notification Hook

Get desktop notifications when Claude needs input:

Copy

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Awaiting your input'"
          }
        ]
      }
    ]
  }
}

```

### [​](#file-protection-hook) File Protection Hook

Block edits to sensitive files:

Copy

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(2 if any(p in path for p in ['.env', 'package-lock.json', '.git/']) else 0)\""
          }
        ]
      }
    ]
  }
}

```

## [​](#learn-more) Learn more

* For reference documentation on hooks, see [Hooks reference](/en/docs/claude-code/hooks).
* For comprehensive security best practices and safety guidelines, see [Security Considerations](/en/docs/claude-code/hooks#security-considerations) in the hooks reference documentation.
* For troubleshooting steps and debugging techniques, see [Debugging](/en/docs/claude-code/hooks#debugging) in the hooks reference
  documentation.

Was this page helpful?

YesNo

[Output styles](/en/docs/claude-code/output-styles)[GitHub Actions](/en/docs/claude-code/github-actions)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.