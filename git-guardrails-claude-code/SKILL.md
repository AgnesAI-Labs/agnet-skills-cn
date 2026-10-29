---
name: git-guardrails-claude-code
name_zh: Git 危险命令拦截
description: >-
  Set up Claude Code hooks to block dangerous git commands (push, reset
  --hard, clean, branch -D, etc.) before they execute. Use when user wants to
  prevent destructive git operations, add git safety hooks, or block git
  push/reset in Claude Code.
description_zh: >-
  装一层 Git 防护，在 push、reset --hard、clean、branch -D
  这类会丢东西的命令执行前先拦下来。适合担心自动化流程误操作仓库、想加一道确认闸的时候。原技能面向 Claude Code 的 hooks
  机制，其他环境需相应调整。
category: development
category_name: Development
category_name_zh: 开发与代码
examples_zh:
  - 帮我拦住危险的 git 命令
  - 加个 git 安全钩子
  - 别让它直接 push 和重置
examples:
  - Block dangerous git commands
  - Add git safety hooks
  - Prevent push and hard reset
author: mattpocock
version: '1.0'
tags:
  - git
  - safety
  - hooks
  - guardrails
installation_notes: >-
  The skill installs from the Skills Marketplace; the hook configuration it
  writes targets Claude Code hooks, so adjust the target file when using
  another harness.
installation_notes_zh: >-
  该技能从桌面端技能市场直接安装；它写入的钩子配置面向 Claude Code 的 hooks 机制，其他环境需要改写入目标。
license: Complete terms in LICENSE.txt
---

# Setup Git Guardrails

Sets up a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them.

## What Gets Blocked

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, Claude sees a message telling it that it does not have authority to access these commands.

## Steps

### 1. Ask scope

Ask the user: install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?

### 2. Copy the hook script

The bundled script is at: [scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

Copy it to the target location based on scope:

- **Project**: `.claude/hooks/block-dangerous-git.sh`
- **Global**: `~/.claude/hooks/block-dangerous-git.sh`

Make it executable with `chmod +x`.

### 3. Add hook to settings

Add to the appropriate settings file:

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

If the settings file already exists, merge the hook into the existing `hooks.PreToolUse` array. Don't overwrite other settings.

### 4. Ask about customization

Ask if user wants to add or remove any patterns from the blocked list. Edit the copied script accordingly.

### 5. Verify

Run a quick test:

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

Should exit with code 2 and print a BLOCKED message to stderr.
