---
name: internal-comms
description: >-
  A set of resources to help me write all kinds of internal communications,
  using the formats that my company likes to use. Claude should use this skill
  whenever asked to write some sort of internal communications (status reports,
  leadership updates, 3P updates, company newsletters, FAQs, incident reports,
  project updates, etc.).
description_zh: 撰写状态报告、FAQ 与内部通讯
category: writing
category_name: Writing & Communication
category_name_zh: 写作与沟通
examples_zh:
  - 写一份项目状态报告
  - 帮我写一封内部通知
  - 整理一份常见问题 FAQ
examples:
  - Write a project status update
  - Draft an internal announcement
  - Put together an FAQ
author: anthropics
version: '1.0'
tags:
  - writing
  - comms
---

## When to use this skill
To write internal communications, use this skill for:
- 3P updates (Progress, Plans, Problems)
- Company newsletters
- FAQ responses
- Status reports
- Leadership updates
- Project updates
- Incident reports

## How to use this skill

To write any internal communication:

1. **Identify the communication type** from the request
2. **Load the appropriate guideline file** from the `examples/` directory:
    - `examples/3p-updates.md` - For Progress/Plans/Problems team updates
    - `examples/company-newsletter.md` - For company-wide newsletters
    - `examples/faq-answers.md` - For answering frequently asked questions
    - `examples/general-comms.md` - For anything else that doesn't explicitly match one of the above
3. **Follow the specific instructions** in that file for formatting, tone, and content gathering

If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format.

## Keywords
3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
