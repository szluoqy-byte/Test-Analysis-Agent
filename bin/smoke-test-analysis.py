#!/usr/bin/env python3
"""Run deterministic smoke checks for example test analysis outputs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TESTPOINT_HEADER = "| ID | 模块 | 测试点 | 类型 | 方法 | 需求依据 | 级别 | 风险/备注 |"
REQUIRED_FILES = [
    ".claude-plugin/plugin.json",
    "docs/test-analysis-agent-design.md",
    "docs/knowledge-skill-memory-boundaries.md",
    "skills/analyze-requirement-testpoints/SKILL.md",
    "skills/memory-context-builder/SKILL.md",
    "knowledge/method-evidence-standard.md",
    "knowledge/risk-level-rules.md",
    "knowledge/testpoint-standard.md",
    "templates/final-report-template.md",
    "templates/method-analysis-template.md",
    "templates/testpoint-output-template.md",
    "templates/context-pack-template.md",
    "quality-gates/output-schema-check.md",
    "quality-gates/semantic-quality-check.md",
    "examples/evaluation-matrix.md",
    "bin/lint-testpoint-report.py",
    "bin/semantic-testpoint-check.py",
]


def collect_testpoint_table(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(TESTPOINT_HEADER)
    except ValueError as exc:
        raise ValueError(f"{path} 未找到测试点表头") from exc

    table: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table.append(line.rstrip())
    return table


def find_artifact(repo_root: Path, stem: str, suffix: str) -> Path:
    candidates = [
        repo_root / "examples" / "outputs" / f"{stem}{suffix}",
        repo_root / "outputs" / "test-points" / f"{stem}{suffix}",
        repo_root / "outputs" / "testpoint-details" / f"{stem}{suffix}",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"未找到 {stem}{suffix}")


def run_command(cmd: list[str], cwd: Path) -> bool:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode == 0


def check_required_files(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for relative in REQUIRED_FILES:
        if not (repo_root / relative).exists():
            missing.append(relative)
    return missing


def check_one_requirement(repo_root: Path, requirement: Path) -> bool:
    stem = requirement.stem
    report = find_artifact(repo_root, stem, ".test-points.md")
    details = find_artifact(repo_root, stem, ".testpoint-details.md")

    print(f"\n== {requirement} ==")
    ok = True
    ok &= run_command([sys.executable, "bin/lint-testpoint-report.py", str(report)], repo_root)
    ok &= run_command([sys.executable, "bin/lint-testpoint-report.py", str(details)], repo_root)
    ok &= run_command([sys.executable, "bin/semantic-testpoint-check.py", str(report)], repo_root)

    report_table = collect_testpoint_table(report)
    details_table = collect_testpoint_table(details)
    if report_table != details_table:
        print(f"失败: {report} 与 {details} 的测试点明细不一致")
        ok = False
    else:
        print("通过: 完整报告与独立明细文件的测试点表一致")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="运行测试分析 Agent 的示例 smoke 检查")
    parser.add_argument("requirements", nargs="*", type=Path, help="需求 Markdown 路径，默认检查 examples/requirements/*.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    missing = check_required_files(repo_root)
    if missing:
        for relative in missing:
            print(f"失败: 缺少关键文件 {relative}")
        return 1
    print("通过: 关键项目文件存在")

    requirements = args.requirements
    if not requirements:
        requirements = sorted((repo_root / "examples" / "requirements").glob("*.md"))
    if not requirements:
        print("失败: 未找到可检查的示例需求")
        return 1

    ok = True
    for requirement in requirements:
        requirement = requirement if requirement.is_absolute() else repo_root / requirement
        if requirement.suffix != ".md" or not requirement.exists():
            print(f"失败: 非法需求文件 {requirement}")
            ok = False
            continue
        ok &= check_one_requirement(repo_root, requirement)

    if not ok:
        return 1
    print("\n通过: smoke 检查全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
