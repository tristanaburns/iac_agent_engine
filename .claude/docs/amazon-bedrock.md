---
title: Claude Code on Amazon Bedrock
source: https://docs.anthropic.com/en/docs/claude-code/amazon-bedrock
fetched: 2025-09-24 20:17:37
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

Deployment

Claude Code on Amazon Bedrock

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

* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [1. Enable model access](#1-enable-model-access)
* [2. Configure AWS credentials](#2-configure-aws-credentials)
* [Advanced credential configuration](#advanced-credential-configuration)
* [3. Configure Claude Code](#3-configure-claude-code)
* [4. Model configuration](#4-model-configuration)
* [5. Output token configuration](#5-output-token-configuration)
* [IAM configuration](#iam-configuration)
* [Troubleshooting](#troubleshooting)
* [Additional resources](#additional-resources)

Deployment

# Claude Code on Amazon Bedrock

Copy page

Learn about configuring Claude Code through Amazon Bedrock, including setup, IAM configuration, and troubleshooting.

Copy page

## [​](#prerequisites) Prerequisites

Before configuring Claude Code with Bedrock, ensure you have:

* An AWS account with Bedrock access enabled
* Access to desired Claude models (e.g., Claude Sonnet 4) in Bedrock
* AWS CLI installed and configured (optional - only needed if you don’t have another mechanism for getting credentials)
* Appropriate IAM permissions

## [​](#setup) Setup

### [​](#1-enable-model-access) 1. Enable model access

First, ensure you have access to the required Claude models in your AWS account:

1. Navigate to the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/)
2. Go to **Model access** in the left navigation
3. Request access to desired Claude models (e.g., Claude Sonnet 4)
4. Wait for approval (usually instant for most regions)

### [​](#2-configure-aws-credentials) 2. Configure AWS credentials

Claude Code uses the default AWS SDK credential chain. Set up your credentials using one of these methods:
**Option A: AWS CLI configuration**

Copy

```
aws configure

```

**Option B: Environment variables (access key)**

Copy

```
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token

```

**Option C: Environment variables (SSO profile)**

Copy

```
aws sso login --profile=<your-profile-name>

export AWS_PROFILE=your-profile-name

```

**Option D: Bedrock API keys**

Copy

```
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key

```

Bedrock API keys provide a simpler authentication method without needing full AWS credentials. [Learn more about Bedrock API keys](https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/).

#### [​](#advanced-credential-configuration) Advanced credential configuration

Claude Code supports automatic credential refresh for AWS SSO and corporate identity providers. Add these settings to your Claude Code settings file (see [Settings](/en/docs/claude-code/settings) for file locations).
When Claude Code detects that your AWS credentials are expired (either locally based on their timestamp or when Bedrock returns a credential error), it will automatically run your configured `awsAuthRefresh` and/or `awsCredentialExport` commands to obtain new credentials before retrying the request.

##### Example configuration

Copy

```
{
  "awsAuthRefresh": "aws sso login --profile myprofile",
  "env": {
    "AWS_PROFILE": "myprofile"
  }
}

```

##### Configuration settings explained

**`awsAuthRefresh`**: Use this for commands that modify the `.aws` directory (e.g., updating credentials, SSO cache, or config files). Output is shown to the user (but user input is not supported), making it suitable for browser-based authentication flows where the CLI displays a code to enter in the browser.
**`awsCredentialExport`**: Only use this if you cannot modify `.aws` and must directly return credentials. Output is captured silently (not shown to the user). The command must output JSON in this format:

Copy

```
{
  "Credentials": {
    "AccessKeyId": "value",
    "SecretAccessKey": "value",
    "SessionToken": "value"
  }
}

```

### [​](#3-configure-claude-code) 3. Configure Claude Code

Set the following environment variables to enable Bedrock:

Copy

```
# Enable Bedrock integration
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1  # or your preferred region

# Optional: Override the region for the small/fast model (Haiku)
export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=us-west-2

```

When enabling Bedrock for Claude Code, keep the following in mind:

* `AWS_REGION` is a required environment variable. Claude Code does not read from the `.aws` config file for this setting.
* When using Bedrock, the `/login` and `/logout` commands are disabled since authentication is handled through AWS credentials.
* You can use settings files for environment variables like `AWS_PROFILE` that you don’t want to leak to other processes. See [Settings](/en/docs/claude-code/settings) for more information.

### [​](#4-model-configuration) 4. Model configuration

Claude Code uses these default models for Bedrock:

| Model type | Default value |
| --- | --- |
| Primary model | `us.anthropic.claude-3-7-sonnet-20250219-v1:0` |
| Small/fast model | `us.anthropic.claude-3-5-haiku-20241022-v1:0` |

To customize models, use one of these methods:

Copy

```
# Using inference profile ID
export ANTHROPIC_MODEL='us.anthropic.claude-opus-4-1-20250805-v1:0'
export ANTHROPIC_SMALL_FAST_MODEL='us.anthropic.claude-3-5-haiku-20241022-v1:0'

# Using application inference profile ARN
export ANTHROPIC_MODEL='arn:aws:bedrock:us-east-2:your-account-id:application-inference-profile/your-model-id'

# Optional: Disable prompt caching if needed
export DISABLE_PROMPT_CACHING=1

```

[Prompt caching](/en/docs/build-with-claude/prompt-caching) may not be available in all regions

### [​](#5-output-token-configuration) 5. Output token configuration

When using Claude Code with Amazon Bedrock, we recommend the following token settings:

Copy

```
# Recommended output token settings for Bedrock
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
export MAX_THINKING_TOKENS=1024

```

**Why these values:**

* **`CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096`**: Bedrock’s burndown throttling logic sets a minimum of 4096 tokens as the max\_token penalty. Setting this lower won’t reduce costs but may cut off long tool uses, causing the Claude Code agent loop to fail persistently. Claude Code typically uses less than 4096 output tokens without extended thinking, but may need this headroom for tasks involving significant file creation or Write tool usage.
* **`MAX_THINKING_TOKENS=1024`**: This provides space for extended thinking without cutting off tool use responses, while still maintaining focused reasoning chains. This balance helps prevent trajectory changes that aren’t always helpful for coding tasks specifically.

## [​](#iam-configuration) IAM configuration

Create an IAM policy with the required permissions for Claude Code:

Copy

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*"
      ]
    }
  ]
}

```

For more restrictive permissions, you can limit the Resource to specific inference profile ARNs.
For details, see [Bedrock IAM documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html).

We recommend creating a dedicated AWS account for Claude Code to simplify cost tracking and access control.

## [​](#troubleshooting) Troubleshooting

If you encounter region issues:

* Check model availability: `aws bedrock list-inference-profiles --region your-region`
* Switch to a supported region: `export AWS_REGION=us-east-1`
* Consider using inference profiles for cross-region access

If you receive an error “on-demand throughput isn’t supported”:

* Specify the model as an [inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID

Claude Code uses the Bedrock [Invoke API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html) and does not support the Converse API.

## [​](#additional-resources) Additional resources

* [Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
* [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
* [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)
* [Claude Code on Amazon Bedrock: Quick Setup Guide](https://community.aws/content/2tXkZKrZzlrlu0KfH8gST5Dkppq/claude-code-on-amazon-bedrock-quick-setup-guide)- [Claude Code Monitoring Implementation (Bedrock)](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)

Was this page helpful?

YesNo

[Overview](/en/docs/claude-code/third-party-integrations)[Google Vertex AI](/en/docs/claude-code/google-vertex-ai)

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Assistant

Responses are generated using AI and may contain mistakes.