# 用户反馈分析 / User Feedback Analysis

面向公众可复用的 Agent Skill：把评论、客服记录、访谈、问卷、商品评价、社区讨论和活动/课程意见转化为**可追溯的主题归类、问题洞察、需求机会和改进建议**。可用于个人、内容创作、电商、教育、公共服务、产品运营和其他行业，不依赖固定行业标签。

- **分类**：商业运营（可在其他市场按需重新分类）
- **英文名称**：User Feedback Analysis
- **Skill ID**：`user-feedback-analysis`
- **版本**：1.0.3
- **作者**：[kiki 77 (debraday885-lab)](https://github.com/debraday885-lab)
- **许可证**：MIT，见 [LICENSE](LICENSE)
- **能力模式**：按需在对话中总结；有能力时可输出 CSV/XLSX/Markdown；无外部 API、无 MCP、无环境依赖要求

## 常见使用方式

- “帮我分析这 30 条商品评论，总结主要优缺点，按主题统计。”
- “把这批客服投诉按原因归类，帮我判断优先处理哪些问题。”
- “这几份访谈里用户真正想解决的事情是什么？明确需求和推断需求分开写。”
- “分析课程问卷，找出学习者最认可与最不满意的地方。”
- “比较最近两个月的用户反馈，但如果时间和口径不一致请说明。”
- “将这些反馈整理成分析报告和需求机会表，附原话证据。”
- “Summarize customer feedback, group common pain points, and suggest evidence-backed improvements.”

## 交付行为

| 数据/需求 | 常见输出 |
| --- | --- |
| 直接粘贴少量评论 | 对话内主题归纳、主要观点、原话、建议 |
| 一批反馈 | 主题分类、频次、正面亮点、主要问题、需求机会 |
| 多群体/多时段数据 | 有前提的分组或趋势对比、数据边界和证据链 |
| 要求文件 | 可交付反馈明细、需求机会清单与分析报告；按宿主支持生成所需格式 |

其中 `templates/feedback-records.csv` 和 `templates/opportunities.csv` 是**空白字段模板**，并不代表自动拥有相关的数据分析或 XLSX 导出工具；实际文件创建仍需宿主可用的文件能力。

## 包结构

```text
user-feedback-analysis/
├── SKILL.md                          # 主要指令、触发与工作流程
├── README.md                         # 使用说明
├── LICENSE                           # MIT
├── references/
│   ├── feedback-taxonomy.md          # 分类、情绪、需求提炼
│   ├── analysis-methods.md           # 频次、对比、优先级
│   └── evidence-quality.md           # 证据、隐私、质量规范
├── templates/
│   ├── feedback-records.csv          # 反馈明细空白字段模板
│   ├── opportunities.csv             # 改进机会空白字段模板
│   └── report-template.md            # 可选分析报告模板
├── examples/
│   ├── synthetic-feedback.csv        # 虚构演示数据，不得当真实证据
│   └── example-analysis.md           # 演示分析结果
```

## 安装或导入

将本 Skill 文件夹导入支持 Agent Skills 的宿主。宿主需要能识别包根目录的 `SKILL.md`。若使用 ZIP，压缩包根目录应直接包含 `SKILL.md`、`README.md` 和 `LICENSE`。

不需要提前安装 MCP、浏览器插件或 Python 包。Skill 依靠宿主模型处理用户提供的反馈；使用表格、文档或互联网工具前，应检查环境实际有哪些能力与权限。

## 规则与限制

- 仅基于用户提供或合法授权的资料分析，不能凭空补用户原话、人数或日期。
- 区分明确诉求、推断需求、建议方案和未经证实的原因。
- 不把少量/偏向投诉的样本解释成总体满意度或总体比例。
- 不将“反馈次数”误写为“独立用户数”；支持一条反馈多主题统计。
- 不自动采集私密数据、不自动回复客户、不修改外部业务系统。
- 文件输出取决于宿主工具能力，无法生成目标格式时需明确告知并提供替代格式。

## License

MIT License © 2026 kiki 77 (debraday885-lab).
