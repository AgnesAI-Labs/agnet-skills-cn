---
name: market-research
name_zh: 市场调研分析
description: >-
  Evidence-based market research for decisions about markets, customers,
  competitors, trends, and opportunities. Use for market sizing, industry or
  competitor analysis, customer demand research, and market-entry or
  product-opportunity assessment; only the modules relevant to the question are
  used.
description_zh: >-
  开展基于证据的市场调研，服务于市场、客户、竞品、趋势与机会相关决策；用于市场规模、行业或竞品分析、客户需求研究、市场进入或产品机会评估，只选用与研究问题相关的模块。
category: business
category_name: Business & Marketing
category_name_zh: 商业运营
examples_zh:
  - 我想在国内做一款低糖气泡茶，预算不大，帮我市场调研一下
  - 对比一下这几家竞品
  - 这个市场值不值得进
examples:
  - Research this market for a low-sugar sparkling tea launch
  - Compare these competitors
  - Is this market worth entering
author: agnes
version: '1.0'
tags:
  - research
  - market
  - competitive-analysis
  - business
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies.
installation_notes_zh: 该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

## 来源与修改说明

- 原始 Skill：`market-research`，作者/版权方：Affaan Mustafa（依据随包 MIT 许可证）。
- 原始来源：[affaan-m/ECC](https://github.com/affaan-m/ECC/tree/90606c8315ee09cafc303515c5f33024db6b9882/.agents/skills/market-research)，路径：`.agents/skills/market-research`。
- 对比基线：`90606c8315ee09cafc303515c5f33024db6b9882`。该提交是本次适配记录的基线；无法据此确认早期获取副本时实际使用的提交。
- 许可证：MIT；完整许可证及原版权声明见本包 `LICENSE`。
- 整理方：Agnes 适配整理；具体个人或法人主体未在现有记录中注明。
- 修改日期：2026-10-21 至 2026-10-23。
- 修改文件及内容：
  - `SKILL.md`：调整研究主题触发条件；增加研究类型路由、研究深度、核心工作流、工具及研究边界、决策备忘录结构和质量门槛。
  - `references/market-sizing.md`：新增市场定义、规模估算、口径比较和算术核验指引。
  - `references/competitor-analysis.md`：新增竞品识别、统一比较和证据记录指引。
  - `references/customer-demand.md`：新增客户需求证据、样本限制和一手研究边界指引。
  - `references/trends-and-opportunity.md`：新增趋势、政策、市场进入和机会分析指引。
  - `agents/openai.yaml`：调整展示短描述和默认提示。
  - `MODIFICATIONS.md`：记录来源、许可、变更文件和核验限制。
  - `SKILL.md`（2026-10-22）：补充外部研究必要性判断、证据需求规划、关键主张交叉核验、原始单位和换算记录，以及质量门槛未通过时的回退和披露规则。
  - `SKILL.md`（2026-10-23）：新增 Quick Scan 与 Decision Memo 报告结构、关键发现字段、来源注记和可读性规范；统一默认 Decision Memo 的格式引用。
- Agnes 适配边界：本包提供研究流程和证据质量指引，不自行提供搜索、网页读取或实体查询能力；执行时只可调用当前会话实际提供的工具。桌面端/Web 端能力覆盖及本包导入后的文件保留情况未验证。
- 详细修改记录：见 [MODIFICATIONS.md](MODIFICATIONS.md)。

# Market Research

Help the user make a better-informed market decision. Start from the decision, choose the smallest research scope that can answer it, and keep evidence, estimates, assumptions, and recommendations distinct. This Skill guides research; it does not provide search services or make unavailable tools available.

## When to Activate

- The user asks about a market's size, structure, growth, or trends.
- The user wants to identify or compare competitors and alternatives.
- The user needs to understand customer segments, demand signals, or unmet needs.
- The user is assessing a market entry, product opportunity, or expansion decision.
- The user asks for related company, investor/fund, technology, or vendor research that informs a market decision.

Do not force a full market report for a narrow question. General brainstorming that does not need external evidence does not require this Skill. This Skill does not provide investment, legal, or financial advice.

## Research Router

Choose one or more modules based on the user's question. Read only the matching reference files:

- Market size, revenue, spending, TAM/SAM/SOM, or forecast → [references/market-sizing.md](references/market-sizing.md).
- Competitor discovery, comparison, positioning, or differentiation → [references/competitor-analysis.md](references/competitor-analysis.md).
- Customer segments, needs, demand, reviews, interviews, or surveys → [references/customer-demand.md](references/customer-demand.md).
- Industry structure, trends, policy, market entry, whitespace, or opportunity assessment → [references/trends-and-opportunity.md](references/trends-and-opportunity.md).

For a broad request, combine only the modules that bear on the stated decision. A market overview does not automatically require named-company dossiers, a survey, or every strategy framework.

## Choose Research Depth

- **Quick Scan**: a directional snapshot, a few high-value findings, key risks, and the largest evidence gaps.
- **Decision Memo**: the default for a decision request; include the relevant market modules, evidence-backed comparison or sizing, implications, and a recommendation.
- **Deep Dive**: use when requested or when the decision clearly needs broader evidence; expand source coverage, methods, counterevidence, and supporting detail.

Match the output length to the task. Do not promise a duration or exhaustive coverage unless the environment and collection scope support it.

## Core Workflow

1. **Clarify the decision and scope.** Identify what decision the research should support. Establish the market/product or category, target customer if relevant, geography, time horizon, and requested depth. Ask only about missing choices that could materially change the answer; otherwise state a reasonable assumption.

2. **Decide whether external research is needed.** Check whether the user's materials and the question are sufficient to answer. If the task only requires organizing or analyzing supplied material, answer from that material and state its coverage limits. Do not start a full market-research workflow for general brainstorming that needs no external evidence. Proceed to external research when the answer depends on outside facts, current information, or independent verification.

3. **Define research questions and evidence needs.** Break the decision into a short list of answerable questions. For each question, identify suitable evidence types, relevant time periods, and whether independent corroboration is needed. Prefer original company disclosures, official statistics, regulators, public filings, and research organizations; use credible secondary sources for context and corroboration.

4. **Check actual capabilities and source access.** Use only search, page-reading, entity, file, or other tools that are present in the current session. In Agnes, use `web_search` to discover sources and `read_webpage` to inspect important pages when available. `entity_search` and `entity_facts` can help identify entities or provide structured background, but do not use them alone to substantiate material claims. Adjust the evidence plan to actual tool limits; never claim a search or read that did not occur.

5. **Choose research depth and route modules.** Select Quick Scan, Decision Memo (the default for a decision request), or Deep Dive. Read only the reference files for the selected modules and combine only those needed to answer the decision. A broad topic does not automatically require every module.

6. **Collect and track evidence.** For each material claim, record the source title, direct URL, publication/update date when available, retrieval date, geography, period, original value and unit, actual/estimate/forecast status, relevant definition or scope, and access status (`full page read`, `search snippet only`, `secondary source`, `entity result`, or `blocked/unavailable`). Search excerpts are leads, not full-source verification.

7. **Analyze, verify, and challenge.** Follow only the selected references and keep the market definition and comparison criteria consistent. Prioritize independent corroboration for decision-critical numbers, claims that underpin the main conclusion, data reported only in search snippets, and conflicting source claims. If independent corroboration is unavailable, label the evidence as single-source and lower confidence accordingly. Check units, currency, arithmetic, periods, geography, definitions, methodology, and actual-versus-forecast status. Preserve source-reported values and show conversion steps. Include relevant counterevidence and the strongest reason the main conclusion could be wrong. Do not invent missing data.

8. **Synthesize for the decision.** State what the evidence supports, what remains uncertain, what the findings imply, and a recommendation with a confidence level. Clearly distinguish sourced facts, estimates, assumptions, inferences, and recommendations when their status might otherwise be unclear. Treat public reviews, forums, search trends, and company marketing as secondary or proxy signals, not representative customer research or proof of willingness to pay.

9. **Run the final quality gate and deliver.** Check the items below. If a failed check could change the conclusion, return to evidence collection or analysis and correct it. If it cannot be resolved, disclose the limitation, adjust the conclusion or confidence, and make the unresolved issue clear in the deliverable. Do not imply exhaustive research when collection was selective.

## Evidence Coverage and Recommendation Threshold

For a Quick Scan or Decision Memo, make the evidence coverage visible in proportion to the scope. Briefly state the geography, period, source types searched, and important evidence that could not be obtained. Do not imply a market-wide review from a few company or news examples.

For each decision-relevant finding, distinguish:

- **Evidence-backed fact:** directly supported by a cited source, with the source's date, scope, and access status clear.
- **Estimate:** calculated from stated inputs and assumptions; show the method and uncertainty.
- **Inference / hypothesis:** analyst interpretation or a proposed explanation, explicitly labeled and linked to the evidence it uses.
- **Unknown:** not established by the available evidence; do not fill the gap with a plausible-sounding claim.

Keep market denominators separate. Production, eligible raw material, installed or planned capacity, shipments, sell-through, revenue, and consumer demand are different measures. Never convert one into another without a supported method. When no reliable category-specific market size exists, say so, explain why a broader proxy cannot answer the question, and identify the smallest evidence-gathering step that could close the gap.

Match the recommendation to evidence strength:

- **Supported:** key decision criteria are backed by sufficiently relevant evidence and material conflicts are resolved or bounded.
- **Directionally supported / conditional:** evidence points one way, but important assumptions or coverage gaps remain; state the conditions and what could reverse the view.
- **Insufficient evidence:** the available evidence cannot support an entry, investment, scale-up, or go/no-go recommendation. Offer a proportionate validation plan instead of implying the action itself is justified.

Do not recommend a pilot, launch, investment, or scale-up solely because a product exists, has been covered in news, appears in a retailer, or has announced capacity. Tie each proposed next step to a hypothesis, a measurable signal, and a decision it would inform. Keep confidence consistent with source quality, coverage, and unresolved uncertainty.

When a product name or category is ambiguous, list the plausible interpretations and how the market frame changes for each. If the distinction changes the research materially, ask a concise clarification before deep research; for a quick scan, state the working interpretation and keep alternate interpretations clearly separate.

## Tool, Account, and Research Boundaries

- Do not require the user to configure a third-party search API key for this Skill. Do not make Exa, Firecrawl, Similarweb, Ahrefs, Apify, other MCPs, scripts, or paid databases mandatory dependencies. If such a service is separately available and authorized in the environment, treat it as an optional source/tool and disclose its use.
- Do not bypass login walls, paywalls, CAPTCHAs, access controls, or site restrictions. If a source is blocked, mark it as unread and look for accessible corroboration.
- Do not send confidential business information, personal data, or secrets in search queries. Generalize sensitive details or ask the user how to proceed.
- Public reviews, forums, search trends, and company marketing are secondary or proxy signals. Do not present them as representative customer research, verified product quality, or proof of willingness to pay.
- The Skill may analyze user-provided interview, survey, review, CRM, or product data. It may help design a survey or interview guide. Do not claim to have conducted primary research unless the data was actually collected through available, authorized tools or supplied by the user. Do not contact respondents or publish/post content without explicit authorization.
- If a page returns an error, challenge, paywall, login requirement, or extraction failure, do not describe it as read. Retry a transient error at most once, then use another permitted source or report the limitation.
- If search providers time out or rate-limit and this affects coverage, say so. If PDFs were not readable with available tools, state that they were not reviewed; do not infer their contents from titles or snippets.

## Report Format

Use a decision-first format. Choose Quick Scan or Decision Memo depth and omit sections that do not help answer the user's question. Keep the opening concise; put methodology detail and source notes after the findings.

### Quick Scan

1. **Title and scope line:** name the market and state geography, working product definition, period, research depth, and retrieval date in one compact line. If the product name is ambiguous, state the chosen interpretation and briefly name the materially different alternative.
2. **Bottom line:** answer the user's decision question in 2–4 sentences. State whether evidence supports the conclusion, supports it conditionally, or is insufficient. Do not repeat the same caveat in later sections.
3. **Key findings:** present at most 3–5 decision-relevant findings. For each, use short labeled lines: `Evidence` (Fact / Estimate / Inference / Unknown, with the key figure and inline citation), `Assessment` (what the evidence means and its limits), and `Implication` (why it matters to the decision). Keep each finding focused on one point.
4. **Market size and evidence gaps:** report category-specific size only when supported. Separate production, eligible inputs, capacity, orders, shipments, sales, and consumer demand. If no reliable market size is available, say that directly and state why available proxy data cannot substitute for it.
5. **Risks and next step:** identify the few uncertainties most likely to change the decision. Any proposed validation step must name the hypothesis, observable metric, and decision it informs. Do not invent numeric success thresholds; ask for the user's economics or label any proposed threshold as a working assumption.
6. **Source notes:** list only material sources, each with publisher/source type, publication date when available, access status (page read or snippet only), and the claims it supports. Keep full citations beside claims as well; source notes supplement rather than replace them.

### Decision Memo

Use the Quick Scan structure, then expand only the selected modules. Add comparison tables for three or more comparable entities or figures; keep table columns consistent and label incompatible definitions instead of forcing a comparison. Put assumptions and methods next to estimates. End with a recommendation, confidence, counterevidence, and unresolved evidence gaps.

### Readability Rules

- Use descriptive headings and short paragraphs. Prefer one main idea per paragraph and no more than one or two numerical claims in a bullet.
- Do not put a long explanation, several statistics, a conversion, caveats, and citations into one bullet. Split them into separate findings or use a compact table when the measures are comparable.
- Use plain labels such as `Fact`, `Estimate`, `Inference`, and `Unknown`; do not decorate every label with bold markers. Do not leave Markdown markers such as `**` visible as literal text.
- Avoid repeating the same qualification in the opening, each finding, and the conclusion. State a limitation once where it is most useful, then refer back only if needed.
- Do not add a generic executive-summary section to a short Quick Scan when the bottom line and key findings already serve that purpose.

### Decision Memo 默认规则

Decision Memo 是需要支持实际决策时的默认深度。按上方 `Decision Memo` 结构组织内容，只保留适用于当前问题的部分；事实、估算、假设、推断和建议在容易混淆时明确标注。转述来源内容，必要时只使用简短引文。

## Quality Gate

Before delivering, confirm that:

- Every material factual claim and number has a nearby source or is labeled as an estimate or assumption.
- Source titles, URLs, dates, and access status reflect what was actually returned or read. Search snippets, entity facts, blocked pages, and promotional claims are not presented as independent verification.
- Source-reported values and units are preserved; currency/unit conversions, arithmetic, and CAGR checks are reproducible. If a decision-critical number's unit or conversion cannot be confirmed, do not present it as a definite conclusion.
- Geography, market scope, definitions, base years, and forecast periods are consistent. Incompatible estimates are not blended; differences are explained.
- Decision-critical claims have been independently corroborated where possible. Uncorroborated single-source evidence is labeled and reflected in confidence.
- Important counterevidence, coverage gaps, blocked sources, and tool failures are disclosed.
- User-provided material, public secondary signals, and actual primary research are distinguished. Reviews, comments, or search trends are not described as validated customer demand.
- The recommendation answers the stated decision and matches the strength of evidence, unresolved questions, and confidence level.
- Evidence coverage is stated at a level appropriate to the research depth; examples are not presented as a market-wide review.
- Production, input availability, planned capacity, shipments, sales, and demand are not conflated; any conversion is supported and shown.
- Ambiguous category terms are clarified or explicitly framed as assumptions, with materially different interpretations kept separate.
- Recommendations are labeled as supported, conditional/directional, or insufficiently evidenced; proposed pilots or next steps specify a hypothesis, measurable signal, and decision informed.
