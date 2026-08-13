---
name: code-review
description: Comprehensive code review checklist for pull requests
description_zh: 面向 pull request 的全面代码审查清单
author: agnes
version: "1.0"
tags:
  - development
  - quality
  - review
installation_notes: This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no additional dependencies.
installation_notes_zh: 该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

# Code Review Checklist

When reviewing code, check each of these areas:

## Functionality

- [ ] Code does what the PR description claims
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

## Code Quality

- [ ] Follows project style guide
- [ ] No hardcoded values that should be configurable
- [ ] Functions are focused and well-named

## Testing

- [ ] New functionality has tests
- [ ] Tests are meaningful, not just for coverage
- [ ] Existing tests still pass

## Security

- [ ] No credentials or secrets in code
- [ ] User input is validated
- [ ] SQL queries are parameterized

## Performance

- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] No unnecessary loops or iterations

## Documentation

- [ ] Public APIs are documented
- [ ] Complex logic has comments explaining "why"
- [ ] README updated if needed
