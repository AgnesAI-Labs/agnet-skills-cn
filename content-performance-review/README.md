# 内容效果分析与复盘

版本：1.1.2

面向个人创作者、内容运营、品牌营销、产品运营和内容团队。用于单篇诊断、批量复盘、跨平台对比、周期或活动复盘、用户反馈、转化评估和连续复盘。

## 文件结构

- `SKILL.md`：任务路由、执行流程、输出要求和边界。
- `LICENSE`：本份 Skill 的许可。
- `references/metric-framework.md`：指标口径、平台差异和可比性。
- `references/analysis-methods.md`：趋势、分层、漏斗、异常和归因。
- `references/content-diagnosis.md`：内容诊断和评论反馈。
- `references/review-guidelines.md`：报告、行动清单和文件复核。
- `scripts/profile_content_data.py`：只读查看 CSV/XLSX 结构。
- `scripts/analyze_content_performance.py`：计算指标并生成基础表、报告和行动清单。
- `requirements.txt`：脚本依赖。

## 使用

导入整个 `content-performance-review` 文件夹。可以说「哪条笔记互动更好」或「复盘这批内容」，也可以用 `$content-performance-review`。

有表格时，在具备 Python 和依赖的环境中运行：

```bash
python -m pip install -r requirements.txt
python scripts/profile_content_data.py 数据文件.xlsx --output 输出目录/数据盘点.md
python scripts/analyze_content_performance.py 数据文件.xlsx --goal engagement --output-dir 输出目录
```

可一次传入多个 CSV、XLSX 或 XLSM。参数和限制见 `scripts/README.md`。

脚本负责可重复的计算和基础文件。内容判断、评论主题和行动解释仍要对照原始素材。脚本不可用时，在回答里计算并说明没有运行脚本。分组合计必须与各条相加一致。没有用户给出的基准或平台官方定义时，不写行业百分比。
