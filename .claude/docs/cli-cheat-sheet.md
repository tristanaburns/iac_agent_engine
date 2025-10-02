# Claude Code CLI Cheat Sheet

---

## Quick Start Commands

```bash
claude --dangerously-skip-permissions
claude --dangerously-skip-permissions --continue
claude --dangerously-skip-permissions --resume
```

### Additional Parameters

| Flag        | Description                | Example           |
| :------- | :---------------------------- | :---------------------------------------------------------- |
| `--add-dir`                      | Add additional working directories for Claude to access (validates each path exists as a directory)            | `claude --add-dir ../apps ../lib`      |
| `--allowedTools`                 | A list of tools that should be allowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings)    | `"Bash(git log:*)" "Bash(git diff:*)" "Read"`               |
| `--disallowedTools`              | A list of tools that should be disallowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings) | `"Bash(git log:*)" "Bash(git diff:*)" "Edit"`               |
| `--print`, `-p`                  | Print response without interactive mode (see [SDK documentation](/en/docs/claude-code/sdk) for programmatic usage details)          | `claude -p "query"`                    |
| `--output-format`                | Specify output format for print mode (options: `text`, `json`, `stream-json`)             | `claude -p "query" --output-format json`                    |
| `--input-format`                 | Specify input format for print mode (options: `text`, `stream-json`)                      | `claude -p --output-format json --input-format stream-json` |
| `--verbose`                      | Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes)                  | `claude --verbose`                     |
| `--max-turns`                    | Limit the number of agentic turns in non-interactive mode            | `claude -p --max-turns 3 "query"`      |
| `--model`                        | Sets the model for the current session with an alias for the latest model (`sonnet` or `opus`) or a model's full name               | `claude --model claude-sonnet-4-20250514`                   |
| `--permission-mode`              | Begin in a specified [permission mode](iam#permission-modes)         | `claude --permission-mode plan`        |
| `--permission-prompt-tool`       | Specify an MCP tool to handle permission prompts in non-interactive mode                  | `claude -p --permission-prompt-tool mcp_auth_tool "query"`  |
| `--resume`                       | Resume a specific session by ID, or by choosing in interactive mode                       | `claude --resume abc123 "query"`       |
| `--continue`                     | Load the most recent conversation in the current directory           | `claude --continue`                    |
| `--dangerously-skip-permissions` | Skip permission prompts (use with caution)      | `claude --dangerously-skip-permissions`                     |

> **Tip:** The `--output-format json` flag is particularly useful for scripting and automation, allowing you to parse Claude's responses programmatically.

## Essential commands

Here are the most important commands for daily use:

| Command            | What it does                      | Example       |
| ------------------ | --------------------------------- | ---------------------------------- |
| `claude`           | Start interactive mode            | `claude`      |
| `claude "task"`    | Run a one-time task               | `claude "fix the build error"`     |
| `claude -p "query"` | Run one-off query, then exit      | `claude -p "explain this function"` |
| `claude --continue`         | Continue most recent conversation | `claude --continue`                         |
| `claude --resume`         | Resume a previous conversation    | `claude --resume`                         |
| `claude commit`    | Create a Git commit               | `claude commit`                    |
| `/clear`           | Clear conversation history        | `> /clear`                         |
| `/help`            | Show available commands           | `> /help`                          |
| `exit` or Ctrl+C   | Exit Claude Code                  | `> exit`      |

See the [CLI reference](/en/docs/claude-code/cli-reference) for a complete list of commands.

---

## Common workflows

Tips:

- Create project-specific subagents in `.claude/agents/` for team sharing
- Use descriptive `description` fields to enable automatic delegation

---

## Work with tests

- Ask for tests that cover edge cases and error conditions
- Request both unit and integration tests when appropriate
- Have Claude explain the testing strategy

---

## Create pull requests

- Ask Claude directly to make a PR for you
- Review Claude's generated PR before submitting
- Ask Claude to highlight potential risks or considerations

---

## Handle documentation

Suppose you need to add or update documentation for your code.

- Find functions without proper JSDoc comments in the auth module
- Add JSDoc comments to the undocumented functions in auth.js
- Improve the generated documentation with more context and examples
- Check if the documentation follows our project standards
- Specify the documentation style you want (JSDoc, docstrings, etc.)
- Ask for examples in the documentation
- Request documentation for public APIs, interfaces, and complex logic

---

## Work with images

You can use any of these methods:

1. Drag and drop an image into the Claude Code window
2. Copy an image and paste it into the CLI with ctrl+v (Do not use cmd+v)
3. Provide an image path to Claude. E.g., "Analyze this image: /path/to/your/image.png"

**Example prompts:**

- What does this image show?
- Describe the UI elements in this screenshot
- Are there any problematic elements in this diagram?
- Here's a screenshot of the error. What's causing it?
- This is our current database schema. How should we modify it for the new feature?
- Generate CSS to match this design mockup
- What HTML structure would recreate this component?

**Tips:**

- Use images when text descriptions would be unclear or cumbersome
- Include screenshots of errors, UI designs, or diagrams for better context
- You can work with multiple images in a conversation
- Image analysis works with diagrams, screenshots, mockups, and more

---

## Reference files and directories

Use @ to quickly include files or directories without waiting for Claude to read them.

### Reference a single file

- Explain the logic in @src/utils/auth.js

This includes the full content of the file in the conversation.

### Reference a directory

- What's the structure of @src/components?

This provides a directory listing with file information.

### Reference MCP resources

- Show me the data from @github:repos/owner/repo/issues

This fetches data from connected MCP servers using the format @server:resource. See [MCP resources](/en/docs/claude-code/mcp#use-mcp-resources) for details.

**Tips:**

- File paths can be relative or absolute
- @ file references add CLAUDE.md in the file's directory and parent directories to context
- Directory references show file listings, not contents
- You can reference multiple files in a single message (e.g., "@file1.js and @file2.js")

---

## Use extended thinking

Suppose you're working on complex architectural decisions, challenging bugs, or planning multi-step implementations that require deep reasoning.

### Provide context and ask Claude to think

- I need to implement a new authentication system using OAuth2 for our API. Think deeply about the best approach for implementing this in our codebase.

Claude will gather relevant information from your codebase and use extended thinking, which will be visible in the interface.

### Refine the thinking with follow-up prompts

- think about potential security vulnerabilities in this approach
- think harder about edge cases we should handle

**Tips to get the most value out of extended thinking:**

Extended thinking is most valuable for complex tasks such as:

- Planning complex architectural changes
- Debugging intricate issues
- Creating implementation plans for new features
- Understanding complex codebases
- Evaluating tradeoffs between different approaches

The way you prompt for thinking results in varying levels of thinking depth:

- "think" triggers basic extended thinking
- intensifying phrases such as "think more", "think a lot", "think harder", or "think longer" triggers deeper thinking

For more extended thinking prompting tips, see [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).

**Note:** Claude will display its thinking process as italic gray text above the response.

---

## Resume previous conversations

Suppose you've been working on a task with Claude Code and need to continue where you left off in a later session.

Claude Code provides two options for resuming previous conversations:

- `--continue` to automatically continue the most recent conversation
- `--resume` to display a conversation picker

### Continue the most recent conversation

```bash
claude --continue
```

This immediately resumes your most recent conversation without any prompts.

### Continue in non-interactive mode

```bash
claude --continue --print "Continue with my task"
```

Use `--print` with `--continue` to resume the most recent conversation in non-interactive mode, perfect for scripts or automation.

### Show conversation picker

```bash
claude --resume
```

This displays an interactive conversation selector showing:

- Conversation start time
- Initial prompt or conversation summary
- Message count

Use arrow keys to navigate and press Enter to select a conversation.

**Tips:**

- Conversation history is stored locally on your machine
- Use `--continue` for quick access to your most recent conversation
- Use `--resume` when you need to select a specific past conversation
- When resuming, you'll see the entire conversation history before continuing
- The resumed conversation starts with the same model and configuration as the original

**How it works:**

1. **Conversation Storage**: All conversations are automatically saved locally with their full message history
2. **Message Deserialization**: When resuming, the entire message history is restored to maintain context
3. **Tool State**: Tool usage and results from the previous conversation are preserved
4. **Context Restoration**: The conversation resumes with all previous context intact

**Examples:**

```bash
# Continue most recent conversation
claude --continue

# Continue most recent conversation with a specific prompt
claude --continue --print "Show me our progress"

# Show conversation picker
claude --resume

# Continue most recent conversation in non-interactive mode
claude --continue --print "Run the tests again"
```

---

## Run parallel Claude Code sessions with Git worktrees

Suppose you need to work on multiple tasks simultaneously with complete code isolation between Claude Code instances.

### Understand Git worktrees

Git worktrees allow you to check out multiple branches from the same repository into separate directories. Each worktree has its own working directory with isolated files, while sharing the same Git history. Learn more in the [official Git worktree documentation](https://git-scm.com/docs/git-worktree).

### Create a new worktree

```bash
# Create a new worktree with a new branch 
git worktree add ../project-feature-a feature-a

# Or create a worktree with an existing branch
git worktree add ../project-bugfix bugfix-123
```

This creates a new directory with a separate working copy of your repository.

### Run Claude Code in each worktree

```bash
# Navigate to your worktree 
cd ../project-feature-a

# Run Claude Code in this isolated environment
claude
```

### Run Claude in another worktree

```bash
cd ../project-bugfix
claude
```

### Manage your worktrees

```bash
# List all worktrees
git worktree list

# Remove a worktree when done
git worktree remove ../project-feature-a
```

**Tips:**

- Each worktree has its own independent file state, making it perfect for parallel Claude Code sessions
- Changes made in one worktree won't affect others, preventing Claude instances from interfering with each other
- All worktrees share the same Git history and remote connections
- For long-running tasks, you can have Claude working in one worktree while you continue development in another
- Use descriptive directory names to easily identify which task each worktree is for
- Remember to initialize your development environment in each new worktree according to your project's setup. Depending on your stack, this might include:
  - JavaScript projects: Running dependency installation (`npm install`, `yarn`)
  - Python projects: Setting up virtual environments or installing with package managers
  - Other languages: Following your project's standard setup process

---

## Use Claude as a unix-style utility

### Add Claude to your verification process

Suppose you want to use Claude Code as a linter or code reviewer.

**Add Claude to your build script:**

```json
// package.json
{
    ...
    "scripts": {
        ...
        "lint:claude": "claude -p 'you are a linter. please look at the changes vs. main and report any issues related to typos. report the filename and line number on one line, and a description of the issue on the second line. do not return any other text.'"
    }
}
```

> **Tips:**
> 
> - Use Claude for automated code review in your CI/CD pipeline
> - Customize the prompt to check for specific issues relevant to your project
> - Consider creating multiple scripts for different types of verification

### Pipe in, pipe out

Suppose you want to pipe data into Claude, and get back data in a structured format.

**Pipe data through Claude:**

```bash
cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt
```

> **Tips:**
> 
> - Use pipes to integrate Claude into existing shell scripts
> - Combine with other Unix tools for powerful workflows
> - Consider using `--output-format` for structured output

### Control output format

Suppose you need Claude's output in a specific format, especially when integrating Claude Code into scripts or other tools.

#### Use text format (default)

```bash
cat data.txt | claude -p 'summarize this data' --output-format text > summary.txt
```

This outputs just Claude's plain text response (default behavior).

#### Use JSON format

```bash
cat code.py | claude -p 'analyze this code for bugs' --output-format json > analysis.json
```

This outputs a JSON array of messages with metadata including cost and duration.

#### Use streaming JSON format

```bash
cat log.txt | claude -p 'parse this log file for errors' --output-format stream-json
```

This outputs a series of JSON objects in real-time as Claude processes the request. Each message is a valid JSON object, but the entire output is not valid JSON if concatenated.

**Tips:**

- Use `--output-format text` for simple integrations where you just need Claude's response
- Use `--output-format json` when you need the full conversation log
- Use `--output-format stream-json` for real-time output of each conversation turn

---

## Custom Commands

Command names are derived from the filename (e.g., `optimize.md` becomes `/optimize`)
- You can organize commands in subdirectories (e.g., `.claude/commands/frontend/component.md` creates `/component` with "(project:frontend)" shown in the description)

### Add command arguments with $ARGUMENTS

Create a command file with the $ARGUMENTS placeholder:

```bash
echo 'Find and fix issue #$ARGUMENTS. Follow these steps: 1. Understand the issue described in the ticket 2. Locate the relevant code in our codebase 3. Implement a solution that addresses the root cause 4. Add appropriate tests 5. Prepare a concise PR description' > .claude/commands/fix-issue.md
```

**Tips:**

- The $ARGUMENTS placeholder is replaced with any text that follows the command
- You can position $ARGUMENTS anywhere in your command template
- Other useful applications: generating test cases for specific functions, creating documentation for components, reviewing code in particular files, or translating content to specified languages







review this file.... C:\github_development\ai-agents\.claude\settings.json .. 
the purpose of this file will be to distribue to all projects... 
the intent of config is to allow you to run at maximum output, coding mode, with full autonomy. 
update the settings.json file to be universal across all projects


the way i will exectue this will be to use the sdk via this file C:\github_development\ai-agents\.claude\claude_code_client_sdk.py ... 
i want you to enhance the script to allow:
stream json output logs to the ./.claude/logs dir
--verbose mode
--system-prompt defined in a markdown file in the ./.claude/system-prompts/ dir (there will be many variations) 
--append-system-prompt defined as an array of markdown files to append to the system prompt defined in the ./.claude/system-prompts .. OR ./.claude/agents dirs
--mcp-config defined in a json file in the ./.claude/mcp-configs/ dir (there will be many variations)
--print mode with a defined array of markdown files in the ./.claude/commands dir and sub dirs (there will be many variations)

