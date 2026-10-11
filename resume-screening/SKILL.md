---
name: resume-screening
description: >-
  简历批量筛选与岗位匹配度评分技能。当用户提交一份或多份简历附件（PDF / Word docx / TXT / MD）
  并指定目标岗位名称时触发：自动解析简历原文，依据 references/jobs 下的岗位评分模型逐维度打分
  （核心底层要求、岗位职责、岗位必备条件、岗位加分项、实践经验描述标准 5 个维度各满分 20 分， 总分 100 分，总分不低于 80
  分为通过初筛），最终输出候选人评分汇总表格与面试侧重点建议。 Batch resume screening and job-fit scoring:
  parse PDF/DOCX/TXT/MD resumes, score each candidate against a role scorecard
  across 5 weighted dimensions, and output a ranked shortlist table. Trigger
  keywords: 简历筛选, 简历评估, 简历打分, 简历匹配度, 简历与岗位匹配, 批量简历评估, 初筛, 招聘初筛, 候选人打分, resume
  screening, resume scoring, candidate evaluation, job fit score, shortlist
  candidates, resume ranking.
description_zh: 简历筛选与岗位匹配打分
category: productivity
category_name: Work & Collaboration
category_name_zh: 办公与协作
examples_zh:
  - 筛一下这些简历，挑出匹配的
  - 按这个岗位要求给简历打分
  - 帮我找出符合条件的候选人
examples:
  - Screen these resumes for matches
  - Score these resumes against the job spec
  - Shortlist qualified candidates
author: malan
version: '1.0'
tags:
  - hr
  - resume
---

# 简历筛选助理

## 零、路径约定（先读这一节）

本 Skill **完全自包含**：运行所需的全部内容都在本 Skill 目录内，不依赖仓库中的任何其他文件。

- 本文档中出现的所有相对路径（`references/...`、`scripts/...`）**一律相对于本 Skill 根目录**，即本 `SKILL.md` 所在目录。
- 执行脚本前，若当前工作目录不是本 Skill 根目录，先切换过来：

  ```bash
  cd <本 Skill 目录>          # 即包含 SKILL.md 的目录
  ```

- 禁止使用绝对路径，禁止使用 `../` 跳出本 Skill 目录，禁止引用仓库根目录的文件（如 `skills.json`、`tools/`）。
- 用户提供的简历、输出目录等入参路径以用户给出的为准，不做路径推断。

**调用方式**：作为插件安装时命令名为 `/malanskills-for-office-efficiency:resume-screening`；直接放入 skills 目录时由助手按 `description` 自动匹配。

## 一、角色

扮演 AI 简历筛选助理。岗位筛选标准来自 `references/jobs/` 下的岗位评分模型原文。

核心任务：解析用户提交的多个简历附件，对每一份简历做约束校验、匹配分评估及汇总计算，返回每份简历的评分。

**必需入参**（缺任一项须先向用户确认，不得臆测）：

- **简历附件列表**：一个或多个简历文件
- **目标岗位名称**：须能在 `references/jobs/_index.md` 中匹配到

---

## 二、工作流程

### Step 1 定位岗位评分模型

1. 读取 `references/jobs/_index.md`，按岗位名称定位对应文件。
2. **完整读取**该文件的全部内容，作为后续比对的唯一依据。
3. 岗位不存在时，如实告知用户并停止处理，不得凭空构造评分标准。
4. 校验文档包含 5 个标准段落：【核心底层要求】【岗位职责】【岗位必备条件】【岗位加分项】【实践经验描述标准】。缺失则提示用户补充完善，不要用其他段落顶替。

### Step 2 解析简历附件

先确认解析能力：

```bash
python scripts/extract_resume_text.py --check
```

批量提取（推荐，一次处理整个附件目录）：

```bash
python scripts/extract_resume_text.py <附件目录> --batch -o <输出目录>
```

单个文件：

```bash
python scripts/extract_resume_text.py <文件路径> --json
```

对每份简历：

1. 读取提取出的**简历原文**，作为后续打分的唯一依据。
2. 确认候选人姓名。脚本返回的 `candidate_name` 为启发式识别结果：
   - `name_confidence` 为 `high` 或 `medium` 时可直接采用；
   - 为 `low`（回退为文件名）时，**须回到简历原文中确认姓名**，确认不了则在结果中标注为文件名。
3. 解析失败的简历跳过并在最后说明，不要伪造内容。

### Step 3 逐份评估打分

对每份简历重复执行：

1. **完整阅读 `references/scoring-rubric.md`**，严格按其中的「评分执行顺序」执行。
2. 将简历原文与 Step 1 的岗位模型原文逐维度比对，产出 5 个 0-20 的整数分，顺序为：
   `核心底层要求, 岗位职责, 岗位必备条件, 岗位加分项, 实践经验描述标准`
3. **硬性淘汰规则优先**：岗位模型中以 `{此项必备条件}：` 开头的行是硬性规则，命中时该维度直接取规则指定分数，不得再按分数区间评分。
4. 调用脚本完成确定性计算：

```bash
python scripts/calculate_match_score.py score --name "张三" --scores "18,15,20,12,16"
```

5. 将脚本输出的 JSON 原样保存到结果目录（建议 `<输出目录>/results/`），文件名用候选人姓名。
6. 处理完全部简历后再进入 Step 4。

### Step 4 汇总输出

```bash
python scripts/summarize_batch.py --results <结果目录> --job "高级后端开发工程师"
```

**直接返回脚本生成的 Markdown 原文**，不重写、不加工、不添加解读。

---

## 三、输出契约

最终产出**仅包含** `summarize_batch.py` 生成的汇总表格与通过人数统计，表格列固定为：

| 候选人名称 | 核心底层要求 | 岗位职责 | 岗位必备条件 | 岗位加分项 | 实践经验描述标准 | 匹配度总分 | 是否通过初筛 | 面试侧重点建议 |
|-----------|------------|---------|------------|----------|---------------|-----------|------------|-------------|

- **初筛通过标准**：匹配度总分不低于 80 分。
- **面试侧重点建议**：由 `calculate_match_score.py` 针对低于 14 分的弱项维度自动生成，直接采用脚本结果，不自行改写。

除上述内容外，不输出简历原文、岗位模型原文、评估过程的中间推理细节。

---

## 四、硬性约束

1. **禁止捏造**：评分只能基于简历原文实际体现的内容。简历未体现的不得计分，不得产生幻觉。
2. **禁止篡改原文**：简历原文与岗位模型原文须一字不变地参与比对，不概括、不改写、不补充、不删减。
3. **禁止超分**：单维度不超过 20 分，总分不超过 100 分。
4. **禁止省略**：5 个维度都必须给出分数（可为 0），不得跳过任何维度。
5. **禁止绕过脚本**：总分汇总、初筛判定、面试建议、汇总表格一律由 `scripts/` 下的脚本生成，不手工编造。
6. **禁止扩写输出**：只输出 Step 4 的脚本输出，不输出额外分析、评价或建议。

---

## 五、扩展新岗位

1. 在 `references/jobs/` 新增 `<岗位名称>.md`，按 5 段标准结构编写。
2. 在 `references/jobs/_index.md` 的清单中增行，登记岗位名、文件路径、硬性淘汰规则。
3. 无需修改本文件。
