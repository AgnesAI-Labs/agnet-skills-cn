# Agent 定时任务平台适配规则

## 核心原则

`scheduled-task.schema.json`定义的是**跨平台任务意图模型**，不是任何平台官方 API 或可直接导入文件。真实平台能力、可用入口、是否允许创建任务及执行环境可能随版本/账号/设备变化。

适配步骤：
1. 确认用户指定的产品、版本与入口（桌面/网页/移动/CLI），必要时查阅当前官方文档。
2. 先给通用的任务卡与可粘贴执行提示词，明确需由谁启用调度。
3. 逐一映射：任务名称、提示词、频率与时区、权限、通知、重试、暂停。目标不支持的字段列为 `unsupported_fields` 和人工处理步骤。
4. 目标平台没有明确导入 API/格式时，**不要杜撰平台原生 JSON**；可以给 UI 配置步骤，但不要说“复制 JSON 即可导入”。
5. 凡需应用自身启动实际任务，必须由用户在该应用中确认；本 Skill 不执行。

## 典型平台注意事项（能力提示，不是导入格式）

| 平台 | 设计注意 | 输出方式 |
|---|---|---|
| Agnes / 其他桌面 Agent | 具体调度入口、时区、参数需按实际版本核验。本 Skill **不得**调用 `platform__manage_scheduled_task`（list/create/run_now 等）；即使用户要求「直接做」也只给界面手工步骤 | 通用任务卡 + 执行指令 + UI 手动配置指引 |
| WorkBuddy | 自然语言创建任务的功能可能与权限、工作空间、通知、产品版本有关 | 先生成可粘贴任务指令，按实际界面填写 |
| Claude Cowork | 任务可包含执行指令、频率与环境/权限等；云端/本地任务能力可能有区别 | 任务提示词 + 适用的频率建议，其他参数依官方入口 |
| ChatGPT Tasks | 原生定时任务的频率与应用事件触发受套餐和功能可用性限制；不假定自定义 Cron 或 JSON 导入 | 自然语言描述 + 应在“已安排”中核对的设置 |
| OpenClaw | 存在多类调度选项及 CLI；字段/标志/时区语义依官方文档版本 | 已核对版本时才给 CLI 命令；否则先给通用配置 |
| 系统 Cron / launchd / Windows Task Scheduler | 各平台时间语义、重试、通知和权限不同；通常不能直接执行 Agent 指令，需有具体命令或脚本入口 | 分开给调度规则和执行入口要求，必要时提醒人工安装 |

## 兼容性核对表

| 字段 | 需要核实 |
|---|---|
| `schedule` | 单次/周期/Cron/事件是否原生支持；时区是否能设置；是否仅支持固定频率 |
| `execution.instruction` | 该入口是否支持完整 Agent 提示词及插件/Skill 调用 |
| `execution.sources` | 数据源能否在无人值守运行时访问；凭据、连接器授权是否持续有效 |
| `execution.working_directory` | 是否允许本地目录；云端运行与桌面运行差异 |
| `retry` / `controls` | 重试、错过补跑、并发限制、暂停是否可配置 |
| `notifications` | 推送/邮件/平台内通知是否可用且授权 |

## 重要反例

- 不能把通用 `task-config.json` 标成“Agnes 可以直接上传”的 JSON。
- 不能把 `0 9 * * 1-5` 当成所有平台都可输入的配置。
- 不能把“执行完自动发送到微信群”当成不需要用户授权的原生功能。
- 不能在加载本 Skill 后调用 Agnes `platform__manage_scheduled_task` 来证明「已经设好」。

## 官方资料（核验日期：2026-11-12）

- Agent Skills 规范：https://agentskills.io/specification
- ChatGPT Tasks：https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
- Claude Cowork：https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork
- OpenClaw schedules：https://docs.openclaw.ai/automation/cron-jobs/schedules

以上来源用于说明**功能差异和验证方法**，不是将具体运行时参数固定在 Skill 中。对平台真实配置的生成应以当前版本文档为准。
