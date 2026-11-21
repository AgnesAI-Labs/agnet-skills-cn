# 内容选题与排期（Content Planning & Scheduling）

帮助普通用户和专业团队把“要发什么内容、为什么做、什么时候做”变成可执行的选题池与内容日历。

- **名称**：内容选题与排期
- **技能标识**：`content-planning-scheduling`
- **版本**：v1.0.4
- **作者**：[kiki 77 (debraday885-lab)](https://github.com/debraday885-lab)
- **分类**：内容创作
- **许可证**：MIT，详见 `LICENSE`

## 可以做什么

- 从零想选题：通过兴趣、经验、受众问题、产品信息、已有素材提出内容主题与切入角度。
- 领域信息很宽泛时，给出可迁移的内容机制和具体选题；可用可替换案例，但不把未提供的材料、工艺或产品当作既有事实，也不把选题写成空泛主题。
- 整理与筛选：把笔记、留言、访谈摘要和已有选题去重分类、评估优先级。
- 规划栏目/系列：把散乱的灵感变成长期可持续的内容结构。
- 编排发布节奏：根据周期、渠道、人员、可用时间和任务依赖安排周/月内容日历。
- 动态调整：延期、插入活动、更新状态、根据用户提供的表现数据调整后续计划。

适用于小红书、抖音、公众号、视频号、B站、博客、知乎、YouTube 等常见内容平台；不绑定特定平台，不要求账号授权。

## 谁可以用

个人创作者、自媒体博主、品牌/市场团队、电商商家、知识分享者、教育工作者、企业内容负责人，以及任何希望持续输出内容的人。

## 直接这样说

在 Agnes 中，如需明确指定本 Skill，可在请求前写 `$content-planning-scheduling`。

1. “我刚开始做手工账号，没经验，先给我三个内容方向和十个选题。”
2. “把我这些客服问题变成小红书选题，帮我去重、排序，给出角度和依据。”
3. “我每周能花 6 小时，想稳定发 2 条短视频，帮我排 4 周的计划。”
4. “做一期‘30 天学摄影’系列，给我每期主题和合理顺序。”
5. “我的内容日历里有 3 条延期了，已发布内容不要改，只调整未来两周。”
6. “围绕产品上新做内容预热、发布、答疑计划，不需要直接帮我发帖。”

## 输出方式

默认直接在对话中提供表格和说明。批量选题或完整排期时，如运行环境支持文件工具，可生成真正的 `内容选题池.xlsx` 与 `内容发布日历.xlsx`；否则提供可复制的 Markdown 表或 CSV。复杂任务还可以输出系列规划、执行清单和调整记录。**不会假装已经导出文件或自动同步平台。**

内置两份 CSV 空模板：
- `assets/templates/topic-pool-template.csv`
- `assets/templates/publishing-calendar-template.csv`

## 安装与文件结构

```text
content-planning-scheduling/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── planning-workflow.md
│   ├── topic-evaluation.md
│   └── output-schemas.md
├── assets/
│   └── templates/
│       ├── topic-pool-template.csv
│       └── publishing-calendar-template.csv
```

这是标准 `SKILL.md` + 可选参考资料/素材的 Agent Skill 目录结构。将**整个目录**（或压缩包，若宿主支持 ZIP 导入）加入支持 Agent Skills 的技能目录或技能市场；路径、安装操作及是否能自动读取附属文件以实际宿主实现为准。

## 来源与修改说明

- 本版本基于 `content-planning-scheduling` v1.0.0 维护，许可证全文见本包 `LICENSE`。
- v1.0.4 禁止在缺少用户计划时用示例数据填满导出表。未改变「不自动发布、不编造数据」的功能边界。
- 市场分发包不含 `tests/`；验收用例只放包外测试目录。

## 能力边界

不自动发布，不接管平台账号，不主动获取私人后台数据，不承诺真实热搜或流量效果，不默认具备实时联网能力。可给出标题角度和简要提纲，但不替代专门的完整文案、设计及视频制作能力。未经验证的选题机会必须写明“待验证”。

## Development & reuse

This is a general-purpose editorial planning skill. It supports idea generation, topic prioritization, series planning, editorial calendars, and re-planning without requiring access to social-media accounts. The instructions follow the user's language and make no assumption of real-time trend access. Licensed under MIT.
