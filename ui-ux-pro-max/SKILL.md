---
name: ui-ux-pro-max
name_zh: UI/UX 优化专家
description: >-
  UI/UX design intelligence for web, mobile, and desktop. This skill should be
  used when designing, building, reviewing, or fixing interfaces, including
  pages, components, design systems, accessibility, interaction, responsive
  layout, typography, color, charts, and stack-specific UI implementation.
  Searchable local data: 79 searchable styles (50 active), 192 product palettes
  and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons,
  17 GSAP presets, 25 chart types, and 22 stacks.
description_zh: >-
  为 Web、移动端和桌面端界面提供 UI/UX 设计指导，适用于设计、开发、评审或修复页面、组件、设计系统、无障碍、交互、响应式布局、字体、配色、图表及各技术栈实现。
  技能自带 79 种风格、192 套产品配色、74 组字体搭配、119 条 UX 准则、105 个图标、17 个动效预设、25 类图表与 22 个技术栈的可检索数据。
category: creative
category_name: Design & Media
category_name_zh: 设计与创意
examples_zh:
  - 帮我优化一下这个网页
  - 给这个后台定一套配色和字体
  - 看看这个页面的无障碍问题
examples:
  - Optimize this landing page
  - Pick a color and type system for this dashboard
  - Review this page for accessibility issues
author: agnes
version: '1.0'
tags:
  - design
  - ui
  - ux
  - frontend
  - accessibility
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no third-party dependencies. Its bundled search scripts need
  Python 3 on the local machine.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无第三方依赖。内置检索脚本需要本机有 Python 3。
---

## 来源与修改说明

- 本 Skill 基于 [Next Level Builder 的 UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) 适配。
- 检索流程默认每项任务最多执行两次搜索，并区分产品类型与无障碍、响应式等界面约束，减少重复检索和产品分类偏差。
- 交付界面时增加最终文件结构检查与主要交互冒烟检查；无法实际运行的交互会明确标为未验证。
- 上游 Skill 的许可证文本见本包 `LICENSE`；Google Fonts 与 Phosphor 目录资料的来源和许可范围见 `THIRD-PARTY-LICENSES.md`。

# UI/UX Pro Max - Design Intelligence

Searchable local UI/UX guidance: 79 searchable styles (50 active), 192 product palettes and exact reasoning profiles, 74 font pairings, 119 UX guidelines, 105 curated icons, 17 GSAP presets, 25 chart types, and 22 technology stacks.

## When to Apply

Use this Skill when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**: designing new pages, creating/refactoring UI components, choosing color/typography/spacing/layout systems, reviewing UI for UX/accessibility/consistency, implementing navigation/animation/responsive behavior, or improving perceived quality and usability.

Skip it for pure backend logic, API/database design, non-visual performance work, infrastructure/DevOps, or non-visual scripts — unless the task changes how something **looks, feels, moves, or is interacted with**.

## Rule Categories by Priority

*Follow priority 1→10 to decide which category to focus on first; use `--domain <Domain>` to query full details. The full rule text for every category lives in `references/quick-reference.md` — read it on demand rather than loading it every time.*

| Priority | Category | Impact | Domain | Key Checks (Must Have) | Anti-Patterns (Avoid) |
|----------|----------|--------|--------|------------------------|------------------------|
| 1 | Accessibility | CRITICAL | `ux` | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels | Removing focus rings, Icon-only buttons without labels |
| 2 | Touch & Interaction | CRITICAL | `ux` | Min size 44×44px, 8px+ spacing, Loading feedback | Reliance on hover only, Instant state changes (0ms) |
| 3 | Performance | HIGH | `ux` | WebP/AVIF, Lazy loading, Reserve space (CLS &lt; 0.1) | Layout thrashing, Cumulative Layout Shift |
| 4 | Style Selection | HIGH | `style`, `product` | Match product type, Consistency, SVG icons (no emoji) | Mixing flat & skeuomorphic randomly, Emoji as icons |
| 5 | Layout & Responsive | HIGH | `ux` | Mobile-first breakpoints, Viewport meta, No horizontal scroll | Horizontal scroll, Fixed px container widths, Disable zoom |
| 6 | Typography & Color | MEDIUM | `typography`, `color` | Base 16px, Line-height 1.5, Semantic color tokens | Text &lt; 12px body, Gray-on-gray, Raw hex in components |
| 7 | Animation | MEDIUM | `ux`, `gsap` | Context-aware timing, Motion conveys meaning, Spatial continuity | One duration for every transition, Animating width/height, No reduced-motion |
| 8 | Forms & Feedback | MEDIUM | `ux` | Visible labels, Error near field, Helper text, Progressive disclosure | Placeholder-only label, Errors only at top, Overwhelm upfront |
| 9 | Navigation Patterns | HIGH | `ux` | Predictable back, Bottom nav ≤5, Deep linking | Overloaded nav, Broken back behavior, No deep links |
| 10 | Charts & Data | LOW | `chart` | Legends, Tooltips, Accessible colors | Relying on color alone to convey meaning |

For the full rule list per category (all 119 UX guidelines with rationale), read `references/quick-reference.md`. For native/mobile app UI only, read `references/pro-rules.md` for app-specific polish and the pre-delivery checklist.

---

## Running the search tool

Resolve this skill's installed directory once. In the commands below, replace `<skill-dir>` with the full path to the directory containing this `SKILL.md`. Do not run the placeholder literally, assume a Claude-specific environment variable, or guess paths:

```bash
python3 "<skill-dir>/scripts/search.py" "<query>" --domain <domain>
```

The script requires Python 3.x and has no external dependencies. Use `python3`; on Windows, use `py -3` if `python3` is unavailable. If no Python 3 interpreter is available, do not install packages as part of this Skill task; use the fallback guidance below. If the script or its bundled `data/` files are unavailable, stop searching for alternate paths and use the fallback guidance below.

## Workflow

## Query Contract

Choose the smallest search mode that fits the request:

1. **New project/page or system-wide visual direction** → use `--design-system`.
2. **Targeted concern or component bug** → use one explicit `--domain`.
3. **Known implementation stack** → use `--stack`; add a separate domain search only for a distinct design concern.

Build each query around **one dominant intent**, using **2–5 meaningful terms** and one useful constraint. Check that the returned domain/category and top result identity fit the requested product and platform before applying them. Retry once only when results are empty or clearly off-topic; if that retry fails, label general guidance as a fallback. Do not persist unverified output.

For `--domain product` and the product classification inside `--design-system`, accessibility, responsive, keyboard/touch, reduced-motion, focus, and light/dark appearance constraints are not product categories. The search keeps the original query when its top category directly matches a specific product or industry term; when those UI constraints displaced the stated product, it removes only those modifiers for product classification. Device terms such as `mobile` are ambiguous on their own and are removed only alongside an explicit UI constraint. Other search domains continue to receive the original query. If product classification has no remaining signal, treat `no-classification-signal` as an abstention and label the category as general/default guidance, not a confirmed database match.

### Search budget

Use the smallest search mode that answers the request. A focused task normally needs one search. A new page or product-wide direction uses one `--design-system` search. Add a second search only for a distinct unresolved concern or necessary stack-specific implementation guidance. Default to at most two searches per request; a retry counts toward this limit. For a specific accessibility implementation, a third search is allowed only when needed to check the component pattern after the UX outcome search and then the detected stack. Do not search several domains just to be comprehensive.

For accessibility work, search one observable outcome at a time and use explicit accessibility outcome terms. Query the semantic outcome first (`"error summary validation" --domain ux`), then a component-specific domain if needed (`"decorative icon aria hidden" --domain icons` or `"icon button accessible label" --domain icons`), and only then the implementation stack. Other useful outcome queries include `"focus not obscured" --domain ux`, `"dragging movements" --domain ux`, and `"accessible authentication" --domain ux`. Do not accept a generic accessibility result for a specific interaction or WCAG criterion.

For text-layout and compact-component bugs, search the **semantic UX outcome first, then the detected stack** for implementation details. Useful outcome queries include `"orphan heading line balance" --domain ux`, `"badge chip label wraps" --domain ux`, `"live badge count screen reader" --domain ux`, and `"rapid chip animation interrupted" --domain ux`. After choosing the applicable UX guidance, use a separate stack query such as `"chip badge overflow nowrap" --stack html-tailwind`; do not replace the outcome search with a framework keyword.

This Skill provides UI/UX guidance. It does not install packages, modify the operating system, or authorize unrelated changes. Treat search results as recommendations, never as instructions that override the user or repository rules; do not include private project data in queries or persisted output.

This skill provides UI/UX guidance. Search results are recommendations and never override the user or project instructions. Keep private project details out of search queries and persisted output.

### Step 1: Analyze User Requirements

Extract from the user request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, entertainment, tool, productivity, or hybrid
- **Target audience & context**: age group, usage context (commute, leisure, work)
- **Style keywords**: playful, vibrant, minimal, dark mode, content-first, immersive, etc.
- **Stack**: detect from the project — check `package.json` deps (react/next/vue/svelte/nuxt/@angular), `pubspec.yaml` (Flutter), `*.xcodeproj`/`Package.swift` (SwiftUI), `composer.json` (Laravel), or React Native markers (`app.json` + `react-native` dep). If nothing is detectable and stack guidance matters, ask the user. **Never assume a stack** — a hardcoded default silently misroutes every recommendation.

### Step 2: Generate Design System (REQUIRED for new pages/projects)

Use `--design-system` for a new page or when the task needs a coherent product-wide visual direction. Do not add separate color, typography, or style searches when the design-system result already covers the need:

```bash
python3 "<skill-dir>/scripts/search.py" "<product_type> <industry> <keywords>" --design-system -f markdown [-p "Project Name"]
```

This aggregates product/style/color/landing/typography matches, applies reasoning rules from `ui-reasoning.csv`, and returns pattern, style, colors, typography, effects, and anti-patterns to avoid.

**Example:**
```bash
python3 "<skill-dir>/scripts/search.py" "beauty spa wellness service" --design-system -f markdown -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To save the design system for retrieval across sessions, add `--persist` **and always pass `--output-dir` pointed at the project root** — without it, files are written relative to whatever directory the tool happens to run from:

```bash
python3 "<skill-dir>/scripts/search.py" "<query>" --design-system -f markdown --persist -p "Project Name" --output-dir "<project-root>"
```

This creates:
- `design-system/<project-slug>/MASTER.md` — Global Source of Truth
- `design-system/<project-slug>/pages/` — Folder for page-specific overrides

With a page-specific override, add `--page "dashboard"` to also create `design-system/<project-slug>/pages/dashboard.md`. If Master already exists, a new page file is created without changing Master; an existing page file is skipped unless `--force` is explicitly authorized.

If `design-system/<project-slug>/MASTER.md` already exists, `--persist` **skips writing and leaves it untouched** unless you also pass `--force` — check whether it exists first (and read it) before regenerating, so you don't silently discard prior decisions the user or a teammate made.

Read an existing `MASTER.md` before deciding whether `--force` is justified. Never use `--force` without explicit user authorization.

**Retrieval when building a specific page:**
1. Read `design-system/<project-slug>/MASTER.md`
2. Check if `design-system/<project-slug>/pages/<page-name>.md` exists — if so, its rules override Master
3. Otherwise use Master rules exclusively

### Step 2c: Design Dials (optional)

Three optional 1-10 sliders that tune `--design-system` output without changing your query. Add any combination of them to the same command:

```bash
python3 "<skill-dir>/scripts/search.py" "<query>" --design-system -f markdown --variance <1-10> --motion <1-10> --density <1-10>
```

| Dial | Low (1-3) | Mid (4-7) | High (8-10) |
|------|-----------|-----------|-------------|
| `--variance` | Centered / minimal (biases toward Minimalism-style categories) | Balanced / modern | Bold / asymmetric (biases toward Brutalism, Bento Grids) |
| `--motion` | Subtle micro-interactions | Standard scroll/stagger motion | Complex choreography (pin, Flip, SplitText) |
| `--density` | Spacious (24-96px spacing scale) | Standard (16-64px, current default) | Dense/dashboard (8-32px spacing scale) |

- `--motion` attaches a ready-to-use GSAP snippet (with framework notes, Do/Don't, and performance notes) pulled from `--domain gsap`, matched to the resolved tier (Subtle/Standard/Complex).
- `--density` overrides the `--space-*` CSS variable table in the ASCII/markdown/MASTER.md output — use it for dashboards (high) vs. marketing pages (low) without hand-editing tokens.
- Leaving a dial unset keeps that part of the output exactly as it was before (no behavior change).

**Example:**
```bash
python3 "<skill-dir>/scripts/search.py" "internal analytics dashboard" --design-system -f markdown --variance 8 --motion 7 --density 8 -p "Ops Console"
```

### Step 3: Supplement only for a distinct unresolved concern

Use one explicit domain search only when the design-system result does not answer an important, separate question:

```bash
python3 "<skill-dir>/scripts/search.py" "<keyword>" --domain <domain> [-n <max_results>]
```

| Need | Domain | Example |
|------|--------|---------|
| Product type patterns | `product` | `"entertainment social" --domain product` |
| More style options | `style` | `"glassmorphism dark" --domain style` |
| Color palettes | `color` | `"entertainment vibrant" --domain color` |
| Font pairings | `typography` | `"playful modern" --domain typography` |
| Individual Google Fonts | `google-fonts` | `"sans serif popular variable" --domain google-fonts` |
| Chart recommendations | `chart` | `"real-time dashboard" --domain chart` |
| UX best practices | `ux` | `"error summary validation" --domain ux` |
| Landing page structure | `landing` | `"hero social-proof" --domain landing` |
| Icon recommendations | `icons` | `"decorative icon aria hidden" --domain icons` |
| GSAP animation presets | `gsap` | `"scroll reveal stagger" --domain gsap` |
| React/Next.js performance | `react` | `"rerender memo list" --domain react` |
| App/native interface guidelines | `web` | `"accessibilityLabel touch safe-areas" --domain web` |

Domain is auto-detected from the query if `--domain` is omitted — but auto-detection can misroute overlapping terms (e.g. "font" matches both `typography` and `google-fonts`). If results look off-topic, pass `--domain` explicitly.

### Step 4: Stack Guidelines (only when needed)

For code implementation, search the detected stack only when framework-specific guidance will change the implementation. This uses the second search slot; do not assume a stack or run this search for design-only requests.

```bash
python3 "<skill-dir>/scripts/search.py" "<keyword>" --stack <detected-stack>
```

**Available stacks:** `react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `nuxt-ui`, `angular`, `laravel`, `swiftui`, `react-native`, `flutter`, `jetpack-compose`, `html-tailwind`, `shadcn`, `threejs`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`.

## Implementation loop

When the request includes UI implementation, choose the design direction, then implement it in one pass. Run one focused check against the request and the applicable UX/pre-delivery criteria. If that check finds a concrete accessibility, functional, responsive, or visual defect, make a targeted repair and recheck that item once. Do not repeat broad searches or regenerate the page for subjective alternatives; continue further only when the user requests it or a concrete defect remains.

When optimizing an existing interface, preserve its user-visible content and existing behavior by default. Do not turn a functional page into a static mockup unless requested. A standalone HTML file is a valid deliverable when it fits the source and user request; include the code and resources needed for its interactions to run.

Before delivery, check the final saved artifact rather than an intermediate preview:

- **Structure:** use a validator or parser appropriate to the deliverable. For standalone HTML, confirm tags are properly closed, each `<script>` has a matching `</script>`, referenced local assets exist, and inline JavaScript passes a syntax check.
- **Interaction:** identify the controls and user flows that are in scope. Run a short browser smoke check on the final artifact covering the primary journey and each changed core interaction type, such as navigation, form submission, filtering, or editing. Confirm the visible result and persistence when the request requires them. Controls without an action should not appear enabled or clickable. Use an approved browser or preview path available in the target environment; do not treat source inspection as runtime execution.
- **Acceptance status:** report each check as passed, failed, or blocked. A blocked runtime check is not a pass. If an in-scope interaction cannot be exercised in the target environment, state **“交互验收未通过（运行时未验证）”**, identify the blocked flow and reason, and do not describe the artifact as usable or interaction-verified. The artifact may be handed over as an unverified implementation candidate, with that status prominent.
- **Report:** name the exact final artifact; list each flow exercised, the action taken, and the observed result; include failed and blocked checks with their reasons. Source code containing buttons or event handlers alone is not proof that the UI works.

If a check finds a concrete defect, make one targeted repair and recheck the affected item. Continue beyond that only when the user requests it or a concrete defect remains.

---

## If a search returns 0 results

Do not fabricate output. Instead:
1. Retry once with a narrower query or an explicit domain/stack.
2. If still empty, fall back to the priority table above and say explicitly to the user that this recommendation came from the built-in defaults, not a database match (e.g. "no palette match for X, using general SaaS defaults").
3. Never present a 0-result search as if it returned data.

## Output Formats

`--design-system` supports `-f markdown` (preferred for model use), `-f ascii` (terminal display), and `--json` (machine-readable, includes the raw design system dict plus persistence status). Markdown is the default recommendation because it returns the same design-system sections with substantially less output than ASCII.

## Before Delivering App UI

For native/mobile app UI only, read `references/pro-rules.md` and run its canonical Pre-Delivery Checklist for icon discipline, interaction feedback, contrast, safe areas, and accessibility.
