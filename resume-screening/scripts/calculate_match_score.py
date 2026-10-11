#!/usr/bin/env python3
"""
简历匹配度评估与计算脚本

本脚本仅负责确定性的计算职责：根据LLM评估出的5个分项分数，
汇总计算总分、判断是否通过初筛（>=80分）、生成面试侧重点建议，
并输出格式化的JSON结果。

说明：
  - 岗位要求5个维度的识别与逐维度评估打分，由执行skill的LLM
    直接基于文本参数（resume_content / job_requirements）完成，
    不在本脚本职责范围内。
  - 本脚本不读取任何文件路径，仅接收候选人名称与5个分项分数作为入参。

Usage:
  python calculate_match_score.py score --name "张三" --scores "20,18,15,12,16"
"""

import argparse
import json
import sys

# 修复Windows控制台编码问题，确保UTF-8输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ==============================================================================
# 常量定义
# ==============================================================================

# 5个维度的名称（按岗位要求文档中的出现顺序）
SECTION_NAMES = [
    "核心底层要求",
    "岗位职责",
    "岗位必备条件",
    "岗位加分项",
    "实践经验描述标准",
]

# 每个维度满分
SECTION_MAX_SCORE = 20

# 总分满分
TOTAL_MAX_SCORE = 100

# 初筛通过分数线
PASS_THRESHOLD = 80

# 弱项判定阈值（低于此分则纳入面试建议重点考察）
WEAK_AREA_THRESHOLD = 14


# ==============================================================================
# 核心功能函数
# ==============================================================================

def validate_scores(scores: list) -> bool:
    """
    校验分项分数列表的合法性。

    Args:
        scores: 5个分项分数的列表

    Returns:
        bool: 是否合法
    """
    if len(scores) != len(SECTION_NAMES):
        return False
    for score in scores:
        if not isinstance(score, int) or score < 0 or score > SECTION_MAX_SCORE:
            return False
    return True


def calculate_total_score(section_scores: list) -> int:
    """
    计算5个分项分数的总和。

    Args:
        section_scores: 5个分项分数的列表

    Returns:
        int: 总分
    """
    return sum(section_scores)


def is_passed(total_score: int) -> bool:
    """
    判断是否通过初筛（总分 >= 80）。

    Args:
        total_score: 总分

    Returns:
        bool: 是否通过
    """
    return total_score >= PASS_THRESHOLD


def generate_interview_suggestion(section_scores: list) -> str:
    """
    根据分项得分情况，自动生成面试侧重点建议。
    对低于14分（满分20分的70%）的维度，给出重点考察建议。

    Args:
        section_scores: 5个分项分数的列表

    Returns:
        str: 面试侧重点建议文本
    """
    weak_areas = []
    for i, name in enumerate(SECTION_NAMES):
        if section_scores[i] < WEAK_AREA_THRESHOLD:
            weak_areas.append(name)

    if not weak_areas:
        return "各维度匹配度均较高，建议面试中做常规技术深度验证即可。"

    suggestion = "侧重考察：" + "、".join(weak_areas) + "方面的实际能力与经验。"
    return suggestion


def format_result(candidate_name: str, section_scores: list) -> dict:
    """
    格式化最终评估结果。

    Args:
        candidate_name: 候选人名称
        section_scores: 5个分项分数的列表

    Returns:
        dict: 格式化的结果
    """
    total = calculate_total_score(section_scores)
    passed = is_passed(total)
    suggestion = generate_interview_suggestion(section_scores)

    result = {
        "候选人名称": candidate_name,
        "分项匹配度": {},
        "匹配度总分": total,
        "是否通过初筛": "通过" if passed else "不通过",
        "面试侧重点建议": suggestion,
    }

    for i, name in enumerate(SECTION_NAMES):
        result["分项匹配度"][name] = section_scores[i]

    return result


# ==============================================================================
# 输入解析辅助函数
# ==============================================================================

def parse_scores_str(scores_str: str) -> list:
    """
    将逗号分隔的分数字符串解析为整数列表。

    Args:
        scores_str: 如 "20,18,15,12,16"

    Returns:
        list: [20, 18, 15, 12, 16]
    """
    parts = scores_str.split(",")
    scores = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            scores.append(int(part))
        except ValueError:
            print(f"错误：无法解析分数 '{part}'，请确保为整数", file=sys.stderr)
            sys.exit(1)
    return scores


# ==============================================================================
# 命令行入口
# ==============================================================================

def cmd_score(args):
    """score 子命令：根据分项分数计算最终结果"""
    scores = parse_scores_str(args.scores)

    if not validate_scores(scores):
        print(
            f"错误：分项分数不合法。需要{len(SECTION_NAMES)}个0-{SECTION_MAX_SCORE}之间的整数",
            file=sys.stderr,
        )
        sys.exit(1)

    result = format_result(args.name, scores)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="简历匹配度评估与计算工具（纯计算：汇总总分、判断初筛、生成面试建议）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
说明：
  岗位要求5个维度的识别与逐维度评估打分由LLM基于文本参数完成，
  本脚本仅负责接收5个分项分数并完成确定性计算。

示例：
  python calculate_match_score.py score --name "张三" --scores "20,18,15,12,16"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # score 子命令
    score_parser = subparsers.add_parser("score", help="根据5个分项分数计算总分、判断初筛并生成面试建议")
    score_parser.add_argument("--name", required=True, help="候选人名称")
    score_parser.add_argument("--scores", required=True, help='5个分项分数，逗号分隔，如 "20,18,15,12,16"（顺序：核心底层要求,岗位职责,岗位必备条件,岗位加分项,实践经验描述标准）')

    args = parser.parse_args()

    if args.command == "score":
        cmd_score(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
