---
name: jd-tailorer
name_zh: JD 简历定制器
description: >-
  First, clearly identify the job requirements, genuine match points, and areas that need to be
  supplemented; then show a preview of the resume adjustments. Once confirmed, create a separate
  job-specific version without overwriting your master resume.
description_zh: >-
  先看清职位要求、真实匹配点与待补足的内容，再展示简历调整预览；确认后制作独立的岗位版本，不覆盖你的简历母版。
category: productivity
category_name: Office Productivity
category_name_zh: 办公效率
examples_zh:
  - 分析这份 JD 与我的简历，先给我匹配点、真实缺口。
examples:
  - Analyze this JD against my resume and first show me the real matches and the gaps.
license: MIT
author: Chasen Liao
version: '1.0.0'
tags:
  - resume
  - job-description
  - matching
  - career
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no
  additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---
# JD 简历定制器

把一份已确认的简历母版针对一个明确岗位进行事实受限的定向优化。

## 前置条件

需要用户的已确认简历母版或可核验经历材料，以及 JD 文本、职位链接或职位文件。材料不足时，先调用 `resume-content-optimization` 或 `resume-builder` 整理事实；不要把未确认的解析文本直接用于定制。

## 工作流程

1. **解构 JD。** 提取硬性要求、优先条件、核心职责、业务场景、关键词和交付物。用户限定只使用其提供的 JD 时，不补充外部岗位、链接、统计或市场结论。
2. **匹配事实。** 对每项要求标记为直接匹配、可迁移匹配、证据不足、真实差距、待确认或不适用。JD 中的词不等于用户已有能力；用户未使用 JD 原词也不等于不匹配。
3. **交付预览。** 在生成定制正文或文件前，向用户逐项展示：将前置的经历/项目、将对齐的真实术语、将删减或弱化的低相关内容，以及必须保留的真实缺口。等待用户确认。
4. **完成定制。** 只重排或改写已经确认的事实，避免关键词堆砌。输出岗位匹配分析、可复制定制正文、与母版的修改对照和待确认清单。
5. **制作独立文件。** 用户确认后，调用 `resume-builder` 创建独立 HTML，或将定制正文交给现有 Markdown 转 Office 和渲染能力。使用不同文件名保存岗位版本；不得覆盖母版。

## 匹配分析格式

使用 [岗位匹配分析模板](references/matching-analysis.md) 输出结果。不得把材料质量评分解释为面试、录用或 ATS 通过概率。

## 硬约束

- 未确认的事实、数字、技能、岗位、项目或因果关系不得进入最终简历；
- 不得把真实缺口伪装成“经验待补充”或通过堆关键词掩盖；
- 不自动提交、投递、登录招聘网站、发送邮件或覆盖现有文件；
- 不做无来源的公司、地区、行业或 ATS 风险判断。

## 来源与修改说明

本包基于 Chasen Liao 的 `jd-tailorer`（`Chasen-Liao/resume-skills`，提交 `a706ae3ad5f603d17d1c587bfb7f0b5abc6f8970`）适配。保留 JD 解构、事实匹配、变更预览和版本隔离；移除了上游的本地脚本、Canvas 与 Git 操作要求，改为同 Agnes 的内容、Office 转换和渲染能力协作。许可证全文见包根 `LICENSE`。
