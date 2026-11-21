#!/usr/bin/env python3
"""Validate the schema and traceability of a fact-checking record.

This validator does NOT establish whether any claim or source is factually true.
No network or third-party dependencies are used.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

STATUSES = {
    "有证据支持", "部分支持", "与证据冲突", "证据不足", "暂无法核实", "已过时"
}
RELATIONSHIPS = {"支持", "部分支持", "冲突", "背景", "无关"}
ACCESS_STATES = {"已读取原文", "已读取用户材料", "仅检索摘要", "无法访问"}
READ_STATES = {"已读取原文", "已读取用户材料"}
MODES = {"快速", "标准", "深度"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERNS = {
    "claims": re.compile(r"^C\d{3,}$"),
    "sources": re.compile(r"^S\d{3,}$"),
    "evidence": re.compile(r"^E\d{3,}$"),
}


class RecordValidationError(ValueError):
    """Invalid record or invalid JSON."""


def load_record(path: str | Path) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as fp:
            result = json.load(fp)
    except (OSError, UnicodeError, json.JSONDecodeError) as err:
        raise RecordValidationError(f"无法读取合法 JSON：{err}") from err
    if not isinstance(result, dict):
        raise RecordValidationError("根结构必须是 JSON 对象")
    return result


def _required_text(obj: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    if not isinstance(obj.get(key), str) or not obj[key].strip():
        errors.append(f"{path}.{key}：必须是非空字符串")


def _list_of_text(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{path}：必须是字符串数组")


def validate_record(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings). Warnings do not block export."""
    errors: list[str] = []
    warnings: list[str] = []
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        errors.append("metadata：必须是对象")
        meta = {}
    for key in ("title", "checked_at", "mode", "scope"):
        _required_text(meta, key, "metadata", errors)
    if isinstance(meta.get("checked_at"), str) and not DATE_PATTERN.fullmatch(meta["checked_at"]):
        errors.append("metadata.checked_at：日期格式必须为 YYYY-MM-DD")
    if meta.get("mode") not in MODES:
        errors.append("metadata.mode：仅可为快速/标准/深度")
    for optional in ("uncovered", "limitations"):
        if optional in meta:
            _list_of_text(meta[optional], "metadata." + optional, errors)
    sets: dict[str, dict[str, dict[str, Any]]] = {}
    for group in ("claims", "sources", "evidence"):
        rows = data.get(group)
        if not isinstance(rows, list):
            errors.append(f"{group}：必须是数组")
            rows = []
        found: dict[str, dict[str, Any]] = {}
        for index, obj in enumerate(rows):
            path = f"{group}[{index}]"
            if not isinstance(obj, dict):
                errors.append(f"{path}：必须是对象")
                continue
            _required_text(obj, "id", path, errors)
            rid = obj.get("id")
            if not isinstance(rid, str):
                continue
            if not ID_PATTERNS[group].fullmatch(rid):
                errors.append(f"{path}.id：必须匹配 {group} 对应的 C/S/E 三位以上编号")
            if rid in found:
                errors.append(f"{path}.id：重复 ID {rid}")
            found[rid] = obj
        sets[group] = found

    claims, sources, evidence = (sets["claims"], sets["sources"], sets["evidence"])
    if not claims:
        errors.append("claims：至少要有一条待核查主张")
    for cid, c in claims.items():
        path = f"claims.{cid}"
        for key in ("original_text", "location", "status", "finding"):
            _required_text(c, key, path, errors)
        if c.get("status") not in STATUSES:
            errors.append(f"{path}.status：不是允许的六种状态")
        if c.get("priority", "中") not in {"高", "中", "低"}:
            errors.append(f"{path}.priority：仅可为高/中/低")
        if c.get("status") == "已过时" and not str(c.get("time_context", "")).strip():
            errors.append(f"{path}.time_context：标记已过时需要具体时间背景")
        if c.get("status") in {"证据不足", "暂无法核实"} and not str(c.get("limitations", "")).strip():
            warnings.append(f"{path}：建议说明具体证据或访问限制")

    for sid, s in sources.items():
        path = f"sources.{sid}"
        for key in ("title", "access_state"):
            _required_text(s, key, path, errors)
        if s.get("access_state") not in ACCESS_STATES:
            errors.append(f"{path}.access_state：不在允许的四种访问状态内")
        for date_field in ("published_at", "accessed_at"):
            value = s.get(date_field, "")
            if value and (not isinstance(value, str) or not DATE_PATTERN.fullmatch(value)):
                errors.append(f"{path}.{date_field}：应为 YYYY-MM-DD 或空字符串")
        if s.get("access_state") in READ_STATES and not str(s.get("locator", s.get("uri", ""))).strip():
            warnings.append(f"{path}：已读取来源但缺少可复查的来源定位或文件名")
        if s.get("access_state") == "已读取原文" and not str(s.get("accessed_at", "")).strip():
            warnings.append(f"{path}：建议记录实际访问日期")

    by_claim: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {cid: [] for cid in claims}
    for eid, ev in evidence.items():
        path = f"evidence.{eid}"
        for key in ("claim_id", "source_id", "relationship", "summary"):
            _required_text(ev, key, path, errors)
        cid, sid = ev.get("claim_id"), ev.get("source_id")
        if cid not in claims:
            errors.append(f"{path}.claim_id：主张 {cid!r} 不存在")
        if sid not in sources:
            errors.append(f"{path}.source_id：来源 {sid!r} 不存在")
        if ev.get("relationship") not in RELATIONSHIPS:
            errors.append(f"{path}.relationship：不是允许的证据关系")
        if cid in claims and sid in sources:
            by_claim[cid].append((ev, sources[sid]))

    for cid, c in claims.items():
        status = c.get("status")
        links = by_claim[cid]
        reliable = [(e, s) for e, s in links if s.get("access_state") in READ_STATES]
        rels = {e.get("relationship") for e, _ in reliable}
        path = f"claims.{cid}"
        if status == "有证据支持" and "支持" not in rels:
            errors.append(f"{path}：有证据支持需有已读取来源且关系为‘支持’的证据")
        if status == "与证据冲突" and "冲突" not in rels:
            errors.append(f"{path}：与证据冲突需有已读取来源且关系为‘冲突’的证据")
        if status == "部分支持" and not (rels & {"部分支持", "支持"}):
            errors.append(f"{path}：部分支持需有已读取来源的有效证据")
        if status == "已过时" and not reliable:
            errors.append(f"{path}：已过时需至少一条来自已读取来源的时效证据")
        if status == "证据不足" and not links:
            warnings.append(f"{path}：没有任何来源记录时更适合‘暂无法核实’")
        if status == "有证据支持" and "冲突" in rels:
            warnings.append(f"{path}：同时存在支持与冲突证据，建议解释或改判")
        if status in {"证据不足", "暂无法核实"} and not c.get("finding", "").strip():
            errors.append(f"{path}.finding：必须说明不确定原因")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验核查记录结构与证据链，不验证事实真假")
    parser.add_argument("input", type=Path, help="记录 JSON 文件")
    args = parser.parse_args()
    try:
        record = load_record(args.input)
    except RecordValidationError as err:
        print(f"[错误] {err}", file=sys.stderr)
        return 2
    errors, warnings = validate_record(record)
    for message in warnings:
        print("[提醒] " + message)
    for message in errors:
        print("[错误] " + message, file=sys.stderr)
    if errors:
        print(f"校验失败：{len(errors)} 个错误，{len(warnings)} 个提醒", file=sys.stderr)
        return 1
    print(f"格式与关联校验通过；{len(warnings)} 个提醒。注意：此结果不代表现实事实已被验证。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
