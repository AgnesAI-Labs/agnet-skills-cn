#!/usr/bin/env python3
"""Export already reviewed fact-check records to CSV and Markdown.

Does not browse, verify facts, create sources, access files named in sources, or
produce XLSX. Uses Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from validate_records import RecordValidationError, load_record, validate_record

CLAIM_HEADERS = [
    "主张ID", "原始陈述", "原文定位", "主张类型", "重要程度", "时间及口径", "核查结果",
    "核查依据及理由", "证据编号", "来源编号", "修订建议", "核查日期", "限制说明"
]
EVIDENCE_HEADERS = ["证据ID", "主张ID", "来源ID", "关系", "证据摘要", "引用定位", "简短摘录", "证据限制"]
SOURCE_HEADERS = ["来源ID", "标题", "作者/机构", "发布日期", "资料统计期", "来源类型", "URL或文件名", "具体位置", "实际查阅日期", "访问状态", "引用条目", "备注"]
REVISION_HEADERS = ["主张ID", "原句", "修订句", "修订理由", "来源编号", "风险提示"]


def safe_csv_cell(value: Any) -> str:
    """Neutralize spreadsheet formula interpretation for untrusted strings."""
    text = "" if value is None else str(value)
    # Protect values beginning with spreadsheet formula operators, allowing leading whitespace.
    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def escape_md(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows([[safe_csv_cell(x) for x in row] for row in rows])


def compile_rows(data: dict[str, Any]) -> dict[str, list[list[Any]]]:
    meta = data["metadata"]
    evidence_for_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in data.get("evidence", []):
        evidence_for_claim[e["claim_id"]].append(e)
    claim_rows: list[list[Any]] = []
    revisions: list[list[Any]] = []
    for c in data["claims"]:
        evs = evidence_for_claim[c["id"]]
        evidence_ids = "; ".join(e["id"] for e in evs)
        source_ids = "; ".join(dict.fromkeys(e["source_id"] for e in evs))
        claim_rows.append([
            c["id"], c["original_text"], c.get("location", ""), c.get("claim_type", ""),
            c.get("priority", ""), c.get("time_context", ""), c["status"], c.get("finding", ""),
            evidence_ids, source_ids, c.get("revision", ""), meta["checked_at"], c.get("limitations", "")
        ])
        if c.get("revision"):
            revisions.append([
                c["id"], c["original_text"], c["revision"], c["finding"],
                source_ids, c.get("limitations", "")
            ])
    evidence_rows = [[
        e["id"], e["claim_id"], e["source_id"], e.get("relationship", ""),
        e.get("summary", ""), e.get("locator", ""), e.get("excerpt", ""), e.get("limitations", "")
    ] for e in data.get("evidence", [])]
    source_rows = [[
        s["id"], s["title"], s.get("author_or_org", ""), s.get("published_at", ""),
        s.get("data_period", ""), s.get("source_type", ""), s.get("uri", ""),
        s.get("locator", ""), s.get("accessed_at", ""), s["access_state"],
        s.get("formatted_reference", ""), s.get("caveats", "")
    ] for s in data.get("sources", [])]
    return {"claims": claim_rows, "evidence": evidence_rows, "sources": source_rows, "revisions": revisions}


def make_report(data: dict[str, Any], rows: dict[str, list[list[Any]]]) -> str:
    meta = data["metadata"]
    lines = [
        f"# {escape_md(meta['title'])} — 核查报告", "",
        f"**核查日期**：{escape_md(meta['checked_at'])}  ",
        f"**模式**：{escape_md(meta['mode'])}  ",
        f"**范围**：{escape_md(meta['scope'])}", "",
        "## 概要", "", escape_md(meta.get("conclusion", "未提供概述")), "",
        "## 逐项结果", "",
        "| 编号 | 原始陈述 | 结果 | 证据编号 | 判断理由 | 建议 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows["claims"]:
        lines.append("| " + " | ".join(escape_md(row[i]) for i in (0, 1, 6, 8, 7, 10)) + " |")
    lines.extend(["", "## 证据记录", ""])
    if rows["evidence"]:
        lines.extend(["| 证据 | 主张 | 来源 | 关系 | 摘要 | 定位 |", "| --- | --- | --- | --- | --- | --- |"])
        for row in rows["evidence"]:
            lines.append("| " + " | ".join(escape_md(row[i]) for i in (0, 1, 2, 3, 4, 5)) + " |")
    else:
        lines.append("没有已记录的证据；不得将本文档描述为已完成外部事实核查。")
    lines.extend(["", "## 资料与引用", ""])
    if rows["sources"]:
        lines.extend(["| 来源 | 标题 | 地址/文件名 | 访问状态 | 定位 |", "| --- | --- | --- | --- | --- |"])
        for row in rows["sources"]:
            lines.append("| " + " | ".join(escape_md(row[i]) for i in (0, 1, 6, 9, 7)) + " |")
    else:
        lines.append("本记录未提供可访问来源。")
    lines.extend(["", "## 未覆盖部分", ""])
    lines.extend(["- " + escape_md(x) for x in meta.get("uncovered", [])] or ["- 未单列"]) 
    lines.extend(["", "## 限制与注意事项", ""])
    lines.extend(["- " + escape_md(x) for x in meta.get("limitations", [])] or ["- 未单列"])
    lines.extend(["", "> 本报告基于输入的核查记录生成。导出脚本不验证事实真假，也不替代专业审核。", ""])
    return "\n".join(lines)


def export_record(data: dict[str, Any], output_dir: Path) -> list[Path]:
    errors, _warnings = validate_record(data)
    if errors:
        raise RecordValidationError("记录不符合导出要求：\n- " + "\n- ".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = compile_rows(data)
    destinations = [
        ("事实核查清单.csv", CLAIM_HEADERS, rows["claims"]),
        ("证据记录.csv", EVIDENCE_HEADERS, rows["evidence"]),
        ("引用目录.csv", SOURCE_HEADERS, rows["sources"]),
    ]
    if rows["revisions"]:
        destinations.append(("修订对照表.csv", REVISION_HEADERS, rows["revisions"]))
    written: list[Path] = []
    for name, headings, content in destinations:
        path = output_dir / name
        write_csv(path, headings, content)
        written.append(path)
    report = output_dir / "核查报告.md"
    report.write_text(make_report(data, rows), encoding="utf-8")
    written.append(report)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="导出核查清单、证据、引用 CSV 和 Markdown 报告")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True, help="新输出目录；请勿指定用户原始数据目录")
    args = parser.parse_args()
    try:
        data = load_record(args.input)
        paths = export_record(data, args.output_dir)
    except (RecordValidationError, OSError) as err:
        print(f"[错误] {err}", file=sys.stderr)
        return 1
    for path in paths:
        print("已生成：" + str(path))
    print("注意：仅导出已提供记录；脚本本身未联网，也未执行任何事实核查。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
