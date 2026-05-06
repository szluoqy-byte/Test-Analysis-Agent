---
name: coverage-review
description: 在测试点生成后使用，用于执行覆盖审查、需求追踪检查、方法应用检查、风险级别检查、输出结构检查和非用例化检查。
---

# 覆盖审查 Skill

本 skill 在最终报告输出前使用，是自我评审和迭代修正入口。

## 输入

- 已生成的测试点表。
- 测试方法路由表。
- 方法分析证据摘要。
- 结构化需求模型。
- 待确认问题。
- `quality-gates/*.md`。
- `knowledge/expert-review-rubric.md`。

## 审查步骤

1. 执行 `testpoint-not-testcase-check.md`。
2. 执行 `coverage-check.md`。
3. 执行 `traceability-check.md`。
4. 执行 `method-application-check.md`。
5. 执行 `risk-priority-check.md`。
6. 执行 `output-schema-check.md`。
7. 执行 `semantic-quality-check.md`。
8. 如果最终报告文件已生成，运行 `bin/lint-testpoint-report.py <报告路径>` 做确定性结构校验。
9. 如果独立测试点明细文件已生成，运行 `bin/lint-testpoint-report.py <明细文件路径>` 做确定性结构校验。
10. 如果最终报告文件已生成，运行 `bin/semantic-testpoint-check.py <报告路径>` 做语义启发式校验。
11. 使用 `knowledge/expert-review-rubric.md` 进行专家评分。
12. 列出通过、警告和失败项。
13. 对阻断报告发布且无法通过修正测试点解决的问题，登记 `CP-REVIEW` 澄清候选。
14. 给出针对性修正建议。

## 输出

使用 `templates/coverage-review-template.md`。

## 约束

- 不静默修复或隐藏失败项。
- 不通过不可追踪的测试点。
- 保留需求歧义。
- 不通过缺少方法分析证据且没有解释的必选方法。
- 如果专家评分低于通过线且原因是输出质量不足，必须修正后再终稿。
- 确定性 lint 失败视为阻断性输出质量问题。
- 本 skill 不直接触发 `AskUserQuestion`；覆盖建议默认不打断用户。
