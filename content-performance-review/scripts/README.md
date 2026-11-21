# 脚本说明：内容数据盘点与效果分析

本目录包含两个可执行脚本，职责不同：

- `profile_content_data.py`：只读结构盘点。识别 CSV/XLSX 的字段、记录数、空值、样例和潜在数值格式问题；不计算业务结论。
- `analyze_content_performance.py`：定量分析与交付引擎。读取一个或多个 CSV/XLSX/XLSM，自动映射常见中英文列名，检查数据质量，计算有明确分母的派生指标，按平台/内容类型分组，生成内容表现分层、维度拆解、发布趋势（满足安全条件时）、Excel 工作簿、Markdown 报告和优化行动清单。

## 环境依赖

```bash
python -m pip install -r requirements.txt
```

## 常用命令

先盘点数据：

```bash
python scripts/profile_content_data.py content-export.xlsx --output data-profile.md
```

按目标进行正式分析：

```bash
python scripts/analyze_content_performance.py content-export.xlsx \
  --goal engagement \
  --output-dir content-review-output
```

支持多个文件（会按语义同义字段逐行合并；脚本会在报告中提示同义列合并）：

```bash
python scripts/analyze_content_performance.py platform-a.csv platform-b.xlsx \
  --goal conversion \
  --output-dir content-review-output
```

指定主指标、单条内容目标值和目标方向：

```bash
python scripts/analyze_content_performance.py content.csv \
  --primary-metric 收藏数 \
  --target-value 100 \
  --target-direction higher \
  --output-dir content-review-output
```

`--target-value` 是单条内容主指标目标，不代表账号或活动总 KPI。若主指标是比率，使用小数输入（例如 10% 输入 `0.1`）。目标方向 `higher` 表示越高越好，`lower` 表示越低越好。

可选 `--sheet 工作表名` 指定 Excel 工作表。默认自动选择同时包含内容字段和效果指标的非空工作表。

## 分析目标

- `auto`：根据可用字段选择探索性主指标，不代表用户 KPI。
- `awareness`：触达人数优先，其次曝光量。
- `views`：播放/阅读量。
- `engagement`：优先使用按触达计算的互动率，其次按播放/阅读、按曝光；缺少分母时才退回互动总量。
- `traffic`：点击数。
- `conversion`：转化数、购买数、注册数或线索数。
- `revenue`：收入。

## 输出

- `内容表现分析表.xlsx`：阅读说明、原始数据、标准化数据、指标字典、平台对比、维度分析、发布趋势、内容明细、数据质量、内容特征、行动清单和图表。
- `运营复盘报告.md`：范围、口径、数据质量、平台/维度表现、组内内容样本、文本结构统计、优化行动和待验证事项。
- `优化行动清单.xlsx`：可编辑的行动、证据、优先级、验证指标、观察周期、负责人和状态。
- `analysis_manifest.json`：运行输入、记录数、主指标、输出路径及提示信息。

## 关键限制

- 完全重复行默认不参与计算，但仍保留在“原始数据”工作表；可用 `--keep-exact-duplicates` 改为保留。
- 重复内容 ID 不会被自动删除；它可能代表多次快照或跨平台内容。存在重复 ID 时会暂停自动发布日期趋势汇总，避免错误累计。
- 计数/金额字段中的百分比文本不会被转换成计数；比率字段中明确带 `%` 的值会转换为小数，裸数值大于 1 时标记单位歧义，不自动换算。
- 互动总量仅在所有已识别互动分项都有值时计算，不把空值默认为 0。
- 跨平台只分平台展示，不合并平台表现总量，也不直接按原始值跨平台排名。
- 文本特征脚本只识别可观察的结构信号；语义、画面、评论主题、用户动机、内容策略归因和实验判断必须由 Agent 阅读原始素材后补充。
- 数据结果是描述性分析；脚本不会证明因果关系，也不提供未经来源确认的行业基准。
