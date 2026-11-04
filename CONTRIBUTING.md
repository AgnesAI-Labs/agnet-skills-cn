# Contributing to Agent Skills

Thank you for your interest in contributing an Agent Skill! 🎉

This repository is a community-driven collection of reusable skills that help AI agents (like Agnes, Claude Desktop, and others) perform real-world tasks more effectively.

This guide explains:

* What makes a good skill
* How to structure your files
* How to validate your submission
* How to submit a pull request successfully

---

## What is an Agent Skill?

An Agent Skill is a reusable set of instructions (and optional supporting files) that teaches an AI agent how to perform a specific workflow or task.

Good examples include:

* Deployment checklists
* Code review workflows
* Incident response procedures
* API integration guides
* Internal tooling workflows
* Templates paired with instructions

Skills should be:

* **Focused** (one workflow or domain per skill)
* **Clear** (written for both humans and agents)
* **Reusable** (not tied to one person’s machine or secrets)

---

## Repository Structure

Each skill lives in its own folder at the root of the repository:

```
api-setup/
  SKILL.md
code-review/
  SKILL.md
  checklist.md
production-deploy/
  SKILL.md
  deploy.sh
  templates/
    config.template.json
```

Every skill **must** include a `SKILL.md` file.

---

## SKILL.md Format

Each `SKILL.md` must contain:

1. YAML frontmatter
2. The skill content written in Markdown

### Required Frontmatter

Your file must start with YAML frontmatter containing at least:

```md
---
name: api-setup
description: Set up API integration with configuration and helper scripts
author: agnes
version: "1.0"
category: development
category_name: Developer Tools
category_name_zh: 开发工具
tags:
- api
- integration
- setup
---
```

Guidelines:

* `name` should match the folder name
* Use lowercase with hyphens (`api-setup`, `code-review`)
* `description` should be clear and concise (1 sentence)
* `author` Creator of the skill (GitHub handle, name, or org)
* `version` Must be a string (quote it), start at "1.0" and increment when you make updates
* `tags` A list of keywords to help discovery in the marketplace, Use lowercase, short words or phrases
* `category` is a stable lowercase ID with optional hyphens; pick it from the category table below
* `category_name` and `category_name_zh` are required English and Chinese display names; every skill and plugin using the same category ID must use identical names

### Categories

The marketplace shows categories in the order below. Use the IDs from this table, and keep `category_name` and `category_name_zh` exactly as written. Adding a category means updating this table and the market's category order together.

| # | category | category_name | category_name_zh |
| --- | --- | --- | --- |
| 1 | `productivity` | Office Productivity | 办公效率 |
| 2 | `content` | Content Creation | 内容创作 |
| 3 | `data` | Data Analysis | 数据分析 |
| 4 | `business` | Business Operations | 商业运营 |
| 5 | `fun` | Fun | 趣味 |
| 6 | `creative` | Design & Creative | 设计创意 |
| 7 | `development` | Developer Tools | 开发工具 |
| 8 | `education` | Education & Research | 教育科研 |
| 9 | `professional` | Professional Domains | 专业领域 |
| 10 | `lifestyle` | Life Services | 生活服务 |

---

## Writing Good Skills

Skills are instructions for agents. Write them to be:

* **Explicit** (don’t assume hidden knowledge)
* **Structured** (use headings, numbered steps, checklists)
* **Verifiable** (include validation or success criteria)

### Recommended structure

```md
---
name: production-deploy
description: Safe deployment workflow for production releases
author: your-name
version: "1.0"
tags:
- deploy
- release
- production
---

# Production Deployment

## Purpose
This skill guides an agent through a safe production deployment.

## Preconditions
- All tests passing
- Required approvals obtained

## Steps
1. Create release branch from main
2. Run `npm run build:prod`
3. Deploy to staging and verify
4. Deploy to production

## Verification
- [ ] Service responds with 200
- [ ] Error rate below 1%

## Rollback
If issues occur:
1. Revert deployment
2. Notify #incidents
3. Open incident report
```

---

## Supporting Files

Skills may include supporting files such as:

* Scripts (`.sh`, `.js`, `.py`)
* Templates
* Example configs
* Checklists

These should live inside the skill folder:

```
api-setup/
  SKILL.md
  setup.sh
  templates/
    config.template.json
```

Avoid including:

* Secrets or API keys
* Personal paths
* Machine-specific assumptions

---

## Validation

All submissions are automatically validated by CI.

Validation checks include:

* Required `SKILL.md` present
* Valid YAML frontmatter
* Folder and name consistency
* Safe file structure

If validation fails, you’ll see feedback directly on your pull request.

You can fix the issues and push updates — the PR will revalidate automatically.

---

## How to Submit a Skill

1. **Fork this repository**
2. Create a new branch
3. Add your skill folder
4. Commit your changes
5. Open a pull request using the Submit a Skill template

You can open a submission PR here:

👉 [Submit your skill](https://github.com/AgnesAI-Labs/agnet-skills-cn/compare/main...your-branch?expand=1)

---

## What Maintainers Look For

We prioritize skills that are:

* Useful to a broad audience
* Clearly written and structured
* Safe (no secrets, no destructive defaults)
* Focused on one workflow or domain

We may suggest revisions, that’s normal and part of the collaboration process.

---

## Need Help?

If you’re unsure whether your idea is a good fit:

* Open a draft pull request
* Ask questions in the PR description
* Start a discussion (if enabled)

We’re happy to help you shape your contribution.

---

Thank you for helping build a high-quality, community-driven skills ecosystem! ✨
