# 定时任务配置 · Scheduled Task Configuration

**中文名称：** 定时任务配置  
**Skill ID：** `scheduled-task-config`  
**版本：** 1.0.2  
**分类：** 办公效率  
**许可：** MIT  
**作者：** [kiki 77 (debraday885-lab)](https://github.com/debraday885-lab)

## 这是什么

一个面向公众、可在支持 Agent Skills 的桌面 AI Agent 中使用的**定时任务配置增强 Skill**。用户不需要先懂 Cron 或 JSON，只要说“每周五下午生成工作周报”，Skill 就能帮助整理任务触发规则、Agent 执行提示词、数据来源、输出要求和异常处理，并按需生成标准配置及检查结果。

它**不是调度服务或常驻自动化进程**。不会替用户直接创建、启动、暂停任务或操作外部系统，也不会调用 Agnes 的 `platform__manage_scheduled_task`。通用 JSON 用于沟通与适配，不保证可直接导入任意 Agent 平台。

## 适用场景

- **周期汇总**：日报、周报、会议准备、学习复盘。
- **定时研究**：行业新闻摘要、竞品动态、资料更新检查。
- **日常提醒**：固定时间提醒、周期计划、待办回顾。
- **技术任务**：生成 Cron 规则草案，检查配置中的时区、参数和异常策略。
- **已有任务管理**：阅读现有定时配置、优化 Agent 指令、修改频率、检查多任务冲突。

## 直接这样调用

在 Agnes 里可在句子前加 `$scheduled-task-config`，明确调用本 Skill。

> $scheduled-task-config 帮我配置一个每周五 18:00 生成周报的定时任务，时区是 Asia/Shanghai；数据来自我提供的工作记录；输出 Markdown，并且找不到记录时不编造内容。

> $scheduled-task-config 每个工作日上午 9 点整理最新消息，我想复制到桌面 Agent 的定时任务界面里。帮我写完整执行指令并检查缺少的权限。

> $scheduled-task-config 帮我检查这段 Cron 有没有问题，并解释下次运行时间会受什么时区影响：`0 9 * * 1-5`。

> $scheduled-task-config 这是已有的任务 JSON：……。只把执行时间从每天 8:00 改为 8:30，不要动其他规则，并列出改动。

> $scheduled-task-config 下面是 10 个定时任务，帮我检查频率、重复与潜在资源冲突，输出校验表。

## 默认交付

1. 任务概览：名称、时间、频率、时区、状态和前置条件。
2. 可复制给 Agent 的**每次执行指令**（不依赖本次对话历史）。
3. 配置风险/待确认项及修正建议。
4. 用户需要时生成 `task-config.json`；多任务或复杂校验按需输出 `配置校验表.xlsx`。
5. 指定已知平台时，提供与平台能力一致的适配建议和人工设置步骤。

## 文件结构

```text
scheduled-task-config/
├── SKILL.md                         # 入口、触发与行为规则
├── README.md                        # 本文
├── LICENSE                          # MIT
├── references/
│   ├── schedule-rules.md            # 时间规则/时区/DST/Cron
│   ├── task-prompt-guide.md         # Agent 执行指令标准
│   ├── validation-rules.md          # 检查、冲突、风险
│   └── platform-adapters.md         # 适配策略与能力差异
├── schemas/
│   └── scheduled-task.schema.json   # 通用 JSON Schema
├── scripts/
│   └── validate_task.py             # Python 标准库静态检查
├── examples/
│   ├── weekly-report.json           # 完整周期任务范例
│   ├── daily-brief-draft.json       # 未确认的草案范例
│   └── workday-cron.md              # Cron 解释范例
└── tests/
    ├── test_validator.py            # 校验脚本测试
    └── acceptance-cases.md          # 15 条对话验收用例
```

## 安装 / 兼容性

将本目录（根上直接含 `SKILL.md`）安装到支持 Agent Skills 的技能目录，目录名使用 `scheduled-task-config`。压缩包若把文件平铺在 ZIP 根上，解压后仍应放进这一同名文件夹。Agnes 等产品实际的安装入口与包格式，以对应版本为准。

无需第三方 Python 依赖；对话式核心能力在无 Python 时仍可使用。可选本地校验：

```bash
python3 scripts/validate_task.py examples/weekly-report.json
python3 scripts/validate_task.py examples/daily-brief-draft.json
python3 -m unittest discover -s tests -v
```

退出码：0 = 无错误（仍可能有警告或待确认）、1 = 发现配置错误、2 = 文件/JSON 无法读取。

本项目的通用 schema 不是任何特定平台的原生配置 API；`ready_for_manual_setup` 也不代表已经创建定时任务。

## License & attribution

Copyright © 2026 kiki 77 (debraday885-lab). Released under the [MIT License](LICENSE).
