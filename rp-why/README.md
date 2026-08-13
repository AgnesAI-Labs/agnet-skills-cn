# rp-why: Gas Town × DOK Framework

> **🪿 Agnes-Specific Skill** — This skill is designed for [Agnes](https://github.com/AgnesAI-Labs/agnet-skills-cn) and reads from Agnes's session directory to analyze your AI collaboration patterns.

A self-reflection framework that measures AI collaboration maturity (Gas Town stages) and cognitive complexity (DOK levels) to reveal growth opportunities.

## Installation

```bash
npx skills add https://github.com/AgnesAI-Labs/agnet-skills-cn --skill rp-why
```

Make sure you have the built-in skills extension enabled in Agnes.

## Quick Start

```
/rp-why current    # Analyze current session
/rp-why init       # Generate baseline from history
/rp-why compare    # Compare session to baseline
```

## What It Does

- **Measures Gas Town Stage** (1-8): How sophisticated are your AI tools?
- **Analyzes DOK Distribution** (1-4): How cognitively complex are your prompts?
- **Identifies Your Quadrant**: Frontier, Growing, Thinking Ahead, Expected, Underutilizing, or Overpowered
- **Provides Growth Nudges**: Actionable suggestions based on your position

## Requirements

- [Agnes](https://github.com/AgnesAI-Labs/agnet-skills-cn) AI agent
- Agnes sessions stored in the default session directory:
  - **macOS/Linux**: `~/.local/share/agnes/sessions/`
  - **Windows**: `%LOCALAPPDATA%\agnes\sessions\`

## Learn More

See [SKILL.md](./SKILL.md) for full documentation, including:
- Theoretical foundations (Yegge's Gas Town, Webb's DOK)
- Integration matrix and zone definitions
- Target user profiles
- Growth nudge system

## Attribution

- **Gas Town Stages**: Steve Yegge, "Welcome to Gas Town" (January 2026)
- **DOK Levels**: Norman Webb (1997)
