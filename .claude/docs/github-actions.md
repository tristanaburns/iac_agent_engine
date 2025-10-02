---
title: Claude Code GitHub Actions
source: https://docs.anthropic.com/en/docs/claude-code/github-actions
fetched: 2025-09-24 20:17:34
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

Claude Code GitHub Actions

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

* [Why use Claude Code GitHub Actions?](#why-use-claude-code-github-actions%3F)
* [What can Claude do?](#what-can-claude-do%3F)
* [Claude Code Action](#claude-code-action)
* [Setup](#setup)
* [Quick setup](#quick-setup)
* [Manual setup](#manual-setup)
* [Upgrading from Beta](#upgrading-from-beta)
* [Essential changes](#essential-changes)
* [Breaking Changes Reference](#breaking-changes-reference)
* [Before and After Example](#before-and-after-example)
* [Example use cases](#example-use-cases)
* [Basic workflow](#basic-workflow)
* [Using slash commands](#using-slash-commands)
* [Custom automation with prompts](#custom-automation-with-prompts)
* [Common use cases](#common-use-cases)
* [Best practices](#best-practices)
* [CLAUDE.md configuration](#claude-md-configuration)
* [Security considerations](#security-considerations)
* [Optimizing performance](#optimizing-performance)
* [CI costs](#ci-costs)
* [Configuration examples](#configuration-examples)
* [Using with AWS Bedrock & Google Vertex AI](#using-with-aws-bedrock-%26-google-vertex-ai)
* [Prerequisites](#prerequisites)
* [For Google Cloud Vertex AI:](#for-google-cloud-vertex-ai%3A)
* [For AWS Bedrock:](#for-aws-bedrock%3A)
* [For Claude API (Direct):](#for-claude-api-direct-%3A)
* [For Google Cloud Vertex AI](#for-google-cloud-vertex-ai)
* [For AWS Bedrock](#for-aws-bedrock)
* [Troubleshooting](#troubleshooting)
* [Claude not responding to @claude commands](#claude-not-responding-to-%40claude-commands)
* [CI not running on Claude’s commits](#ci-not-running-on-claude%E2%80%99s-commits)
* [Authentication errors](#authentication-errors)
* [Advanced configuration](#advanced-configuration)
* [Action parameters](#action-parameters)
* [Using claude\_args](#using-claude-args)
* [Alternative integration methods](#alternative-integration-methods)
* [Customizing Claude’s behavior](#customizing-claude%E2%80%99s-behavior)

Build with Claude Code

# Claude Code GitHub Actions

Copy page

Learn about integrating Claude Code into your development workflow with Claude Code GitHub Actions

Copy page

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project’s standards.

Claude Code GitHub Actions is built on top of the [Claude Code
SDK](/en/docs/claude-code/sdk), which enables programmatic integration of
Claude Code into your applications. You can use the SDK to build custom
automation workflows beyond GitHub Actions.

## [​](#why-use-claude-code-github-actions%3F) Why use Claude Code GitHub Actions?

* **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
* **Automated code implementation**: Turn issues into working code with a single command
* **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
* **Simple setup**: Get started in minutes with our installer and API key
* **Secure by default**: Your code stays on Github’s runners

## [​](#what-can-claude-do%3F) What can Claude do?

Claude Code provides a powerful GitHub Action that transforms how you work with code:

### [​](#claude-code-action) Claude Code Action

This GitHub Action allows you to run Claude Code within your GitHub Actions workflows. You can use this to build any custom workflow on top of Claude Code.
[View repository →](https://github.com/anthropics/claude-code-action)

## [​](#setup) Setup

## [​](#quick-setup) Quick setup

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`.
This command will guide you through setting up the GitHub app and required secrets.

* You must be a repository admin to install the GitHub app and add secrets -
  This quickstart method is only available for direct Claude API users. If
  you’re using AWS Bedrock or Google Vertex AI, please see the [Using with AWS
  Bedrock & Google Vertex AI](#using-with-aws-bedrock-%26-google-vertex-ai)
  section.

## [​](#manual-setup) Manual setup

If the `/install-github-app` command fails or you prefer manual setup, please follow these manual setup instructions:

1. **Install the Claude GitHub app** to your repository: <https://github.com/apps/claude>
2. **Add ANTHROPIC\_API\_KEY** to your repository secrets ([Learn how to use secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions))
3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository’s `.github/workflows/`

After completing either the quickstart or manual setup, test the action by
tagging `@claude` in an issue or PR comment!

## [​](#upgrading-from-beta) Upgrading from Beta

Claude Code GitHub Actions v1.0 introduces breaking changes that require updating your workflow files in order to upgrade to v1.0 from the beta version.

If you’re currently using the beta version of Claude Code GitHub Actions, we recommend that you update your workflows to use the GA version. The new version simplifies configuration while adding powerful new features like automatic mode detection.

### [​](#essential-changes) Essential changes

All beta users must make these changes to their workflow files in order to upgrade:

1. **Update the action version**: Change `@beta` to `@v1`
2. **Remove mode configuration**: Delete `mode: "tag"` or `mode: "agent"` (now auto-detected)
3. **Update prompt inputs**: Replace `direct_prompt` with `prompt`
4. **Move CLI options**: Convert `max_turns`, `model`, `custom_instructions`, etc. to `claude_args`

### [​](#breaking-changes-reference) Breaking Changes Reference

| Old Beta Input | New v1.0 Input |
| --- | --- |
| `mode` | *(Removed - auto-detected)* |
| `direct_prompt` | `prompt` |
| `override_prompt` | `prompt` with GitHub variables |
| `custom_instructions` | `claude_args: --system-prompt` |
| `max_turns` | `claude_args: --max-turns` |
| `model` | `claude_args: --model` |
| `allowed_tools` | `claude_args: --allowedTools` |
| `disallowed_tools` | `claude_args: --disallowedTools` |
| `claude_env` | `settings` JSON format |

### [​](#before-and-after-example) Before and After Example

**Beta version:**

Copy

```
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag"
    direct_prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    custom_instructions: "Follow our coding standards"
    max_turns: "10"
    model: "claude-3-5-sonnet-20241022"

```

**GA version (v1.0):**

Copy

```
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-20250514

```

The action now automatically detects whether to run in interactive mode (responds to `@claude` mentions) or automation mode (runs immediately with a prompt) based on your configuration.

## [​](#example-use-cases) Example use cases

Claude Code GitHub Actions can help you with a variety of tasks. The [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) contains ready-to-use workflows for different scenarios.

### [​](#basic-workflow) Basic workflow

Copy

```
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # Responds to @claude mentions in comments

```

### [​](#using-slash-commands) Using slash commands

Copy

```
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/review"
          claude_args: "--max-turns 5"

```

### [​](#custom-automation-with-prompts) Custom automation with prompts

Copy

```
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model claude-opus-4-1-20250805"

```

### [​](#common-use-cases) Common use cases

In issue or PR comments:

Copy

```
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component

```

Claude will automatically analyze the context and respond appropriately.

## [​](#best-practices) Best practices

### [​](#claude-md-configuration) CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns. This file guides Claude’s understanding of your project standards.

### [​](#security-considerations) Security considerations

Never commit API keys directly to your repository!

Always use GitHub Secrets for API keys:

* Add your API key as a repository secret named `ANTHROPIC_API_KEY`
* Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
* Limit action permissions to only what’s necessary
* Review Claude’s suggestions before merging

Always use GitHub Secrets (e.g., `${{ secrets.ANTHROPIC_API_KEY }}`) rather than hardcoding API keys directly in your workflow files.

### [​](#optimizing-performance) Optimizing performance

Use issue templates to provide context, keep your `CLAUDE.md` concise and focused, and configure appropriate timeouts for your workflows.

### [​](#ci-costs) CI costs

When using Claude Code GitHub Actions, be aware of the associated costs:
**GitHub Actions costs:**

* Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes
* See [GitHub’s billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) for detailed pricing and minute limits

**API costs:**

* Each Claude interaction consumes API tokens based on the length of prompts and responses
* Token usage varies by task complexity and codebase size
* See [Claude’s pricing page](https://claude.com/platform/api) for current token rates

**Cost optimization tips:**

* Use specific `@claude` commands to reduce unnecessary API calls
* Configure appropriate `--max-turns` in `claude_args` to prevent excessive iterations
* Set workflow-level timeouts to avoid runaway jobs
* Consider using GitHub’s concurrency controls to limit parallel runs

## [​](#configuration-examples) Configuration examples

The Claude Code Action v1 simplifies configuration with unified parameters:

Copy

```
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Your instructions here" # Optional
    claude_args: "--max-turns 5" # Optional CLI arguments

```

Key features:

* **Unified prompt interface** - Use `prompt` for all instructions
* **Slash commands** - Pre-built prompts like `/review` or `/fix`
* **CLI passthrough** - Any Claude Code CLI argument via `claude_args`
* **Flexible triggers** - Works with any GitHub event

Visit the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) for complete workflow files.

When responding to issue or PR comments, Claude automatically responds to @claude mentions. For other events, use the `prompt` parameter to provide instructions.

## [​](#using-with-aws-bedrock-%26-google-vertex-ai) Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can use Claude Code GitHub Actions with your own cloud infrastructure. This approach gives you control over data residency and billing while maintaining the same functionality.

### [​](#prerequisites) Prerequisites

Before setting up Claude Code GitHub Actions with cloud providers, you need:

#### [​](#for-google-cloud-vertex-ai%3A) For Google Cloud Vertex AI:

1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

#### [​](#for-aws-bedrock%3A) For AWS Bedrock:

1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

1

Create a custom GitHub App (Recommended for 3P Providers)

For best control and security when using 3P providers like Vertex AI or Bedrock, we recommend creating your own GitHub App:

1. Go to <https://github.com/settings/apps/new>
2. Fill in the basic information:
   * **GitHub App name**: Choose a unique name (e.g., “YourOrg Claude Assistant”)
   * **Homepage URL**: Your organization’s website or the repository URL
3. Configure the app settings:
   * **Webhooks**: Uncheck “Active” (not needed for this integration)
4. Set the required permissions:
   * **Repository permissions**:
     + Contents: Read & Write
     + Issues: Read & Write
     + Pull requests: Read & Write
5. Click “Create GitHub App”
6. After creation, click “Generate a private key” and save the downloaded `.pem` file
7. Note your App ID from the app settings page
8. Install the app to your repository:
   * From your app’s settings page, click “Install App” in the left sidebar
   * Select your account or organization
   * Choose “Only select repositories” and select the specific repository
   * Click “Install”
9. Add the private key as a secret to your repository:
   * Go to your repository’s Settings → Secrets and variables → Actions
   * Create a new secret named `APP_PRIVATE_KEY` with the contents of the `.pem` file
10. Add the App ID as a secret:

* Create a new secret named `APP_ID` with your GitHub App’s ID

This app will be used with the [actions/create-github-app-token](https://github.com/actions/create-github-app-token) action to generate authentication tokens in your workflows.

**Alternative for Claude API or if you don’t want to setup your own Github app**: Use the official Anthropic app:

1. Install from: <https://github.com/apps/claude>
2. No additional configuration needed for authentication

2

Configure cloud provider authentication

Choose your cloud provider and set up secure authentication:

AWS Bedrock

**Configure AWS to allow GitHub Actions to authenticate securely without storing credentials.**
> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup**:

1. **Enable Amazon Bedrock**:
   * Request access to Claude models in Amazon Bedrock
   * For cross-region models, request access in all required regions
2. **Set up GitHub OIDC Identity Provider**:
   * Provider URL: `https://token.actions.githubusercontent.com`
   * Audience: `sts.amazonaws.com`
3. **Create IAM Role for GitHub Actions**:
   * Trusted entity type: Web identity
   * Identity provider: `token.actions.githubusercontent.com`
   * Permissions: `AmazonBedrockFullAccess` policy
   * Configure trust policy for your specific repository

**Required Values**:After setup, you’ll need:

* **AWS\_ROLE\_TO\_ASSUME**: The ARN of the IAM role you created

OIDC is more secure than using static AWS access keys because credentials are temporary and automatically rotated.

See [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) for detailed OIDC setup instructions.

Google Vertex AI

**Configure Google Cloud to allow GitHub Actions to authenticate securely without storing credentials.**
> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup**:

1. **Enable APIs** in your Google Cloud project:
   * IAM Credentials API
   * Security Token Service (STS) API
   * Vertex AI API
2. **Create Workload Identity Federation resources**:
   * Create a Workload Identity Pool
   * Add a GitHub OIDC provider with:
     + Issuer: `https://token.actions.githubusercontent.com`
     + Attribute mappings for repository and owner
     + **Security recommendation**: Use repository-specific attribute conditions
3. **Create a Service Account**:
   * Grant only `Vertex AI User` role
   * **Security recommendation**: Create a dedicated service account per repository
4. **Configure IAM bindings**:
   * Allow the Workload Identity Pool to impersonate the service account
   * **Security recommendation**: Use repository-specific principal sets

**Required Values**:After setup, you’ll need:

* **GCP\_WORKLOAD\_IDENTITY\_PROVIDER**: The full provider resource name
* **GCP\_SERVICE\_ACCOUNT**: The service account email address

Workload Identity Federation eliminates the need for downloadable service account keys, improving security.

For detailed setup instructions, consult the [Google Cloud Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation).

3

Add Required Secrets

Add the following secrets to your repository (Settings → Secrets and variables → Actions):

#### [​](#for-claude-api-direct-%3A) For Claude API (Direct):

1. **For API Authentication**:
   * `ANTHROPIC_API_KEY`: Your Claude API key from [console.anthropic.com](https://console.anthropic.com)
2. **For GitHub App (if using your own app)**:
   * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

#### [​](#for-google-cloud-vertex-ai) For Google Cloud Vertex AI

1. **For GCP Authentication**:
   * `GCP_WORKLOAD_IDENTITY_PROVIDER`
   * `GCP_SERVICE_ACCOUNT`
2. **For GitHub App (if using your own app)**:
   * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

#### [​](#for-aws-bedrock) For AWS Bedrock

1. **For AWS Authentication**:
   * `AWS_ROLE_TO_ASSUME`
2. **For GitHub App (if using your own app)**:
   * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

4

Create workflow files

Create GitHub Actions workflow files that integrate with your cloud provider. The examples below show complete configurations for both AWS Bedrock and Google Vertex AI:

AWS Bedrock workflow

**Prerequisites:**

* AWS Bedrock access enabled with Claude model permissions
* GitHub configured as an OIDC identity provider in AWS
* IAM role with Bedrock permissions that trusts GitHub Actions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `AWS_ROLE_TO_ASSUME` | ARN of the IAM role for Bedrock access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

Copy

```
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    env:
      AWS_REGION: us-west-2
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: us-west-2

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          use_bedrock: "true"
          claude_args: '--model us.anthropic.claude-sonnet-4-20250514-v1:0 --max-turns 10'

```

The model ID format for Bedrock includes the region prefix (e.g., `us.anthropic.claude...`) and version suffix.

Google Vertex AI workflow

**Prerequisites:**

* Vertex AI API enabled in your GCP project
* Workload Identity Federation configured for GitHub
* Service account with Vertex AI permissions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload identity provider resource name |
| `GCP_SERVICE_ACCOUNT` | Service account email with Vertex AI access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

Copy

```
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          trigger_phrase: "@claude"
          use_vertex: "true"
          claude_args: '--model claude-sonnet-4@20250514 --max-turns 10'
        env:
          ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
          CLOUD_ML_REGION: us-east5
          VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5

```

The project ID is automatically retrieved from the Google Cloud authentication step, so you don’t need to hardcode it.

## [​](#troubleshooting) Troubleshooting

### [​](#claude-not-responding-to-%40claude-commands) Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

### [​](#ci-not-running-on-claude%E2%80%99s-commits) CI not running on Claude’s commits

Ensure you’re using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

### [​](#authentication-errors) Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.

## [​](#advanced-configuration) Advanced configuration

### [​](#action-parameters) Action parameters

The Claude Code Action v1 uses a simplified configuration:

| Parameter | Description | Required |
| --- | --- | --- |
| `prompt` | Instructions for Claude (text or slash command) | No\* |
| `claude_args` | CLI arguments passed to Claude Code | No |
| `anthropic_api_key` | Claude API key | Yes\*\* |
| `github_token` | GitHub token for API access | No |
| `trigger_phrase` | Custom trigger phrase (default: “@claude”) | No |
| `use_bedrock` | Use AWS Bedrock instead of Claude API | No |
| `use_vertex` | Use Google Vertex AI instead of Claude API | No |

\*Prompt is optional - when omitted for issue/PR comments, Claude responds to trigger phrase  
\*\*Required for direct Claude API, not for Bedrock/Vertex

#### [​](#using-claude-args) Using claude\_args

The `claude_args` parameter accepts any Claude Code CLI arguments:

Copy

```
claude_args: "--max-turns 5 --model claude-sonnet-4-20250514 --mcp-config /path/to/config.json"

```

Common arguments:

* `--max-turns`: Maximum conversation turns (default: 10)
* `--model`: Model to use (e.g., `claude-sonnet-4-20250514`)
* `--mcp-config`: Path to MCP configuration
* `--allowed-tools`: Comma-separated list of allowed tools
* `--debug`: Enable debug output

### [​](#alternative-integration-methods) Alternative integration methods

While the `/install-github-app` command is the recommended approach, you can also:

* **Custom GitHub App**: For organizations needing branded usernames or custom authentication flows. Create your own GitHub App with required permissions (contents, issues, pull requests) and use the actions/create-github-app-token action to generate tokens in your workflows.
* **Manual GitHub Actions**: Direct workflow configuration for maximum flexibility
* **MCP Configuration**: Dynamic loading of Model Context Protocol servers

See the [Claude Code Action repository](https://github.com/anthropics/claude-code-action) for detailed documentation.

### [​](#customizing-claude%E2%80%99s-behavior) Customizing Claude’s behavior

You can configure Claude’s behavior in two ways:

1. **CLAUDE.md**: Define coding standards, review criteria, and project-specific rules in a `CLAUDE.md` file at the root of your repository. Claude will follow these guidelines when creating PRs and responding to requests. Check out our [Memory documentation](/en/docs/claude-code/memory) for more details.
2. **Custom prompts**: Use the `prompt` parameter in the workflow file to provide workflow-specific instructions. This allows you to customize Claude’s behavior for different workflows or tasks.

Claude will follow these guidelines when creating PRs and responding to requests.

Was this page helpful?

YesNo

[Hooks](/en/docs/claude-code/hooks-guide)[GitLab CI/CD](/en/docs/claude-code/gitlab-ci-cd)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.