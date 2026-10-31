---
name: scientific-thinking-scholar-evaluation
name_zh: 学术评审
description: >-
  Review papers, proposals, methods sections, literature reviews, and research
  writing against a fixed nine-dimension rubric: scores, hard defects separated
  from improvable parts, and concrete revision advice. Requires the user to
  supply the text, section, or file; no scores without material.
description_zh: >-
  按固定量规评审论文、开题、方法章节、文献综述或研究写作：九个维度打分，分开硬伤和可改处，并给出具体修订建议。用户说“帮我审这篇”“看一下方法严不严谨”“主张有没有文献支撑”且已提供或可以提供待评材料时使用。
  没有正文、章节或文件时先要材料，不编造分数。订餐、写代码、纯翻译、医疗诊断或法律结论不要用本 Skill。
category: education
category_name: Education & Research
category_name_zh: 教育科研
examples_zh:
  - 帮我审一下这篇论文的方法部分严不严谨
  - 这个开题报告有哪些硬伤
  - 这条结论有没有文献支撑
examples:
  - Review the methods section of this paper
  - Find the weak points in this proposal
  - Check whether this claim is supported by its citations
author: agnes
version: '1'
tags:
  - academic
  - review
  - research
  - writing
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies. The user supplies the manuscript
  text, section, or file to review.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。待评审的正文、章节或文件由用户提供。
---

## 来源与修改说明

- 本 Skill 基于 [scientific-thinking-scholar-evaluation](https://github.com/affaan-m/ecc) 适配，调用名：`scientific-thinking-scholar-evaluation`。
- 本版本变化：
  - 没有待评材料时先补问正文、章节粘贴或文件，不编造分数或证据核对。
  - 用用户的对话语言撰写评价；量规维度在输出中中英并列。
  - 订餐、写代码、纯翻译等非学术评审请求不进入本流程。
- 上游许可证全文见本包 `LICENSE`（MIT，Copyright (c) 2026 Affaan Mustafa）。

# 学术评审

按可重复量规评价学术或科学文本。先确认待评对象和评价范围，再打分并给出可执行的修改建议。

## 何时使用

- 评审研究论文、开题报告、学位论文章节或文献综述。
- 核对主张是否有被引文献支撑。
- 评价方法、研究设计、分析或局限性。
- 用同一量规比较两篇及以上作品的质量或相关性。
- 产出用于修改的结构化反馈。

不要用于：点餐、写代码、纯翻译、医疗诊断、法律案件结论，或用户未提供、也无法提供待评材料的空评。

## 材料要求

开始打分前，必须有待评材料，例如：粘贴的正文或章节、用户给出的文件，或当前对话里已经完整出现的稿件。

若材料不足：

1. 说明还缺什么（全文、摘要+方法+结果、还是仅某一节）。
2. 请用户粘贴文本或提供文件。
3. 在材料到达前不要输出 1–5 分、总分或“证据已核对”的结论。

若用户指定了文件但无法读取：说明读不到，请改粘贴关键章节，不要根据文件名或标题编造评价。

引用是否支撑主张：只根据当前可读文本判断。未打开被引文献时，把需要外核的条目放进「尚需核对的证据」，不要写成已经核对原文。

## 评价范围

先识别文本类型：

- 实证研究论文
- 理论论文
- 技术报告
- 系统综述或叙述性综述
- 研究计划 / 开题
- 学位论文章节
- 会议摘要或短文

再选择范围：

- **全面**：全部量规维度
- **专项**：一两个维度，例如方法或引用
- **比较**：多篇作品用同一量规排序

用户未指定时：单篇完整稿默认全面；用户只贴方法节则只评方法及相关维度，其余标 `N/A`。

## 量规

适用维度按 1 到 5 打分：

- 5：优秀；清楚、严谨、达到可投稿水准
- 4：良好；只需小改
- 3：尚可；有实质缺口但能用
- 2：弱；需要大改
- 1：差；效度或表达有严重问题

不适用的维度用 `N/A`。

### 1. 问题与研究问题（Problem and Research Question）

- 问题是否清楚、具体？
- 贡献是否有意义？
- 范围和假设是否写明？
- 研究问题与声称的贡献是否匹配？

### 2. 文献与背景（Literature and Context）

- 是否覆盖相关已有工作？
- 是综合，还是只罗列文献？
- 缺口是否判断准确？
- 近期文献与奠基文献是否平衡？

### 3. 方法（Methodology）

- 方法能否回答研究问题？
- 设计选择是否有理由？
- 变量、数据、被试或材料是否写清？
- 他人能否复现？
- 是否承认伦理与现实约束？

### 4. 数据与证据（Data and Evidence）

- 数据来源是否可信、合适？
- 样本量或语料覆盖是否足够？
- 纳入、排除和预处理是否有记录？
- 是否讨论缺失数据与偏倚风险？

### 5. 分析（Analysis）

- 统计、质性或计算方法是否合适？
- 基线与对照是否公平？
- 需要时是否有不确定性、敏感性或稳健性检查？
- 是否考虑其他解释？

### 6. 结果与解释（Results and Interpretation）

- 结果是否表达清楚？
- 主张是否落在证据范围内？
- 图、表、指标是否可读？
- 阴性或零结果是否诚实处理？

### 7. 局限与效度威胁（Limitations and Threats to Validity）

- 局限是否具体，而不是套话？
- 是否处理内部、外部、构念和结论效度风险？
- 是否区分推测与已证明结果？

### 8. 写作与结构（Writing and Structure）

- 论证是否好跟随？
- 各节是否围绕研究问题组织？
- 定义和符号是否清楚？
- 语气是否精确、学术？

### 9. 引用（Citations）

- 被引文献是否支撑所附着的主张？
- 能用原始文献时是否用了原始文献？
- 综述是否标成综述？
- 预印本是否标成预印本？
- 题录和链接是否正确（仅限当前材料可见部分）？

## 评审步骤

1. 读摘要、引言、图表和结论，抓住声称的贡献。
2. 读方法与结果，判断证据质量。
3. 用当前可读文本核对最强主张；不能外核的标为待核。
4. 给每个适用维度打分，并写一句证据。
5. 把阻断发表或阻断答辩的问题与普通修改建议分开。
6. 以可执行的下一步修改结束。

## 输出模板

```markdown
# 学术评审：<对象>

## 总体判断

- 总分：<1-5 或 N/A>
- 把握：<高 | 中 | 低>
- 摘要：<3–5 句>

## 维度分数

| 维度 | 分数 | 证据 | 修改优先级 |
| --- | ---: | --- | --- |
| 问题与研究问题 |  |  |  |
| 文献与背景 |  |  |  |
| 方法 |  |  |  |
| 数据与证据 |  |  |  |
| 分析 |  |  |  |
| 结果与解释 |  |  |  |
| 局限与效度威胁 |  |  |  |
| 写作与结构 |  |  |  |
| 引用 |  |  |  |

## 硬伤

## 建议修改

## 尚需核对的证据
```

## 注意

- 分数不能代替具体反馈；每个分数旁要有来自文本的证据。
- 不要因为稿件省略了其范围之外的维度而扣分。
- 不要把引用量、期刊或作者声望当成质量证明。
- 不要仅因摘要里出现主张就接受它。
- 不要在没有待评材料时输出完整评分表。
