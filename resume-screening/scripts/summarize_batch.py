#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历评分结果批量汇总 —— 生成 Markdown 汇总表格

仅做确定性的格式化汇总：读取目录下所有 calculate_match_score.py 产出的结果 JSON，
按匹配度总分降序排列，渲染为固定格式的 Markdown 表格。
本脚本不重新评分、不改写面试建议，一切以 JSON 中已有结果为准。

用法：
  python summarize_batch.py --results <结果目录> --job "目标岗位名称"
  python summarize_batch.py --results <结果目录> --job "目标岗位名称" --sort name
  python summarize_batch.py --results <结果目录> --job "目标岗位名称" --fail-only
"""

import argparse
import glob
import json
import os
import sys

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# 5 个维度的名称与顺序（与 calculate_match_score.py 保持一致）
SECTION_NAMES = [
    "核心底层要求",
    "岗位职责",
    "岗位必备条件",
    "岗位加分项",
    "实践经验描述标准",
]

HEADERS = ["候选人名称"] + SECTION_NAMES + [
    "匹配度总分", "是否通过初筛", "面试侧重点建议",
]

# 表格分隔行宽度（仅影响可读性，不影响解析）
SEPARATOR_WIDTHS = {
    "候选人名称": 11,
    "核心底层要求": 12,
    "岗位职责": 9,
    "岗位必备条件": 12,
    "岗位加分项": 10,
    "实践经验描述标准": 15,
    "匹配度总分": 11,
    "是否通过初筛": 12,
    "面试侧重点建议": 13,
}


def load_results(results_dir):
    """读取目录下所有 JSON 结果文件"""
    rows = []
    for path in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[警告] 跳过无法解析的结果文件 {path}: {e}", file=sys.stderr)
            continue

        sections = data.get("分项匹配度", {}) or {}
        row = {
            "候选人名称": data.get("候选人名称", "未知"),
            "匹配度总分": data.get("匹配度总分", 0),
            "是否通过初筛": data.get("是否通过初筛", "未知"),
            "面试侧重点建议": data.get("面试侧重点建议", ""),
        }
        for name in SECTION_NAMES:
            row[name] = sections.get(name, 0)
        rows.append(row)

    return rows


def sort_rows(rows, key):
    """排序：total=按总分降序；name=按姓名升序"""
    if key == "name":
        return sorted(rows, key=lambda r: r["候选人名称"])
    return sorted(rows, key=lambda r: (-r["匹配度总分"], r["候选人名称"]))


def render_table(rows):
    """渲染 Markdown 表格"""
    lines = [
        "| " + " | ".join(HEADERS) + " |",
        "|" + "|".join(
            "-" * SEPARATOR_WIDTHS.get(h, 11) for h in HEADERS
        ) + "|",
    ]
    for r in rows:
        cells = [r["候选人名称"]]
        cells += [str(r[n]) for n in SECTION_NAMES]
        cells += [
            str(r["匹配度总分"]),
            r["是否通过初筛"],
            r["面试侧重点建议"],
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="简历评分结果批量汇总（生成 Markdown 表格，不重新评分）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--results", required=True,
                        help="存放各份评分结果 JSON 的目录")
    parser.add_argument("--job", required=True, help="目标岗位名称")
    parser.add_argument("--sort", choices=["total", "name"], default="total",
                        help="排序方式：total=按总分降序（默认），name=按姓名升序")
    parser.add_argument("--fail-only", action="store_true",
                        help="仅输出不通过初筛的候选人")
    args = parser.parse_args()

    if not os.path.isdir(args.results):
        print(f"错误：'{args.results}' 不是有效目录", file=sys.stderr)
        sys.exit(1)

    rows = load_results(args.results)
    if not rows:
        print(f"错误：目录 '{args.results}' 中没有找到任何评分结果 JSON", file=sys.stderr)
        sys.exit(1)

    # 统计基于全量数据，不受 --fail-only 过滤影响
    total_count = len(rows)
    passed_count = sum(1 for r in rows if r["是否通过初筛"] == "通过")

    if args.fail_only:
        rows = [r for r in rows if r["是否通过初筛"] != "通过"]
    if not rows:
        print("（无符合筛选条件的候选人）")

    rows = sort_rows(rows, args.sort)

    out = [
        "## 简历筛选结果汇总",
        "",
        f"**目标岗位：** {args.job}",
        "",
        render_table(rows),
        "",
        f"**初筛通过 {passed_count} 人 / 共 {total_count} 人**"
        f"（通过标准：匹配度总分不低于 80 分）",
    ]
    print("\n".join(out))


if __name__ == "__main__":
    main()
