---
title: Add Claude Code to your IDE
source: https://docs.anthropic.com/en/docs/claude-code/ide-integrations
fetched: 2025-09-24 20:17:33
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

Configuration

Add Claude Code to your IDE

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

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [From your IDE](#from-your-ide)
* [From external terminals](#from-external-terminals)
* [Configuration](#configuration)
* [JetBrains plugin settings](#jetbrains-plugin-settings)
* [General Settings](#general-settings)
* [ESC key configuration](#esc-key-configuration)
* [Troubleshooting](#troubleshooting)
* [VS Code extension not installing](#vs-code-extension-not-installing)
* [JetBrains plugin not working](#jetbrains-plugin-not-working)
* [Security](#security)

Configuration

# Add Claude Code to your IDE

Copy page

Learn how to add Claude Code to your favorite IDE

Copy page

Claude Code works great with any Integrated Development Environment (IDE) that has a terminal. Just run `claude`, and you’re ready to go.
In addition, Claude Code provides dedicated integrations for popular IDEs, which provide features like interactive diff viewing, selection context sharing, and more. These integrations currently exist for:

* **Visual Studio Code** (including popular forks like Cursor, Windsurf, and VSCodium)
* **JetBrains IDEs** (including IntelliJ, PyCharm, Android Studio, WebStorm, PhpStorm and GoLand)

## [​](#features) Features

* **Quick launch**: Use `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open
  Claude Code directly from your editor, or click the Claude Code button in the
  UI
* **Diff viewing**: Code changes can be displayed directly in the IDE diff
  viewer instead of the terminal. You can configure this in `/config`
* **Selection context**: The current selection/tab in the IDE is automatically
  shared with Claude Code
* **File reference shortcuts**: Use `Cmd+Option+K` (Mac) or `Alt+Ctrl+K`
  (Linux/Windows) to insert file references (e.g., @File#L1-99)
* **Diagnostic sharing**: Diagnostic errors (lint, syntax, etc.) from the IDE
  are automatically shared with Claude as you work

## [​](#installation) Installation

* VS Code+
* JetBrains

To install Claude Code on VS Code and popular forks like Cursor, Windsurf, and VSCodium:

1. Open VS Code
2. Open the integrated terminal
3. Run `claude` - the extension will auto-install

## [​](#usage) Usage

### [​](#from-your-ide) From your IDE

Run `claude` from your IDE’s integrated terminal, and all features will be active.

### [​](#from-external-terminals) From external terminals

Use the `/ide` command in any external terminal to connect Claude Code to your IDE and activate all features.
If you want Claude to have access to the same files as your IDE, start Claude Code from the same directory as your IDE project root.

## [​](#configuration) Configuration

IDE integrations work with Claude Code’s configuration system:

1. Run `claude`
2. Enter the `/config` command
3. Adjust your preferences. Setting the diff tool to `auto` will enable automatic IDE detection

### [​](#jetbrains-plugin-settings) JetBrains plugin settings

You can configure Claude Code plugin settings by going to **Settings → Tools → Claude Code [Beta]**. Here are the available settings:

#### [​](#general-settings) General Settings

* **Claude command**: Specify a custom command to run Claude (e.g., `claude`, `/usr/local/bin/claude`, or `npx @anthropic/claude`) when clicking on the Claude icon
* **Suppress notification for Claude command not found**: Skip notifications about not finding the Claude command
* **Enable using Option+Enter for multi-line prompts** (macOS only): When enabled, Option+Enter inserts new lines in Claude Code prompts. Disable this if you’re experiencing issues with the Option key being captured unexpectedly (requires terminal restart)
* **Enable automatic updates**: Automatically check for and install plugin updates (applied on restart)

For WSL users: You may find it useful to set `wsl -d Ubuntu -- bash -lic "claude"` as your Claude command (replace `Ubuntu` with your WSL distribution name)

#### [​](#esc-key-configuration) ESC key configuration

If the ESC key doesn’t interrupt Claude Code operations in JetBrains terminals:

1. Go to Settings → Tools → Terminal
2. Either:
   * Uncheck “Move focus to the editor with Escape”, or
   * Click “Configure terminal keybindings” and delete the “Switch focus to Editor” shortcut
3. Apply the changes

This allows the ESC key to properly interrupt Claude Code operations.

## [​](#troubleshooting) Troubleshooting

### [​](#vs-code-extension-not-installing) VS Code extension not installing

* Ensure you’re running Claude Code from VS Code’s integrated terminal
* Ensure that the CLI corresponding to your IDE is installed:
  + For VS Code: `code` command should be available
  + For Cursor: `cursor` command should be available
  + For Windsurf: `windsurf` command should be available
  + For VSCodium: `codium` command should be available
  + If not installed, use `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
    and search for “Shell Command: Install ‘code’ command in PATH” (or the
    equivalent for your IDE)
* Check that VS Code has permission to install extensions

### [​](#jetbrains-plugin-not-working) JetBrains plugin not working

* Ensure you’re running Claude Code from the project root directory
* Check that the JetBrains plugin is enabled in the IDE settings
* Completely restart the IDE. You may need to do this multiple times
* For JetBrains Remote Development, ensure that the Claude Code plugin is
  installed in the remote host and not locally on the client

If you’re using WSL or WSL2 and the IDE is not detected, see our [WSL2 troubleshooting guide](/en/docs/claude-code/troubleshooting#jetbrains-ide-not-detected-on-wsl2) for networking configuration and firewall settings.

For additional help, refer to our
[troubleshooting guide](/en/docs/claude-code/troubleshooting).

## [​](#security) Security

When Claude Code runs in an IDE with auto-edit permissions enabled, it may be able to modify IDE configuration files that can be automatically executed by your IDE. This may increase the risk of running Claude Code in auto-edit mode and allow bypassing Claude Code’s permission prompts for bash execution. When running in an IDE, consider enabling IDE security features (such as [VS Code Restricted Mode](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust#_restricted-mode)), using manual approval mode for edits, or taking extra care to ensure Claude is only used with trusted prompts.

Was this page helpful?

YesNo

[Settings](/en/docs/claude-code/settings)[Terminal configuration](/en/docs/claude-code/terminal-config)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.