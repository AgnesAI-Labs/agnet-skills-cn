#!/usr/bin/env python3
"""Evidence-first content performance analysis for CSV/XLSX exports.

The script performs deterministic quantitative work and creates reviewable artifacts.
It does not infer semantic causes or platform metric definitions that are not supplied.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ALIASES: dict[str, list[str]] = {
    "content_id": ["内容id", "内容编号", "笔记id", "笔记编号", "视频id", "作品id", "作品编号", "文章id", "post id", "post_id", "content id", "content_id", "id"],
    "platform": ["平台", "发布平台", "平台名称", "渠道", "渠道名称", "媒体平台", "platform", "channel"],
    "title": ["标题", "内容标题", "笔记标题", "视频标题", "文章标题", "title", "content title"],
    "content_type": ["内容类型", "内容形式", "形式", "类型", "内容形态", "content type", "format"],
    "account": ["账号", "账号名称", "账户", "account", "channel name"],
    "campaign": ["活动", "活动名称", "营销活动", "campaign", "campaign name"],
    "paid_status": ["投放状态", "流量类型", "自然/付费", "自然付费", "流量来源类型", "paid or organic", "paid status"],
    "audience": ["目标受众", "受众", "人群", "audience", "target audience"],
    "topic": ["选题", "主题", "内容主题", "栏目", "topic", "subject", "category"],
    "published_at": ["发布时间", "发布日期", "发布日", "创建时间", "publish date", "published at", "published_at", "date"],
    "data_date": ["统计日期", "数据日期", "抓取日期", "导出日期", "snapshot date", "data date"],
    "observation_days": ["观察天数", "发布天数", "发布后天数", "数据观察天数", "observation days", "age days"],
    "impressions": ["曝光", "曝光量", "曝光次数", "总曝光", "展示", "展示量", "impressions"],
    "reach": ["触达", "触达人数", "覆盖人数", "覆盖用户数", "reach", "unique reach"],
    "views": ["播放", "播放量", "播放次数", "观看", "观看量", "阅读量", "阅读次数", "浏览量", "浏览次数", "views", "view count", "reads"],
    "unique_views": ["独立观看人数", "独立播放人数", "独立阅读人数", "unique views", "unique viewers"],
    "watch_time": ["总观看时长", "观看时长", "播放时长", "总播放时长", "watch time", "total watch time"],
    "avg_watch_time": ["平均观看时长", "人均观看时长", "平均播放时长", "average view duration", "avg watch time"],
    "completion_rate": ["完播率", "阅读完成率", "完成率", "completion rate", "completion_rate", "average percentage viewed"],
    "likes": ["点赞", "点赞数", "点赞量", "喜欢", "likes", "post likes"],
    "comments": ["评论", "评论数", "评论量", "评论条数", "comments"],
    "shares": ["分享", "分享数", "分享量", "转发", "转发数", "转发量", "shares"],
    "saves": ["收藏", "收藏数", "收藏量", "saves", "bookmarks"],
    "reactions": ["其他互动", "其他互动数", "other interactions", "other reactions"],
    "engagement_total_source": ["互动总量", "总互动", "总互动量", "互动次数", "互动量", "engagements", "total engagements"],
    "clicks": ["点击", "点击量", "点击次数", "链接点击", "clicks", "link clicks"],
    "profile_visits": ["主页访问", "主页访问量", "主页访客", "profile visits", "profile views"],
    "follows": ["新增关注", "涨粉", "新增粉丝", "新增粉丝数", "关注数", "followers gained", "follows"],
    "leads": ["线索", "线索数", "有效线索", "有效线索数", "leads"],
    "registrations": ["注册", "注册数", "新增注册", "registrations", "signups"],
    "purchases": ["购买", "购买数", "订单数", "成交订单", "purchases", "orders"],
    "conversions": ["转化", "转化数", "转化人数", "有效转化", "有效转化数", "conversion", "conversions"],
    "revenue": ["收入", "营收", "成交金额", "销售额", "revenue", "sales"],
    "spend": ["花费", "消耗", "投放成本", "广告费用", "成本", "spend", "ad spend", "cost"],
    "ctr": ["点击率", "点击通过率", "ctr", "click through rate"],
    "engagement_rate": ["互动率", "engagement rate", "engagement_rate"],
    "comment_text": ["评论内容", "评论文本", "用户评论", "评论原文", "comment", "comment text"],
    "body_text": ["正文", "内容正文", "文案", "内容文案", "内容", "脚本", "视频脚本", "描述", "内容描述", "body", "text", "script", "description"],
}

COUNT_FIELDS = {
    "impressions", "reach", "views", "unique_views", "likes", "comments", "shares", "saves",
    "reactions", "engagement_total_source", "clicks", "profile_visits", "follows", "leads", "registrations", "purchases", "conversions",
}
RATE_FIELDS = {"completion_rate", "ctr", "engagement_rate"}
NUMERIC_FIELDS = COUNT_FIELDS | RATE_FIELDS | {"watch_time", "avg_watch_time", "observation_days", "revenue", "spend"}
NONNEGATIVE_FIELDS = NUMERIC_FIELDS
FIELD_LABELS = {
    "content_id": "内容ID", "platform": "平台", "title": "标题", "content_type": "内容类型", "account": "账号", "campaign": "活动", "paid_status": "流量类型", "audience": "目标受众", "topic": "主题",
    "published_at": "发布时间", "data_date": "统计日期", "observation_days": "观察天数",
    "impressions": "曝光量", "reach": "触达人数", "views": "播放/阅读量", "unique_views": "独立观看/阅读人数",
    "watch_time": "总观看时长", "avg_watch_time": "平均观看时长", "completion_rate": "完播/完成率",
    "likes": "点赞数", "comments": "评论数", "shares": "分享数", "saves": "收藏数", "reactions": "其他互动", "engagement_total_source": "平台来源互动总量",
    "clicks": "点击数", "profile_visits": "主页访问", "follows": "新增关注", "leads": "线索数",
    "registrations": "注册数", "purchases": "购买/订单数", "conversions": "转化数", "revenue": "收入",
    "spend": "投放成本", "ctr": "来源点击率", "engagement_rate": "来源互动率", "body_text": "正文/脚本", "comment_text": "评论文本",
    "engagement_total": "互动总量（已识别分项）", "engagement_rate_reach": "互动率（按触达；已识别分项）", "engagement_rate_views": "互动率（按播放/阅读；已识别分项）", "engagement_rate_impressions": "互动率（按曝光；已识别分项）", "click_rate_impressions": "点击率（按曝光）", "conversion_rate_clicks": "点击转化率", "cpm": "CPM", "cpc": "CPC", "cpa": "CPA", "roas": "ROAS",
}


def norm_header(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[\s_\-（）()【】\[\]：:·/\\]+", "", text)
    return text


def detect_mapping(columns: list[Any]) -> dict[str, str]:
    normalized = {str(c): norm_header(c) for c in columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in ALIASES.items():
        alias_norms = [norm_header(a) for a in aliases]
        exact = [col for col, n in normalized.items() if n in alias_norms]
        if exact:
            # Prefer the shortest exact source header, then original order.
            mapping[canonical] = sorted(exact, key=lambda x: (len(x), list(normalized).index(x)))[0]
    return mapping


def detect_mapping_sources(columns: list[Any]) -> dict[str, list[str]]:
    """Return every matching source column so mixed exports can be coalesced safely."""
    normalized = {str(c): norm_header(c) for c in columns}
    result: dict[str, list[str]] = {}
    for canonical, aliases in ALIASES.items():
        alias_norms = [norm_header(a) for a in aliases]
        matches = [col for col, n in normalized.items() if n in alias_norms]
        if matches:
            result[canonical] = sorted(matches, key=lambda x: (len(x), list(normalized).index(x)))
    return result


def read_csv_robust(path: Path) -> tuple[pd.DataFrame, str]:
    errors = []
    for encoding in ("utf-8-sig", "utf-16", "gb18030", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                sample = handle.read(8192)
            # Sniff common export delimiters but intentionally exclude pipe: pipes often occur in titles/text.
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
            except csv.Error:
                delimiter = ","
            frame = pd.read_csv(path, encoding=encoding, dtype=object, sep=delimiter)
            if frame.empty and len(frame.columns) == 0:
                raise ValueError("CSV 文件没有表头或数据")
            return frame, encoding
        except Exception as exc:  # try next encoding/parser combination
            errors.append(f"{encoding}: {exc}")
    raise ValueError("无法读取 CSV。尝试编码/解析方式失败：" + " | ".join(errors[-3:]))


def load_inputs(paths: list[Path], sheet_name: str | None) -> tuple[pd.DataFrame, list[str], list[dict[str, Any]]]:
    frames: list[pd.DataFrame] = []
    notes: list[str] = []
    source_info: list[dict[str, Any]] = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            frame, encoding = read_csv_robust(path)
            if frame.empty:
                notes.append(f"{path.name}：文件有表头但没有数据行。")
                continue
            frame["_source_file"] = path.name
            frame["_source_sheet"] = "CSV"
            frame["_source_row"] = range(2, len(frame) + 2)
            frames.append(frame)
            source_info.append({"file": path.name, "sheet": "CSV", "rows": len(frame), "encoding": encoding})
        elif suffix in {".xlsx", ".xlsm"}:
            try:
                sheets = pd.read_excel(path, sheet_name=None, dtype=object, engine="openpyxl")
            except Exception as exc:
                raise ValueError(f"无法读取 Excel 文件 {path.name}: {exc}") from exc
            detailed_candidates = []
            summary_candidates = []
            for name, frame in sheets.items():
                if sheet_name and name != sheet_name:
                    continue
                if frame is None or frame.empty or len(frame.columns) == 0:
                    continue
                detected = detect_mapping(list(frame.columns))
                has_metric = any(k in detected for k in COUNT_FIELDS | RATE_FIELDS | {"revenue", "spend", "watch_time", "avg_watch_time"})
                has_content_identity = any(k in detected for k in ("content_id", "title", "published_at"))
                has_platform_dimension = "platform" in detected
                if has_metric and has_content_identity:
                    detailed_candidates.append((name, frame))
                elif has_metric and has_platform_dimension:
                    summary_candidates.append((name, frame))
            # Prefer content-level sheets; do not accidentally append a platform summary/metric tab to content rows.
            selected = detailed_candidates if detailed_candidates else summary_candidates
            if not selected and sheet_name:
                raise ValueError(f"Excel 中未找到指定工作表：{sheet_name}")
            if not selected:
                nonempty = [(n, f) for n, f in sheets.items() if f is not None and not f.empty]
                if nonempty:
                    selected = [nonempty[0]]
                    notes.append(f"{path.name}：没有自动识别到同时包含内容字段和效果指标的工作表，暂用首个非空工作表 {nonempty[0][0]}，请核对。")
            for name, frame in selected:
                frame = frame.copy()
                frame["_source_file"] = path.name
                frame["_source_sheet"] = name
                frame["_source_row"] = range(2, len(frame) + 2)
                frames.append(frame)
                source_info.append({"file": path.name, "sheet": name, "rows": len(frame), "encoding": "Excel"})
        else:
            raise ValueError(f"不支持的文件格式：{path.name}。请使用 CSV、XLSX 或 XLSM。")
    if not frames:
        raise ValueError("没有读取到可分析的数据行。请检查文件是否为空、是否选择了正确工作表。")
    combined = pd.concat(frames, ignore_index=True, sort=False)
    return combined, notes, source_info


def parse_numeric(value: Any, field: str) -> tuple[float | None, str | None]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None, None
    if pd.isna(value):
        return None, None
    if isinstance(value, (int, float, np.number)):
        number = float(value)
        if not math.isfinite(number):
            return None, "非有限数值"
        return number, None
    raw = str(value).strip()
    if raw == "" or raw.lower() in {"na", "n/a", "null", "none", "-", "—"}:
        return None, None
    is_percent = raw.endswith("%") or raw.endswith("％")
    cleaned = raw.replace(",", "").replace("，", "").replace("￥", "").replace("¥", "").replace("$", "").replace("€", "").replace("£", "").replace("元", "").replace("人", "").replace("次", "").replace("条", "").replace("笔", "").replace("小时", "").replace("分钟", "").strip()
    if is_percent:
        cleaned = cleaned[:-1].strip()
    try:
        number = float(cleaned)
    except ValueError:
        return None, "无法解析为数值"
    if not math.isfinite(number):
        return None, "非有限数值"
    if is_percent:
        if field in RATE_FIELDS:
            return number / 100.0, None
        return None, "计数/金额字段出现百分比格式，未纳入数值计算"
    if field in RATE_FIELDS and number > 1:
        return number, "比率字段使用大于1的裸数值，可能是百分数也可能是异常值；未自动换算"
    return number, None


def detect_text_features(frame: pd.DataFrame, mapping: dict[str, str], labels: pd.Series) -> pd.DataFrame:
    title_col = mapping.get("title")
    body_col = mapping.get("body_text")
    if not title_col and not body_col:
        return pd.DataFrame()
    result = pd.DataFrame(index=frame.index)
    title = frame[title_col].fillna("").astype(str) if title_col else pd.Series("", index=frame.index)
    body = frame[body_col].fillna("").astype(str) if body_col else pd.Series("", index=frame.index)
    combined = title + " " + body
    result["标题字数"] = title.str.len()
    result["正文/脚本字数"] = body.str.len()
    result["包含疑问表达"] = combined.str.contains(r"[?？]|为什么|如何|怎么|是否", regex=True)
    result["包含数字"] = combined.str.contains(r"\d", regex=True)
    result["包含括号/引号"] = combined.str.contains(r"[【】\[\]（）()“”\"']", regex=True)
    result["包含步骤/清单表达"] = combined.str.contains(r"\b\d+[.、)]|第一|首先|步骤|清单|方法[一二三四五六七八九十]", regex=True)
    result["包含行动引导"] = combined.str.contains(r"关注|评论|收藏|转发|点击|私信|购买|立即|领取|下载|subscribe|comment|save|share|click|buy", case=False, regex=True)
    result["包含证据/案例表达"] = combined.str.contains(r"数据|研究|报告|案例|实测|实测|来源|测试|对比|study|research|case|test", case=False, regex=True)
    result["表现分层"] = labels.reindex(frame.index).fillna("未分层")
    result.insert(0, "标题", title)
    return result


def safe_md(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    text = str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return text[:180]


def fmt_num(value: Any, percent: bool = False) -> str:
    if value is None or pd.isna(value):
        return "—"
    if percent:
        return f"{float(value):.1%}"
    return f"{float(value):,.2f}".rstrip("0").rstrip(".")


def build_metric_table(mapping: dict[str, str]) -> pd.DataFrame:
    rows = []
    for canonical, source in mapping.items():
        if canonical in NUMERIC_FIELDS:
            unit = "%（仅明确带%时转为小数；裸值>1不自动换算）" if canonical in RATE_FIELDS else "按来源字段单位"
            rows.append({"通用字段": FIELD_LABELS.get(canonical, canonical), "来源字段": source, "单位/处理规则": unit, "状态": "已映射"})
    derived = [
        ("互动总量（已识别分项）", "本文件已识别的点赞+评论+分享+收藏+其他互动字段求和", "只代表已识别分项；未提供的互动类型不视为0，也不等于完整互动总量/独立互动人数"),
        ("互动率_触达", "互动总量÷触达人数", "分母为0/缺失时不计算"),
        ("互动率_播放", "互动总量÷播放/阅读量", "分母为0/缺失时不计算"),
        ("互动率_曝光", "互动总量÷曝光量", "分母为0/缺失时不计算"),
        ("点击率_曝光", "点击数÷曝光量", "仅为本文件可计算口径，不代表平台官方CTR"),
        ("转化率_点击", "转化数÷点击数", "仅当两者可关联且口径一致时参考"),
        ("CPM", "投放成本÷曝光量×1000", "成本与曝光必须同周期同范围"),
        ("CPC", "投放成本÷点击数", "成本与点击必须同周期同范围"),
        ("CPA", "投放成本÷转化数", "转化事件定义须明确"),
        ("ROAS", "收入÷投放成本", "收入归因范围和退款口径需确认"),
    ]
    for name, formula, note in derived:
        rows.append({"通用字段": name, "来源字段": "派生", "单位/处理规则": formula, "状态": note})
    return pd.DataFrame(rows)


def choose_primary_metric(goal: str, mapping: dict[str, str], data: pd.DataFrame, requested: str | None, mapping_sources: dict[str, list[str]] | None = None) -> tuple[str | None, str]:
    if requested:
        if requested in data.columns:
            return requested, "用户指定字段"
        for key, source in mapping.items():
            candidates = (mapping_sources or {}).get(key, [source])
            if requested in candidates:
                return key, "用户指定来源字段"
        raise ValueError(f"指定主指标列不存在：{requested}")
    if goal == "awareness":
        order = ["reach", "impressions"]
    elif goal == "views":
        order = ["views", "unique_views"]
    elif goal == "engagement":
        order = ["engagement_rate_reach", "engagement_rate_views", "engagement_rate_impressions", "engagement_total", "engagement_total_source"]
    elif goal == "traffic":
        order = ["clicks"]
    elif goal == "conversion":
        order = ["conversions", "purchases", "registrations", "leads"]
    elif goal == "revenue":
        order = ["revenue"]
    else:
        # Exploratory default only; it is not treated as the user's business KPI.
        order = ["views", "reach", "impressions", "engagement_total", "engagement_total_source", "clicks"]
    for key in order:
        if key in data.columns and data[key].notna().any():
            return key, "按用户目标选择" if goal != "auto" else "探索性主指标（未提供业务目标）"
    return None, "没有可用主指标"


def add_derived_metrics(data: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    out = data.copy()
    interaction_cols = [c for c in ("likes", "comments", "shares", "saves", "reactions") if c in out.columns]
    if interaction_cols:
        out["engagement_total"] = out[interaction_cols].sum(axis=1, min_count=len(interaction_cols))
    else:
        out["engagement_total"] = np.nan
    for denominator, label in (("reach", "reach"), ("views", "views"), ("impressions", "impressions")):
        if denominator in out.columns and "engagement_total" in out.columns:
            den = out[denominator].replace(0, np.nan)
            out[f"engagement_rate_{label}"] = out["engagement_total"] / den
    if "clicks" in out.columns and "impressions" in out.columns:
        out["click_rate_impressions"] = out["clicks"] / out["impressions"].replace(0, np.nan)
    conversion_fields = [c for c in ("conversions", "purchases", "registrations", "leads") if c in out.columns]
    if conversion_fields and "clicks" in out.columns:
        # Do not sum multiple conversion event types; use a single canonical conversions field if available.
        conv = out["conversions"] if "conversions" in out.columns else out[conversion_fields[0]]
        out["conversion_rate_clicks"] = conv / out["clicks"].replace(0, np.nan)
    if "spend" in out.columns and "impressions" in out.columns:
        out["cpm"] = out["spend"] / out["impressions"].replace(0, np.nan) * 1000
    if "spend" in out.columns and "clicks" in out.columns:
        out["cpc"] = out["spend"] / out["clicks"].replace(0, np.nan)
    if "spend" in out.columns:
        conv = out["conversions"] if "conversions" in out.columns else (out[conversion_fields[0]] if conversion_fields else None)
        if conv is not None:
            out["cpa"] = out["spend"] / conv.replace(0, np.nan)
        if "revenue" in out.columns:
            out["roas"] = out["revenue"] / out["spend"].replace(0, np.nan)
    return out


def quality_report(raw: pd.DataFrame, data: pd.DataFrame, mapping: dict[str, str], parse_issues: list[dict[str, Any]], exact_duplicates: int, duplicate_ids: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    rows.append({"问题类型": "记录总数", "字段/范围": "全部", "数量": len(raw), "说明": "输入文件合并后的原始记录数"})
    rows.append({"问题类型": "完全重复行", "字段/范围": "全部字段", "数量": exact_duplicates, "说明": "分析时默认排除完全重复行；原始数据仍保留在工作簿"})
    rows.append({"问题类型": "重复内容ID", "字段/范围": mapping.get("content_id", "未识别"), "数量": duplicate_ids, "说明": "相同内容ID出现多次的记录数；可能是多次快照、跨平台记录或重复导出，需结合数据粒度判断"})
    interaction_fields = [x for x in ("likes", "comments", "shares", "saves", "reactions") if x in data.columns]
    if interaction_fields:
        rows.append({"问题类型": "互动指标覆盖范围", "字段/范围": "互动总量/互动率", "数量": len(interaction_fields), "说明": "本次仅汇总已识别分项：" + "、".join(FIELD_LABELS.get(x, x) for x in interaction_fields) + "；未提供分项不视为0，结果不代表完整互动总量"})
    for field, source in mapping.items():
        if field not in NUMERIC_FIELDS:
            continue
        if field not in data.columns:
            continue
        missing = int(data[field].isna().sum())
        if missing:
            rows.append({"问题类型": "缺失/无法解析", "字段/范围": FIELD_LABELS.get(field, field), "数量": missing, "说明": f"来源字段：{source}；包含原始空值或无法解析值"})
        neg = int((data[field] < 0).sum())
        if neg:
            rows.append({"问题类型": "负值", "字段/范围": FIELD_LABELS.get(field, field), "数量": neg, "说明": "指标通常不应为负；未自动删除"})
        if field in RATE_FIELDS:
            invalid = int(((data[field] < 0) | (data[field] > 1)).sum())
            if invalid:
                rows.append({"问题类型": "比率范围/单位待核实", "字段/范围": FIELD_LABELS.get(field, field), "数量": invalid, "说明": "存在小于0或大于100%的值；裸数值>1不会自动换算"})
    for issue in parse_issues:
        rows.append({"问题类型": issue["type"], "字段/范围": issue["field"], "数量": issue["count"], "说明": issue["detail"]})
    if not mapping.get("platform"):
        rows.append({"问题类型": "缺少平台维度", "字段/范围": "平台", "数量": 1, "说明": "无法开展平台内分组或跨平台对比"})
    if not mapping.get("title"):
        rows.append({"问题类型": "缺少内容素材字段", "字段/范围": "标题/正文", "数量": 1, "说明": "无法基于文本分析内容特征；只能做数据表现分析"})
    if "observation_days" in data.columns and data["observation_days"].dropna().nunique() > 1:
        rows.append({"问题类型": "观察窗口不一致", "字段/范围": FIELD_LABELS.get("observation_days", "观察天数"), "数量": int(data["observation_days"].dropna().nunique()), "说明": "不同内容的统计观察天数不一致；内容累计量比较可能偏向发布更早或观察更久的内容"})
    elif "observation_days" not in data.columns:
        rows.append({"问题类型": "未提供观察窗口", "字段/范围": "观察天数/数据截至日期", "数量": 1, "说明": "无法确认每条内容累计指标的可比时间窗口；请避免直接按累计量判断内容优劣"})
    return pd.DataFrame(rows)


def summarize_groups(data: pd.DataFrame, primary: str | None, group_cols: list[str], target_value: float | None = None, target_direction: str = "higher") -> pd.DataFrame:
    if not group_cols:
        temp = data.copy()
        temp["分析分组"] = "全部样本"
        group_cols = ["分析分组"]
    rows = []
    for keys, group in data.groupby(group_cols, dropna=False, sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {FIELD_LABELS.get(col, col): ("未提供" if pd.isna(val) else str(val)) for col, val in zip(group_cols, keys)}
        row["内容记录数"] = len(group)
        for metric in ("impressions", "reach", "views", "engagement_total", "engagement_total_source", "clicks", "conversions", "purchases", "registrations", "leads", "revenue", "spend"):
            if metric in group.columns and group[metric].notna().any():
                row[f"{FIELD_LABELS.get(metric, metric)}_合计_已知值"] = group[metric].sum(min_count=1)
                row[f"{FIELD_LABELS.get(metric, metric)}_有效记录数"] = int(group[metric].notna().sum())
                row[f"{FIELD_LABELS.get(metric, metric)}_缺失记录数"] = int(group[metric].isna().sum())
                row[f"{FIELD_LABELS.get(metric, metric)}_中位数"] = group[metric].median()
        if primary and primary in group.columns:
            row["主指标"] = FIELD_LABELS.get(primary, primary)
            row["主指标有效记录数"] = int(group[primary].notna().sum())
            row["主指标缺失记录数"] = int(group[primary].isna().sum())
            row["主指标中位数"] = group[primary].median()
            row["主指标均值"] = group[primary].mean()
            row["主指标最大值"] = group[primary].max()
            if target_value is not None:
                achieved = group[primary] >= target_value if target_direction == "higher" else group[primary] <= target_value
                row["目标值"] = target_value
                row["达标记录数"] = int(achieved.fillna(False).sum())
                row["目标达成率"] = float(achieved.sum() / group[primary].notna().sum()) if group[primary].notna().sum() else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def rank_content(data: pd.DataFrame, primary: str | None, group_cols: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    out = data.copy()
    out["表现分层"] = "未分层"
    if not primary or primary not in out.columns:
        return out, out["表现分层"]
    valid = out[primary].notna()
    if not group_cols:
        group_cols = []
    group_iter = out.loc[valid].groupby(group_cols, dropna=False, sort=False) if group_cols else [("全部样本", out.loc[valid])]
    for _, group in group_iter:
        if len(group) < 4:
            continue
        pct_rank = group[primary].rank(method="average", pct=True)
        out.loc[group.index[pct_rank >= 0.75], "表现分层"] = "高表现组（本组上四分位）"
        out.loc[group.index[pct_rank <= 0.25], "表现分层"] = "待优化组（本组下四分位）"
        out.loc[group.index[(pct_rank > 0.25) & (pct_rank < 0.75)], "表现分层"] = "中间组"
    out["组内排名"] = np.nan
    if group_cols:
        for _, group in out.loc[valid].groupby(group_cols, dropna=False, sort=False):
            out.loc[group.index, "组内排名"] = group[primary].rank(method="min", ascending=False)
    else:
        out.loc[valid, "组内排名"] = out.loc[valid, primary].rank(method="min", ascending=False)
    return out, out["表现分层"]


def make_actions(data: pd.DataFrame, mapping: dict[str, str], primary: str | None, quality: pd.DataFrame, group_cols: list[str], ranked: pd.DataFrame) -> pd.DataFrame:
    actions: list[dict[str, Any]] = []
    def add(issue: str, evidence: str, action: str, priority: str, metric: str, validation: str, period: str) -> None:
        actions.append({"对应发现/问题": issue, "证据": evidence, "建议行动": action, "优先级": priority, "主要观察指标": metric, "验证方式": validation, "建议观察周期/样本": period, "负责人": "待指定", "状态": "待执行", "复盘记录": ""})
    if primary is None:
        add("缺少可用于目标评估的主指标", "当前字段未识别出可用主指标", "补充与本次目标匹配的核心指标，并确认字段定义、分母和观察窗口", "高", "用户确认的目标指标", "补齐字段后重新计算", "下次数据导出")
    if "平台" in [FIELD_LABELS.get(c, c) for c in group_cols] and data["platform"].nunique(dropna=True) > 1:
        add("数据包含多个平台", "不同平台的曝光、播放和互动口径可能不同", "先在各平台内部比较同类内容；仅对定义、单位和观察窗口一致的指标做横向比较", "高", "平台内主指标中位数/目标完成率", "检查平台定义及样本窗口后再比较", "下一轮复盘")
    if (quality["问题类型"] == "完全重复行").any() and int(quality.loc[quality["问题类型"] == "完全重复行", "数量"].iloc[0]) > 0:
        n = int(quality.loc[quality["问题类型"] == "完全重复行", "数量"].iloc[0])
        add("存在完全重复记录", f"识别到 {n} 条完全重复行，分析计算默认排除", "核对导出方式，确认重复记录是否由重复导出造成；若是每日快照，应按快照日期保留而非直接去重", "高", "记录数、内容ID、统计日期", "对照平台后台导出和原始文件", "本次数据清洗")
    if (quality["问题类型"].isin(["观察窗口不一致", "未提供观察窗口"])).any():
        issue_rows = quality[quality["问题类型"].isin(["观察窗口不一致", "未提供观察窗口"])]
        add("内容观察窗口不一致或缺失", "数据质量检查发现累计数据的观察天数/截至日期不完整", "统一内容发布后的统计窗口，或补充每条内容的数据截至日期；在窗口统一前不要仅按累计量给内容排优劣", "高", "统一观察窗口后的主指标", "按发布后相同天数重新导出或建立快照口径", "下一次内容复盘前")
    if (quality["问题类型"] == "数值格式异常").any():
        issues = quality[quality["问题类型"] == "数值格式异常"]
        add("部分指标存在数值格式异常", "；".join(f"{r['字段/范围']}：{r['数量']} 条" for _, r in issues.iterrows()), "回到平台原始导出核对百分比、计数、金额和单位；确认后再纳入计算，不要直接把格式异常值当作0", "高", "字段解析成功率", "修正来源数据或确认字段单位后重新运行", "本次数据清洗")
    if not mapping.get("title") and not mapping.get("body_text"):
        add("缺少内容文本素材", "数据中没有识别到标题或正文/脚本字段", "补充内容标题、正文、脚本或素材说明，以便开展内容特征诊断；当前不对内容原因作推断", "中", "内容特征覆盖率", "抽取一批内容素材与数据ID关联后复盘", "下一轮数据准备")
    if "clicks" in data.columns and any(x in data.columns for x in ("conversions", "purchases", "registrations", "leads")):
        conv_col = "conversions" if "conversions" in data.columns else next(x for x in ("purchases", "registrations", "leads") if x in data.columns)
        eligible = data["clicks"].notna() & data[conv_col].notna() & (data["clicks"] > 0)
        if eligible.any():
            cr = data.loc[eligible, conv_col] / data.loc[eligible, "clicks"]
            if len(cr) >= 4:
                add("存在可计算的点击到转化指标", f"可计算样本 {len(cr)} 条，中位数 {cr.median():.1%}、范围 {cr.min():.1%}–{cr.max():.1%}；当前未提供目标或历史基准，不判断高低", "按平台、活动、内容类型和观察窗口拆解，并检查内容承诺、落地页、转化步骤和归因窗口；不要仅凭该比率认定内容导致转化变化", "中", f"{FIELD_LABELS.get(conv_col, conv_col)}/点击数", "与历史同口径数据或明确目标比较，再检查分环节流失", "下一轮活动/内容周期")
    if primary and primary in data.columns and "表现分层" in ranked.columns:
        has_tiers = ranked["表现分层"].isin(["高表现组（本组上四分位）", "待优化组（本组下四分位）"]).any()
        if has_tiers:
            add("已形成组内高低表现内容分层", f"按 {FIELD_LABELS.get(primary, primary)} 在平台/内容类型组内排序；高低组仅代表本批样本相对位置", "结合高低组的标题、正文、形式、发布时间、投放状态和观察窗口逐条检查；将共同特征转为下一轮可控测试，不直接当作因果结论", "中", "比较高低组特征及护栏指标", "保持平台/内容形式/观察窗口可比，单次优先测试少数变量", "下一批同类内容，建议积累足够样本后复盘")
    if not actions:
        add("当前数据暂未触发明确的自动诊断规则", "没有足够证据支持自动提出特定优化方向", "结合业务目标、内容素材和运营背景进行人工/模型定性复核，避免为了给建议而给出泛化结论", "低", "由用户确认", "补充内容素材或下一周期数据", "下一轮复盘")
    return pd.DataFrame(actions)


def excel_safe_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame({"说明": ["无可展示记录"]})
    out = frame.copy()
    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].map(lambda x: x if not isinstance(x, (dict, list, tuple, set)) else json.dumps(x, ensure_ascii=False))
    return out


def style_workbook(path: Path) -> None:
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="243B53")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        if ws.max_row >= 1:
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(vertical="center", wrap_text=True)
            ws.row_dimensions[1].height = 30
        for col_idx in range(1, ws.max_column + 1):
            values = [str(ws.cell(row, col_idx).value or "") for row in range(1, min(ws.max_row, 100) + 1)]
            width = min(max(max((len(v) for v in values), default=10) + 2, 10), 34)
            ws.column_dimensions[get_column_letter(col_idx)].width = width
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(path)


def add_excel_charts(path: Path, platform_summary: pd.DataFrame, ranking: pd.DataFrame, primary: str | None) -> None:
    wb = load_workbook(path)
    if "图表" in wb.sheetnames:
        del wb["图表"]
    ws = wb.create_sheet("图表")
    ws["A1"] = "内容表现对比图表"
    ws["A1"].font = Font(bold=True, size=16)
    row = 3
    # A platform sample-size chart is safe to compare; it does not compare platform performance.
    if not platform_summary.empty and "内容记录数" in platform_summary.columns and "平台" in platform_summary.columns:
        ws.cell(row, 1, "各平台样本数量（仅表示样本规模，不代表效果高低）")
        row += 1
        ws.cell(row, 1, "平台")
        ws.cell(row, 2, "内容记录数")
        for i, (_, item) in enumerate(platform_summary.iterrows(), start=row + 1):
            ws.cell(i, 1, str(item["平台"]))
            ws.cell(i, 2, int(item["内容记录数"]))
        last = row + len(platform_summary)
        chart = BarChart()
        chart.type = "bar"
        chart.style = 10
        chart.title = "各平台样本数量"
        chart.y_axis.title = "平台"
        chart.x_axis.title = "记录数"
        chart.add_data(Reference(ws, min_col=2, min_row=row, max_row=last), titles_from_data=True)
        chart.set_categories(Reference(ws, min_col=1, min_row=row + 1, max_row=last))
        chart.height = 7
        chart.width = 16
        ws.add_chart(chart, f"D{row}")
        row = last + 18
    # Performance charts are created separately within each platform + content-type cohort.
    if primary and not ranking.empty and "平台" in ranking.columns and "标题" in ranking.columns:
        metric_label = FIELD_LABELS.get(primary, primary)
        if metric_label in ranking.columns:
            group_cols = [c for c in ("平台", "内容类型") if c in ranking.columns]
            cohorts = ranking.groupby(group_cols, dropna=False, sort=False) if group_cols else [("全部样本", ranking)]
            for keys, group in cohorts:
                if not isinstance(keys, tuple):
                    keys = (keys,)
                valid = group[pd.to_numeric(group[metric_label], errors="coerce").notna()].copy()
                if valid.empty:
                    continue
                valid[metric_label] = pd.to_numeric(valid[metric_label], errors="coerce")
                top = valid.sort_values(metric_label, ascending=False).head(10)
                cohort_name = " / ".join(str(x) for x in keys)
                ws.cell(row, 1, f"组内 Top {len(top)}：{cohort_name}（按 {metric_label}，不跨平台混排）")
                row += 1
                ws.cell(row, 1, "内容标题")
                ws.cell(row, 2, metric_label)
                for i, (_, item) in enumerate(top.iterrows(), start=row + 1):
                    ws.cell(i, 1, str(item.get("标题", "未提供标题"))[:60])
                    ws.cell(i, 2, float(item[metric_label]))
                last = row + len(top)
                chart = BarChart()
                chart.type = "bar"
                chart.style = 11
                chart.title = f"{cohort_name}：{metric_label} Top {len(top)}"
                chart.y_axis.title = "内容"
                chart.x_axis.title = metric_label
                chart.add_data(Reference(ws, min_col=2, min_row=row, max_row=last), titles_from_data=True)
                chart.set_categories(Reference(ws, min_col=1, min_row=row + 1, max_row=last))
                chart.height = max(6, min(10, 4 + len(top) * 0.35))
                chart.width = 18
                ws.add_chart(chart, f"D{row}")
                row = last + 18
    for col in (1, 2):
        ws.column_dimensions[get_column_letter(col)].width = 34 if col == 1 else 18
    wb.save(path)


def generate_report(path: Path, source_info: list[dict[str, Any]], notes: list[str], mapping: dict[str, str], data: pd.DataFrame, primary: str | None, primary_reason: str, goal: str, quality: pd.DataFrame, platform_summary: pd.DataFrame, dimension_summary: pd.DataFrame, trend_summary: pd.DataFrame, ranking: pd.DataFrame, features: pd.DataFrame, actions: pd.DataFrame, exact_duplicates: int) -> None:
    lines = [
        "# 内容效果分析与复盘报告", "",
        "> 本报告由可复核的数据处理脚本生成。自动规则只描述数据中可观察到的现象，不自动证明内容特征与效果之间的因果关系。", "",
        "## 1. 分析范围与方法", "",
        f"- 输入文件：{', '.join(x['file'] for x in source_info)}",
        f"- 数据记录：{len(data)} 条（完全重复行 {exact_duplicates} 条已从默认计算样本排除；原始记录保留在工作簿）",
        f"- 分析目标：{goal}",
        f"- 主指标：{FIELD_LABELS.get(primary, primary) if primary else '未识别'}（{primary_reason}）",
        "- 单条内容目标值：详见工作簿“阅读说明”；未提供目标值时不判断达标。",
        f"- 字段映射：{', '.join(f'{FIELD_LABELS.get(k,k)}←{v}' for k,v in mapping.items()) or '未识别'}",
        "- 说明：如未提供业务目标，主指标仅用于探索性排序，不代表 KPI 达成。",
        "",
        "## 2. 数据质量与限制", "",
    ]
    for s in source_info:
        lines.append(f"- {s['file']} / {s['sheet']}：{s['rows']} 条；读取方式：{s['encoding']}")
    for note in notes:
        lines.append(f"- 注意：{note}")
    if not quality.empty:
        lines += ["", "| 问题类型 | 字段/范围 | 数量 | 说明 |", "|---|---|---:|---|"]
        for _, r in quality.iterrows():
            lines.append(f"| {safe_md(r['问题类型'])} | {safe_md(r['字段/范围'])} | {safe_md(r['数量'])} | {safe_md(r['说明'])} |")
    lines += ["", "## 3. 平台/内容分组表现", ""]
    if platform_summary.empty:
        lines.append("暂无可用分组汇总。")
    else:
        display_cols = [c for c in platform_summary.columns if c in {"平台", "内容类型", "主题", "内容记录数", "主指标有效记录数", "主指标缺失记录数", "主指标中位数", "主指标均值", "主指标最大值", "目标值", "达标记录数", "目标达成率"}]
        if not display_cols:
            display_cols = list(platform_summary.columns[:5])
        lines.append("| " + " | ".join(display_cols) + " |")
        lines.append("|" + "|".join(["---"] * len(display_cols)) + "|")
        for _, r in platform_summary.iterrows():
            vals = []
            for c in display_cols:
                value = r.get(c)
                if c in {"主指标中位数", "主指标均值", "主指标最大值"} and pd.notna(value):
                    vals.append(fmt_num(value, bool(primary and (primary in RATE_FIELDS or primary.startswith("engagement_rate") or primary.startswith("click_rate")))))
                elif c == "目标达成率" and pd.notna(value):
                    vals.append(fmt_num(value, True))
                elif c == "目标值" and pd.notna(value):
                    vals.append(fmt_num(value, bool(primary and (primary in RATE_FIELDS or primary.startswith("engagement_rate") or primary.startswith("click_rate")))))
                else:
                    vals.append(safe_md(value))
            lines.append("| " + " | ".join(vals) + " |")
        if data.get("platform", pd.Series(dtype=object)).nunique(dropna=True) > 1:
            lines.append("\n不同平台的主指标中位数仅作各平台内部概览；除非已确认定义、单位、观察窗口一致，不做跨平台绝对排名或求和。")
    lines += ["", "## 4. 主题/形式/活动等维度分析", ""]
    if dimension_summary.empty:
        lines.append("当前没有足够的主题、形式、活动、账号或投放字段可用于维度拆解。")
    else:
        dim_cols = [c for c in dimension_summary.columns if c in {"分析维度", "平台", "主题", "内容类型", "活动", "账号", "流量类型", "内容记录数", "主指标有效记录数", "主指标缺失记录数", "主指标中位数", "目标值", "达标记录数", "目标达成率"}]
        if not dim_cols:
            dim_cols = list(dimension_summary.columns[:6])
        lines.append("| " + " | ".join(dim_cols) + " |")
        lines.append("|" + "|".join(["---"] * len(dim_cols)) + "|")
        for _, r in dimension_summary.iterrows():
            vals = []
            for c in dim_cols:
                value = r.get(c)
                if c in {"主指标中位数", "主指标均值", "主指标最大值"} and pd.notna(value):
                    vals.append(fmt_num(value, bool(primary and (primary in RATE_FIELDS or primary.startswith("engagement_rate") or primary.startswith("click_rate")))))
                elif c == "目标达成率" and pd.notna(value):
                    vals.append(fmt_num(value, True))
                elif c == "目标值" and pd.notna(value):
                    vals.append(fmt_num(value, bool(primary and (primary in RATE_FIELDS or primary.startswith("engagement_rate") or primary.startswith("click_rate")))))
                else:
                    vals.append(safe_md(value))
            lines.append("| " + " | ".join(vals) + " |")
    lines += ["", "## 5. 发布趋势", ""]
    if trend_summary.empty:
        lines.append("未识别到可用于按发布日期分析的有效日期字段，或主指标缺失；未生成时间趋势结论。")
    else:
        lines.append("已按平台和发布日期汇总内容数量、主指标均值与中位数。此处是按内容发布日期分组，不等于平台每日新增/累计数据趋势。")
        lines.append("详细数据见工作簿“发布趋势”工作表。")
    lines += ["", "## 6. 内容表现样本", ""]
    primary_label = FIELD_LABELS.get(primary, primary) if primary else None
    if primary and primary_label in ranking.columns:
        group_cols = [c for c in ("平台", "内容类型") if c in ranking.columns]
        cohorts = ranking.groupby(group_cols, dropna=False, sort=False) if group_cols else [("全部样本", ranking)]
        cols = [c for c in ["平台", "内容类型", "标题", "内容ID", primary_label, "表现分层"] if c in ranking.columns]
        lines.append("按平台/内容类型分别列出组内表现较高的内容；不跨平台混排。")
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + "|".join(["---"] * len(cols)) + "|")
        for _, group in cohorts:
            top = group[pd.to_numeric(group[primary_label], errors="coerce").notna()].sort_values(primary_label, ascending=False).head(3)
            for _, r in top.iterrows():
                vals = []
                for c in cols:
                    value = r.get(c)
                    if c == primary_label and pd.notna(value):
                        vals.append(fmt_num(value, primary in RATE_FIELDS or primary.startswith("engagement_rate") or primary.startswith("click_rate")))
                    else:
                        vals.append(safe_md(value))
                lines.append("| " + " | ".join(vals) + " |")
    else:
        lines.append("当前没有可用主指标，不能进行内容效果排名。")
    lines += ["", "## 7. 内容文本结构特征（规则性统计，不等同于语义判断）", ""]
    if features.empty:
        lines.append("没有识别到标题/正文/脚本字段，或当前素材不足。不能据此推断标题、脚本、画面或选题原因。")
    else:
        feature_cols = [c for c in features.columns if c not in {"标题", "表现分层"}]
        lines.append(f"已对 {len(features)} 条内容提取文本结构特征，包括字数、疑问表达、数字、清单、行动引导和证据表达。详细结果见工作簿“内容特征”工作表。")
        if "表现分层" in features.columns and features["表现分层"].nunique() > 1:
            for label, group in features.groupby("表现分层"):
                lines.append(f"- {label}：{len(group)} 条；平均标题字数 {group['标题字数'].mean():.1f}。")
        lines.append("注意：这些只是可观察文本特征的描述性统计。具体选题价值、表达质量、叙事结构、画面和用户需求，需要 Agent 结合原始内容素材进一步阅读判断。")
    lines += ["", "## 8. 优化行动建议", ""]
    for i, (_, r) in enumerate(actions.iterrows(), 1):
        lines += [f"### {i}. {r['对应发现/问题']}（优先级：{r['优先级']}）", f"- 证据：{r['证据']}", f"- 建议：{r['建议行动']}", f"- 验证：{r['主要观察指标']}；{r['验证方式']}；{r['建议观察周期/样本']}", ""]
    lines += ["## 9. 需要 Agent/运营人员进一步判断的事项", "", "- 结合原始标题、正文、脚本、图片/视频素材，分析内容主题、受众需求、开场、结构、信息价值、表达、视觉呈现和 CTA；本脚本不会伪装成已经完成语义/视觉理解。", "- 核实平台官方指标定义、付费/自然流量、内容观察窗口和归因规则。", "- 将观察到的共同特征转为小规模、可控的验证实验，不直接写成因果结论。", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_analysis(args: argparse.Namespace) -> dict[str, Any]:
    paths = [Path(p).expanduser() for p in args.inputs]
    for p in paths:
        if not p.is_file():
            raise ValueError(f"输入文件不存在：{p}")
    raw, notes, source_info = load_inputs(paths, args.sheet)
    mapping_sources = detect_mapping_sources(list(raw.columns))
    mapping = {field: sources[0] for field, sources in mapping_sources.items()}
    for field, sources in mapping_sources.items():
        if len(sources) > 1:
            notes.append(f"字段 {FIELD_LABELS.get(field, field)} 同时存在多个同义来源列（{', '.join(sources)}），已按每行优先取非空值合并；请核对这些列是否确实同口径。")
    data = pd.DataFrame(index=raw.index)
    parse_issues: list[dict[str, Any]] = []
    for field, sources in mapping_sources.items():
        # Coalesce semantically equivalent columns across files/sheets (e.g. 播放量 and views).
        source_label = " / ".join(sources)
        if len(sources) > 1:
            candidates = raw[sources].replace(r"^\s*$", np.nan, regex=True)
            conflict_mask = candidates.apply(lambda row: row.dropna().astype(str).str.strip().nunique() > 1, axis=1)
            source_series = candidates.bfill(axis=1).iloc[:, 0]
            if conflict_mask.any():
                source_series = source_series.copy()
                source_series.loc[conflict_mask] = np.nan
                parse_issues.append({"type": "同义字段值冲突", "field": FIELD_LABELS.get(field, field), "count": int(conflict_mask.sum()), "detail": f"同一记录的同义列 {source_label} 存在不同非空值，已将冲突记录留空，需人工核对"})
        else:
            source_series = raw[sources[0]]
        if field in NUMERIC_FIELDS:
            parsed = source_series.map(lambda v: parse_numeric(v, field))
            data[field] = parsed.map(lambda x: x[0])
            issue_rows = parsed.map(lambda x: x[1])
            issue_count = int(issue_rows.notna().sum())
            if issue_count:
                examples = issue_rows.dropna().value_counts().head(2).to_dict()
                parse_issues.append({"type": "数值格式异常", "field": FIELD_LABELS.get(field, field), "count": issue_count, "detail": f"来源字段 {source_label}；问题示例：{examples}"})
        elif field in {"published_at", "data_date"}:
            data[field] = pd.to_datetime(source_series, errors="coerce")
        else:
            data[field] = source_series.astype("string").str.strip()
    # Keep source identifiers and a source-content snapshot for traceability.
    for col in ("_source_file", "_source_sheet", "_source_row"):
        data[col] = raw[col] if col in raw.columns else ""
    if "content_id" not in data.columns:
        data["content_id"] = [f"ROW-{i+1:05d}" for i in range(len(data))]
        notes.append("未识别到内容ID，已使用行号生成临时记录ID；这不代表平台真实内容ID。")
    if "platform" not in data.columns:
        data["platform"] = "未提供平台"
    else:
        data["platform"] = data["platform"].fillna("未提供平台").replace("", "未提供平台")
    if "content_type" not in data.columns:
        data["content_type"] = "未提供类型"
    else:
        data["content_type"] = data["content_type"].fillna("未提供类型").replace("", "未提供类型")
    if "title" not in data.columns and mapping.get("title"):
        data["title"] = raw[mapping["title"]]
    # Exact duplicate detection across user source fields, excluding metadata columns.
    raw_compare_cols = [c for c in raw.columns if not str(c).startswith("_source_")]
    exact_mask = raw[raw_compare_cols].duplicated(keep="first") if raw_compare_cols else pd.Series(False, index=raw.index)
    exact_duplicates = int(exact_mask.sum())
    analysis_data = data.loc[~exact_mask].copy() if not args.keep_exact_duplicates else data.copy()
    # Detect content IDs repeated in the analysis grain.
    duplicate_ids = int(analysis_data["content_id"].duplicated(keep=False).sum()) if "content_id" in analysis_data.columns else 0
    analysis_data = add_derived_metrics(analysis_data, mapping)
    # Keep original text columns for the feature extraction step.
    feature_raw = raw.loc[analysis_data.index].copy()
    feature_mapping = dict(mapping)
    for text_field in ("title", "body_text"):
        sources = mapping_sources.get(text_field, [])
        if len(sources) > 1:
            synthetic_col = f"__coalesced_{text_field}"
            feature_raw[synthetic_col] = feature_raw[sources].bfill(axis=1).iloc[:, 0]
            feature_mapping[text_field] = synthetic_col
    features = detect_text_features(feature_raw, feature_mapping, pd.Series("未分层", index=analysis_data.index))
    group_cols = ["platform"]
    if "content_type" in analysis_data.columns and analysis_data["content_type"].nunique(dropna=False) > 1:
        group_cols.append("content_type")
    primary, primary_reason = choose_primary_metric(args.goal, mapping, analysis_data, args.primary_metric, mapping_sources)
    ranked, labels = rank_content(analysis_data, primary, group_cols)
    # Update feature group labels after rank classification.
    if not features.empty:
        features["表现分层"] = labels.reindex(features.index).fillna("未分层")
        features = features.reset_index(drop=True)
    group_summary = summarize_groups(analysis_data, primary, group_cols, args.target_value, args.target_direction)
    # Platform-only comparison, preserving platform-specific data instead of summing platforms.
    platform_summary = summarize_groups(analysis_data, primary, ["platform"], args.target_value, args.target_direction)
    dimension_parts = []
    for dim in ("topic", "content_type", "campaign", "paid_status", "account"):
        if dim in analysis_data.columns and analysis_data[dim].nunique(dropna=True) > 1:
            part = summarize_groups(analysis_data, primary, ["platform", dim], args.target_value, args.target_direction)
            part.insert(0, "分析维度", FIELD_LABELS.get(dim, dim))
            dimension_parts.append(part)
    dimension_summary = pd.concat(dimension_parts, ignore_index=True, sort=False) if dimension_parts else pd.DataFrame()
    trend_summary = pd.DataFrame()
    trend_field = "published_at" if "published_at" in analysis_data.columns and analysis_data["published_at"].notna().any() else None
    if trend_field and primary and primary in analysis_data.columns and duplicate_ids == 0:
        trend_data = analysis_data[analysis_data[trend_field].notna()].copy()
        if not trend_data.empty:
            trend_data["发布日"] = trend_data[trend_field].dt.strftime("%Y-%m-%d")
            trend_summary = trend_data.groupby(["platform", "发布日"], dropna=False).agg(内容数=("content_id", "count"), 主指标中位数=(primary, "median"), 主指标均值=(primary, "mean")).reset_index()
            trend_summary = trend_summary.rename(columns={"platform": "平台"})
    elif trend_field and duplicate_ids > 0:
        notes.append("检测到重复内容ID，可能存在重复导出或多次快照；为避免重复计数，未自动生成发布日期趋势汇总。请先确认数据粒度。")
    quality = quality_report(raw, analysis_data, mapping, parse_issues, exact_duplicates, duplicate_ids)
    actions = make_actions(analysis_data, mapping, primary, quality, group_cols, ranked)
    # Display frames with Chinese headers and original title/IDs.
    rank_display = ranked.copy()
    rename = {k: FIELD_LABELS.get(k, k) for k in rank_display.columns if k in FIELD_LABELS}
    rank_display = rank_display.rename(columns=rename)
    for col in ["_source_file", "_source_sheet", "_source_row"]:
        if col in rank_display.columns:
            rank_display = rank_display.rename(columns={col: {"_source_file": "来源文件", "_source_sheet": "来源工作表", "_source_row": "来源行号"}[col]})
    features_display = features.copy()
    platform_summary_display = platform_summary.rename(columns={k: FIELD_LABELS.get(k, k) for k in platform_summary.columns if k in FIELD_LABELS})
    raw_out = raw.copy()
    norm_out = analysis_data.copy().rename(columns={k: FIELD_LABELS.get(k, k) for k in analysis_data.columns if k in FIELD_LABELS})
    for col in ["_source_file", "_source_sheet", "_source_row"]:
        if col in norm_out.columns:
            norm_out = norm_out.rename(columns={col: {"_source_file": "来源文件", "_source_sheet": "来源工作表", "_source_row": "来源行号"}[col]})
    metric_table = build_metric_table(mapping)
    readme = pd.DataFrame([
        {"项目": "分析目标", "说明": args.goal},
        {"项目": "主指标", "说明": FIELD_LABELS.get(primary, primary) if primary else "未识别"},
        {"项目": "主指标选择依据", "说明": primary_reason},
        {"项目": "单条内容目标值", "说明": f"{args.target_value}（方向：{args.target_direction}）" if args.target_value is not None else "未提供"},
        {"项目": "分析记录数", "说明": len(analysis_data)},
        {"项目": "完全重复行", "说明": f"{exact_duplicates}；默认从计算样本排除，原始数据保留"},
        {"项目": "互动指标覆盖", "说明": "仅汇总已识别的点赞/评论/分享/收藏/其他互动字段；缺失分项不默认为0"},
        {"项目": "平台比较", "说明": "按平台分别展示；不同平台指标口径未核实时，不做绝对横向排名或求和"},
        {"项目": "分层规则", "说明": "每个分析组至少4条有效记录时，按主指标组内百分位分为上四分位/中间/下四分位；小样本不强行分层"},
        {"项目": "重要限制", "说明": "脚本完成定量计算和文本结构特征统计；语义、画面、用户动机及因果判断需 Agent 阅读原始素材并核实"},
    ] + [{"项目": "数据读取", "说明": f"{x['file']} / {x['sheet']}：{x['rows']}条；{x['encoding']}"} for x in source_info] + [{"项目": "提示", "说明": n} for n in notes])
    out_dir = Path(args.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "运营复盘报告.md"
    workbook_path = out_dir / "内容表现分析表.xlsx"
    actions_path = out_dir / "优化行动清单.xlsx"
    generate_report(report_path, source_info, notes, mapping, analysis_data, primary, primary_reason, args.goal, quality, platform_summary_display, dimension_summary, trend_summary, rank_display, features_display, actions, exact_duplicates)
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        excel_safe_frame(readme).to_excel(writer, sheet_name="阅读说明", index=False)
        excel_safe_frame(raw_out).to_excel(writer, sheet_name="原始数据", index=False)
        excel_safe_frame(norm_out).to_excel(writer, sheet_name="标准化数据", index=False)
        excel_safe_frame(metric_table).to_excel(writer, sheet_name="指标字典", index=False)
        excel_safe_frame(platform_summary_display).to_excel(writer, sheet_name="平台对比", index=False)
        excel_safe_frame(dimension_summary).to_excel(writer, sheet_name="维度分析", index=False)
        excel_safe_frame(trend_summary).to_excel(writer, sheet_name="发布趋势", index=False)
        excel_safe_frame(rank_display).to_excel(writer, sheet_name="内容明细", index=False)
        excel_safe_frame(quality).to_excel(writer, sheet_name="数据质量", index=False)
        excel_safe_frame(features_display).to_excel(writer, sheet_name="内容特征", index=False)
        excel_safe_frame(actions).to_excel(writer, sheet_name="行动清单", index=False)
    style_workbook(workbook_path)
    add_excel_charts(workbook_path, platform_summary_display, rank_display, primary)
    with pd.ExcelWriter(actions_path, engine="openpyxl") as writer:
        excel_safe_frame(actions).to_excel(writer, sheet_name="优化行动清单", index=False)
    style_workbook(actions_path)
    manifest = {
        "status": "completed", "inputs": source_info, "records_analyzed": len(analysis_data),
        "exact_duplicate_rows_excluded": 0 if args.keep_exact_duplicates else exact_duplicates,
        "primary_metric": primary, "primary_metric_reason": primary_reason,
        "outputs": [str(workbook_path), str(report_path), str(actions_path)],
        "notes": notes,
    }
    (out_dir / "analysis_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest, "quality": quality, "mapping": mapping, "ranked": ranked, "actions": actions, "features": features}


def main() -> int:
    parser = argparse.ArgumentParser(description="分析 CSV/XLSX 内容表现并生成可复核的 Excel、报告和行动清单")
    parser.add_argument("inputs", nargs="+", help="一个或多个 CSV/XLSX/XLSM 文件")
    parser.add_argument("--goal", choices=["auto", "awareness", "views", "engagement", "traffic", "conversion", "revenue"], default="auto", help="分析目标；auto 仅选择探索性主指标")
    parser.add_argument("--primary-metric", help="指定主指标列名（必须与原始列名完全一致）")
    parser.add_argument("--target-value", type=float, help="单条内容主指标目标值；仅用于逐条内容达标统计，不等同于账号总KPI")
    parser.add_argument("--target-direction", choices=["higher", "lower"], default="higher", help="目标方向：higher 表示越高越好，lower 表示越低越好")
    parser.add_argument("--sheet", help="Excel 指定工作表名称；不指定则自动识别内容数据工作表")
    parser.add_argument("--output-dir", default="content-review-output", help="输出目录")
    parser.add_argument("--keep-exact-duplicates", action="store_true", help="保留完全重复行参与计算（默认排除计算但保留原始记录）")
    args = parser.parse_args()
    try:
        result = run_analysis(args)
        manifest = result["manifest"]
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print("\n质量问题摘要：")
        print(result["quality"].to_string(index=False))
        return 0
    except Exception as exc:
        print(f"分析失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
