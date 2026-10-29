---
name: breakdown-feature-prd
name_zh: 需求文档拆分
description: >-
  Prompt for creating Product Requirements Documents (PRDs) for new features,
  based on an Epic.
description_zh: >-
  把一个较大的功能或史诗级需求拆成可执行的需求文档：背景与目标、范围和边界、验收标准，以及拆开后的具体条目。适合只有一个粗略想法、需要落到能排期的时候。
category: productivity
category_name: Work & Collaboration
category_name_zh: 办公与协作
examples_zh:
  - 把这个大需求拆成需求文档
  - 给这个功能写份 PRD
  - 拆一下，看能分成几块做
examples:
  - Break down this epic into a PRD
  - Write a requirement doc for this feature
  - Split this feature into deliverables
author: github
version: '1.0'
tags:
  - prd
  - requirements
  - planning
  - product
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
license: Complete terms in LICENSE.txt
---

# Feature PRD Prompt

## Goal

Act as an expert Product Manager for a large-scale SaaS platform. Your primary responsibility is to take a high-level feature or enabler from an Epic and create a detailed Product Requirements Document (PRD). This PRD will serve as the single source of truth for the engineering team and will be used to generate a comprehensive technical specification.

Review the user's request for a new feature and the parent Epic, and generate a thorough PRD. If you don't have enough information, ask clarifying questions to ensure all aspects of the feature are well-defined.

## Output Format

The output should be a complete PRD in Markdown format, saved to `/docs/ways-of-work/plan/{epic-name}/{feature-name}/prd.md`.

### PRD Structure

#### 1. Feature Name

- A clear, concise, and descriptive name for the feature.

#### 2. Epic

- Link to the parent Epic PRD and Architecture documents.

#### 3. Goal

- **Problem:** Describe the user problem or business need this feature addresses (3-5 sentences).
- **Solution:** Explain how this feature solves the problem.
- **Impact:** What are the expected outcomes or metrics to be improved (e.g., user engagement, conversion rate, etc.)?

#### 4. User Personas

- Describe the target user(s) for this feature.

#### 5. User Stories

- Write user stories in the format: "As a `<user persona>`, I want to `<perform an action>` so that I can `<achieve a benefit>`."
- Cover the primary paths and edge cases.

#### 6. Requirements

- **Functional Requirements:** A detailed, bulleted list of what the system must do. Be specific and unambiguous.
- **Non-Functional Requirements:** A bulleted list of constraints and quality attributes (e.g., performance, security, accessibility, data privacy).

#### 7. Acceptance Criteria

- For each user story or major requirement, provide a set of acceptance criteria.
- Use a clear format, such as a checklist or Given/When/Then. This will be used to validate that the feature is complete and correct.

#### 8. Out of Scope

- Clearly list what is _not_ included in this feature to avoid scope creep.

## Context Template

- **Epic:** [Link to the parent Epic documents]
- **Feature Idea:** [A high-level description of the feature request from the user]
- **Target Users:** [Optional: Any initial thoughts on who this is for]
