---
title: Troubleshooting
source: https://docs.anthropic.com/en/docs/claude-code/troubleshooting
fetched: 2025-09-24 20:17:13
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

Troubleshooting

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

* [Common installation issues](#common-installation-issues)
* [Windows installation issues: errors in WSL](#windows-installation-issues%3A-errors-in-wsl)
* [Linux and Mac installation issues: permission or command not found errors](#linux-and-mac-installation-issues%3A-permission-or-command-not-found-errors)
* [Recommended solution: Native Claude Code installation](#recommended-solution%3A-native-claude-code-installation)
* [Alternative solution: Migrate to local installation](#alternative-solution%3A-migrate-to-local-installation)
* [Permissions and authentication](#permissions-and-authentication)
* [Repeated permission prompts](#repeated-permission-prompts)
* [Authentication issues](#authentication-issues)
* [Performance and stability](#performance-and-stability)
* [High CPU or memory usage](#high-cpu-or-memory-usage)
* [Command hangs or freezes](#command-hangs-or-freezes)
* [Search and discovery issues](#search-and-discovery-issues)
* [Slow or incomplete search results on WSL](#slow-or-incomplete-search-results-on-wsl)
* [IDE integration issues](#ide-integration-issues)
* [JetBrains IDE not detected on WSL2](#jetbrains-ide-not-detected-on-wsl2)
* [WSL2 networking modes](#wsl2-networking-modes)
* [Reporting Windows IDE integration issues (both native and WSL)](#reporting-windows-ide-integration-issues-both-native-and-wsl)
* [ESC key not working in JetBrains (IntelliJ, PyCharm, etc.) terminals](#esc-key-not-working-in-jetbrains-intellij%2C-pycharm%2C-etc-terminals)
* [Markdown formatting issues](#markdown-formatting-issues)
* [Missing language tags in code blocks](#missing-language-tags-in-code-blocks)
* [Inconsistent spacing and formatting](#inconsistent-spacing-and-formatting)
* [Best practices for markdown generation](#best-practices-for-markdown-generation)
* [Getting more help](#getting-more-help)

Build with Claude Code

# Troubleshooting

Copy page

Discover solutions to common issues with Claude Code installation and usage.

Copy page

## [​](#common-installation-issues) Common installation issues

### [​](#windows-installation-issues%3A-errors-in-wsl) Windows installation issues: errors in WSL

You might encounter the following issues in WSL:
**OS/platform detection issues**: If you receive an error during installation, WSL may be using Windows `npm`. Try:

* Run `npm config set os linux` before installation
* Install with `npm install -g @anthropic-ai/claude-code --force --no-os-check` (Do NOT use `sudo`)

**Node not found errors**: If you see `exec: node: not found` when running `claude`, your WSL environment may be using a Windows installation of Node.js. You can confirm this with `which npm` and `which node`, which should point to Linux paths starting with `/usr/` rather than `/mnt/c/`. To fix this, try installing Node via your Linux distribution’s package manager or via [`nvm`](https://github.com/nvm-sh/nvm).
**nvm version conflicts**: If you have nvm installed in both WSL and Windows, you may experience version conflicts when switching Node versions in WSL. This happens because WSL imports the Windows PATH by default, causing Windows nvm/npm to take priority over the WSL installation.
You can identify this issue by:

* Running `which npm` and `which node` - if they point to Windows paths (starting with `/mnt/c/`), Windows versions are being used
* Experiencing broken functionality after switching Node versions with nvm in WSL

To resolve this issue, fix your Linux PATH to ensure the Linux node/npm versions take priority:
**Primary solution: Ensure nvm is properly loaded in your shell**
The most common cause is that nvm isn’t loaded in non-interactive shells. Add the following to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

Copy

```
# Load nvm if it exists
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

```

Or run directly in your current session:

Copy

```
source ~/.nvm/nvm.sh

```

**Alternative: Adjust PATH order**
If nvm is properly loaded but Windows paths still take priority, you can explicitly prepend your Linux paths to PATH in your shell configuration:

Copy

```
export PATH="$HOME/.nvm/versions/node/$(node -v)/bin:$PATH"

```

Avoid disabling Windows PATH importing (`appendWindowsPath = false`) as this breaks the ability to easily call Windows executables from WSL. Similarly, avoid uninstalling Node.js from Windows if you use it for Windows development.

### [​](#linux-and-mac-installation-issues%3A-permission-or-command-not-found-errors) Linux and Mac installation issues: permission or command not found errors

When installing Claude Code with npm, `PATH` problems may prevent access to `claude`.
You may also encounter permission errors if your npm global prefix is not user writable (eg. `/usr`, or `/usr/local`).

#### [​](#recommended-solution%3A-native-claude-code-installation) Recommended solution: Native Claude Code installation

Claude Code has a native installation that doesn’t depend on npm or Node.js.

The native Claude Code installer is currently in beta.

Use the following command to run the native installer.
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

This command installs the appropriate build of Claude Code for your operating system and architecture and adds a symlink to the installation at `~/.local/bin/claude`.

Make sure that you have the installation directory in your system PATH.

#### [​](#alternative-solution%3A-migrate-to-local-installation) Alternative solution: Migrate to local installation

Alternatively, if Claude Code will run, you can migrate to a local installation:

Copy

```
claude migrate-installer

```

This moves Claude Code to `~/.claude/local/` and sets up an alias in your shell configuration. No `sudo` is required for future updates.
After migration, restart your shell, and then verify your installation:
On macOS/Linux/WSL:

Copy

```
which claude  # Should show an alias to ~/.claude/local/claude

```

On Windows:

Copy

```
where claude  # Should show path to claude executable

```

Verify installation:

Copy

```
claude doctor # Check installation health

```

## [​](#permissions-and-authentication) Permissions and authentication

### [​](#repeated-permission-prompts) Repeated permission prompts

If you find yourself repeatedly approving the same commands, you can allow specific tools
to run without approval using the `/permissions` command. See [Permissions docs](/en/docs/claude-code/iam#configuring-permissions).

### [​](#authentication-issues) Authentication issues

If you’re experiencing authentication problems:

1. Run `/logout` to sign out completely
2. Close Claude Code
3. Restart with `claude` and complete the authentication process again

If problems persist, try:

Copy

```
rm -rf ~/.config/claude-code/auth.json
claude

```

This removes your stored authentication information and forces a clean login.

## [​](#performance-and-stability) Performance and stability

### [​](#high-cpu-or-memory-usage) High CPU or memory usage

Claude Code is designed to work with most development environments, but may consume significant resources when processing large codebases. If you’re experiencing performance issues:

1. Use `/compact` regularly to reduce context size
2. Close and restart Claude Code between major tasks
3. Consider adding large build directories to your `.gitignore` file

### [​](#command-hangs-or-freezes) Command hangs or freezes

If Claude Code seems unresponsive:

1. Press Ctrl+C to attempt to cancel the current operation
2. If unresponsive, you may need to close the terminal and restart

### [​](#search-and-discovery-issues) Search and discovery issues

If Search tool, `@file` mentions, custom agents, and custom slash commands aren’t working, install system `ripgrep`:

Copy

```
# macOS (Homebrew)  
brew install ripgrep

# Windows (winget)
winget install BurntSushi.ripgrep.MSVC

# Ubuntu/Debian
sudo apt install ripgrep

# Alpine Linux
apk add ripgrep

# Arch Linux
pacman -S ripgrep

```

Then set `USE_BUILTIN_RIPGREP=0` in your [environment](/en/docs/claude-code/settings#environment-variables).

### [​](#slow-or-incomplete-search-results-on-wsl) Slow or incomplete search results on WSL

Disk read performance penalties when [working across file systems on WSL](https://learn.microsoft.com/en-us/windows/wsl/filesystems) may result in fewer-than-expected matches (but not a complete lack of search functionality) when using Claude Code on WSL.

`/doctor` will show Search as OK in this case.

**Solutions:**

1. **Submit more specific searches**: Reduce the number of files searched by specifying directories or file types: “Search for JWT validation logic in the auth-service package” or “Find use of md5 hash in JS files”.
2. **Move project to Linux filesystem**: If possible, ensure your project is located on the Linux filesystem (`/home/`) rather than the Windows filesystem (`/mnt/c/`).
3. **Use native Windows instead**: Consider running Claude Code natively on Windows instead of through WSL, for better file system performance.

## [​](#ide-integration-issues) IDE integration issues

### [​](#jetbrains-ide-not-detected-on-wsl2) JetBrains IDE not detected on WSL2

If you’re using Claude Code on WSL2 with JetBrains IDEs and getting “No available IDEs detected” errors, this is likely due to WSL2’s networking configuration or Windows Firewall blocking the connection.

#### [​](#wsl2-networking-modes) WSL2 networking modes

WSL2 uses NAT networking by default, which can prevent IDE detection. You have two options:
**Option 1: Configure Windows Firewall** (recommended)

1. Find your WSL2 IP address:

   Copy

   ```
   wsl hostname -I
   # Example output: 172.21.123.456

   ```
2. Open PowerShell as Administrator and create a firewall rule:

   Copy

   ```
   New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16

   ```

   (Adjust the IP range based on your WSL2 subnet from step 1)
3. Restart both your IDE and Claude Code

**Option 2: Switch to mirrored networking**
Add to `.wslconfig` in your Windows user directory:

Copy

```
[wsl2]
networkingMode=mirrored

```

Then restart WSL with `wsl --shutdown` from PowerShell.

These networking issues only affect WSL2. WSL1 uses the host’s network directly and doesn’t require these configurations.

For additional JetBrains configuration tips, see our [IDE integration guide](/en/docs/claude-code/ide-integrations#jetbrains-plugin-settings).

### [​](#reporting-windows-ide-integration-issues-both-native-and-wsl) Reporting Windows IDE integration issues (both native and WSL)

If you’re experiencing IDE integration problems on Windows, please [create an issue](https://github.com/anthropics/claude-code/issues) with the following information: whether you are native (git bash), or WSL1/WSL2, WSL networking mode (NAT or mirrored), IDE name/version, Claude Code extension/plugin version, and shell type (bash/zsh/etc)

### [​](#esc-key-not-working-in-jetbrains-intellij%2C-pycharm%2C-etc-terminals) ESC key not working in JetBrains (IntelliJ, PyCharm, etc.) terminals

If you’re using Claude Code in JetBrains terminals and the ESC key doesn’t interrupt the agent as expected, this is likely due to a keybinding clash with JetBrains’ default shortcuts.
To fix this issue:

1. Go to Settings → Tools → Terminal
2. Either:
   * Uncheck “Move focus to the editor with Escape”, or
   * Click “Configure terminal keybindings” and delete the “Switch focus to Editor” shortcut
3. Apply the changes

This allows the ESC key to properly interrupt Claude Code operations.

## [​](#markdown-formatting-issues) Markdown formatting issues

Claude Code sometimes generates markdown files with missing language tags on code fences, which can affect syntax highlighting and readability in GitHub, editors, and documentation tools.

### [​](#missing-language-tags-in-code-blocks) Missing language tags in code blocks

If you notice code blocks like this in generated markdown:

Copy

```
```
function example() {
  return "hello";
}
```

```

Instead of properly tagged blocks like:

Copy

```
```javascript
function example() {
  return "hello";
}
```

```

**Solutions:**

1. **Ask Claude to add language tags**: Simply request “Please add appropriate language tags to all code blocks in this markdown file.”
2. **Use post-processing hooks**: Set up automatic formatting hooks to detect and add missing language tags. See the [markdown formatting hook example](/en/docs/claude-code/hooks-guide#markdown-formatting-hook) for implementation details.
3. **Manual verification**: After generating markdown files, review them for proper code block formatting and request corrections if needed.

### [​](#inconsistent-spacing-and-formatting) Inconsistent spacing and formatting

If generated markdown has excessive blank lines or inconsistent spacing:
**Solutions:**

1. **Request formatting corrections**: Ask Claude to “Fix spacing and formatting issues in this markdown file.”
2. **Use formatting tools**: Set up hooks to run markdown formatters like `prettier` or custom formatting scripts on generated markdown files.
3. **Specify formatting preferences**: Include formatting requirements in your prompts or project [memory](/en/docs/claude-code/memory) files.

### [​](#best-practices-for-markdown-generation) Best practices for markdown generation

To minimize formatting issues:

* **Be explicit in requests**: Ask for “properly formatted markdown with language-tagged code blocks”
* **Use project conventions**: Document your preferred markdown style in [CLAUDE.md](/en/docs/claude-code/memory)
* **Set up validation hooks**: Use post-processing hooks to automatically verify and fix common formatting issues

## [​](#getting-more-help) Getting more help

If you’re experiencing issues not covered here:

1. Use the `/bug` command within Claude Code to report problems directly to Anthropic
2. Check the [GitHub repository](https://github.com/anthropics/claude-code) for known issues
3. Run `/doctor` to check the health of your Claude Code installation
4. Ask Claude directly about its capabilities and features - Claude has built-in access to its documentation

Was this page helpful?

YesNo

[Model Context Protocol (MCP)](/en/docs/claude-code/mcp)[Overview](/en/docs/claude-code/sdk/sdk-overview)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.