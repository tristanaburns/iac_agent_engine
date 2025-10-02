---
title: Manage costs effectively
source: https://docs.anthropic.com/en/docs/claude-code/costs
fetched: 2025-09-24 20:17:36
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

Manage costs effectively

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

* [Track your costs](#track-your-costs)
* [Using the /cost command](#using-the-%2Fcost-command)
* [Additional tracking options](#additional-tracking-options)
* [Managing costs for teams](#managing-costs-for-teams)
* [Rate limit recommendations](#rate-limit-recommendations)
* [Reduce token usage](#reduce-token-usage)
* [Background token usage](#background-token-usage)
* [Tracking version changes and updates](#tracking-version-changes-and-updates)
* [Current version information](#current-version-information)
* [Understanding changes in Claude Code behavior](#understanding-changes-in-claude-code-behavior)
* [When cost reporting changes](#when-cost-reporting-changes)

Administration

# Manage costs effectively

Copy page

Learn how to track and optimize token usage and costs when using Claude Code.

Copy page

Claude Code consumes tokens for each interaction. The average cost is $6 per developer per day, with daily costs remaining below $12 for 90% of users.
For team usage, Claude Code charges by API token consumption. On average, Claude Code costs ~$100-200/developer per month with Sonnet 4 though there is large variance depending on how many instances users are running and whether they’re using it in automation.

## [​](#track-your-costs) Track your costs

### [​](#using-the-%2Fcost-command) Using the `/cost` command

The `/cost` command is not intended for Claude Max and Pro subscribers.

The `/cost` command provides detailed token usage statistics for your current session:

Copy

```
Total cost:            $0.55
Total duration (API):  6m 19.7s
Total duration (wall): 6h 33m 10.2s
Total code changes:    0 lines added, 0 lines removed

```

### [​](#additional-tracking-options) Additional tracking options

Check [historical usage](https://support.claude.com/en/articles/9534590-cost-and-usage-reporting-in-console) in the Claude Console (requires Admin or Billing role) and set [workspace spend limits](https://support.claude.com/en/articles/9796807-creating-and-managing-workspaces) for the Claude Code workspace (requires Admin role).

When you first authenticate Claude Code with your Claude Console account, a workspace called “Claude Code” is automatically created for you. This workspace provides centralized cost tracking and management for all Claude Code usage in your organization.

## [​](#managing-costs-for-teams) Managing costs for teams

When using Claude API, you can limit the total Claude Code workspace spend. To configure, [follow these instructions](https://support.claude.com/en/articles/9796807-creating-and-managing-workspaces). Admins can view cost and usage reporting by [following these instructions](https://support.claude.com/en/articles/9534590-cost-and-usage-reporting-in-console).
On Bedrock and Vertex, Claude Code does not send metrics from your cloud. In order to get cost metrics, several large enterprises reported using [LiteLLM](/en/docs/claude-code/bedrock-vertex-proxies#litellm), which is an open-source tool that helps companies [track spend by key](https://docs.litellm.ai/docs/proxy/virtual_keys#tracking-spend). This project is unaffiliated with Anthropic and we have not audited its security.

### [​](#rate-limit-recommendations) Rate limit recommendations

When setting up Claude Code for teams, consider these Token Per Minute (TPM) and Request Per Minute (RPM) per-user recommendations based on your organization size:

| Team size | TPM per user | RPM per user |
| --- | --- | --- |
| 1-5 users | 200k-300k | 5-7 |
| 5-20 users | 100k-150k | 2.5-3.5 |
| 20-50 users | 50k-75k | 1.25-1.75 |
| 50-100 users | 25k-35k | 0.62-0.87 |
| 100-500 users | 15k-20k | 0.37-0.47 |
| 500+ users | 10k-15k | 0.25-0.35 |

For example, if you have 200 users, you might request 20k TPM for each user, or 4 million total TPM (200\*20,000 = 4 million).
The TPM per user decreases as team size grows because we expect fewer users to use Claude Code concurrently in larger organizations. These rate limits apply at the organization level, not per individual user, which means individual users can temporarily consume more than their calculated share when others aren’t actively using the service.

If you anticipate scenarios with unusually high concurrent usage (such as live training sessions with large groups), you may need higher TPM allocations per user.

## [​](#reduce-token-usage) Reduce token usage

* **Compact conversations:**
  + Claude uses auto-compact by default when context exceeds 95% capacity
  + Toggle auto-compact: Run `/config` and navigate to “Auto-compact enabled”
  + Use `/compact` manually when context gets large
  + Add custom instructions: `/compact Focus on code samples and API usage`
  + Customize compaction by adding to CLAUDE.md:

    Copy

    ```
    # Summary instructions

    When you are using compact, please focus on test output and code changes

    ```
* **Write specific queries:** Avoid vague requests that trigger unnecessary scanning
* **Break down complex tasks:** Split large tasks into focused interactions
* **Clear history between tasks:** Use `/clear` to reset context

Costs can vary significantly based on:

* Size of codebase being analyzed
* Complexity of queries
* Number of files being searched or modified
* Length of conversation history
* Frequency of compacting conversations

## [​](#background-token-usage) Background token usage

Claude Code uses tokens for some background functionality even when idle:

* **Conversation summarization**: Background jobs that summarize previous conversations for the `claude --resume` feature
* **Command processing**: Some commands like `/cost` may generate requests to check status

These background processes consume a small amount of tokens (typically under $0.04 per session) even without active interaction.

## [​](#tracking-version-changes-and-updates) Tracking version changes and updates

### [​](#current-version-information) Current version information

To check your current Claude Code version and installation details:

Copy

```
claude doctor

```

This command shows your version, installation type, and system information.

### [​](#understanding-changes-in-claude-code-behavior) Understanding changes in Claude Code behavior

Claude Code regularly receives updates that may change how features work, including cost reporting:

* **Version tracking**: Use `claude doctor` to see your current version
* **Behavior changes**: Features like `/cost` may display information differently across versions
* **Documentation access**: Claude always has access to the latest documentation, which can help explain current feature behavior

### [​](#when-cost-reporting-changes) When cost reporting changes

If you notice changes in how costs are displayed (such as the `/cost` command showing different information):

1. **Verify your version**: Run `claude doctor` to confirm your current version
2. **Consult documentation**: Ask Claude directly about current feature behavior, as it has access to up-to-date documentation
3. **Contact support**: For specific billing questions, contact Anthropic support through your Console account

For team deployments, we recommend starting with a small pilot group to
establish usage patterns before wider rollout.

Was this page helpful?

YesNo

[Monitoring](/en/docs/claude-code/monitoring-usage)[Analytics](/en/docs/claude-code/analytics)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.