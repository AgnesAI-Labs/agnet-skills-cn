---
name: conventional-commit
name_zh: 约定式提交信息
description: >-
  Prompt and workflow for generating conventional commit messages using a
  structured XML format. Guides users to create standardized, descriptive
  commit messages in line with the Conventional Commits specification,
  including instructions, examples, and validation.
description_zh: >-
  按 Conventional Commits
  规范写提交信息：类型、范围、描述、正文与脚注分别怎么填，附示例和自检方法。适合团队要统一提交历史格式的时候。
category: development
category_name: Development
category_name_zh: 开发与代码
examples_zh:
  - 按规范写条提交信息
  - 这个提交信息格式对不对
  - 用约定式提交格式
examples:
  - Write a conventional commit message
  - Format this commit properly
  - Use the conventional commits spec
author: github
version: '1.0'
tags:
  - git
  - commit
  - convention
  - changelog
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
license: Complete terms in LICENSE.txt
---

### Instructions

```xml
	<description>This file contains a prompt template for generating conventional commit messages. It provides instructions, examples, and formatting guidelines to help users write standardized, descriptive commit messages in accordance with the Conventional Commits specification.</description>
```

### Workflow

**Follow these steps:**

1. Run `git status` to review changed files.
2. Run `git diff` or `git diff --cached` to inspect changes.
3. Stage your changes with `git add <file>`.
4. Construct your commit message using the following XML structure.
5. After generating your commit message, Copilot will automatically run the following command in your integrated terminal (no confirmation needed):

```bash
git commit -m "type(scope): description"
```

6. Just execute this prompt and Copilot will handle the commit for you in the terminal.

### Commit Message Structure

```xml
<commit-message>
	<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert</type>
	<scope>()</scope>
	<description>A short, imperative summary of the change</description>
	<body>(optional: more detailed explanation)</body>
	<footer>(optional: e.g. BREAKING CHANGE: details, or issue references)</footer>
</commit-message>
```

### Examples

```xml
<examples>
	<example>feat(parser): add ability to parse arrays</example>
	<example>fix(ui): correct button alignment</example>
	<example>docs: update README with usage instructions</example>
	<example>refactor: improve performance of data processing</example>
	<example>chore: update dependencies</example>
	<example>feat!: send email on registration (BREAKING CHANGE: email service required)</example>
</examples>
```

### Validation

```xml
<validation>
	<type>Must be one of the allowed types. See <reference>https://www.conventionalcommits.org/en/v1.0.0/#specification</reference></type>
	<scope>Optional, but recommended for clarity.</scope>
	<description>Required. Use the imperative mood (e.g., "add", not "added").</description>
	<body>Optional. Use for additional context.</body>
	<footer>Use for breaking changes or issue references.</footer>
</validation>
```

### Final Step

```xml
<final-step>
	<cmd>git commit -m "type(scope): description"</cmd>
	<note>Replace with your constructed message. Include body and footer if needed.</note>
</final-step>
```
