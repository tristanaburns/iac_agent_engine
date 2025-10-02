---
title: Headless mode
source: https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-headless
fetched: 2025-09-24 20:17:31
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

Claude Code SDK

Headless mode

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

* [Overview](#overview)
* [Basic usage](#basic-usage)
* [Configuration Options](#configuration-options)
* [Multi-turn conversations](#multi-turn-conversations)
* [Output Formats](#output-formats)
* [Text Output (Default)](#text-output-default)
* [JSON Output](#json-output)
* [Streaming JSON Output](#streaming-json-output)
* [Input Formats](#input-formats)
* [Text Input (Default)](#text-input-default)
* [Streaming JSON Input](#streaming-json-input)
* [Agent Integration Examples](#agent-integration-examples)
* [SRE Incident Response Bot](#sre-incident-response-bot)
* [Automated Security Review](#automated-security-review)
* [Multi-turn Legal Assistant](#multi-turn-legal-assistant)
* [Best Practices](#best-practices)
* [Related Resources](#related-resources)

Claude Code SDK

# Headless mode

Copy page

Run Claude Code programmatically without interactive UI

Copy page

## [​](#overview) Overview

The headless mode allows you to run Claude Code programmatically from command line scripts and automation tools without any interactive UI.

## [​](#basic-usage) Basic usage

The primary command-line interface to Claude Code is the `claude` command. Use the `--print` (or `-p`) flag to run in non-interactive mode and print the final result:

Copy

```
claude -p "Stage my changes and write a set of commits for them" \
  --allowedTools "Bash,Read" \
  --permission-mode acceptEdits

```

## [​](#configuration-options) Configuration Options

The SDK leverages all the CLI options available in Claude Code. Here are the key ones for SDK usage:

| Flag | Description | Example |
| --- | --- | --- |
| `--print`, `-p` | Run in non-interactive mode | `claude -p "query"` |
| `--output-format` | Specify output format (`text`, `json`, `stream-json`) | `claude -p --output-format json` |
| `--resume`, `-r` | Resume a conversation by session ID | `claude --resume abc123` |
| `--continue`, `-c` | Continue the most recent conversation | `claude --continue` |
| `--verbose` | Enable verbose logging | `claude --verbose` |
| `--append-system-prompt` | Append to system prompt (only with `--print`) | `claude --append-system-prompt "Custom instruction"` |
| `--allowedTools` | Space-separated list of allowed tools, or    string of comma-separated list of allowed tools | `claude --allowedTools mcp__slack mcp__filesystem`  `claude --allowedTools "Bash(npm install),mcp__filesystem"` |
| `--disallowedTools` | Space-separated list of denied tools, or    string of comma-separated list of denied tools | `claude --disallowedTools mcp__splunk mcp__github`  `claude --disallowedTools "Bash(git commit),mcp__github"` |
| `--mcp-config` | Load MCP servers from a JSON file | `claude --mcp-config servers.json` |
| `--permission-prompt-tool` | MCP tool for handling permission prompts (only with `--print`) | `claude --permission-prompt-tool mcp__auth__prompt` |

For a complete list of CLI options and features, see the [CLI reference](/en/docs/claude-code/cli-reference) documentation.

## [​](#multi-turn-conversations) Multi-turn conversations

For multi-turn conversations, you can resume conversations or continue from the most recent session:

Copy

```
# Continue the most recent conversation
claude --continue "Now refactor this for better performance"

# Resume a specific conversation by session ID
claude --resume 550e8400-e29b-41d4-a716-446655440000 "Update the tests"

# Resume in non-interactive mode
claude --resume 550e8400-e29b-41d4-a716-446655440000 "Fix all linting issues" --no-interactive

```

## [​](#output-formats) Output Formats

### [​](#text-output-default) Text Output (Default)

Copy

```
claude -p "Explain file src/components/Header.tsx"
# Output: This is a React component showing...

```

### [​](#json-output) JSON Output

Returns structured data including metadata:

Copy

```
claude -p "How does the data layer work?" --output-format json

```

Response format:

Copy

```
{
  "type": "result",
  "subtype": "success",
  "total_cost_usd": 0.003,
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 800,
  "num_turns": 6,
  "result": "The response text here...",
  "session_id": "abc123"
}

```

### [​](#streaming-json-output) Streaming JSON Output

Streams each message as it is received:

Copy

```
claude -p "Build an application" --output-format stream-json

```

Each conversation begins with an initial `init` system message, followed by a list of user and assistant messages, followed by a final `result` system message with stats. Each message is emitted as a separate JSON object.

## [​](#input-formats) Input Formats

### [​](#text-input-default) Text Input (Default)

Copy

```
# Direct argument
claude -p "Explain this code"

# From stdin
echo "Explain this code" | claude -p

```

### [​](#streaming-json-input) Streaming JSON Input

A stream of messages provided via `stdin` where each message represents a user turn. This allows multiple turns of a conversation without re-launching the `claude` binary and allows providing guidance to the model while it is processing a request.
Each message is a JSON ‘User message’ object, following the same format as the output message schema. Messages are formatted using the [jsonl](https://jsonlines.org/) format where each line of input is a complete JSON object. Streaming JSON input requires `-p` and `--output-format stream-json`.

Copy

```
echo '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"Explain this code"}]}}' | claude -p --output-format=stream-json --input-format=stream-json --verbose

```

## [​](#agent-integration-examples) Agent Integration Examples

### [​](#sre-incident-response-bot) SRE Incident Response Bot

Copy

```
#!/bin/bash

# Automated incident response agent
investigate_incident() {
    local incident_description="$1"
    local severity="${2:-medium}"

    claude -p "Incident: $incident_description (Severity: $severity)" \
      --append-system-prompt "You are an SRE expert. Diagnose the issue, assess impact, and provide immediate action items." \
      --output-format json \
      --allowedTools "Bash,Read,WebSearch,mcp__datadog" \
      --mcp-config monitoring-tools.json
}

# Usage
investigate_incident "Payment API returning 500 errors" "high"

```

### [​](#automated-security-review) Automated Security Review

Copy

```
# Security audit agent for pull requests
audit_pr() {
    local pr_number="$1"

    gh pr diff "$pr_number" | claude -p \
      --append-system-prompt "You are a security engineer. Review this PR for vulnerabilities, insecure patterns, and compliance issues." \
      --output-format json \
      --allowedTools "Read,Grep,WebSearch"
}

# Usage and save to file
audit_pr 123 > security-report.json

```

### [​](#multi-turn-legal-assistant) Multi-turn Legal Assistant

Copy

```
# Legal document review with session persistence
session_id=$(claude -p "Start legal review session" --output-format json | jq -r '.session_id')

# Review contract in multiple steps
claude -p --resume "$session_id" "Review contract.pdf for liability clauses"
claude -p --resume "$session_id" "Check compliance with GDPR requirements"
claude -p --resume "$session_id" "Generate executive summary of risks"

```

## [​](#best-practices) Best Practices

* **Use JSON output format** for programmatic parsing of responses:

  Copy

  ```
  # Parse JSON response with jq
  result=$(claude -p "Generate code" --output-format json)
  code=$(echo "$result" | jq -r '.result')
  cost=$(echo "$result" | jq -r '.cost_usd')

  ```
* **Handle errors gracefully** - check exit codes and stderr:

  Copy

  ```
  if ! claude -p "$prompt" 2>error.log; then
      echo "Error occurred:" >&2
      cat error.log >&2
      exit 1
  fi

  ```
* **Use session management** for maintaining context in multi-turn conversations
* **Consider timeouts** for long-running operations:

  Copy

  ```
  timeout 300 claude -p "$complex_prompt" || echo "Timed out after 5 minutes"

  ```
* **Respect rate limits** when making multiple requests by adding delays between calls

## [​](#related-resources) Related Resources

* [CLI usage and controls](/en/docs/claude-code/cli-reference) - Complete CLI documentation
* [Common workflows](/en/docs/claude-code/common-workflows) - Step-by-step guides for common use cases

Was this page helpful?

YesNo

[Python SDK reference](/en/docs/claude-code/sdk/sdk-python)[Streaming Input](/en/docs/claude-code/sdk/streaming-vs-single-mode)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.