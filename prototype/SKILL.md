---
name: prototype
name_zh: 一次性原型验证
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like. For polished production UI work, use the frontend-design skill; this one produces throwaway prototypes only.
description_zh: >-
  用丢弃式代码回答一个设计问题：逻辑类做成单页 HTML，用按钮和引导流程把状态机跑一遍；界面类生成多个差异明显的版本，用一个路由加切换栏对比。适合先验证想法、还没打算写正式代码的时候。正式界面开发用 frontend-design，本技能只产出用完即弃的原型。
category: creative
category_name: Design & Media
category_name_zh: 设计与创意
examples_zh:
  - 先做个原型看看这套状态流转顺不顺
  - 给我几个差别大点的界面方案
  - 这个交互先跑个 demo 试试
examples:
  - Prototype this state machine
  - Show me a few very different UI options
  - Build a throwaway demo for this interaction
author: mattpocock
version: '1.0'
tags:
  - development
  - prototype
  - design
  - exploration
  - ui
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too (the verdict and the question it settled) in the issue or a commit. The main branch keeps only the validated decision.
