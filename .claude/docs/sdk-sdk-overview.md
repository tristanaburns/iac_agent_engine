---
title: Overview
source: https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-overview
fetched: 2025-09-24 20:17:30
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

Overview

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

* [SDK Options](#sdk-options)
* [Why use the Claude Code SDK?](#why-use-the-claude-code-sdk%3F)
* [What can you build with the SDK?](#what-can-you-build-with-the-sdk%3F)
* [Core Concepts](#core-concepts)
* [Authentication](#authentication)
* [Full Claude Code Feature Support](#full-claude-code-feature-support)
* [System Prompts](#system-prompts)
* [Tool Permissions](#tool-permissions)
* [Model Context Protocol (MCP)](#model-context-protocol-mcp)
* [Related Resources](#related-resources)

Claude Code SDK

# Overview

Copy page

Build custom AI agents with the Claude Code SDK

Copy page

## [​](#sdk-options) SDK Options

The Claude Code SDK is available in multiple forms to suit different use cases:

* **[Headless Mode](/en/docs/claude-code/sdk/sdk-headless)** - For CLI scripts and automation
* **[TypeScript SDK](/en/docs/claude-code/sdk/sdk-typescript)** - For Node.js and web applications
* **[Python SDK](/en/docs/claude-code/sdk/sdk-python)** - For Python applications and data science
* **[Streaming vs Single Mode](/en/docs/claude-code/sdk/streaming-vs-single-mode)** - Understanding input modes and best practices

## [​](#why-use-the-claude-code-sdk%3F) Why use the Claude Code SDK?

Built on top of the agent harness that powers Claude Code, the Claude Code SDK provides all the building blocks you need to build production-ready agents.
Taking advantage of the work we’ve done on Claude Code including:

* **Context Management**: Automatic compaction and context management to ensure your agent doesn’t run out of context.
* **Rich tool ecosystem**: File operations, code execution, web search, and MCP extensibility
* **Advanced permissions**: Fine-grained control over agent capabilities
* **Production essentials**: Built-in error handling, session management, and monitoring
* **Optimized Claude integration**: Automatic prompt caching and performance optimizations

## [​](#what-can-you-build-with-the-sdk%3F) What can you build with the SDK?

Here are some example agent types you can create:
**Coding agents:**

* SRE agents that diagnose and fix production issues
* Security review bots that audit code for vulnerabilities
* Oncall engineering assistants that triage incidents
* Code review agents that enforce style and best practices

**Business agents:**

* Legal assistants that review contracts and compliance
* Finance advisors that analyze reports and forecasts
* Customer support agents that resolve technical issues
* Content creation assistants for marketing teams

## [​](#core-concepts) Core Concepts

### [​](#authentication) Authentication

For basic authentication, retrieve an Claude API key from the [Claude Console](https://console.anthropic.com/) and set the `ANTHROPIC_API_KEY` environment variable.
The SDK also supports authentication via third-party API providers:

* **Amazon Bedrock**: Set `CLAUDE_CODE_USE_BEDROCK=1` environment variable and configure AWS credentials
* **Google Vertex AI**: Set `CLAUDE_CODE_USE_VERTEX=1` environment variable and configure Google Cloud credentials

For detailed configuration instructions for third-party providers, see the [Amazon Bedrock](/en/docs/claude-code/amazon-bedrock) and [Google Vertex AI](/en/docs/claude-code/google-vertex-ai) documentation.

### [​](#full-claude-code-feature-support) Full Claude Code Feature Support

The SDK provides access to all the default features available in Claude Code, leveraging the same file system-based configuration:

* **Subagents**: Launch specialized agents stored as Markdown files in `./.claude/agents/`
* **Hooks**: Execute custom commands configured in `./.claude/settings.json` that respond to tool events
* **Slash Commands**: Use custom commands defined as Markdown files in `./.claude/commands/`
* **Memory (CLAUDE.md)**: Maintain project context through `CLAUDE.md` files that provide persistent instructions and context

These features work identically to their Claude Code counterparts by reading from the same file system locations.

### [​](#system-prompts) System Prompts

System prompts define your agent’s role, expertise, and behavior. This is where you specify what kind of agent you’re building.

### [​](#tool-permissions) Tool Permissions

Control which tools your agent can use with fine-grained permissions:

* `allowedTools` - Explicitly allow specific tools
* `disallowedTools` - Block specific tools
* `permissionMode` - Set overall permission strategy

### [​](#model-context-protocol-mcp) Model Context Protocol (MCP)

Extend your agents with custom tools and integrations through MCP servers. This allows you to connect to databases, APIs, and other external services.

## [​](#related-resources) Related Resources

* [CLI Reference](/en/docs/claude-code/cli-reference) - Complete CLI documentation
* [GitHub Actions Integration](/en/docs/claude-code/github-actions) - Automate your GitHub workflow
* [MCP Documentation](/en/docs/claude-code/mcp) - Extend Claude with custom tools
* [Common Workflows](/en/docs/claude-code/common-workflows) - Step-by-step guides
* [Troubleshooting](/en/docs/claude-code/troubleshooting) - Common issues and solutions

Was this page helpful?

YesNo

[Troubleshooting](/en/docs/claude-code/troubleshooting)[TypeScript SDK reference](/en/docs/claude-code/sdk/sdk-typescript)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.