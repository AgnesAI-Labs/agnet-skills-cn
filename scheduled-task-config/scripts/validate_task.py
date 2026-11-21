#!/usr/bin/env python3
"""离线定时任务意图配置检查器（Python 标准库，无调度/联网副作用）。

用法: python3 scripts/validate_task.py path/to/task-config.json [--json]
0=无 ERROR; 1=有 ERROR; 2=JSON/IO 读取失败。
注意: 只做基础结构和业务规则静态校验，不替代完整 JSON Schema 或平台验证。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LEVEL_ORDER = {"ERROR": 0, "QUESTION": 1, "WARNING": 2}
WEEKDAYS = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
ALLOWED_KINDS = {"one_time", "daily", "weekly", "monthly", "interval", "cron", "event"}


def add(issues: list[dict], level: str, code: str, path: str, message: str) -> None:
    issues.append({"level": level, "code": code, "path": path, "message": message})


def subobj(root: dict, key: str, issues: list[dict], required: bool = False) -> dict:
    item = root.get(key)
    if item is None:
        if required:
            add(issues, "ERROR", "MISSING_SECTION", key, "缺少必填对象")
        return {}
    if not isinstance(item, dict):
        add(issues, "ERROR", "BAD_TYPE", key, "必须是 JSON 对象")
        return {}
    return item


def require_text(obj: dict, key: str, path: str, issues: list[dict], ready: bool) -> None:
    if not isinstance(obj.get(key), str) or not obj[key].strip():
        add(issues, "ERROR" if ready else "QUESTION", "MISSING_TEXT", f"{path}.{key}", "缺少非空文本字段")


def dt(value: Any, path: str, issues: list[dict]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        add(issues, "ERROR", "INVALID_DATETIME", path, "需提供 ISO 8601 日期时间（含时区偏移）")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        add(issues, "ERROR", "INVALID_DATETIME", path, "ISO 8601 时间格式不正确")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        add(issues, "ERROR", "TIMEZONE_OFFSET_MISSING", path, "时间戳必须包含 UTC 偏移，如 +08:00 或 Z")
        return None
    return parsed


def check_timezone(value: Any, issues: list[dict], ready: bool) -> ZoneInfo | None:
    if not isinstance(value, str) or not value.strip():
        add(issues, "ERROR" if ready else "QUESTION", "TIMEZONE_REQUIRED", "schedule.timezone", "缺少 IANA 时区，例如 Asia/Shanghai")
        return None
    try:
        return ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        add(issues, "ERROR", "TIMEZONE_INVALID", "schedule.timezone", "不是当前环境可识别的 IANA 时区")
        return None


def check_local_time(value: Any, issues: list[dict], ready: bool) -> None:
    if value is None:
        add(issues, "ERROR" if ready else "QUESTION", "TIME_REQUIRED", "schedule.time_local", "需要明确本地执行时间 HH:MM")
    elif not isinstance(value, str) or not TIME_PATTERN.fullmatch(value):
        add(issues, "ERROR", "TIME_INVALID", "schedule.time_local", "应为 00:00–23:59 的 HH:MM 时间")


def check_cron_atom(atom: str, low: int, high: int) -> bool:
    """仅识别常见5字段数字形式，不解析平台专有修饰符。"""
    for part in atom.split(","):
        match = re.fullmatch(r"(\*|\d+|\d+-\d+)(?:/(\d+))?", part)
        if not match:
            return False
        base, step = match.groups()
        if step is not None and int(step) < 1:
            return False
        if base == "*":
            continue
        nums = [int(x) for x in base.split("-")]
        if not all(low <= x <= high for x in nums):
            return False
        if len(nums) == 2 and nums[0] > nums[1]:
            return False
    return True


def check_cron(expr: Any, issues: list[dict], ready: bool) -> None:
    if not isinstance(expr, str) or not expr.strip():
        add(issues, "ERROR" if ready else "QUESTION", "CRON_REQUIRED", "schedule.expression", "缺少 Cron 表达式")
        return
    fields = expr.split()
    if len(fields) != 5:
        add(issues, "ERROR" if ready else "QUESTION", "CRON_FIELD_COUNT", "schedule.expression", "本通用模型默认按标准 5 字段数字 Cron 检查；6/7 字段是平台方言，请核验目标调度器，不要据此否定任务本身")
        return
    bounds = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    if not all(check_cron_atom(field, *lim) for field, lim in zip(fields, bounds)):
        add(issues, "ERROR" if ready else "QUESTION", "CRON_INVALID", "schedule.expression", "字段含非通用数字语法或越界；请核对方言和目标调度器，不要据此否定任务本身")
    elif fields[2] != "*" and fields[4] != "*":
        add(issues, "WARNING", "CRON_DIALECT", "schedule.expression", "日期字段与星期字段同时限制时，各 Cron 方言的 OR/AND 语义可能不同")


def validate(data: Any) -> list[dict]:
    issues: list[dict] = []
    if not isinstance(data, dict):
        add(issues, "ERROR", "ROOT_NOT_OBJECT", "$", "根内容必须是 JSON 对象")
        return issues

    if data.get("schema_version") != "1.0.0":
        add(issues, "ERROR", "SCHEMA_VERSION", "schema_version", "schema_version 应为 1.0.0")

    task = subobj(data, "task", issues, required=True)
    schedule = subobj(data, "schedule", issues, required=True)
    execution = subobj(data, "execution", issues, required=True)
    platform = subobj(data, "platform", issues, required=True)
    retry = subobj(data, "retry", issues)
    notifications = subobj(data, "notifications", issues)
    controls = subobj(data, "controls", issues)
    status = task.get("status", "draft")
    if not isinstance(status, str) or status not in {"draft", "ready_for_manual_setup", "paused"}:
        add(issues, "ERROR", "BAD_STATUS", "task.status", "状态只能是 draft / ready_for_manual_setup / paused")
    ready = status == "ready_for_manual_setup"

    require_text(task, "name", "task", issues, ready=True)
    require_text(task, "goal", "task", issues, ready=ready)
    require_text(execution, "instruction", "execution", issues, ready=ready)
    if isinstance(execution.get("instruction"), str) and len(execution["instruction"].strip()) < 30:
        add(issues, "WARNING", "PROMPT_SHORT", "execution.instruction", "指令较短，检查是否包含输入来源、时间范围、完成标准与失败条件")

    kind = schedule.get("kind")
    if not isinstance(kind, str) or kind not in ALLOWED_KINDS:
        add(issues, "ERROR", "KIND_INVALID", "schedule.kind", "触发类型不在允许值中")
    tz = None
    if isinstance(kind, str) and kind in {"one_time", "daily", "weekly", "monthly", "cron"}:
        tz = check_timezone(schedule.get("timezone"), issues, ready)
    elif kind == "interval" and schedule.get("timezone") is not None:
        tz = check_timezone(schedule.get("timezone"), issues, ready)

    if kind == "one_time":
        if schedule.get("at") is None:
            add(issues, "ERROR" if ready else "QUESTION", "ONCE_AT_REQUIRED", "schedule.at", "单次任务必须给出带偏移的绝对时间")
        else:
            parsed = dt(schedule["at"], "schedule.at", issues)
            if parsed and tz:
                converted = parsed.astimezone(tz)
                if parsed.utcoffset() != converted.utcoffset():
                    add(issues, "WARNING", "OFFSET_DIFFERENCE", "schedule.at", "时间戳偏移与指定 IANA 时区当时的偏移不同；确认是否刻意使用另一时区表示同一时刻")
    if isinstance(kind, str) and kind in {"daily", "weekly", "monthly"}:
        check_local_time(schedule.get("time_local"), issues, ready)
    if kind == "weekly":
        days = schedule.get("days_of_week")
        if not isinstance(days, list) or not days:
            add(issues, "ERROR" if ready else "QUESTION", "WEEKDAYS_REQUIRED", "schedule.days_of_week", "每周任务需至少指定一天")
        elif any(not isinstance(x, str) or x not in WEEKDAYS for x in days) or len(set(days)) != len(days):
            add(issues, "ERROR", "WEEKDAYS_INVALID", "schedule.days_of_week", "星期必须使用不重复的 MO/TU/WE/TH/FR/SA/SU")
    if kind == "monthly":
        day = schedule.get("day_of_month")
        if type(day) is not int or not 1 <= day <= 31:
            add(issues, "ERROR" if ready else "QUESTION", "MONTHDAY_INVALID", "schedule.day_of_month", "每月执行日必须为 1–31 的整数；特殊月末工作日需平台扩展")
        elif day > 28 and (not isinstance(schedule.get("missing_day_policy"), str) or schedule.get("missing_day_policy") not in {"skip", "last_day"}):
            add(issues, "ERROR" if ready else "QUESTION", "SHORT_MONTH_POLICY", "schedule.missing_day_policy", "29–31 日可能不存在，请选择 skip 或 last_day")
    if kind == "interval":
        n, unit = schedule.get("every"), schedule.get("unit")
        if type(n) is not int or n < 1 or not isinstance(unit, str) or unit not in {"minutes", "hours", "days", "weeks"}:
            add(issues, "ERROR" if ready else "QUESTION", "INTERVAL_INVALID", "schedule", "间隔任务需要正整数 every 和 unit（minutes/hours/days/weeks）")
        if type(n) is int and unit == "minutes" and n < 15:
            add(issues, "WARNING", "HIGH_FREQUENCY", "schedule.every", "高频执行可能受到宿主频率、额度和并发限制")
        if schedule.get("anchor_at") is not None:
            dt(schedule["anchor_at"], "schedule.anchor_at", issues)
    if kind == "cron":
        check_cron(schedule.get("expression"), issues, ready)
    if kind == "event":
        require_text(schedule, "event_source", "schedule", issues, ready)
        require_text(schedule, "event_name", "schedule", issues, ready)
        if not platform.get("capabilities_verified"):
            add(issues, "QUESTION", "EVENT_PLATFORM_UNVERIFIED", "platform", "事件触发需先核验目标平台具备监听能力")

    start = dt(schedule["start_at"], "schedule.start_at", issues) if "start_at" in schedule else None
    end = dt(schedule["end_at"], "schedule.end_at", issues) if "end_at" in schedule else None
    if start and end and start > end:
        add(issues, "ERROR", "TIME_RANGE_REVERSED", "schedule", "结束时间不得早于开始时间")
    if schedule.get("holiday_calendar_ref") is not None and (not isinstance(schedule.get("holiday_calendar_ref"), str) or not schedule.get("holiday_calendar_ref")):
        add(issues, "QUESTION", "CALENDAR_MISSING", "schedule.holiday_calendar_ref", "节假日日历引用为空")
    if schedule.get("custom_rule"):
        add(issues, "QUESTION", "CUSTOM_RULE_ADAPTER", "schedule.custom_rule", "自定义规则无法靠标准调度字段保证，请核验目标平台或外部日历能力")

    sources = execution.get("sources", [])
    if not isinstance(sources, list):
        add(issues, "ERROR", "SOURCES_TYPE", "execution.sources", "来源字段必须是列表")
    else:
        for i, src in enumerate(sources):
            if not isinstance(src, dict):
                add(issues, "ERROR", "SOURCE_TYPE", f"execution.sources[{i}]", "来源必须是对象")
                continue
            access = src.get("access")
            if access not in {"confirmed", "needs_authorization", "unknown"}:
                add(issues, "ERROR", "ACCESS_INVALID", f"execution.sources[{i}].access", "权限状态应是 confirmed / needs_authorization / unknown")
            elif access != "confirmed":
                add(issues, "QUESTION", "SOURCE_NOT_READY", f"execution.sources[{i}].access", "来源访问权限或可用性尚待核实")
            if not src.get("locator"):
                add(issues, "QUESTION", "SOURCE_LOCATOR_MISSING", f"execution.sources[{i}].locator", "数据源定位信息尚未提供")

    effects = execution.get("side_effects", "read_only")
    if not isinstance(effects, str) or effects not in {"read_only", "external_write", "destructive"}:
        add(issues, "ERROR", "SIDE_EFFECT_INVALID", "execution.side_effects", "操作类型不合法")
    if effects != "read_only" and execution.get("approval_required") is not True:
        add(issues, "ERROR", "APPROVAL_REQUIRED", "execution.approval_required", "对外写入或删除操作必须要求用户批准")

    attempts = retry.get("max_attempts", 1)
    if type(attempts) is not int or not 1 <= attempts <= 20:
        add(issues, "ERROR", "RETRY_INVALID", "retry.max_attempts", "最大尝试次数需为 1–20 的整数（含首次）")
    elif attempts > 1 and effects != "read_only":
        add(issues, "WARNING", "RETRY_DUPLICATE", "retry.max_attempts", "存在副作用的任务重试可能重复执行，应制定幂等/去重策略")
    backoff = retry.get("backoff_seconds", 0)
    if type(backoff) is not int or backoff < 0:
        add(issues, "ERROR", "BACKOFF_INVALID", "retry.backoff_seconds", "退避秒数应为非负整数")

    channel = notifications.get("channel", "none")
    if not isinstance(channel, str) or channel not in {"none", "platform_default", "push", "email", "chat", "webhook"}:
        add(issues, "ERROR", "CHANNEL_INVALID", "notifications.channel", "未知通知渠道")
    if channel == "none" and (notifications.get("on_success") or notifications.get("on_failure")):
        add(issues, "QUESTION", "NOTIFICATION_CHANNEL_MISSING", "notifications.channel", "已要求通知但没有可用渠道")
    if not isinstance(controls.get("missed_run", "platform_default"), str) or controls.get("missed_run", "platform_default") not in {"platform_default", "skip", "run_once"}:
        add(issues, "ERROR", "MISSED_RUN_INVALID", "controls.missed_run", "未知的错过执行策略")
    if not isinstance(controls.get("overlap_policy", "platform_default"), str) or controls.get("overlap_policy", "platform_default") not in {"platform_default", "skip_new", "queue", "allow"}:
        add(issues, "ERROR", "OVERLAP_INVALID", "controls.overlap_policy", "未知的任务重叠策略")

    if not isinstance(platform.get("target"), str) or not platform.get("target", "").strip():
        add(issues, "ERROR", "PLATFORM_TARGET", "platform.target", "平台目标应提供非空值；未知可用 generic")
    if platform.get("deployment_state") != "not_deployed":
        add(issues, "ERROR", "DEPLOYMENT_STATE", "platform.deployment_state", "本 Skill 仅生成未部署配置，必须标注 not_deployed")
    if type(platform.get("capabilities_verified")) is not bool:
        add(issues, "ERROR", "CAPABILITIES_TYPE", "platform.capabilities_verified", "应为 true/false，不得凭空标记已核验")
    unsupported = platform.get("unsupported_fields", [])
    if not isinstance(unsupported, list) or any(not isinstance(x, str) for x in unsupported):
        add(issues, "ERROR", "UNSUPPORTED_TYPE", "platform.unsupported_fields", "应为字符串列表")
    elif unsupported:
        add(issues, "WARNING", "UNSUPPORTED_FIELDS", "platform.unsupported_fields", "目标平台存在不支持的字段，需给替代办法")

    questions = data.get("open_questions", [])
    if not isinstance(questions, list) or any(not isinstance(x, str) for x in questions):
        add(issues, "ERROR", "QUESTIONS_TYPE", "open_questions", "应为字符串列表")
    elif questions:
        add(issues, "QUESTION", "OPEN_QUESTIONS", "open_questions", f"还有 {len(questions)} 个需要确认的问题")
    assumptions = data.get("assumptions", [])
    if not isinstance(assumptions, list) or any(not isinstance(x, dict) for x in assumptions):
        add(issues, "ERROR", "ASSUMPTIONS_TYPE", "assumptions", "应为假设对象列表")
    elif any(a.get("confirmed") is not True for a in assumptions):
        add(issues, "QUESTION", "ASSUMPTIONS_UNCONFIRMED", "assumptions", "存在尚未确认的假设")

    # 按键值和文本识别潜在明文，不在检查输出中暴露其内容。
    def has_plain_secret(node):
        if isinstance(node, dict):
            for key, value in node.items():
                is_secret_key = bool(re.search(r"(?i)(?:^|_)(?:api_key|access_token|password|secret|cookie|private_key)$", key))
                if is_secret_key and isinstance(value, str) and len(value) >= 8 and not value.startswith(("${", "secret://", "vault://", "env:")):
                    return True
                if has_plain_secret(value):
                    return True
        elif isinstance(node, list):
            return any(has_plain_secret(value) for value in node)
        elif isinstance(node, str):
            return bool(re.search(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret|cookie)\s*[:=]\s*[\"']?[a-z0-9_\-\.]{12,}", node))
        return False
    if has_plain_secret(data):
        add(issues, "WARNING", "POSSIBLE_SECRET", "$", "可能包含明文凭据；请使用安全引用并检查后再分享")

    # schema 允许的其他基础字段也应满足约定类型，避免以非法类型通过初检。
    if "approval_required" in execution and type(execution["approval_required"]) is not bool:
        add(issues, "ERROR", "APPROVAL_TYPE", "execution.approval_required", "必须为 true/false")
    if "on_success" in notifications and type(notifications["on_success"]) is not bool:
        add(issues, "ERROR", "NOTIFICATION_TYPE", "notifications.on_success", "必须为 true/false")
    if "on_failure" in notifications and type(notifications["on_failure"]) is not bool:
        add(issues, "ERROR", "NOTIFICATION_TYPE", "notifications.on_failure", "必须为 true/false")
    if "on_failure" in retry and (not isinstance(retry["on_failure"], str) or retry["on_failure"] not in {"notify", "manual_review", "skip", "pause", "platform_default"}):
        add(issues, "ERROR", "FAILURE_POLICY_INVALID", "retry.on_failure", "失败策略不在允许范围内")
    if ready and any(it["level"] == "QUESTION" for it in issues):
        add(issues, "ERROR", "NOT_READY", "task.status", "存在待确认事项，不能标为 ready_for_manual_setup")

    return sorted(issues, key=lambda x: (LEVEL_ORDER[x["level"]], x["path"], x["code"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="定时任务配置静态检查（不创建或运行计划任务）")
    parser.add_argument("path", type=Path, help="配置 JSON 路径")
    parser.add_argument("--json", action="store_true", help="输出机器可读的检查结果 JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"无法读取或解析 JSON：{exc}", file=sys.stderr)
        return 2
    issues = validate(data)
    if args.json:
        print(json.dumps({"errors": sum(x["level"] == "ERROR" for x in issues), "issues": issues}, ensure_ascii=False, indent=2))
    elif issues:
        for item in issues:
            print(f"[{item['level']}] {item['code']} · {item['path']}: {item['message']}")
        print(f"静态检查结束：{sum(x['level']=='ERROR' for x in issues)} 个错误，{sum(x['level']=='QUESTION' for x in issues)} 项待确认，{sum(x['level']=='WARNING' for x in issues)} 条警告；未执行任务。")
    else:
        print("静态检查通过：未发现脚本覆盖范围内的错误/待确认/警告；未核验目标平台，也未执行任务。")
    return 1 if any(x["level"] == "ERROR" for x in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
