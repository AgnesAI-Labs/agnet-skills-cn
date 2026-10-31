---
name: scientific-thinking-literature-review
name_zh: 文献综述
description: >-
  Turn a research question into a reproducible literature review: search
  protocol, screening, thematic synthesis, evidence grading, citation checks,
  and a search log. Searches and logs when public sources are reachable;
  otherwise it synthesizes only the records or PDFs the user provided and says
  no systematic search was run. Asks for a question and material when neither is
  given. Not for translation, coding, or single-paper review scoring.
description_zh: >-
  把研究问题做成可复现的文献综述：检索协议、筛选、主题综合、证据分级和引用核对，并留下检索日志。用户说“帮我做文献综述”“梳理这个领域现状”“这些题录帮我综合一下”时使用。
  能访问公开库就检索并记录；否则只综合用户给的题录或 PDF，不得声称已做系统检索。没有问题也没有文献时先补问。订餐、写代码、纯翻译、单篇审稿打分不要用本 Skill。
category: education
category_name: Education & Research
category_name_zh: 教育科研
examples_zh:
  - 帮我做一份关于大模型辅助代码审查的研究现状综述
  - 梳理这个领域现在的研究现状
  - 这些题录帮我综合一下
examples:
  - Build a literature review on LLM-assisted code review
  - Map the current state of this research area
  - Synthesize these records for me
author: agnes
version: '1.1'
tags:
  - academic
  - literature-review
  - research
  - citations
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies. Reviewing without web access is
  supported and is reported as a limited review.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。无法联网时仍可使用，但只综合用户提供的材料，并在结果里注明。
---

## 来源与修改说明

- 本 Skill 基于 [scientific-thinking-literature-review](https://github.com/affaan-m/ecc) 适配，调用名：`scientific-thinking-literature-review`。
- 相对 `agnes1` 的变化：
  - 证据表只用标准 Markdown 表格：单元格内禁止 `<br>`、HTML 和硬换行；一行一条研究，过长内容改到表下列表。
  - 档位 B：抽取表只填用户材料里出现的字段，不把通识或百科里的实验数字写进证据表。
  - 未读全文时，具体疗效/指标数字必须标明「来自摘要/二次报道」或放入「尚需核对」，不要写成已读全文结果。
- 上游许可证全文见本包 `LICENSE`（MIT，Copyright (c) 2026 Affaan Mustafa）。

# 文献综述

在学术、生物医学、技术或科学主题上，把问题做成可复现的综述：计划检索、筛选来源、综合证据、核对应和留下日志。

## 何时使用

- 做叙述性、范围性或系统性文献综述。
- 综合某一研究问题的现状。
- 找缺口、矛盾或后续研究方向。
- 为论文或报告准备有文献支撑的背景。
- 比较同行评议、预印本、专利和技术报告中的证据。

不要用于：点餐、写代码、纯翻译，或只要给单篇稿件打分（那是学术评审，不是本流程）。点餐请求直接退出本 Skill，不要输出综述模板。

## 检索能力与降级

开始综合前，先标明本次实际用了哪一档，并写进输出里的「证据来源」：

| 档位 | 条件 | 允许写出的结论 |
| --- | --- | --- |
| A. 公开检索 | 当前环境能访问公开网页或文献库（如 PubMed、arXiv、出版社摘要页） | 可按协议检索、记检索日志；能核到的 DOI/PMID/arXiv ID 再写入参考文献 |
| B. 用户供稿 | 用户给了题录、摘要、PDF 或粘贴正文，但无法外检索 | 只综合这些材料；综述类型写「基于用户提供文献的 scoping/narrative」；不得写已检索某库、不得编造未出现的条目 |
| C. 材料不足 | 既没有可检索条件，用户也没给文献 | 先要研究问题和/或题录/文件；不要输出完整综述或参考文献表 |

若用户要求 systematic review 或 meta-analysis，但只有 B 或 C：说明达不到可复现系统检索，改做 scoping/narrative，或请用户补充检索结果导出。

不要把搜索摘要片段当成已读全文。未打开全文时，发现与主张分开写，把「需读全文」列入局限。

不要编造检索命中数、PMID、DOI 或论文标题。核不到的标识不要写进参考文献，放到「尚需核对」。导不出命中数时写「未导出」，不要填一个假数字。

档位 B：抽取表、主题综合和参考文献都只使用用户材料里出现的题名、作者、年份和标识。训练数据或百科里的样本量、语料规模、BLEU/GLUE 等数字，不得当作本次证据写入抽取表；若必须提示，放到「缺口与局限」并写明「非用户材料、未在本次核验」。

档位 A：未读全文时，具体疗效百分比、血红蛋白变化、样本量等须写成「来自摘要/新闻稿，未读全文」，或只放在「尚需核对」。

## 综述类型

- **Narrative review**：宽综合，适合定向。
- **Scoping review**：画概念、方法与证据缺口。
- **Systematic review**：预定义协议、可复现检索、显式纳入排除。
- **Meta-analysis**：系统综述加上定量效应合并。没有效应量数据时不要做 meta-analysis，也不要编造合并效应。

询问用户需要哪一档严谨程度。未指定时：探索性工作默认 scoping；声称发表或临床主张时，仅在达到档位 A 且有可复现协议时才按 systematic 写，否则明确降级。

## 流程

### 1. 明确问题

把提示转成可检索的研究问题。

临床医学或生物医学用 PICO：

- Population
- Intervention or exposure
- Comparator
- Outcome

技术工作用：

- 系统或领域
- 方法或干预
- 比较基线
- 评价指标

若用户只给了文献、没有问题：从材料归纳候选问题，请用户确认后再综合。

### 2. 计划检索

在收集来源前写出协议：

- 拟检索的库
- 日期范围
- 语言
- 文献类型
- 纳入标准
- 排除标准
- 确切检索式

建议覆盖（档位 A 时按实际能访问的选用，不能访问的在日志里写「未检索」）：

- 生物医学：PubMed
- 计算机、数理、预印本：arXiv
- 较广的发现：Semantic Scholar 或 Crossref
- 领域来源：临床试验注册、专利、标准或官方技术文档

档位 B：跳过外检索，把用户清单当作已获得集合，仍写纳入排除规则并说明来源仅限用户提供。

### 3. 检索并记录

检索日志要能复现。表格遵守下方「表格与版式」。档位 B 把「库」写成「用户提供」，条数为用户实际给出的条目，检索式写「不适用」。

原始 ID、URL、DOI、摘要和笔记与最终综述正文分开保存。

### 4. 去重

顺序：

1. DOI
2. PMID 或 arXiv ID
3. 完全相同标题
4. 归一化标题 + 第一作者 + 年份

记录去掉多少重复。

### 5. 筛选

分阶段：标题 → 摘要 → 全文（只有当前读得到的全文）。

系统性工作时记录排除原因：错误人群、错误干预、错误结局、非原始研究、重复、无全文、超出日期。

### 6. 抽取

证据摘要用标准 Markdown 表，一行一条研究。单元格只写短语，不把方法、结局、局限堆进同一格。

列：研究｜设计｜对象｜方法｜对照｜结局｜要点｜局限。

列不下的细节放到表下的条目列表，例如：

```markdown
| 研究 | 设计 | 对象 | 方法 | 对照 | 结局 | 要点 | 局限 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Frangoul 2024 | III 期单臂 | 重度 SCD | CRISPR-Cas9 编辑 BCL11A | 无 | 摘要称多数患者无重度 VOC | 已获批 CRISPR 疗法 | 单臂、样本小 |

- Frangoul 2024（PMID …）：具体百分比、随访月数见「尚需核对」或摘要原文，未读全文则不在表内展开。
```

技术文献可在表下补数据集、基准、指标。

### 7. 综合

按主题归类，不要一篇篇摘要堆砌。

可用镜头：最强证据、冲突证据、方法弱点、人群或数据限制、时效与重复、实践含义、未回答问题。

主张按把握分开：

- **高**：多来源、质量高、有重复
- **中**：说得通，但受样本、方法或时效限制
- **低**：早期、推测、单来源或测量弱

集合外的后续工作（用户题录或本次检索未纳入的）只写在「缺口」，不要写进证据摘要表。

### 8. 核对引用

定稿前：

- 核得到的才写 DOI、PMID、arXiv ID 或官方 URL
- 核对作者名与年份（以当前可读文本为准）
- 不要把论文没有的主张安到它头上
- 预印本标成预印本
- 综述与原始研究分开标注
- 未打开的原文列入「尚需核对」，不要写成已核原文

## 表格与版式

对话里的表必须能被普通 Markdown 渲染，不要为了挤格而写 HTML。

- 只用 `|` 分隔的 Markdown 表；表头与分隔行 `| --- |` 齐全。
- **单元格内禁止** `<br>`、`<br/>`、其他 HTML 标签、以及单元格内部换行。
- 一行只描述一条研究或一条检索记录；禁止把整表粘成一段带很多 `|` 的长文本。
- 一格只放一句或几个词。PMID、随访、百分比等若使该格变长，改到表下编号列表。
- 列数尽量不超过 8。需要更多字段时拆成「主表 + 表下注释」，不要加宽到横向挤爆。
- 不要用 HTML `<table>`。

## 输出模板

```markdown
# 文献综述：<主题>

生成日期：<date>
综述类型：<narrative | scoping | systematic | meta-analysis>（实际达到的档位）
证据来源：<A 公开检索 / B 用户供稿 / C 不足未完成>
检索窗口：<dates 或 不适用>
数据库：<实际用到的，未用到的不要写>

## 研究问题

## 检索策略

## 纳入与排除

## 证据摘要

（此处为短单元格 Markdown 表，表下可跟列表）

## 主题综合

## 缺口与局限

## 参考文献

## 检索日志

## 尚需核对
```

## 注意

- 不要把搜索摘要片段当成证据。
- 预印本、综述和原始研究必须标注，不要混成同一证据级别。
- 不要漏掉阴性或冲突发现。
- 没有可复现协议，不要声称 systematic-review 严谨度。
- 单库结论必须把范围限制在该库；档位 B 必须写明文献集合来自用户。
- 用用户的对话语言撰写。
