"""使用标准库 unittest 验证核心风险边界。"""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_task import validate  # noqa: E402


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT / "examples" / "weekly-report.json").read_text(encoding="utf-8"))
        cls.draft = json.loads((ROOT / "examples" / "daily-brief-draft.json").read_text(encoding="utf-8"))

    def codes(self, data):
        return {item["code"] for item in validate(data)}

    def test_clean_weekly_config(self):
        self.assertEqual(validate(self.sample), [])

    def test_draft_requires_timezone_and_source_authorization(self):
        codes = self.codes(self.draft)
        self.assertIn("TIMEZONE_REQUIRED", codes)
        self.assertIn("SOURCE_NOT_READY", codes)
        self.assertIn("OPEN_QUESTIONS", codes)
        self.assertNotIn("NOT_READY", codes)

    def test_ready_with_questions_is_error(self):
        item = copy.deepcopy(self.draft)
        item["task"]["status"] = "ready_for_manual_setup"
        self.assertIn("NOT_READY", self.codes(item))

    def test_invalid_weekday(self):
        item = copy.deepcopy(self.sample)
        item["schedule"]["days_of_week"] = ["FR", "FR"]
        self.assertIn("WEEKDAYS_INVALID", self.codes(item))

    def test_nonexistent_timezone(self):
        item = copy.deepcopy(self.sample)
        item["schedule"]["timezone"] = "Mars/Utopia"
        self.assertIn("TIMEZONE_INVALID", self.codes(item))

    def test_invalid_time(self):
        item = copy.deepcopy(self.sample)
        item["schedule"]["time_local"] = "25:61"
        self.assertIn("TIME_INVALID", self.codes(item))

    def test_missing_month_end_policy(self):
        item = copy.deepcopy(self.sample)
        item["schedule"] = {"kind": "monthly", "timezone": "Asia/Shanghai", "time_local": "09:00", "day_of_month": 31}
        self.assertIn("SHORT_MONTH_POLICY", self.codes(item))

    def test_cron_out_of_range(self):
        item = copy.deepcopy(self.sample)
        item["schedule"] = {"kind": "cron", "timezone": "Asia/Shanghai", "expression": "99 25 * * *"}
        self.assertIn("CRON_INVALID", self.codes(item))

    def test_good_cron(self):
        item = copy.deepcopy(self.sample)
        item["schedule"] = {"kind": "cron", "timezone": "Asia/Shanghai", "expression": "0 9 * * 1-5"}
        self.assertEqual(validate(item), [])

    def test_six_field_cron_is_question_when_draft(self):
        item = copy.deepcopy(self.sample)
        item["task"]["status"] = "draft"
        item["schedule"] = {"kind": "cron", "timezone": "Asia/Shanghai", "expression": "0 0 9 * * 1-5"}
        issues = {row["code"]: row["level"] for row in validate(item)}
        self.assertEqual(issues.get("CRON_FIELD_COUNT"), "QUESTION")
        self.assertNotIn("NOT_READY", issues)

    def test_one_time_requires_offset(self):
        item = copy.deepcopy(self.sample)
        item["schedule"] = {"kind": "one_time", "timezone": "Asia/Shanghai", "at": "2026-12-01T09:00:00"}
        self.assertIn("TIMEZONE_OFFSET_MISSING", self.codes(item))

    def test_side_effects_require_approval(self):
        item = copy.deepcopy(self.sample)
        item["execution"]["side_effects"] = "destructive"
        self.assertIn("APPROVAL_REQUIRED", self.codes(item))

    def test_retry_requires_idempotency_warning(self):
        item = copy.deepcopy(self.sample)
        item["execution"]["side_effects"] = "external_write"
        item["execution"]["approval_required"] = True
        item["retry"]["max_attempts"] = 3
        self.assertIn("RETRY_DUPLICATE", self.codes(item))

    def test_invalid_end_date(self):
        item = copy.deepcopy(self.sample)
        item["schedule"]["start_at"] = "2027-01-01T00:00:00+08:00"
        item["schedule"]["end_at"] = "2026-12-01T00:00:00+08:00"
        self.assertIn("TIME_RANGE_REVERSED", self.codes(item))

    def test_event_needs_verified_platform(self):
        item = copy.deepcopy(self.sample)
        item["task"]["status"] = "draft"
        item["schedule"] = {"kind": "event", "event_source": "mail", "event_name": "new_message"}
        self.assertIn("EVENT_PLATFORM_UNVERIFIED", self.codes(item))


    def test_bad_types_do_not_crash(self):
        for section, field, value in [
            ("task", "status", []),
            ("schedule", "kind", []),
            ("schedule", "days_of_week", [[], "FR"]),
            ("execution", "side_effects", []),
            ("notifications", "channel", []),
            ("controls", "overlap_policy", [])
        ]:
            item = copy.deepcopy(self.sample)
            item.setdefault(section, {})[field] = value
            self.assertTrue(any(i["level"] == "ERROR" for i in validate(item)), f"{section}.{field}")

    def test_deployed_claim_rejected(self):
        item = copy.deepcopy(self.sample)
        item["platform"]["deployment_state"] = "active"
        self.assertIn("DEPLOYMENT_STATE", self.codes(item))


if __name__ == "__main__":
    unittest.main()
