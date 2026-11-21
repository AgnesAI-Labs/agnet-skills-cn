#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check short-video storyboard exported as CSV from the included Excel template.

Usage:
  python scripts/validate_storyboard.py storyboard.csv --target-duration 30

This is a structural check only. Creative quality, truth, visual feasibility,
voiceover pacing and production permissions still require human review.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

REQUIRED = ["镜头编号", "镜头时长(秒)", "画面内容与人物动作"]
TIME_COLUMNS = ["起始时间(秒)", "结束时间(秒)"]
TOLERANCE = 0.05  # seconds, avoids floating-point noise


def number_or_none(value):
    value = str(value or "").strip()
    if not value:
        return None
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None


def nonblank(value):
    return bool(str(value or "").strip())


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="CSV exported from the storyboard template")
    parser.add_argument("--target-duration", type=float, default=None,
                        help="Optional expected total duration (seconds)")
    args = parser.parse_args(argv)
    path = Path(args.csv_file)
    if not path.exists():
        print(f"错误：文件不存在：{path}")
        return 2
    if args.target_duration is not None and args.target_duration <= 0:
        print("错误：目标时长应大于 0 秒")
        return 2

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            rows = list(reader)
    except Exception as exc:
        print(f"错误：无法读取 CSV：{exc}")
        return 2

    missing = [column for column in REQUIRED if column not in headers]
    if missing:
        print("错误：缺少必要字段：" + "、".join(missing))
        return 2

    issues = []
    warnings = []
    seen = set()
    total = 0.0
    checked_count = 0
    last_end = None
    has_time = all(col in headers for col in TIME_COLUMNS)
    if not has_time:
        warnings.append("CSV 缺少完整起止时间字段，不能检查镜头时间线空档或重叠")

    for csv_line, row in enumerate(rows, start=2):
        # Template sheets contain preformatted empty rows: ignore them.
        if not any(nonblank(value) for value in row.values()):
            continue
        checked_count += 1
        shot_id = str(row.get("镜头编号") or "").strip()
        label = shot_id or f"第{csv_line}行"
        if not shot_id:
            issues.append(f"第 {csv_line} 行：镜头编号为空")
        elif shot_id in seen:
            issues.append(f"第 {csv_line} 行：镜头编号重复（{shot_id}）")
        seen.add(shot_id)

        visual = str(row.get("画面内容与人物动作") or "").strip()
        if not visual:
            issues.append(f"第 {csv_line} 行：画面内容与人物动作为空（{label}）")

        raw_duration = row.get("镜头时长(秒)")
        duration = number_or_none(raw_duration)
        if duration is None:
            issues.append(f"第 {csv_line} 行：镜头时长缺失或不是数字（{label}）")
        elif duration <= 0:
            issues.append(f"第 {csv_line} 行：镜头时长必须大于 0（{label}）")
        else:
            total += duration

        if has_time:
            start = number_or_none(row.get("起始时间(秒)"))
            end = number_or_none(row.get("结束时间(秒)"))
            if (start is None) != (end is None):
                issues.append(f"第 {csv_line} 行：起始时间与结束时间需要同时填写（{label}）")
            elif start is not None and end is not None:
                if start < 0 or end <= start:
                    issues.append(f"第 {csv_line} 行：起止时间无效（{label}）")
                else:
                    if duration is not None and duration > 0 and abs((end - start) - duration) > 1.0:
                        issues.append(f"第 {csv_line} 行：起止时间差与镜头时长相差超过 1 秒（{label}）")
                    if last_end is not None:
                        delta = start - last_end
                        if delta > TOLERANCE:
                            issues.append(f"第 {csv_line} 行：与上个镜头之间存在 {delta:.2f} 秒空档（{label}）")
                        elif delta < -TOLERANCE:
                            notes = " ".join(str(row.get(k) or "") for k in ["转场/剪辑提示", "备注/待确认"])
                            if any(key in notes for key in ["叠化", "重叠", "多轨", "画中画", "交叉剪辑"]):
                                warnings.append(f"第 {csv_line} 行：时间线重叠 {abs(delta):.2f} 秒，已在备注中说明（{label}）")
                            else:
                                issues.append(f"第 {csv_line} 行：与上个镜头重叠 {abs(delta):.2f} 秒，需说明原因（{label}）")
                    elif start > TOLERANCE:
                        issues.append(f"第 {csv_line} 行：第一镜头从 {start:.2f} 秒开始，起始存在空档（{label}）")
                    last_end = end
            elif last_end is not None:
                warnings.append(f"第 {csv_line} 行：未填镜头起止时间，后续连续性无法完全检查（{label}）")
                last_end = None

    if not checked_count:
        issues.append("分镜表没有有效数据行")
    if args.target_duration is not None:
        allowed = max(2.0, args.target_duration * 0.05)
        if abs(total - args.target_duration) > allowed:
            issues.append(f"镜头时长合计与目标时长偏差超过 {allowed:.1f} 秒")
        if last_end is not None and abs(last_end - args.target_duration) > allowed:
            issues.append("最后一个镜头结束时间与目标时长存在明显偏差")

    print(f"有效镜头数量：{checked_count}")
    print(f"镜头时长合计：{total:.1f} 秒")
    if args.target_duration is not None:
        print(f"目标时长：{args.target_duration:.1f} 秒；差值：{total - args.target_duration:+.1f} 秒")
    if warnings:
        print("\n提示：")
        for msg in warnings:
            print("- " + msg)
    if issues:
        print("\n发现问题：")
        for msg in issues:
            print("- " + msg)
        return 1
    print("\n基础检查通过。还需人工检查创意质量、口播可读性、事实、授权及镜头可执行性。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
