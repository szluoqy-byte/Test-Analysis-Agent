#!/usr/bin/env python3
"""Lint a Markdown testcase design input file for downstream testcase design."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "# ",
    "## 1. 需求信息",
    "## 2. 测试场景清单",
    "## 3. 测试场景详情",
    "## 4. 接口测试清单",
    "## 5. 接口测试详情",
    "## 6. 待确认信息",
    "## 7. 输入完整性自检",
]

REQUIREMENT_INFO_HEADER = "| 字段 | 内容 |"
SCENARIO_HEADER = "| 场景 ID | 场景名称 | 场景测试类型 | 场景目标 |"
CONDITION_HEADER = "| 条件项 | 内容 |"
SCENARIO_TESTPOINT_HEADER = "| 测试点 ID | 测试点 | 大类 | 子类 | 级别 | 风险/备注 |"
INTERFACE_LIST_HEADER = "| 序号 | 接口名称 | 接口请求方式 | 接口测试类型 |"
INTERFACE_TESTPOINT_HEADER = "| 测试点 ID | 测试点 | 大类 | 子类 | 风险/备注 |"
QUESTION_HEADER = "| 问题 ID | 问题 | 影响场景/测试点 | 当前处理 |"
SELF_CHECK_HEADER = "| 检查项 | 是否满足 | 说明 |"

REQUIRED_INFO_FIELDS = {"需求 ID", "需求名称", "需求描述", "本次不覆盖内容"}
REQUIRED_CONDITIONS = {
    "场景入口/触发方式",
    "执行用户/角色",
    "前置条件",
    "测试数据因子",
    "业务设计约束",
}
DEFAULT_ALLOWED_CATEGORY_PAIRS = {
    ("功能性", "功能正确性测试"),
    ("功能性", "功能交互测试"),
    ("功能性", "协议一致性测试"),
    ("性能", "性能规格测试"),
    ("性能", "资源效率测试"),
    ("兼容性", "配套兼容性测试"),
    ("兼容性", "互通测试"),
    ("易用性", "用户体验测试"),
    ("易用性", "全球化测试"),
    ("可靠性", "容错容灾测试"),
    ("可靠性", "过载测试"),
    ("可靠性", "耐力测试"),
    ("可靠性", "可用性测试"),
}
ALLOWED_LEVELS = {"Level 0", "Level 1", "Level 2", "Level 3", "Level 4"}
BANNED_COLUMNS = {"方法", "需求依据", "模块", "操作步骤", "测试数据", "预期结果"}
HARD_STEP_WORDS = ("点击", "然后", "步骤", "断言", "执行用例", "输入以下", "预期结果")
SOFT_STEP_WORDS = ("输入", "选择", "调用接口")
METHOD_ARTIFACT_WORDS = ("边界值", "等价类", "判定表", "组合矩阵", "状态迁移矩阵", "测试设计方法")
EMPTY_MARKERS = {"", "<需要确认的问题>", "<影响场景/测试点>", "<测试场景名称>"}
GENERIC_REFERENCE_WORDS = (
    "见原始需求",
    "详见原始需求",
    "参考原始需求",
    "见需求",
    "详见需求",
    "参考需求",
    "按需求",
    "按需实现",
    "同上",
    "TBD",
    "待补充",
    "待定",
)


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def collect_table(lines: list[str], header: str) -> list[tuple[int, list[str]]]:
    rows: list[tuple[int, list[str]]] = []
    try:
        start = lines.index(header)
    except ValueError:
        return rows

    for index in range(start + 2, len(lines)):
        line = lines[index]
        if not line.startswith("|"):
            break
        rows.append((index + 1, split_row(line)))
    return rows


def collect_all_tables(lines: list[str], header: str) -> list[list[tuple[int, list[str]]]]:
    tables: list[list[tuple[int, list[str]]]] = []
    for start, line in enumerate(lines):
        if line != header:
            continue
        rows: list[tuple[int, list[str]]] = []
        for index in range(start + 2, len(lines)):
            row = lines[index]
            if not row.startswith("|"):
                break
            rows.append((index + 1, split_row(row)))
        tables.append(rows)
    return tables


def normalize_heading_name(value: str) -> str:
    return re.sub(r"\s*（.*?）\s*$", "", value).strip()


def load_allowed_category_pairs() -> set[tuple[str, str]]:
    repo_root = Path(__file__).resolve().parents[1]
    type_path = repo_root / "knowledge" / "basic-test-types.md"
    if not type_path.exists():
        return DEFAULT_ALLOWED_CATEGORY_PAIRS

    pairs: set[tuple[str, str]] = set()
    categories_without_subtypes: set[str] = set()
    current_category = ""
    for line in type_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current_category = normalize_heading_name(line[3:])
            if current_category and current_category != "目录":
                categories_without_subtypes.add(current_category)
            continue
        if line.startswith("### ") and current_category:
            subtype = normalize_heading_name(line[4:])
            if subtype:
                pairs.add((current_category, subtype))
                categories_without_subtypes.discard(current_category)

    for category in categories_without_subtypes:
        pairs.add((category, category))
    return pairs or DEFAULT_ALLOWED_CATEGORY_PAIRS


def allowed_type_names(allowed_pairs: set[tuple[str, str]]) -> set[str]:
    names: set[str] = set()
    for category, subtype in allowed_pairs:
        names.add(category)
        names.add(subtype)
        names.add(f"{category}测试")
    return names


def split_type_names(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[、,，/]+", value) if part.strip()]


def has_generic_reference(value: str) -> bool:
    compact = value.strip()
    if not compact:
        return False
    return any(word in compact for word in GENERIC_REFERENCE_WORDS)


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: lint-testcase-design-input.py <测试用例设计输入.md>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    allowed_category_pairs = load_allowed_category_pairs()
    allowed_type_values = allowed_type_names(allowed_category_pairs)

    for section in REQUIRED_SECTIONS:
        if section == "# ":
            if not lines or not lines[0].startswith("# ") or "测试用例设计输入" not in lines[0]:
                errors.append("缺少 Markdown 一级标题，或标题未声明“测试用例设计输入”")
        elif section not in text:
            errors.append(f"缺少必需章节: {section}")

    for header in [
        REQUIREMENT_INFO_HEADER,
        SCENARIO_HEADER,
        CONDITION_HEADER,
        SCENARIO_TESTPOINT_HEADER,
        INTERFACE_LIST_HEADER,
        SELF_CHECK_HEADER,
    ]:
        if header not in text:
            errors.append(f"缺少必需表头: {header}")

    for line_number, line in enumerate(lines, start=1):
        if not line.startswith("|"):
            continue
        cells = set(split_row(line))
        for column in BANNED_COLUMNS:
            if column in cells:
                errors.append(f"第 {line_number} 行：出现不属于设计输入的列名: {column}")

    info_rows = collect_table(lines, REQUIREMENT_INFO_HEADER)
    info_fields = {cells[0]: cells[1] for _, cells in info_rows if len(cells) == 2}
    for field in REQUIRED_INFO_FIELDS:
        value = info_fields.get(field, "")
        if not value:
            errors.append(f"需求信息缺少内容: {field}")
        elif has_generic_reference(value):
            errors.append(f"需求信息 `{field}` 使用了非自包含占位表达: {value}")

    scenario_rows = [
        (line_number, cells)
        for line_number, cells in collect_table(lines, SCENARIO_HEADER)
        if cells and re.fullmatch(r"SC-\d{3}", cells[0])
    ]
    if not scenario_rows:
        errors.append("测试场景清单未找到 SC-* 场景行")

    expected_scene_id = 1
    scenario_ids: list[str] = []
    for line_number, cells in scenario_rows:
        if len(cells) != 4:
            errors.append(f"第 {line_number} 行：场景清单期望 4 列，实际 {len(cells)} 列")
            continue
        scene_id, name, scene_type, goal = cells
        expected = f"SC-{expected_scene_id:03d}"
        if scene_id != expected:
            errors.append(f"第 {line_number} 行：期望场景 ID {expected}，实际 {scene_id}")
        expected_scene_id += 1
        scenario_ids.append(scene_id)
        for label, value in [("场景名称", name), ("场景测试类型", scene_type), ("场景目标", goal)]:
            if not value:
                errors.append(f"第 {line_number} 行：{label} 不能为空")
        for scene_type_name in split_type_names(scene_type):
            if scene_type_name not in allowed_type_values:
                errors.append(f"第 {line_number} 行：场景测试类型不在基础测试类型知识库中: {scene_type_name}")
        if name in {"功能测试", "接口测试", "性能测试", "测试场景"}:
            warnings.append(f"第 {line_number} 行：场景名称可能过于泛化: {name}")

    headings = {line.strip() for line in lines if line.startswith("### ")}
    for scene_id in scenario_ids:
        if not any(heading.startswith(f"### {scene_id} ") for heading in headings):
            errors.append(f"缺少场景详情标题: ### {scene_id} <场景名称>")

    condition_tables = collect_all_tables(lines, CONDITION_HEADER)
    if len(condition_tables) < len(scenario_ids):
        errors.append(
            f"场景测试条件表数量不足，场景 {len(scenario_ids)} 个，条件表 {len(condition_tables)} 个"
        )
    for table_index, rows in enumerate(condition_tables[: len(scenario_ids)], start=1):
        condition_values = {cells[0]: cells[1] for _, cells in rows if len(cells) == 2}
        missing = sorted(REQUIRED_CONDITIONS - set(condition_values))
        if missing:
            errors.append(f"第 {table_index} 个场景缺少必填条件: {'、'.join(missing)}")
        for condition in REQUIRED_CONDITIONS:
            value = condition_values.get(condition, "")
            if not value:
                errors.append(f"第 {table_index} 个场景的条件 `{condition}` 内容为空")
            elif has_generic_reference(value):
                errors.append(f"第 {table_index} 个场景的条件 `{condition}` 使用了非自包含占位表达: {value}")
        data_factors = condition_values.get("测试数据因子", "")
        if data_factors and not any(mark in data_factors for mark in ["：", ":", "、", "/", "；", ";"]):
            warnings.append(f"第 {table_index} 个场景的测试数据因子可能不够结构化")
        constraints = condition_values.get("业务设计约束", "")
        if constraints in {"符合需求", "按需求实现", ""}:
            warnings.append(f"第 {table_index} 个场景的业务设计约束过于泛化")

    scenario_tp_tables = collect_all_tables(lines, SCENARIO_TESTPOINT_HEADER)
    scenario_tp_rows = [
        (line_number, cells)
        for rows in scenario_tp_tables
        for line_number, cells in rows
        if cells and cells[0].startswith("TP-")
    ]
    if len(scenario_tp_tables) < len(scenario_ids):
        errors.append(
            f"场景测试点表数量不足，场景 {len(scenario_ids)} 个，测试点表 {len(scenario_tp_tables)} 个"
        )
    if not scenario_tp_rows:
        errors.append("未找到 TP-* 场景测试点")

    expected_tp_id = 1
    for line_number, cells in scenario_tp_rows:
        if len(cells) != 6:
            errors.append(f"第 {line_number} 行：场景测试点期望 6 列，实际 {len(cells)} 列")
            continue
        test_id, testpoint, category, subtype, level, risk_note = cells
        expected = f"TP-{expected_tp_id:03d}"
        if test_id != expected:
            errors.append(f"第 {line_number} 行：期望测试点 ID {expected}，实际 {test_id}")
        expected_tp_id += 1
        if (category, subtype) not in allowed_category_pairs:
            errors.append(f"第 {line_number} 行：非法大类/子类组合 {category}/{subtype}")
        if level not in ALLOWED_LEVELS:
            errors.append(f"第 {line_number} 行：非法级别 {level}")
        for label, value in [("测试点", testpoint), ("风险/备注", risk_note)]:
            if not value:
                errors.append(f"第 {line_number} 行：{label} 不能为空")
            elif has_generic_reference(value):
                errors.append(f"第 {line_number} 行：{label} 使用了非自包含占位表达: {value}")
        if any(word in testpoint for word in HARD_STEP_WORDS):
            errors.append(f"第 {line_number} 行：测试点存在用例化表达: {testpoint}")
        if any(word in testpoint for word in SOFT_STEP_WORDS):
            warnings.append(f"第 {line_number} 行：请检查疑似步骤化表达: {testpoint}")
        if any(word in testpoint for word in METHOD_ARTIFACT_WORDS):
            errors.append(f"第 {line_number} 行：测试点泄漏测试设计方法或方法产物: {testpoint}")
        if len(testpoint) < 10:
            warnings.append(f"第 {line_number} 行：测试点可能过短，需体现被测对象和验证特性")

    interface_rows = collect_table(lines, INTERFACE_LIST_HEADER)
    has_interface = any(
        len(cells) == 4 and cells[0].isdigit() and cells[1] not in {"", "不适用"}
        for _, cells in interface_rows
    )
    if interface_rows:
        for line_number, cells in interface_rows:
            if len(cells) != 4:
                errors.append(f"第 {line_number} 行：接口清单期望 4 列，实际 {len(cells)} 列")
                continue
            seq, name, request, test_type = cells
            if seq.isdigit() and name != "不适用":
                for label, value in [("接口名称", name), ("接口请求方式", request), ("接口测试类型", test_type)]:
                    if not value:
                        errors.append(f"第 {line_number} 行：{label} 不能为空")
                    elif has_generic_reference(value):
                        errors.append(f"第 {line_number} 行：{label} 使用了非自包含占位表达: {value}")
                for interface_type_name in split_type_names(test_type):
                    if interface_type_name not in allowed_type_values:
                        errors.append(
                            f"第 {line_number} 行：接口测试类型不在基础测试类型知识库中: {interface_type_name}"
                        )
    elif "## 4. 接口测试清单" in text:
        errors.append("接口测试清单为空，若无接口测试对象需填写“不适用”")

    interface_tp_rows = [
        (line_number, cells)
        for rows in collect_all_tables(lines, INTERFACE_TESTPOINT_HEADER)
        for line_number, cells in rows
        if cells and cells[0].startswith("ITP-")
    ]
    if has_interface and not interface_tp_rows:
        errors.append("接口清单存在独立接口，但接口测试详情未找到 ITP-* 测试点")

    expected_itp_id = 1
    for line_number, cells in interface_tp_rows:
        if len(cells) != 5:
            errors.append(f"第 {line_number} 行：接口测试点期望 5 列，实际 {len(cells)} 列")
            continue
        test_id, testpoint, category, subtype, risk_note = cells
        expected = f"ITP-{expected_itp_id:03d}"
        if test_id != expected:
            errors.append(f"第 {line_number} 行：期望接口测试点 ID {expected}，实际 {test_id}")
        expected_itp_id += 1
        if (category, subtype) not in allowed_category_pairs:
            errors.append(f"第 {line_number} 行：非法接口大类/子类组合 {category}/{subtype}")
        for label, value in [("接口测试点", testpoint), ("风险/备注", risk_note)]:
            if not value:
                errors.append(f"第 {line_number} 行：{label} 不能为空")
            elif has_generic_reference(value):
                errors.append(f"第 {line_number} 行：{label} 使用了非自包含占位表达: {value}")
        if any(word in testpoint for word in HARD_STEP_WORDS):
            errors.append(f"第 {line_number} 行：接口测试点存在用例化表达: {testpoint}")
        if any(word in testpoint for word in METHOD_ARTIFACT_WORDS):
            errors.append(f"第 {line_number} 行：接口测试点泄漏测试设计方法或方法产物: {testpoint}")

    if QUESTION_HEADER in text:
        for line_number, cells in collect_table(lines, QUESTION_HEADER):
            if len(cells) != 4:
                errors.append(f"第 {line_number} 行：待确认信息期望 4 列，实际 {len(cells)} 列")
                continue
            question_id, question, impact, handling = cells
            if question_id.startswith("Q-"):
                if question in EMPTY_MARKERS or impact in EMPTY_MARKERS or not handling:
                    errors.append(f"第 {line_number} 行：待确认信息存在空问题行")
    elif "本次无待确认信息。" not in text:
        warnings.append("未找到待确认信息表，也未声明“本次无待确认信息。”")

    self_check_rows = collect_table(lines, SELF_CHECK_HEADER)
    if not self_check_rows:
        errors.append("输入完整性自检未找到检查项")
    for line_number, cells in self_check_rows:
        if len(cells) != 3:
            errors.append(f"第 {line_number} 行：自检表期望 3 列，实际 {len(cells)} 列")
            continue
        item, satisfied, note = cells
        if not item or not satisfied or not note:
            errors.append(f"第 {line_number} 行：自检表存在空字段")
        if has_generic_reference(note):
            errors.append(f"第 {line_number} 行：自检说明使用了非自包含占位表达: {note}")
        if satisfied not in {"是", "否", "不适用", "部分满足"}:
            warnings.append(f"第 {line_number} 行：自检结果建议使用 是/否/不适用/部分满足")

    for warning in warnings:
        print(f"警告: {warning}")
    for error in errors:
        print(f"失败: {error}")

    if errors:
        return 1
    print(f"通过: {input_path} 已通过测试用例设计输入确定性校验")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
