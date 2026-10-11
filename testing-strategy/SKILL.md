---
name: testing-strategy
description: Guidelines for writing effective tests in this project
description_zh: 在本项目中编写有效测试的指南
category: development
category_name: Development
category_name_zh: 开发与代码
examples_zh:
  - 帮我规划这个功能的测试策略
  - 这些改动该测哪些场景
  - 补一份测试计划
examples:
  - Plan a testing strategy for this feature
  - What scenarios should I test for these changes?
  - Write a test plan
author: agnes
version: '1.0'
tags:
  - testing
  - development
  - quality
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop
  with no additional dependencies.
installation_notes_zh: 该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

# Testing Guidelines

## Unit Tests

- Test one thing per test
- Use descriptive test names: `test_user_creation_fails_with_invalid_email`
- Mock external dependencies
- Keep tests fast and isolated

## Integration Tests

- Test API endpoints with realistic data
- Verify database state changes
- Clean up test data after each test
- Use test fixtures for common scenarios

## Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm test:unit

# Run integration tests (requires database)
npm test:integration

# Run tests with coverage
npm test:coverage
```

## Test Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Tests requiring external services
├── fixtures/       # Shared test data
└── helpers/        # Test utilities
```

## Best Practices

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One assertion per test**: When possible, test one behavior
3. **Descriptive names**: Test names should describe the scenario
4. **No test interdependence**: Tests should run in any order
5. **Clean state**: Each test starts with a known state

## Coverage Goals

- Aim for 80%+ line coverage
- Focus on critical paths first
- Don't sacrifice test quality for coverage numbers
