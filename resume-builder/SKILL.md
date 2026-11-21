---
name: resume-builder
name_zh: 可编辑简历构建器
description: >-
  Organize your real experiences into a clear, continuously editable master resume; update
  incrementally from an old resume, or sort out education, experience, projects, and skills from
  scratch.
description_zh: >-
  把真实经历整理成清楚、可继续编辑的简历母版；从旧简历增量更新，也可从零梳理教育、经历、项目和技能。
category: productivity
category_name: Office Productivity
category_name_zh: 办公效率
examples_zh:
  - 根据我的旧简历制作一份可编辑的中文基础简历。
examples:
  - Build an editable Chinese base resume from my old resume.
license: MIT
author: Chasen Liao
version: '1.0.2'
tags:
  - resume
  - html
  - pdf
  - career
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no
  additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---
# 可编辑简历构建器

将用户确认的经历整理成适合继续编辑、转换和定制的简历母版。

## 输入与事实边界

可接受旧简历、经历描述、项目材料、教育信息、技能、目标岗位或已确认的简历正文。

1. 有旧简历时，先列出已识别事实、模糊项和可能过期项；只对缺口增量追问。
2. 没有旧简历时，按基础信息、教育、经历、项目、技能的顺序逐步采访，不一次性抛出问卷。
3. 对经历职责、成果和数字需要更深入核验或招聘者视角判断时，调用 `resume-content-optimization`。
4. 只将用户确认的事实写入最终正文；待确认内容只留在清单，不写入简历。

## 母版结构

根据用户背景和目标，组织为：姓名与联系方式、求职意向或职业概述、核心能力、工作/实习经历、项目经历、教育背景，以及确有必要的证书或作品集链接。

- 经历按目标岗位相关性排序；应届生可前置项目或校园经历。
- 每条经历写清个人职责、行动、交付物和可核验影响；团队数据与个人贡献分开标明口径。
- 严格 ATS 场景采用单栏、标准标题、可复制正文和稳定阅读顺序；不依赖图片或装饰承载关键信息。
- 不把接触过的工具写成精通，不把团队成果写成个人成果，不为填满一页虚构内容。

## 制作与交付

1. 在用户确认正文和版式方向后，若当前环境具备受控文件写入能力，创建独立、单文件、可编辑的 HTML 简历；使用系统字体回退，避免把关键文字做成图片。包内保留六套视觉样式、HTML 示例、PDF/PNG 渲染脚本、版面测量和 ATS 校验器。
2. 生成前先告知目标文件名和位置；如同名文件已存在，先取得用户确认再覆盖。
3. 需要可编辑 Word 时，输出结构化 Markdown/正文并交给已配置的“Markdown 转 Office”能力。不得在其未实际运行时声称 Word 已生成。
4. 需要 PDF、截图或视觉复核时，优先使用包内 `scripts/render_resume.mjs` 与 `scripts/validate_resume.py`；只有用户授权并且 `runtime/` 依赖已安装时才执行。也可使用已配置的 Rendex/渲染能力；只有实际检查到产物后，才报告文件交付完成。
5. 用户明确要求本地逐项修改已有视觉 HTML 时，可在已初始化运行时中使用 `runtime/bin/resume-skills.mjs editor` 启动仅监听本机回环地址的 Canvas 编辑器。编辑后必须重新运行渲染与校验；不要自动启动编辑器、打开端口或覆盖用户文件。
5. 交付时说明母版与可针对岗位调整的部分；需要具体职位定制时转交 `jd-tailorer`。

## 不要做

- 未经用户明确授权，不执行 npm、pip、Python、PowerShell 或 Git 命令；
- 未经用户明确授权，不下载字体、浏览器或其他运行时依赖；
- 不上传、发送、发布用户简历；
- 不在未取得确认时修改、删除或覆盖用户文件。

## 来源与修改说明

本包基于 Chasen Liao 的 `resume-builder`（`Chasen-Liao/resume-skills`，提交 `a706ae3ad5f603d17d1c587bfb7f0b5abc6f8970`）适配。保留“先确认事实、制作母版、以 HTML 作为可编辑交付”的核心流程，以及上游六套样式、HTML 示例、Node/Playwright 渲染、PNG 预览、版面测量、Python ATS 校验和本地 Canvas 编辑器；将运行时置于包内 `runtime/` 并修正脚本路径。许可证全文见包根 `LICENSE`。
