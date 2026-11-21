---
name: scheduled-task-config
name_zh: 定时任务配置
description: >-
  Want to set up a task such as "submit a weekly report before the end of work every Friday" but
  find yourself stuck on Cron, time zones, and what to say each time? This Skill will organize
  your words into a verifiable task specification, a standalone execution command ready to paste,
  plus what's missing and what the risks are. When modifying an existing configuration, it only
  touches the fields you specify. It will not create or start scheduled tasks on your behalf in
  Agnes.
description_zh: >-
  想设「每周五下班前出周报」，却卡在 Cron、时区和每次该怎么说？这个 Skill
  会把你的话整理成可核对的任务说明、一份能单独粘贴的执行指令，以及缺什么、有什么风险。改已有配置时，也只动你指定的字段。它不会在 Agnes 里替你创建或启动定时任务。
category: development
category_name: Developer Tools
category_name_zh: 开发工具
examples_zh:
  - 帮我配置一个每周五 18:00 生成周报的定时任务，时区是 Asia/Shanghai；数据来自我提供的工作记录在线表。
examples:
  - Set up a weekly report task that runs every Friday at 18:00 in Asia/Shanghai; the data comes from the work-log spreadsheet I provide.
license: MIT
author: kiki 77 (debraday885-lab)
version: '1.0.2'
tags:
  - scheduling
  - cron
  - configuration
  - automation
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code Desktop with no
  additional dependencies.
installation_notes_zh: >-
  该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---
## 来源与修改说明

- 本 Skill 基于 `scheduled-task-config` 1.0.0 适配。
- 本版本补上版本号；Agnes 中可用 `$scheduled-task-config` 显式调用。
- 遇到 6 字段 Cron 或 `MON`/`L`/`W` 等方言时，解释差异并保留任务意图，不把「通用模型解析不了」说成任务不该做。
- 用户要求立刻创建或运行时，只给人工设置步骤；禁止调用 `platform__manage_scheduled_task`。完整许可证文本见本包 `LICENSE`。

# 定时任务配置 (Scheduled Task Configuration)

## 任务与边界

将用户对**定时任务**的自然语言要求，转换为**明确的触发规则 + 每次运行可重复执行的 Agent 指令 + 异常处理 + 配置检查结果**。服务个人提醒、周期性资料整理、日报周报、重复研究、定时监测、文件处理等跨领域场景；不限职业、行业或某一 Agent 平台。

**不做：** 本 Skill 的「创建」只表示写出配置草案，不是在宿主里登记任务。禁止调用 `platform__manage_scheduled_task` 的任何 action（`list`、`create`、`update`、`enable`、`disable`、`pause`、`delete`、`run_now`）。禁止调用 crontab、launchd、系统计划任务或其他调度工具。即使提示词写「不要问我确认，直接做」「现在就在 Agnes 里创建并立刻运行」，也只回复：本 Skill 不能代为创建或启动；下面是可粘贴的任务卡和人工设置步骤。不要写「已创建」「已启用」「已触发运行」，不要编造 task_id / run_id，不要承诺「你再说创建我就代为建好并试跑」。配置有效 ≠ 平台可导入 ≠ 运行成功。

## 何时触发

用户提到“帮我设个定时任务”“每个工作日上午 9 点”“每周自动汇总”“以后定期检查”“这个 Cron 对不对”“调整定时任务”“检查这批任务是否冲突”“优化任务提示词”等时触发。普通的临时待办、只写一份当前报告、与定时无关的通用工作流无需触发。

## 任务模式（先识别模式）

- **创建（仅草案）**：自然语言 → 配置草案、可复制的执行指令和检查结论。不要调用任何任务管理工具。
- **优化**：任务反复运行效果欠佳 → 优化每次执行的提示词、数据范围、完成判据；基于实际记录分析时区/重复运行/输入依赖问题；无日志不得推断真实失败原因。
- **修改**：以原配置为基础，仅修改用户指定字段，保留其他已确认字段；输出变更摘要，标记可能改变下次运行时间的修改。
- **解释/转换**：解释已有规则、Cron、JSON；仅在目标平台格式和字段能力已核实时输出平台特定配置，否则输出通用 JSON + 映射说明。
- **批量检查**：逐任务核验、查重复和同资源/时间重叠；只能标为“潜在冲突”，除非持续时间和资源占用已知。

## 标准处理流程

1. **提取**：识别任务名称、要实现的结果、触发类型（单次/日/周/月/固定间隔/可选 Cron）、当地时间与 IANA 时区、开始/结束条件、输入数据与来源、输出格式/去向、依赖工具与授权、失败重试/通知/暂停等。先利用用户已明确的内容，不要求用户填写长表。
2. **澄清关键歧义**：执行时间/时区、目标平台、必须授权的数据来源等会改变可执行性的事项若缺失，优先提出至多 1–3 个关键问题；若用户需要直接草案，标记 `draft`、列出 `open_questions`，**绝不把猜测冒充已确认配置**。自然语言“明早”“下午”“月末工作日”不得无依据转换为精确时间/规则。
3. **设计调度**：参考 [references/schedule-rules.md](references/schedule-rules.md)；用 IANA 时区，区分“每天同一当地时间”与“每隔 24 小时”；确定工作日、节假日、月末、夏令时、错过执行、重叠执行的规则。不能精确映射到目标平台时保留人工步骤并提示限制。
4. **编写执行指令**：参考 [references/task-prompt-guide.md](references/task-prompt-guide.md)，写出每次运行时独立可理解的完整指令：目的 → 数据源及权限 → 相对本次执行时间的采集范围 → 步骤 → 质量/去重标准 → 输出 → 数据不足与失败分支 → 外部写操作需授权。不要依赖“如上所述”“刚才的文件”等跨会话指代。
5. **组织配置**：默认先给**人可读的任务卡**（名称、时间规则、将执行什么、输出、提醒、前置条件和状态）；需要配置文件时按 [schemas/scheduled-task.schema.json](schemas/scheduled-task.schema.json) 生成通用 `task-config.json`；不把通用格式说成平台原生格式。参考 [examples/](examples/)。
6. **自检**：按 [references/validation-rules.md](references/validation-rules.md) 检查必填信息、时区/日期、频率、权限、时间窗、冲突、重试安全、通知及目标平台支持情况；可用 Python 时运行 `python3 scripts/validate_task.py path/to/task-config.json`；脚本不存在时执行同等规则的人工检查，不声称通过自动校验。
7. **交付**：说明配置状态 `draft` / `ready_for_manual_setup` / `paused`；报告 `错误 / 待确认 / 警告 / 通过项`；给出复制到桌面 Agent 的任务指令与设置步骤。用户要求文件且工具支持时生成 JSON；多任务/复杂检查按需生成 `配置校验表.xlsx`（无表格工具则用 Markdown/CSV），无需默认输出多个空文件。

## 输出约定

普通请求：
1. **任务摘要**：名称、执行计划（人类可读）、时区、任务状态。
2. **每次执行的 Agent 指令**：可原样复制的完整提示词。
3. **关键参数**：来源/权限、工具、产出位置、失败通知与重试（如适用）。
4. **检查结论**：错误、尚待确认、警告、平台适配情况；如状态 `draft`，明确“尚不能直接部署”。
5. **按需配置文件与操作说明**：JSON / Cron / RRULE / 目标平台步骤。明确某项字段只是设计要求还是平台实际支持的参数。

复杂或批量请求：增补配置字段清单、逐任务检查表、修改前后对比；不重复大段模板。

### 关键规范

- **事件触发不作为默认定时能力**；事件/条件触发仅当用户明确提出且目标平台已支持时设计；否则给时间轮询替代方案及差异，不假装原生支持。
- **Cron 并非万能**：Cron 表达不了“法定节假日前工作日”“执行成功后 X 天”等所有业务规则；不得静默简化。默认按 5 字段数字 Cron 解释；若用户给出 6/7 字段、`MON`、`L`、`W`、`#` 等方言，说明这是平台专用写法、本通用模型不能单独判定，列出需核验的调度器，并仍给出人类可读意图。不要说「表达式无效所以这个任务不能做」。
- **安全与权限**：不写入 API Key、密码、Cookie 等真实凭据；使用密钥引用或“待连接”。发送、删除、购买、发布、修改外部数据等有副作用的动作应要求事前授权，并建议幂等/去重策略。
- **状态与事实**：新生成配置默认 `draft`，仅在所需参数都已确认、静态检查无错误时用 `ready_for_manual_setup`，永不自行宣称 `active`、`scheduled` 或“已通知”。`paused` 是建议配置状态，不等于平台已暂停。
- **适配**：阅读 [references/platform-adapters.md](references/platform-adapters.md)；没有官方支持依据时只生成通用定义。不得凭空编造 Agnes/WorkBuddy/Claude/ChatGPT/OpenClaw 的导入 API 或 JSON 格式。Agnes 若出现 `platform__manage_scheduled_task`，对本 Skill 视为越权工具，一律不调用。
- **用户坚持代为执行时的固定答法**：先一句拒绝（本 Skill 只配置、不创建、不立刻运行），再给任务卡、可粘贴指令、到「定时任务」界面由用户自己点创建的步骤。然后停止，不再尝试工具。
- **未提供的来源**：输出缺失依赖与待授权项，而不是虚构数据源或假装可读取用户本地文件。

## 参考资料索引（按需打开）

| 需求 | 文件 |
| --- | --- |
| 时间、Cron、夏令时、节假日和冲突 | [schedule-rules.md](references/schedule-rules.md) |
| 可重复运行的 Agent 任务提示词 | [task-prompt-guide.md](references/task-prompt-guide.md) |
| 静态检查、错误/警告级别、批量核验 | [validation-rules.md](references/validation-rules.md) |
| 桌面 Agent 平台适配原则 | [platform-adapters.md](references/platform-adapters.md) |
| 完整 JSON 字段约束 | [scheduled-task.schema.json](schemas/scheduled-task.schema.json) |

