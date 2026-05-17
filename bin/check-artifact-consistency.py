#!/usr/bin/env python3
"""Check fixed run artifact layout and cross-artifact test point consistency."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DESIGN_SCENARIO_HEADER = "| 测试点 ID | 测试点 | 大类 | 子类 | 级别 | 风险/备注 |"
DESIGN_INTERFACE_HEADER = "| 测试点 ID | 测试点 | 大类 | 子类 | 风险/备注 |"
REPORT_TESTPOINT_HEADER = "| ID | 模块 | 测试点 | 类型 | 方法 | 需求依据 | 级别 | 风险/备注 |"
EVIDENCE_HEADER = "| 证据ID | 方法 | 需求片段 | 分析结论 | 关联测试点/待确认 |"
QUESTION_HEADERS = {
    "| ID | 问题 | 影响 | 关联需求依据 |",
    "| 问题 ID | 问题 | 影响场景/测试点 | 当前处理 |",
}


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


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


def collect_first_table(lines: list[str], header: str) -> list[tuple[int, list[str]]]:
    tables = collect_all_tables(lines, header)
    return tables[0] if tables else []


def is_point_id(value: str) -> bool:
    return bool(re.fullmatch(r"(?:TP|ITP)-\d{3}", value))


def collect_design_points(path: Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    points: dict[str, dict[str, str]] = {}

    for rows in collect_all_tables(lines, DESIGN_SCENARIO_HEADER):
        for line_number, cells in rows:
            if len(cells) != 6 or not is_point_id(cells[0]):
                continue
            point_id, text, category, subtype, level, risk = cells
            points[point_id] = {
                "line": str(line_number),
                "text": text,
                "category": category,
                "subtype": subtype,
                "level": level,
                "risk": risk,
            }

    for rows in collect_all_tables(lines, DESIGN_INTERFACE_HEADER):
        for line_number, cells in rows:
            if len(cells) != 5 or not is_point_id(cells[0]):
                continue
            point_id, text, category, subtype, risk = cells
            points[point_id] = {
                "line": str(line_number),
                "text": text,
                "category": category,
                "subtype": subtype,
                "level": "",
                "risk": risk,
            }
    return points


def collect_report_points(path: Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    points: dict[str, dict[str, str]] = {}
    for line_number, cells in collect_first_table(lines, REPORT_TESTPOINT_HEADER):
        if len(cells) != 8 or not is_point_id(cells[0]):
            continue
        point_id, module, text, test_type, method, basis, level, risk = cells
        points[point_id] = {
            "line": str(line_number),
            "module": module,
            "text": text,
            "type": test_type,
            "method": method,
            "basis": basis,
            "level": level,
            "risk": risk,
        }
    return points


def collect_evidence_links(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    links: set[str] = set()
    for _, cells in collect_first_table(lines, EVIDENCE_HEADER):
        if len(cells) != 5:
            continue
        for point_id in re.findall(r"(?:TP|ITP|Q)-\d{3}", cells[4]):
            links.add(point_id)
    return links


def collect_question_ids(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    questions: set[str] = set()
    for header in QUESTION_HEADERS:
        for _, cells in collect_first_table(lines, header):
            if cells and re.fullmatch(r"Q-\d{3}", cells[0]):
                questions.add(cells[0])
    return questions


def table_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(REPORT_TESTPOINT_HEADER)
    except ValueError:
        return []
    table: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table.append(line.rstrip())
    return table


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: check-artifact-consistency.py <outputs/runs/<run-id>>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1])
    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.is_dir():
        print(f"失败: 运行目录不存在: {run_dir}")
        return 1

    required_paths = [
        run_dir / "deliverables" / "testcase-design-input.md",
        run_dir / "process" / "context-pack.md",
    ]
    for required in required_paths:
        if not required.exists():
            errors.append(f"缺少固定运行产物: {required.relative_to(run_dir)}")

    design_path = run_dir / "deliverables" / "testcase-design-input.md"
    report_path = run_dir / "reports" / "test-analysis-report.md"
    detail_path = run_dir / "legacy" / "testpoint-details.md"

    if design_path.exists() and report_path.exists():
        design_points = collect_design_points(design_path)
        report_points = collect_report_points(report_path)

        missing_in_report = sorted(set(design_points) - set(report_points))
        extra_in_report = sorted(set(report_points) - set(design_points))
        if missing_in_report:
            errors.append("过程报告缺少主交付件测试点: " + "、".join(missing_in_report))
        if extra_in_report:
            errors.append("过程报告存在主交付件外测试点: " + "、".join(extra_in_report))

        for point_id in sorted(set(design_points) & set(report_points)):
            design_point = design_points[point_id]
            report_point = report_points[point_id]
            for field, label in [("text", "测试点"), ("risk", "风险/备注")]:
                if design_point[field] != report_point[field]:
                    errors.append(
                        f"{point_id} {label} 不一致: 主交付件 `{design_point[field]}` / 过程报告 `{report_point[field]}`"
                    )
            if design_point["level"] and design_point["level"] != report_point["level"]:
                errors.append(
                    f"{point_id} 级别不一致: 主交付件 `{design_point['level']}` / 过程报告 `{report_point['level']}`"
                )

        evidence_links = collect_evidence_links(report_path)
        question_ids = collect_question_ids(report_path)
        valid_links = set(design_points) | question_ids
        unknown_links = sorted(link for link in evidence_links if link not in valid_links)
        missing_evidence = sorted(set(design_points) - evidence_links)
        if unknown_links:
            errors.append("方法证据引用未知 ID: " + "、".join(unknown_links))
        if missing_evidence:
            warnings.append("以下测试点未被方法证据直接关联: " + "、".join(missing_evidence))

    if detail_path.exists() and report_path.exists():
        report_table = table_lines(report_path)
        detail_table = table_lines(detail_path)
        if report_table != detail_table:
            errors.append("过程报告与兼容明细的测试点明细表不一致")

    for warning in warnings:
        print(f"警告: {warning}")
    for error in errors:
        print(f"失败: {error}")

    if errors:
        return 1
    print(f"通过: {run_dir} 运行产物路径和跨产物一致性校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
