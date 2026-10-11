# resume-screening

> 简历批量筛选与岗位匹配度评分 / Batch resume screening and job-fit scoring

依据岗位评分模型对多份简历逐维度打分，输出候选人评分汇总表格、是否通过初筛与面试侧重点建议。
Score every resume against a role scorecard, then output a ranked shortlist table with pass/fail and interview focus areas.

| | |
|---|---|
| **分类 / Category** | `talent-acquisition` 招聘与人才评估 |
| **入口 / Entry** | [`SKILL.md`](SKILL.md) |
| **规范 / Spec** | [Agent Skills](https://agentskills.io/specification) |
| **许可 / License** | MIT |
| **自包含 / Self-contained** | 是，运行不依赖本仓库其他文件 |

## 目录结构 / Layout

```text
resume-screening/
├── SKILL.md                          # 唯一入口：路径约定、角色、工作流、输出契约、约束
├── README.md                         # 本文件
├── references/                       # 领域知识，按需读取
│   ├── scoring-rubric.md             # 5 维度评分细则与硬性淘汰规则优先级
│   └── jobs/
│       ├── _index.md                 # 岗位索引（岗位名 → 文件路径 → 硬性规则）
│       └── 高级后端开发工程师.md      # 岗位评分模型原文
└── scripts/                          # 确定性计算，零框架依赖
    ├── extract_resume_text.py        # 简历文本提取（PDF / docx / txt / md）
    ├── calculate_match_score.py      # 分项分数 → 总分 / 初筛 / 面试建议
    └── summarize_batch.py            # 多份结果 JSON → Markdown 汇总表格
```

本目录可整体复制到任意位置独立使用，所有路径均相对本目录。

## 安装 / Install

**作为 Claude Code 插件的一部分**

```bash
claude plugin marketplace add malan-skills/malanskills_for_office_efficiency
claude plugin install malanskills-for-office-efficiency@malanskills-office-efficiency
```

**单独安装 / Install standalone**

| 作用域 Scope | 路径 Path |
|---|---|
| 用户级 User | `~/.claude/skills/resume-screening/` |
| 项目级 Project | `<项目根>/.claude/skills/resume-screening/` |
| CodeBuddy | `~/.codebuddy/skills/resume-screening/` |

```bash
# 从本仓库只取这一个 Skill
npx skills add malan-skills/malanskills_for_office_efficiency --skill resume-screening
```

## 依赖 / Dependencies

按需安装，`extract_resume_text.py --check` 可查看当前环境缺什么。
Install on demand; run `--check` to see what is missing.

```bash
pip install pypdf pdfplumber pdfminer.six pypdfium2   # PDF 解析（多引擎容错，至少装一个）
pip install python-docx                              # Word 简历解析
```

纯文本（`.txt` / `.md`）解析无需任何依赖。Plain-text resumes need no dependency.

## 使用 / Usage

直接向助手提出请求，附上简历文件并指明岗位 / Attach resumes and name the target role:

```
帮我评估这 5 份简历对「高级后端开发工程师」岗位的匹配度
Screen these 5 resumes against the "Senior Backend Engineer" role and rank them.
```

命令行直接跑脚本时，先进入本目录：

```bash
cd resume-screening
python3 scripts/extract_resume_text.py <附件目录> --batch -o <输出目录>
python3 scripts/calculate_match_score.py score --name "张三" --scores "18,15,20,12,16"
python3 scripts/summarize_batch.py --results <结果目录> --job "高级后端开发工程师"
```

## 评分模型 / Scoring Model

- 5 个维度各满分 20 分，总分 100 分 / 5 dimensions, 20 points each, 100 total
- 初筛通过标准：总分不低于 80 分 / Pass threshold: 80 out of 100
- 岗位模型中以 `{此项必备条件}：` 开头的行为硬性淘汰规则，优先于分数区间执行
  Lines starting with `{此项必备条件}：` are hard knock-out rules and take priority over score ranges

## 新增岗位 / Adding a Role

1. 在 `references/jobs/` 新增 `<岗位名称>.md`，按 5 段标准结构编写：【核心底层要求】【岗位职责】【岗位必备条件】【岗位加分项】【实践经验描述标准】。
2. 在 `references/jobs/_index.md` 增行登记。无需改动 `SKILL.md` 与脚本。
3. No change needed in `SKILL.md` or the scripts.
