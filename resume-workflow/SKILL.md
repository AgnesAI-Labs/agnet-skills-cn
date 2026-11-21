---
name: resume-workflow
name_zh: 简历求职工作流
description: >-
  Start from your old resume or real experiences, gradually sort out credible content, and build a
  master resume that can be maintained over the long term; when you need to apply for a specific
  position, generate a separate customized version.
description_zh: >-
  从旧简历或真实经历开始，逐步梳理可信内容，建立可长期维护的简历母版；需要投递具体岗位时，再生成独立的定制版本。
category: productivity
category_name: Office Productivity
category_name_zh: 办公效率
examples_zh:
  - 帮我用旧简历建立一份可编辑母版，再根据这份产品运营 JD 制作投递版本。
examples:
  - Use my old resume to build an editable master, then create an application version for this product operations JD.
license: MIT
author: Chasen Liao
version: '1.0.0'
tags:
  - resume
  - workflow
  - job-search
  - career
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no
  additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---
# 简历工作流

为用户提供一条可追溯的简历制作路径：先核验经历与目标，再制作可编辑母版，最后按具体 JD 生成独立的投递版本。

## 何时使用

- 用户想制作、更新、优化或持续维护一份简历；
- 用户既需要内容优化，也需要可编辑 HTML、Word 或 PDF 交付；
- 用户要为多个公司或岗位维护不同版本。

不要用于自动投递、登录招聘平台、联系招聘方或承诺通过 ATS、面试、录用或薪资结果。

## 总体流程

1. **确定任务与材料。** 读取用户提供的简历、经历、项目材料和 JD；确认目标岗位、地区、语言和交付格式。只缺少当前步骤必要信息时再追问。
2. **内容与事实阶段。** 对诊断、经历挖掘、成果提炼、真实性核验、招聘者视角审核，优先调用 `resume-content-optimization`。未确认的事实、数字、头衔和因果关系不得写入可复制正文。
3. **母版阶段。** 需要新建或更新可编辑基础简历时，调用 `resume-builder`。母版是后续定制的内容与版式基线；除非用户确认，不覆盖已有文件或版本。
4. **岗位定制阶段。** 用户提供具体 JD 后，调用 `jd-tailorer`。先交付岗位要求地图、匹配证据、真实缺口和拟改动预览；只有用户确认预览后，才制作该岗位版本。
5. **文件交付阶段。** 可编辑 HTML 由 `resume-builder` 制作；需要 Word 时，将已确认正文交给现有“Markdown 转 Office”能力；需要 PDF、截图或视觉检查时交给现有 Rendex/渲染能力。只有工具实际返回产物后，才能说文件已经生成。

## 版本与隐私边界

- 每个岗位定制版单独命名并保存，至少包含公司、岗位和日期；不得静默覆盖母版。
- 用户未确认的内容只放入待确认清单或匹配分析，不进入最终简历。
- 不主动索取身份证号、家庭住址、婚姻、健康等与简历无关的敏感信息。
- 不自动初始化、提交或推送 Git，不上传简历到任何招聘网站或第三方服务。

## 交付说明

根据用户请求，清楚列出：材料范围、已确认亮点、可复制正文、待确认事项、岗位匹配和真实缺口、已生成的文件及其路径（如实际生成）。

## 来源与修改说明

本包基于 Chasen Liao 的 `resume-workflow`（`Chasen-Liao/resume-skills`，提交 `a706ae3ad5f603d17d1c587bfb7f0b5abc6f8970`）适配。为适配 Agnes 专家协作，移除了对上游本地 Canvas、Node/Python 渲染脚本和 Git 操作的必需依赖，改为衔接现有的内容优化、Office 转换和 Rendex 能力；许可证全文见包根 `LICENSE`。
