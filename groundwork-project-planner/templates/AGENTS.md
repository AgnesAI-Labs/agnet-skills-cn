# AGENTS.md

> One line: what this project is and who it is for.

## Every session

1. Read `docs/PROGRESS.md` and `docs/TASKS.md` before doing anything.
2. Work on one task from `docs/TASKS.md` at a time.
3. After each finished task, offer to run `$groundwork-project-planner update` (append `docs/PROGRESS.md`, tick `docs/TASKS.md`); run it when the user is wrapping up.

## How to build

Build every feature from first principles:

- Before building, state the real problem and the constraints in plain terms.
- Question assumptions and inherited patterns; do not copy the usual approach or boilerplate by default.
- Derive the simplest solution that satisfies those fundamentals.
- When proposing a non-obvious approach, explain the reasoning briefly.

## Docs (read only when the task needs them)

- `docs/PRD.md`: what we are building, for whom, non-goals.
- `docs/ARCHITECTURE.md`: stack, folders, data flow.
- `docs/DESIGN.md`: colors, fonts, components, vibe.
- `docs/ROADMAP.md`: milestones and phases.
- `docs/MARKETING.md`: audience, positioning, voice.

> Delete lines for docs this project does not have.

## Commands

> How to install, run, test and lint, one command per line.

## Coding style

> Language conventions, naming, formatting, file layout rules.

## Never

> Things an agent must never do, e.g. add a dependency without asking, edit generated files, commit secrets, skip tests.

## Ask first

> Changes that need a human yes, e.g. schema changes, new services, deleting files.

- Reversing a decision. Before reversing or "fixing" anything that looks intentional, check the Decisions sections in `docs/`; never reverse a recorded decision without asking the user.
