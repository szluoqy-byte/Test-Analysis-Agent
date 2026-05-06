---
name: analyze-requirement-testpoints
description: 当用户要求基于单个 Markdown 需求文档生成测试点分析报告时使用。该 skill 是主入口，负责串联记忆上下文、需求结构化、交互澄清、测试方法路由、测试点生成、覆盖审查和最终报告输出；入参来自 $ARGUMENTS。
---

# 需求测试点分析主入口

本 skill 是完整链路入口。目标是从 `$ARGUMENTS` 指定的一份 Markdown 需求文档生成测试点分析报告。

## 必需输入

- `$ARGUMENTS`：一个 `.md` 需求文档路径。

## 执行流程

1. 校验输入必须是单个 Markdown 文件。
2. 使用 `memory-context-builder` 生成 `memory/latest-context-pack.md`。
3. 使用 `requirement-testability` 生成结构化需求模型。
4. 使用 `clarification-gate` 判断是否存在阻塞级待确认问题。
5. 如果存在 `Blocking` 问题，优先在主会话中调用 Claude Code 的 `AskUserQuestion` 进行交互澄清，并将回答记录到 `outputs/clarifications/<需求文件名>.clarification-session.md`。
6. 用户回答后，将已确认内容作为本次运行上下文合并进结构化需求模型；选择“暂不确认”的问题作为待确认风险点继续，不写成已确认规则。
7. 使用 `testing-method-router` 判断每个需求片段适用的测试方法。
8. 按方法路由调用必要的专项 skill：
   - `risk-based-test-analysis`
   - `boundary-equivalence-analysis`
   - `state-transition-analysis`
   - `decision-table-analysis`
   - `scenario-flow-analysis`
   - `permission-role-analysis`
   - `interface-contract-analysis`
   - `data-consistency-analysis`
   - `combinatorial-compatibility-analysis`
9. 汇总专项 skill 产出的 `ME-*` 方法分析证据。
10. 使用 `testpoint-generation` 基于方法证据生成测试点明细。
11. 使用 `coverage-review` 执行覆盖审查、质量门禁和专家评分。
12. 如果质量门禁因输出质量失败，修正后重新审查；如果因需求信息缺失失败，保留失败项并生成“待确认问题”。
13. 将最终报告写入 `outputs/test-points/<需求文件名>.test-points.md`。
14. 将测试点明细表单独写入 `outputs/testpoint-details/<需求文件名>.testpoint-details.md`，便于后续评审、导入表格或继续生成测试用例。

## 输出要求

- 使用 `templates/final-report-template.md`。
- 必须包含测试方法路由表，让评审者看到使用了哪些测试理论。
- 必须包含方法分析证据摘要，让评审者看到每种测试方法的分析过程。
- 如果触发过澄清，必须在“待确认问题”或报告摘要中说明已确认答案、暂不确认风险和澄清会话产物路径。
- 每条测试点必须在 `测试点` 描述中体现被测对象、特定场景和验证特性，并包含 `方法` 字段。
- 必须包含质量门禁结果、专家评分和 memory 更新建议。
- 必须额外生成仅包含测试点明细的独立 Markdown 文件，使用 `templates/testpoint-output-template.md`。

## 硬性约束

- 不生成测试用例。
- 不生成操作步骤。
- 不编造需求中没有的业务规则。
- `AskUserQuestion` 只在主会话中触发，不交给 subagent 内部触发。
- 用户对澄清问题的回答默认只作用于本次分析。
- 未经用户明确确认，不写入 memory 源文件。
