---
title: Claude Code overview
source: https://docs.anthropic.com/en/docs/claude-code/
fetched: 2025-09-24 20:17:09
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

Getting started

Claude Code overview

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

* [Get started in 30 seconds](#get-started-in-30-seconds)
* [What Claude Code does for you](#what-claude-code-does-for-you)
* [Why developers love Claude Code](#why-developers-love-claude-code)
* [Next steps](#next-steps)
* [Additional resources](#additional-resources)

Getting started

# Claude Code overview

Copy page

Learn about Claude Code, Anthropic’s agentic coding tool that lives in your terminal and helps you turn ideas into code faster than ever before.

Copy page

## [​](#get-started-in-30-seconds) Get started in 30 seconds

Prerequisites:

* [Node.js 18 or newer](https://nodejs.org/en/download/)
* A [Claude.ai](https://claude.ai) (recommended) or [Claude Console](https://console.anthropic.com/) account

Copy

```
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Navigate to your project
cd your-awesome-project

# Start coding with Claude
claude
# You'll be prompted to log in on first use

```

That’s it! You’re ready to start coding with Claude. [Continue with Quickstart (5 mins) →](/en/docs/claude-code/quickstart)
(Got specific setup needs or hit issues? See [advanced setup](/en/docs/claude-code/setup) or [troubleshooting](/en/docs/claude-code/troubleshooting).)

## [​](#what-claude-code-does-for-you) What Claude Code does for you

* **Build features from descriptions**: Tell Claude what you want to build in plain English. It will make a plan, write the code, and ensure it works.
* **Debug and fix issues**: Describe a bug or paste an error message. Claude Code will analyze your codebase, identify the problem, and implement a fix.
* **Navigate any codebase**: Ask anything about your team’s codebase, and get a thoughtful answer back. Claude Code maintains awareness of your entire project structure, can find up-to-date information from the web, and with [MCP](/en/docs/claude-code/mcp) can pull from external datasources like Google Drive, Figma, and Slack.
* **Automate tedious tasks**: Fix fiddly lint issues, resolve merge conflicts, and write release notes. Do all this in a single command from your developer machines, or automatically in CI.

## [​](#why-developers-love-claude-code) Why developers love Claude Code

* **Works in your terminal**: Not another chat window. Not another IDE. Claude Code meets you where you already work, with the tools you already love.
* **Takes action**: Claude Code can directly edit files, run commands, and create commits. Need more? [MCP](/en/docs/claude-code/mcp) lets Claude read your design docs in Google Drive, update your tickets in Jira, or use *your* custom developer tooling.
* **Unix philosophy**: Claude Code is composable and scriptable. `tail -f app.log | claude -p "Slack me if you see any anomalies appear in this log stream"` *works*. Your CI can run `claude -p "If there are new text strings, translate them into French and raise a PR for @lang-fr-team to review"`.
* **Enterprise-ready**: Use the Claude API, or host on AWS or GCP. Enterprise-grade [security](/en/docs/claude-code/security), [privacy](/en/docs/claude-code/data-usage), and [compliance](https://trust.anthropic.com/) is built-in.

## [​](#next-steps) Next steps

[## Quickstart

See Claude Code in action with practical examples](/en/docs/claude-code/quickstart)[## Common workflows

Step-by-step guides for common workflows](/en/docs/claude-code/common-workflows)[## Troubleshooting

Solutions for common issues with Claude Code](/en/docs/claude-code/troubleshooting)[## IDE setup

Add Claude Code to your IDE](/en/docs/claude-code/ide-integrations)

## [​](#additional-resources) Additional resources

[## Host on AWS or GCP

Configure Claude Code with Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/third-party-integrations)[## Settings

Customize Claude Code for your workflow](/en/docs/claude-code/settings)[## Commands

Learn about CLI commands and controls](/en/docs/claude-code/cli-reference)[## Reference implementation

Clone our development container reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer)[## Security

Discover Claude Code’s safeguards and best practices for safe usage](/en/docs/claude-code/security)[## Privacy and data usage

Understand how Claude Code handles your data](/en/docs/claude-code/data-usage)

Was this page helpful?

YesNo

[Quickstart](/en/docs/claude-code/quickstart)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.