# 信息核查与引用整理 · Information Verification & Citation

一个面向公众的通用 AI Agent Skill，用于核查文字、数字、事件、网络消息、报告与学术资料的事实依据，整理可追溯引用，并在必要时给出审慎的修订建议。适合普通用户、学生、教师、创作者、运营、研究人员及办公场景。

> 核心原则：**有证据才下结论；没有证据就明确说明，不编造来源。**

## 能做什么

- **事实主张识别**：从一句话、长文、PPT、表格或截图中提取可核查陈述。
- **数据与准确性核查**：检查数字、日期、单位、时间范围、统计口径、引述与因果措辞。
- **来源查找与评估**：在宿主具备工具和访问权限时检索资料，优先原始来源并说明来源可靠性和独立性。
- **多源交叉验证**：比较相互矛盾的证据，而不是按搜索结果数量投票。
- **引用整理**：默认编号引用；按要求整理 APA、MLA、Chicago、GB/T 7714 等格式的参考文献初稿。
- **结果交付**：快速给结论，或输出逐项清单、修订建议、引用目录、深度核查报告。

## 一句话调用

在 Agnes 中可用 `$information-verification-citation` 后接任务，例如：

- `$information-verification-citation 这个说法真的假的？帮我找到可靠依据。`
- `$information-verification-citation 检查一下这篇文章，哪些地方证据不足？`
- `$information-verification-citation 这两个报告写的用户规模不一样，原因在哪里？`
- `$information-verification-citation 检查我这份 PPT 里的数据有没有口径问题。`
- `$information-verification-citation 核对论文里的引用，再整理成 APA 格式。`
- `$information-verification-citation 帮我把这份报告里的重要数字核查后导出 Excel。`

**不必事先整理来源，也不必提供固定字段。** 但若没有联网工具或缺少材料，Skill 会清楚标注哪些项目无法核实。

## 输出示例

对简短说法，默认：**核查结论、关键依据、注意事项、建议表述**。

多项核查时可生成：

- `事实核查清单.xlsx`：逐条事实、证据与修订建议（模板见 `assets/`）
- `引用目录.csv`：作者/机构、来源、时间、原始位置及访问情况
- `核查报告.md`：核查范围、主要问题、逐项证据、未检查范围与限制
- `修订对照表.xlsx`：可选，原句与修正文本对照

## 安装

1. 导入整个 `information-verification-citation` 目录。该目录根上应直接包含 `SKILL.md`、`README.md` 和 `LICENSE`，不要再套一层同名文件夹。
2. 在 Agnes 中可将该目录放入技能目录后使用；其他客户端以各自官方安装方式为准。
3. 可用 `$information-verification-citation` 后接一句核查任务，确认是否加载本 Skill。

### Agnes 中的建议名称和分类

- 名称：**信息核查与引用整理**
- 英文名称：**Information Verification & Citation**
- 分类：**办公效率**
- Skill ID：`information-verification-citation`

本包采用带 YAML frontmatter 的 `SKILL.md` 目录形式：解压或导入后，包根目录直接包含 `SKILL.md`。重新打包时保持这一相对路径，不要把文件再套进第二层目录。

## 文件结构

```text
information-verification-citation/          # 包根，导入后不要再套一层
├── SKILL.md                          # 主执行指令
├── README.md                         # 使用说明
├── LICENSE                           # MIT
├── CHANGELOG.md
├── references/
│   ├── verification-rules.md         # 事实与六状态判定
│   ├── source-evaluation.md          # 来源可信度和冲突
│   ├── citation-styles.md            # 引用规范与缺失字段
│   └── output-spec.md                # 数据结构/输出约束
├── assets/
│   └── 事实核查清单模板.xlsx
├── scripts/
│   ├── validate_records.py          # 记录格式与证据链检查
│   └── export_records.py            # JSON → CSV / Markdown
└── examples/
    └── sample-records.json          # 演示输入（不作为真实事实）
```

## 脚本（完全可选）

Python 3.9+，无需第三方 Python 依赖：

```bash
python scripts/validate_records.py examples/sample-records.json
python scripts/export_records.py examples/sample-records.json --output-dir ./output
```

脚本**不联网、不判断事实真假、不调用外部 API**。仅校验主张/证据/来源之间的 ID 关联和必要约束，生成便于复核的报告和 CSV。XLSX 模板预置；填充 XLSX 需要宿主已有电子表格处理能力，否则可交付 CSV。

## 能力边界

- 证据不充分、来源不可访问时不输出确定性“真/假”结论。
- 不伪造文献、DOI、页码、发布机构、核查过程或数据。
- 不把截图、转载、搜索摘要、同向数据变化视作独立事实或因果证据。
- 不绕过登录权限、付费墙，不上传未经授权的私人文件。
- 不替代法律、医学、财务或其他正式专业审计。
- 不自动修改用户原始文件、发布内容或操作外部账号。

## 作者与许可

- Author: [kiki 77 (debraday885-lab)](https://github.com/debraday885-lab)
- License: MIT
- Version: 1.0.1

## 开发者参考

结构参考 Open Agent Skills 的 `SKILL.md` 规范，以及渐进披露、按需读取参考文件的 Skill 编写原则。具体的 Agent 调用、联网和文件能力取决于使用它的宿主环境。
