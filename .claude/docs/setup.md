---
title: Set up Claude Code
source: https://docs.anthropic.com/en/docs/claude-code/setup
fetched: 2025-09-24 20:17:12
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

Administration

Set up Claude Code

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

* [System requirements](#system-requirements)
* [Additional dependencies](#additional-dependencies)
* [Standard installation](#standard-installation)
* [Windows setup](#windows-setup)
* [Alternative installation methods](#alternative-installation-methods)
* [Global npm installation](#global-npm-installation)
* [Native binary installation (Beta)](#native-binary-installation-beta)
* [Local installation](#local-installation)
* [Running on AWS or GCP](#running-on-aws-or-gcp)
* [Update Claude Code](#update-claude-code)
* [Auto updates](#auto-updates)
* [Update manually](#update-manually)

Administration

# Set up Claude Code

Copy page

Install, authenticate, and start using Claude Code on your development machine.

Copy page

## [​](#system-requirements) System requirements

* **Operating Systems**: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows 10+ (with WSL 1, WSL 2, or Git for Windows)
* **Hardware**: 4GB+ RAM
* **Software**: [Node.js 18+](https://nodejs.org/en/download)
* **Network**: Internet connection required for authentication and AI processing
* **Shell**: Works best in Bash, Zsh or Fish
* **Location**: [Anthropic supported countries](https://www.anthropic.com/supported-countries)

### [​](#additional-dependencies) Additional dependencies

* **ripgrep**: Usually included with Claude Code. If search functionality fails, see [search troubleshooting](/en/docs/claude-code/troubleshooting#search-and-discovery-issues).

## [​](#standard-installation) Standard installation

To install Claude Code, run the following command:

Copy

```
npm install -g @anthropic-ai/claude-code

```

Do NOT use `sudo npm install -g` as this can lead to permission issues and security risks.
If you encounter permission errors, see [configure Claude Code](/en/docs/claude-code/troubleshooting#linux-permission-issues) for recommended solutions.

Some users may be automatically migrated to an improved installation method.
Run `claude doctor` after installation to check your installation type.

After the installation process completes, navigate to your project and start Claude Code:

Copy

```
cd your-awesome-project
claude

```

Claude Code offers the following authentication options:

1. **Claude Console**: The default option. Connect through the Claude Console and complete the OAuth process. Requires active billing at [console.anthropic.com](https://console.anthropic.com). A “Claude Code” workspace will be automatically created for usage tracking and cost management.
2. **Claude App (with Pro or Max plan)**: Subscribe to Claude’s [Pro or Max plan](https://claude.com/pricing) for a unified subscription that includes both Claude Code and the web interface. Get more value at the same price point while managing your account in one place. Log in with your Claude.ai account. During launch, choose the option that matches your subscription type.
3. **Enterprise platforms**: Configure Claude Code to use [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/third-party-integrations) for enterprise deployments with your existing cloud infrastructure.

Claude Code securely stores your credentials. See [Credential Management](/en/docs/claude-code/iam#credential-management) for details.

## [​](#windows-setup) Windows setup

**Option 1: Claude Code within WSL**

* Both WSL 1 and WSL 2 are supported

**Option 2: Claude Code on native Windows with Git Bash**

* Requires [Git for Windows](https://git-scm.com/downloads/win)
* For portable Git installations, specify the path to your `bash.exe`:

  Copy

  ```
  $env:CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"

  ```

## [​](#alternative-installation-methods) Alternative installation methods

Claude Code offers multiple installation methods to suit different environments.
If you encounter any issues during installation, consult the [troubleshooting guide](/en/docs/claude-code/troubleshooting#linux-permission-issues).

Run `claude doctor` after installation to check your installation type and version.

### [​](#global-npm-installation) Global npm installation

Traditional method shown in the [install steps above](#install-and-authenticate)

### [​](#native-binary-installation-beta) Native binary installation (Beta)

If you have an existing installation of Claude Code, use `claude install` to start the native binary installation.
For a fresh install, run the following command:
**macOS, Linux, WSL:**

Copy

```
# Install stable version (default)
curl -fsSL https://claude.ai/install.sh | bash

# Install latest version
curl -fsSL https://claude.ai/install.sh | bash -s latest

# Install specific version number
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58

```

**Alpine Linux and other musl/uClibc-based distributions**: The native build requires you to install `libgcc`, `libstdc++`, and `ripgrep`. Install (Alpine: `apk add libgcc libstdc++ ripgrep`) and set `USE_BUILTIN_RIPGREP=0`.

**Windows PowerShell:**

Copy

```
# Install stable version (default)
irm https://claude.ai/install.ps1 | iex

# Install latest version
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) latest

# Install specific version number
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) 1.0.58


```

**Windows CMD:**

Copy

```
REM Install stable version (default)
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

REM Install latest version
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd latest && del install.cmd

REM Install specific version number
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd 1.0.58 && del install.cmd

```

The native Claude Code installer is supported on macOS, Linux, and Windows.

Make sure that you remove any outdated aliases or symlinks.
Once your installation is complete, run `claude doctor` to verify the installation.

### [​](#local-installation) Local installation

* After global install via npm, use `claude migrate-installer` to move to local
* Avoids autoupdater npm permission issues
* Some users may be automatically migrated to this method

## [​](#running-on-aws-or-gcp) Running on AWS or GCP

By default, Claude Code uses the Claude API.
For details on running Claude Code on AWS or GCP, see [third-party integrations](/en/docs/claude-code/third-party-integrations).

## [​](#update-claude-code) Update Claude Code

### [​](#auto-updates) Auto updates

Claude Code automatically keeps itself up to date to ensure you have the latest features and security fixes.

* **Update checks**: Performed on startup and periodically while running
* **Update process**: Downloads and installs automatically in the background
* **Notifications**: You’ll see a notification when updates are installed
* **Applying updates**: Updates take effect the next time you start Claude Code

**Disable auto-updates:**
Set the `DISABLE_AUTOUPDATER` environment variable in your shell or [settings.json file](/en/docs/claude-code/settings):

Copy

```
export DISABLE_AUTOUPDATER=1

```

### [​](#update-manually) Update manually

Copy

```
claude update

```

Was this page helpful?

YesNo

[Development containers](/en/docs/claude-code/devcontainer)[Identity and Access Management](/en/docs/claude-code/iam)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.