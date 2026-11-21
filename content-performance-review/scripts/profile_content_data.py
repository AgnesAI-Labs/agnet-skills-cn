#!/usr/bin/env python3
"""Read-only structural profiler for CSV/XLSX exports with safe Markdown output."""
from __future__ import annotations
import argparse, csv, math, statistics, sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

MAX_ROWS = 100_000
SAMPLE_LIMIT = 5


def clean_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value).replace("\n", " ").replace("\r", " ").strip()[:160]


def md_escape(value: Any) -> str:
    return clean_value(value).replace("|", "\\|").replace("`", "\\`")


def looks_numeric(values: list[Any]) -> dict[str, Any] | None:
    nums, percent_count, plain_count = [], 0, 0
    for value in values:
        if value is None or str(value).strip() == "":
            continue
        raw = str(value).strip().replace(",", "")
        is_percent = raw.endswith("%") or raw.endswith("％")
        if is_percent:
            raw = raw[:-1]
            percent_count += 1
        else:
            plain_count += 1
        try:
            number = float(raw)
            if math.isfinite(number):
                nums.append(number)
        except (TypeError, ValueError):
            continue
    if not nums:
        return None
    return {
        "numeric_count": len(nums), "min": min(nums), "median": statistics.median(nums), "max": max(nums),
        "contains_percent_strings": percent_count > 0,
        "contains_plain_numeric_strings": plain_count > 0,
        "mixed_percent_and_plain": percent_count > 0 and plain_count > 0,
        "unit_warning": "百分比与裸数值混合；本盘点不做单位换算" if percent_count > 0 and plain_count > 0 else ("含百分比文本；数值概况沿用百分号前原值" if percent_count > 0 else ""),
    }


def summarize_rows(headers: list[str], rows: Iterable[Iterable[Any]], sheet_name: str, limit: int) -> dict[str, Any]:
    columns: list[list[Any]] = [[] for _ in headers]
    row_count = 0
    for row in rows:
        if row_count >= limit:
            break
        values = list(row)
        for index in range(len(headers)):
            columns[index].append(values[index] if index < len(values) else None)
        row_count += 1
    column_summaries = []
    for header, values in zip(headers, columns):
        nonblank = [v for v in values if v is not None and str(v).strip() != ""]
        counts = Counter(clean_value(v) for v in nonblank)
        column_summaries.append({
            "name": header, "non_empty": len(nonblank), "empty": row_count - len(nonblank),
            "unique_non_empty": len(counts), "sample_values": [v for v, _ in counts.most_common(SAMPLE_LIMIT)],
            "numeric_summary": looks_numeric(nonblank),
        })
    return {"sheet": sheet_name, "rows_profiled": row_count, "row_limit": limit, "columns": column_summaries}


def profile_csv(path: Path, limit: int) -> list[dict[str, Any]]:
    last_error = None
    for encoding in ("utf-8-sig", "utf-16", "gb18030", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.reader(handle)
                headers = next(reader, [])
                if not headers:
                    return [{"sheet": "CSV", "rows_profiled": 0, "row_limit": limit, "columns": [], "encoding": encoding, "empty_file": True}]
                profile = summarize_rows(headers, reader, "CSV", limit)
                profile["encoding"] = encoding
                return [profile]
        except UnicodeError as exc:
            last_error = exc
    raise RuntimeError(f"无法识别 CSV 编码：{last_error}")


def profile_xlsx(path: Path, limit: int) -> list[dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("读取 XLSX 需要 openpyxl") from exc
    workbook = load_workbook(path, read_only=True, data_only=True)
    profiles = []
    try:
        for worksheet in workbook.worksheets:
            iterator = worksheet.iter_rows(values_only=True)
            first = next(iterator, ())
            if not first:
                profiles.append({"sheet": worksheet.title, "rows_profiled": 0, "row_limit": limit, "columns": [], "empty_sheet": True})
                continue
            headers = [clean_value(value) or f"未命名列_{i + 1}" for i, value in enumerate(first)]
            profiles.append(summarize_rows(headers, iterator, worksheet.title, limit))
    finally:
        workbook.close()
    return profiles


def render_markdown(path: Path, profiles: list[dict[str, Any]]) -> str:
    lines = [f"# 数据结构盘点：{md_escape(path.name)}", "", "> 本报告仅描述文件结构和字段概况，不代表业务指标口径已确认，也未修改原文件。", ""]
    for profile in profiles:
        lines += [f"## 工作表：{md_escape(profile['sheet'])}", "", f"- 盘点记录数：{profile['rows_profiled']}", f"- 盘点上限：{profile['row_limit']}"]
        if "encoding" in profile:
            lines.append(f"- 文件编码：{profile['encoding']}")
        if profile.get("empty_file") or profile.get("empty_sheet"):
            lines += ["- 文件/工作表为空，没有可盘点的数据。", ""]
            continue
        lines += ["", "| 字段 | 非空 | 空值 | 非空唯一值 | 样例值 | 数值概况（最小/中位/最大） |", "|---|---:|---:|---:|---|---|"]
        for col in profile["columns"]:
            numeric = col["numeric_summary"]
            numeric_text = "—" if not numeric else f"{numeric['min']:g} / {numeric['median']:g} / {numeric['max']:g}"
            if numeric and numeric.get("mixed_percent_and_plain"):
                numeric_text += "（百分比/裸值混合，未换算）"
            elif numeric and numeric.get("contains_percent_strings"):
                numeric_text += "（含百分号文本，显示百分号前原值，未换算）"
            sample = "；".join(md_escape(x) for x in col["sample_values"])
            lines.append(f"| {md_escape(col['name'])} | {col['non_empty']} | {col['empty']} | {col['unique_non_empty']} | {sample} | {numeric_text} |")
        lines.append("")
    lines += ["## 使用提醒", "", "- 请确认每列指标的真实定义、单位、分母和统计周期。", "- 百分比文本和裸数值混合时，本盘点不自动换算。", "- 唯一值数量和数值概况仅用于快速识别字段，不代表数据质量结论。", "- 对超过盘点上限的文件，本报告只覆盖前述行数；正式分析应使用全量数据。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="只读盘点内容效果数据 CSV/XLSX 结构")
    parser.add_argument("input", help="输入 CSV 或 XLSX 文件")
    parser.add_argument("--output", help="输出 Markdown 文件；默认打印到终端")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    args = parser.parse_args()
    source = Path(args.input).expanduser()
    if not source.is_file():
        parser.error(f"文件不存在：{source}")
    if args.max_rows < 1:
        parser.error("--max-rows 必须大于 0")
    if source.stat().st_size == 0:
        profiles = [{"sheet": "CSV", "rows_profiled": 0, "row_limit": args.max_rows, "columns": [], "empty_file": True}]
    elif source.suffix.lower() == ".csv":
        profiles = profile_csv(source, args.max_rows)
    elif source.suffix.lower() in (".xlsx", ".xlsm"):
        profiles = profile_xlsx(source, args.max_rows)
    else:
        parser.error("仅支持 .csv、.xlsx、.xlsm")
    report = render_markdown(source, profiles)
    if args.output:
        destination = Path(args.output).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(report, encoding="utf-8")
        print(f"已生成：{destination}")
    else:
        print(report)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2)
