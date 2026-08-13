# Agent Skills

A collection of reusable **Agent Skills** maintained by Block to help AI agents perform real-world tasks more effectively.

These skills are designed to be:
- ✅ Portable across agents (Agnes, Claude Desktop, and others that support agent skills)
- ✅ Easy to install
- ✅ Easy to understand before installing
- ✅ Community-extensible

---

## What are Agent Skills?

Agent Skills are reusable sets of instructions and supporting resources that teach an AI agent how to perform a specific workflow or task.

A skill might include:
- A structured checklist (e.g. code review)
- A workflow (e.g. deploying a service)
- Domain knowledge (e.g. using a specific API)
- Supporting files like scripts, templates, or examples

Each skill lives in its own folder and includes a `SKILL.md` file.

---

## Installing a Skill

You can install skills using the `skills` CLI:

```bash
npx skills add https://github.com/AgnesAI-Labs/agnet-skills-cn --skill api-setup
```
Make sure you have the built in skills extension enabled

This will install the skill locally so compatible agents (like Agnes or Claude Desktop) can automatically load and use it.

## Browse Skills

You can browse all available skills via the Agnes Skills Marketplace:
👉 https://kiwiar-ai.github.io/agnet-skills/skills

There you can:

- Read the full skill before installing

- Copy the install command

- View source on GitH

## Contributing a Skill

We love community contributions and welcome new skills from anyone.

If you’ve built a useful workflow, checklist, or guide that could help other agents (and humans), you can submit it to this repository.

### How to contribute

1. Fork this repository
2. Create a new branch for your skill
3. Add your skill folder (with `SKILL.md` and any supporting files)
4. Commit your changes
5. [Open a pull request](https://github.com/AgnesAI-Labs/agnet-skills-cn/compare/main...your-branch?expand=1)  

#### Skill requirements (quick version)

Each skill must include a `SKILL.md` file with the following required frontmatter:

```md
---
name: api-setup
description: Set up API integration with configuration and helper scripts
author: agnes
version: "1.0"
tags:
  - api
  - integration
  - setup
---
```

For detailed guidelines, formatting rules, and examples, see the [full contribution guide](https://github.com/AgnesAI-Labs/agnet-skills-cn/blob/main/CONTRIBUTING.md)

#### Optional frontmatter fields

Beyond the required fields, skills may declare optional fields consumed by the Agnes Skills Marketplace (docs site build and desktop app):

```md
---
name: example
description: English description shown in the marketplace
description_zh: 中文描述，市场在中文 locale 下展示
installation_notes: English install notes shown in the detail view
installation_notes_zh: 中文安装说明
is_builtin: false   # default false; builtin skills are disabled in the desktop marketplace
---
```

- `description_zh` / `installation_notes_zh` — localized strings; when absent the English `description` / `installation_notes` is shown for all locales.
- `installation_notes` / `installation_notes_zh` — shown in the skill detail view so users know what the skill needs (e.g. a separately installed CLI) before installing.
- `is_builtin` — defaults to `false`; set to `true` only for skills bundled with the desktop app, which are then shown but disabled in the marketplace.

Every submission is automatically validated using our skills validator, and feedback will appear directly on your PR.

### Not sure if your idea qualifies?

Good candidates for skills include:
- Repeatable workflows (deployments, releases, migrations)
- Checklists (code review, incident response, security audits)
- Domain knowledge (APIs, internal tools, infrastructure patterns)
- Templates or scripts paired with instructions

If you’re unsure, feel free to open a draft PR or start a discussion.

---

## MCP Plugin Data

`mcp/servers.json` is the single source of truth for the MCP plugin catalog consumed by the Agnes Code desktop app's plugins marketplace (and mirrored to the docs site as `static/servers.json` by the docs site build).

To add, update, or remove a plugin entry, edit `mcp/servers.json` directly. Keep entries complete for both locales — every entry should carry both `description` / `description_zh` (and `installation_notes` / `installation_notes_zh` where applicable) so the marketplace renders correctly in English and Chinese. Entry shape must stay compatible with the desktop app's plugin schema (`name`, `description`, `command`, `env`, `supportedPlatforms`, etc.); when adding new fields, update the desktop app first and keep this file in sync.
