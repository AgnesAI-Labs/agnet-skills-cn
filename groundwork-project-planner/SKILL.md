---
name: groundwork-project-planner
name_zh: 项目规划访谈
description: >-
  Interview the user and prepare lean planning docs (AGENTS.md, PRD, ARCHITECTURE, DESIGN,
  TASKS, PROGRESS, ROADMAP, MARKETING) before a new project or for one already under way,
  then keep them current. Write files only when the host provides authorized project-file
  access; otherwise return complete ready-to-save documents and say they were not saved.
  Use when starting, planning, scoping or kicking off a project; adopting an existing
  project from accessible materials; resuming from available planning docs; or updating
  those docs after work.
description_zh: >-
  通过分轮访谈梳理项目目标、核心需求、实施范围、关键任务与待解决的问题，并根据项目规模整理相应的规划文档。适用于新项目启动、已有项目规划梳理和进度恢复，帮助将初步想法转化为清晰的项目计划。
category: productivity
category_name: Office Productivity
category_name_zh: 办公效率
examples_zh:
  - 我想开始一个个人小项目，请先访谈我，帮我确定目标、核心流程、首版范围和不做什么
examples:
  - I want to start a small personal project. Interview me first to pin down the goal, the core flow, what is in the first version, and what is out of scope.
license: MIT
author: Tekeshwar Singh
version: '1.0'
tags:
  - project-planning
  - interview
  - prd
  - roadmap
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no
  additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

## Source and adaptation notes

- Adapted from [tsvillain/groundwork](https://github.com/tsvillain/groundwork), originally named `groundwork`; the upstream Skill and templates are MIT licensed. The complete license is included in `LICENSE`.
- This adaptation treats supplied decisions as settled, recalculates material unknowns after each answer, and prohibits task trackers as a substitute for project documents. It writes and verifies project files only through available authorized file access; otherwise it returns complete ready-to-save documents without claiming they were created. The user guide uses the name Groundwork Project Planner and matches those access and cross-session limits.

# Groundwork Project Planner

Plan once, then let the docs carry context between sessions and between agents.
The interview is the product: sharp questions produce docs worth following.
Templates live in `templates/`, next to this file.

## The doc set

| File | Job | When to read |
|------|-----|--------------|
| `AGENTS.md` (project root) | Rules for agents plus an index of the docs | Every session |
| `docs/PROGRESS.md` | Log: done, broke, next | Every session |
| `docs/TASKS.md` | Small steps for the current milestone only | Every session |
| `docs/PRD.md` | What it is, for whom, non-goals | When a task touches scope |
| `docs/ARCHITECTURE.md` | Stack, folders, data flow | When a task touches structure |
| `docs/DESIGN.md` | Colors, fonts, components, vibe | When a task touches UI |
| `docs/ROADMAP.md` | Milestones and phases | When picking the next milestone |
| `docs/MARKETING.md` | Audience, positioning, voice | When writing public copy |

ROADMAP holds milestones. TASKS holds only the current milestone's steps. PROGRESS records what happened. Do not let them overlap.

## Scale to the project

Ask how big the project is before writing anything. Create only what fits:

- **Tiny** (weekend toy, script, experiment): AGENTS.md, PROGRESS.md, TASKS.md. Fold a two-line "what and why" into AGENTS.md instead of a PRD.
- **Small** (useful tool, few weeks): add PRD.md and ARCHITECTURE.md. Add DESIGN.md only if it has a UI.
- **Serious** (product, public launch, users who are not you): the full set, including ROADMAP.md and MARKETING.md.

Skip a doc rather than fill it with guesses. It can be added later when the need is real.

## Commands

The first word after the skill name picks the mode: `$groundwork-project-planner init`, `$groundwork-project-planner adopt`, `$groundwork-project-planner resume`, `$groundwork-project-planner update`.
With no command, pick the mode from the request. If still unclear, look at the project: no code means init, code but no `docs/PROGRESS.md` means adopt, `docs/PROGRESS.md` present means resume.

## Use only context that is actually available

### New-session continuation with missing context

This rule takes precedence over the normal `init`/`adopt` interview and file-planning flow. Use only the current conversation and relevant project materials that are actually available. Do not assume cross-session memory or claim access to another conversation. When the user asks to continue an earlier conversation that is not visible, do not search chat history, call chat-recall/history tools, or query another session unless the user explicitly asks you to retrieve a specific conversation or transcript. Do not ask the user to remember, reconstruct, or paste the old interview. Reply briefly: say you cannot see the earlier conversation, so cannot assess its completeness or list files, then ask only “What would you like me to work on now?” Do not begin the standard project intake, ask for project details, show project-size/file mappings, or narrate Skill rules. Preserve facts visible in the current conversation and relevant project materials. Never infer project size, scope, decisions, or a planning-file list from unavailable context.

## Modes

When explicitly invoked, begin with a brief, task-specific acknowledgment and move into the requested mode. Do not add a generic assistant/company self-introduction unless the host requires it.

For a new-project `init` interview, do not browse the web, open webpages, or call unrelated external tools to answer ordinary scoping questions or to infer local runtime availability. Use the user's supplied context and stable technical knowledge, clearly mark uncertainty, and make local verification a later implementation step. Use external research only when the user requests it or when current external information is necessary to answer the actual request; keep the call directly relevant and state its purpose. Never send a dummy or unrelated URL. Do not call tools merely because they are available.

### init: interview, then deliver

Before each interview turn, sort relevant details into known, unknown, and undecided. Keep this accounting internal unless a brief recap helps the user correct a misunderstanding. Treat explicit user statements and exclusions as settled; do not ask them again in alternate wording. If the user says a decision is undecided, has no preference, or asks you to recommend, treat that as permission to recommend—not as a reason to ask the same preference question again. After gathering the facts that materially affect a choice, recommend a suitable option, give a concise reason, and ask whether the user accepts it before recording it as decided.

**Build each turn to move the interview forward.** When information is still needed, ask up to three specific, answerable questions whose answers could change the goal, core flow, v1 scope, a material implementation decision, or a required boundary. After each user reply—including acceptance of a recommendation—recalculate the known, unknown, and undecided items from the full conversation. Ask only about material gaps that actually remain; never announce a fixed number of future questions or assume gaps remain. If no material gaps remain, say so and move to the next requested planning step without inventing questions. Do not send a filler turn such as “let me confirm the basics” without an actual question. If the user asks to clarify goals, core flow, v1 scope, and non-goals, select the highest-value unanswered items and ask them directly; do not make the user restate information already supplied. For low-impact unspecified behavior, choose the simplest reasonable default and label it as an assumption. Before asking, check whether either plausible answer would materially change the first milestone; if not, use a default and keep moving. Do not interrupt the interview to settle URL punctuation, empty-result wording, or similar details unless the user makes them consequential. If the user requests a one-shot questionnaire, follow that request while still avoiding settled facts and irrelevant questions.

**When the user changes one settled decision:** update that decision and carry every other confirmed fact forward. Do not add adjacent implementation details (such as a command-line interface, error handling, or file behavior) unless they are necessary to evaluate the requested change. If a detail is needed but unspecified, label one simple assumption and keep it brief; ask only when plausible answers would materially change the first milestone. When the user asks only to record a change, summarize the changed decision and its material impact; do not repeat the full project brief or produce a file list unless requested or needed for the next agreed step.

**When the user asks you to recommend, choose.** If the user says their stack is undecided, has no preference, or asks for a recommendation, select one primary option and explain briefly why it fits the stated needs. Ask whether the user accepts that recommendation. Do not turn the request into a comparison quiz or ask the user to choose between options before giving your recommendation. Mention an alternative only when materially necessary to explain a real tradeoff. Never introduce an OS-dependent alternative simply because the user does not want to install software. Keep stack preference separate from whether a runtime exists on the user's machine.

**Final check before sending an `init` interview reply.** Compare every proposed claim and question with what the user actually said:

- Treat explicit platform, input, output, exact matching rules, URL schemes, and exclusions as settled. For terminal paste, use interactive standard input ending at EOF (Ctrl-D on macOS) by default; do not ask about pipes, arguments, clipboard, or delimiters unless material.
- If the user asks for a stack recommendation and the requirements are sufficient, respond in this order: (1) recommend one primary option with its project-fit reason; (2) state runtime availability as unknown unless verified; (3) make verification a pre-implementation gate; (4) ask only “Do you accept this recommendation?” Do not ask which language they prefer after they said it is undecided or asked you to choose.
- Unless the user explicitly requests a comparison, give only the primary recommendation and justify it by the project's own requirements. Do not compare it to another language, shell, command, or tool, and do not mention `bash`, `awk`, `sed`, or `grep` as a contrast. Do not announce that you are omitting, rejecting, or not discussing alternatives (for example, “I do not recommend the alternative direction” or “I will not compare Shell/awk”). Simply leave them out and continue with the requested recommendation.
- In an ordinary project interview, do not make claims about which software is or is not included in a specific operating-system release, or which vendor package provides it. This includes claims such as “macOS version X does/does not include Python” or “Xcode Command Line Tools are required.” These facts are unnecessary to a project-fit recommendation and must not be inserted as caveats. State only that this machine's runtime availability is unknown unless it was directly verified or the user asked for that platform fact.
- “Uses only the Python standard library” means no third-party packages; it does **not** mean Python is installed or satisfy a “do not install software” constraint by itself. Never use “zero install” or “no install required” unless both runtime and dependencies have been verified in the target environment. When runtime is unknown, do not promise that any option avoids installation; state that implementation depends on the runtime already being available, and make verification a gate.
- Never mention presumed OS availability—even as a caveated guess. Statements such as “macOS usually includes Python,” “awk is probably available,” or “this is almost certainly installed, though I have not checked” remain unsupported availability claims; the caveat does not make them acceptable. Do not use a presumed OS-provided toolchain to claim that a no-install constraint is satisfied. If useful, simply omit the availability speculation and report the verification step.
- Do not ask about URL punctuation, quote handling, empty-result text, or other minor behavior when the user has not made it consequential; state a simple default. If terminal paste is specified, do not ask whether to use stdin, a pipe, arguments, clipboard, or an end marker.
- Remove any question whose plausible answers would not change the first milestone. When only stack acceptance remains, send exactly one confirmation question and no other question—numbered, unnumbered, or framed as an optional follow-up. Do not append questions about URL boundaries, punctuation, quote handling, empty-result behavior, directories, invocation style, or separators; choose and label sensible defaults for these unless the user explicitly makes one consequential.
- Before sending, count every question mark and every imperative asking the user to decide. If the user has already supplied the project behavior and only the stack is undecided, the response may ask only whether the user accepts the recommended stack.
- Do not use a tool to fill space or demonstrate activity. For an ordinary project interview, use no browser/web call; only use an external tool when it is requested or necessary for a material, current fact.

Cover only the relevant topics, spread across turns as needed:

- User and use case: a specific person/group and when they need the project.
- Core loop and v1 completion: the smallest useful flow and what can wait.
- Non-goals and agent boundaries: what is out of scope and any restrictions the user actually wants recorded.
- Stack and environment: language/framework/runtime preferences and known constraints.
- UI direction only for UI projects.
- Project size: infer Tiny/Small/Serious when the user's description clearly establishes it (for example, a weekend personal script); otherwise ask.

For a Tiny project's initial planning-file list, include only the three planning documents: `AGENTS.md`, `docs/PROGRESS.md`, and `docs/TASKS.md`. Do not include scripts, source files, project-specific tests, or other implementation outputs in that list. `TASKS.md` may describe future implementation work when appropriate, but the planning stage itself must not create or present code files as files being created. If the user says not to write files or code, do not create either.

**No task-tracker calls during planning interviews.** From the first `init`/`adopt` interview turn through all follow-ups and until the planning-document phase is complete, do not create, write, update, or query a task-management tool or independent tracker. This includes any connected tool or API that creates, updates, or queries todos, tasks, projects, checklists, or session trackers, regardless of its tool name or whether the list is described as internal, temporary, or only for conversation memory. Do not call such a tool during the interview, even if a connected tracker is available or the interview spans separate user turns. For a continuation request, retain interview state only in the conversation and do not substitute tool-based memory. Do not reclassify a tracker update as “not independent” to bypass this rule; retain interview state in the conversation context. User requests to continue, summarize, or ask the next questions do not authorize tracker use. The only exceptions are: (1) the user explicitly asks to create or update a task tracker, or (2) the host strictly requires a tracker call. In either exception, first explain the exact required action and its effect; otherwise, do not call the tool. This rule applies even when a tracker tool is available and even when no project files are being written.

For serious projects, also ask for milestones (ROADMAP) and the audience, competitors and voice (MARKETING).

Then deliver the docs:

**Check file capability before promising a write.** Use a project-file tool only when the host actually provides it and the user has authorized the target paths. A tool name mentioned in instructions is not evidence that the tool exists. Do not call shell, terminal, filesystem, artifact, or other tools speculatively. Do not use a todo, task, project, checklist, session tracker, chat history, or external service as a substitute for project-file access.

- **File mode:** when authorized project-file read/write tools are available, write the selected documents to the approved paths and verify those exact files exist before reporting them as created.
- **Document mode:** when project-file write access is unavailable, produce the complete final content for every selected document in the response, each under its exact intended path. Replace or remove all template guidance and placeholders. State clearly that the documents are prepared but not saved. Do not offer a mere outline or claim completion without the full document contents.
- If the user explicitly requires files on disk and the host cannot write them, explain the capability limit and provide document mode as the usable result. Do not retry nonexistent tools or ask the user to believe files were created.

- In file mode, copy each chosen template into place: `AGENTS.md` at the project root, everything else in `docs/`. In document mode, use the same paths as headings for the complete document contents.
- Before writing, provide one internally consistent file list: exact paths, count, and purpose. Ensure the count matches the listed rows and each path matches the selected project structure.
- Replace every guidance line with real content from the interview. Delete sections that do not apply. Leave no placeholders.
- Do not invent project-specific rules, requirements, commands, decisions, or restrictions. In `AGENTS.md`, include rules only when grounded in the user's instructions, existing project rules, or the template's clearly identified defaults. Never add blanket rules that tell agents to skip relevant code/context inspection or execute tasks without confirmation the user requested.
- In `TASKS.md`, keep only actionable steps for the first milestone. Put verification criteria on the task they verify; do not add a standalone task whose only purpose is to mark work complete.
- Keep the prefilled "How to build" rule in AGENTS.md by default; the user may edit or drop it.
- Write TASKS.md as small steps for the first milestone only, each finishable in one sitting.
- Start PROGRESS.md with one entry recording the delivery accurately: “docs created” in file mode or “docs prepared, not saved” in document mode.
- If the project already has an `AGENTS.md` or `CLAUDE.md`, merge: keep existing content, add the rules and the docs index as new sections, and never overwrite or delete what is there. If only `CLAUDE.md` exists, add the docs index to it and ask before creating `AGENTS.md` beside it.
- Show the user a short summary of what was written and ask for corrections.
- Report files as created only after confirming they exist at the exact paths. Distinguish planned, prepared-but-unsaved, and created files. If the host gives only a temporary workspace, state that persistence is not guaranteed; do not move files elsewhere without the user's direction.
- Do not begin implementation code as part of the planning-doc step. Continue into implementation only when the user asks to proceed.

### adopt: read the code, then fill the gaps

For a project that already has code but no Groundwork Project Planner docs: joined mid-way, inherited, or stalled. Read before asking; never ask what the code already answers.

If repository files are not accessible, do not pretend to inspect them or call unavailable shell/file tools. Work from project materials the user has already supplied. If those materials are insufficient for adoption, name the specific missing material needed for the next decision; document mode remains available for the resulting planning docs.

1. **Read the repo.** README, the manifest (`package.json`, `pyproject.toml` or similar), the folder layout, the last ~30 commits, TODO and FIXME comments, and failing tests or build output if they are cheap to get.
2. **Show what you see.** Draft the answers the code implies (stack, structure, what works, what is half-built, likely size) and present them as "here is what I see, correct me".
3. **Interview only the gaps**, with init's pushback: who it is for, what done looks like for v1, the non-goals, what an agent must never do. Always ask: what were you trying to do when you got stuck?
4. **Write the docs** as in init, with these differences:
   - Start PROGRESS.md with an "adopted" entry summarising the history: done, broken, half-built.
   - Write TASKS.md for the next milestone, starting with the steps to get unstuck.
   - Write ARCHITECTURE.md as the code is, not as it should be.
   - Where the README or existing docs disagree with the code, do not guess which is right: record each drift as an open question in PRD.md (in PROGRESS.md for tiny projects).

### resume: say where things stand

Resume only from planning docs available in the current conversation or through authorized project-file access. If none are available, say that the current project state cannot be reconstructed from the visible context; do not search unrelated chats or invent progress.

1. Read `AGENTS.md`, `docs/PROGRESS.md` and `docs/TASKS.md`. Nothing else yet.
2. Tell the user in a few lines: what was last done, what is broken or open, what is next.
3. Pick the next unticked task and confirm it with the user before starting.
4. Open PRD, ARCHITECTURE, DESIGN, ROADMAP or MARKETING only when the chosen task needs them.

If TASKS.md is fully ticked, read ROADMAP.md, propose the next milestone's tasks, and replace TASKS.md with them after the user agrees.

### update: after each task and at wrap-up

Run after each finished task (offer it) and whenever the user says they are wrapping up. Docs that go stale are worse than no docs.

In document mode, return the complete updated contents for every affected planning doc and mark them prepared but unsaved. Never update an external task tracker in place of `docs/TASKS.md` or `docs/PROGRESS.md`.

1. Append a dated entry to `docs/PROGRESS.md`: done, broke, next. Keep it short and concrete. Never rewrite past entries.
2. Tick finished items in `docs/TASKS.md`. Add newly discovered steps. Remove steps that no longer make sense, and note why in PROGRESS.
3. If a decision changed the stack, scope or design, update the matching doc in the same pass and append a dated line to its Decisions section: `- YYYY-MM-DD: what changed - why`. Never delete past decision lines; mark superseded ones `(superseded YYYY-MM-DD)`.
4. If an agent rule was learned the hard way, add it to `AGENTS.md`.
5. Tell the user in one or two lines what changed in the docs.

## Rules for writing the docs

- Short and scannable: bullets over prose, one idea per line.
- Specific over generic: "Postgres 16 on Fly.io", not "a database".
- Every doc earns its place. If nobody will read it, do not write it.
