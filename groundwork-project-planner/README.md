<h1 align="center">Groundwork Project Planner</h1>

> Agnes package name: `$groundwork-project-planner`. Adapted from [tsvillain/groundwork](https://github.com/tsvillain/groundwork); MIT license text is included in `LICENSE`.

<h3 align="center">Plan once. Carry project context through clear documents.</h3>

## What it is

Start a new project with an AI agent and no plan, and the agent guesses: the stack, the scope, the look, what done means.
It does not matter whether it is a side project, a startup, client work or a team repo.
And every new session starts from zero: switch between projects or step away for a week, and the first question is always "where was I?".

Groundwork Project Planner addresses that before the first line of code.
It interviews you, pushes back until the answers are concrete, and prepares a small set of planning docs sized to the project. When Agnes has authorized access to project files, it can save and verify them. Without that access, it returns the complete ready-to-save documents and clearly says they were not saved.
When saved planning docs are available in the current session or through authorized project-file access, they give you and an agent a shared project record: a short core for each session, with the rest opened only when a task needs it.
After a task, Groundwork Project Planner can update those documents in place when file access is available, or return their complete updated contents for you to save.
Already deep into a project and lost? When relevant project materials are accessible, Groundwork Project Planner can inspect them, tell you what it sees, and ask only what those materials cannot answer. Without accessible materials, it names the specific information needed instead of guessing.

Groundwork Project Planner is not an app and not a CLI.
This Agnes package contains an Agent Skill `SKILL.md` and its planning templates.

## Adaptation note

This adaptation clarifies interview and delivery behavior: use only the current conversation and relevant project materials, never assume cross-session memory, and do not search other chats unless asked to retrieve a specific conversation. When one decision changes, update it and preserve the rest without adding unrequested implementation detail. Project files are saved only when Agnes has authorized access to them; without that access, the Skill returns complete ready-to-save documents and does not claim they were created. It does not use task trackers as substitute storage.

## Features

- **A focused interview** - asks direct, answerable questions about the remaining decisions, in turns of up to three; it avoids filler turns and does not reopen settled details.
- **Honest document delivery** - saves and verifies files when authorized project-file access exists; otherwise returns full ready-to-save documents, labeled with their intended paths.
- **Scales to project size** - a weekend toy gets three docs; a serious product gets all eight.
- **Core first, detail on demand** - when the planning docs are accessible, Groundwork Project Planner starts with `AGENTS.md`, `PROGRESS.md` and `TASKS.md`, and opens the PRD, architecture, design, roadmap or marketing docs only when a task needs them.
- **Adopt an existing project** - when project materials are accessible, reads the README, manifest, layout, recent commits and TODOs, says "here is what I see, correct me", asks only the gaps plus "what were you doing when you got stuck?", and prepares docs that start with getting unstuck.
- **Commands** - `$groundwork-project-planner init`, `$groundwork-project-planner adopt`, `$groundwork-project-planner resume` and `$groundwork-project-planner update` pick a mode directly.
- **Grounded recommendations** - gives one clear recommendation when asked, separates technical fit from machine availability, and does not guess that a platform has a required tool.
- **Resume from available docs** - when the planning docs are accessible, `$groundwork-project-planner resume` reports what was done, what broke, and the next task. It never invents missing cross-session context.
- **Update after each task** - the agent can log progress and tick tasks after finished work. It saves changes when authorized file access exists; otherwise it returns the complete updated documents and labels them unsaved.
- **First-principles build rule** - every generated `AGENTS.md` tells agents to state the real problem, question inherited patterns, and build the simplest thing that fits; edit or drop it.
- **Safe merge when files are accessible** - an accessible existing `AGENTS.md` or `CLAUDE.md` keeps its content; Groundwork Project Planner adds its rules and docs index alongside.

## Quick Start

### Install and invoke

In Agnes, invoke this package as `$groundwork-project-planner` followed by the mode you want:

- `$groundwork-project-planner init` to plan a new project
- `$groundwork-project-planner adopt` to understand an existing codebase
- `$groundwork-project-planner resume` to pick up a project from accessible planning docs
- `$groundwork-project-planner update` to record progress in accessible planning docs or prepare their updated contents

### Talk to it

```sh
> $groundwork-project-planner init — plan a new project: a booking app for a client's physio clinic

# Groundwork Project Planner asks a few questions at a time, and pushes back:

  Who is it for? "Clinics" is too broad - who books, and who manages the schedule?

> patients booking 30-minute slots on their phones; two physios managing their own calendars

# ...a few answers later it prepares AGENTS.md and docs/, sized to the project.
# It saves them only when authorized project-file access is available;
# otherwise it returns their complete contents and labels them unsaved.
# Later, in a session where the saved planning docs are accessible:

> $groundwork-project-planner resume

  Done: slot picker. Broke: timezones in reminder emails. Next: physio calendar view. Start it?
```

Already have code but no plan, or stuck halfway? Adopt it:

```sh
> $groundwork-project-planner adopt

  Here is what I see: Next.js 15 + Prisma on Postgres, auth and the slot picker work,
  payments half-built (stripe.ts, 3 TODOs), last commit 5 weeks ago. Correct me.
  What were you trying to do when you got stuck?

> stripe webhooks kept failing locally

# ...it asks only the gaps (who, v1, non-goals), then prepares the docs:
# PROGRESS starts with an "adopted" entry, TASKS starts with getting unstuck.
```

### Commands

Use `$groundwork-project-planner` plus a mode word to select a mode.

| Command | Use it when |
|---------|-------------|
| `$groundwork-project-planner init` | Starting a new project from nothing |
| `$groundwork-project-planner adopt` | The project has accessible code or supplied materials but no Groundwork Project Planner docs |
| `$groundwork-project-planner resume` | Picking a project back up when its planning docs are accessible |
| `$groundwork-project-planner update` | After a task or at wrap-up: save changes when authorized, or return complete updated contents |

After this package is loaded, a plain request may let Groundwork Project Planner infer a mode from the visible context. It does not infer project state from files or conversations it cannot access.

## How It Works

```
                            you
                             │
          new project ───────┴─────── existing code
                │                          │
                ▼                          ▼
 ┌─────────────────────────┐  ┌──────────────────────────┐
 │ init: the interview     │  │ adopt: read the repo     │
 │ who, core loop, v1,     │  │ "here is what I see",    │
 │ non-goals, stack, vibe, │  │ ask only the gaps, plus  │
 │ never-dos, size         │  │ "where did you get stuck"│
 └────────────┬────────────┘  └─────────────┬────────────┘
              └──────────────┬──────────────┘
                             ▼
 saved project or prepared document set
 your-project/
 ├── AGENTS.md            rules + docs index      always read
 └── docs/
     ├── PROGRESS.md      done, broke, next       always read
     ├── TASKS.md         current milestone       always read
     └── PRD, ARCHITECTURE, DESIGN,               on demand
         ROADMAP, MARKETING
                    │
                    ▼
 ┌──── each session with accessible docs ──────┐
 │                                             │
 │   resume ──► build one task ──► update ──┐  │
 │     ▲                                    │  │
 │     └────────────────────────────────────┘  │
 └─────────────────────────────────────────────┘
```

**init** interviews you and prepares only the docs that fit.
**adopt** reads accessible project materials first, confirms what it sees, asks only what the materials cannot answer, and prepares docs that describe the project as it is; README-versus-code drift becomes open questions, not guesses.
**resume** reads accessible core docs, says where things stand, and picks the next task. Without those docs, it states that the project state cannot be reconstructed from the visible context.
**update** updates `PROGRESS.md` and `TASKS.md` after finished work. It saves the changes only with authorized project-file access; otherwise it returns the complete updated contents and says they were not saved.

## The doc set

When files are saved, `AGENTS.md` goes at the project root and everything else goes in `docs/`. Whether an agent loads `AGENTS.md` automatically depends on that agent and its access to the project.

| Always read, every session | Read on demand, when a task needs it |
|----------------------------|--------------------------------------|
| `AGENTS.md`: rules for agents plus an index of the docs | `PRD.md`: what you are building and for whom |
| `PROGRESS.md`: done, broke, next | `ARCHITECTURE.md`: stack, folders, data flow |
| `TASKS.md`: small steps for the current milestone | `DESIGN.md`: colors, fonts, components, vibe |
| | `ROADMAP.md`: milestones and phases |
| | `MARKETING.md`: audience, positioning, voice |

## License

MIT - see [LICENSE](LICENSE).

