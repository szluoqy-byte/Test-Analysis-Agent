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
2. 使用 `memory-context-builder` 生成 `memory/latest-context-pack.md`，并登记可能的 memory 澄清候选。
3. 在 `CP-MEMORY` 检查点使用 `clarification-gate`；仅当 memory 冲突会影响需求理解时才触发 `AskUserQuestion`。
4. 使用 `requirement-testability` 生成结构化需求模型，并登记业务规则、状态、权限、边界和接口契约澄清候选。
5. 在 `CP-REQUIREMENT` 检查点使用 `clarification-gate`；这是主要澄清点，但仍遵循非必要不触发。
6. 使用 `testing-method-router` 判断每个需求片段适用的测试方法，并登记影响方法必要性的澄清候选。
7. 在 `CP-ROUTING` 检查点使用 `clarification-gate`；性能、安全、兼容等范围问题默认作为 `Important` 保留，除非不确认会导致高风险遗漏。
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
9. 汇总专项 skill 产出的 `ME-*` 方法分析证据，并登记专项方法缺口澄清候选。
10. 在 `CP-METHOD` 检查点使用 `clarification-gate`；仅对会导致决策表、状态图、权限矩阵或接口契约失真的高风险缺口提问。
11. 使用 `testpoint-generation` 基于方法证据生成测试点明细；原则上不在本阶段打断用户，缺口写为待确认风险点。
12. 使用 `coverage-review` 执行覆盖审查、质量门禁和专家评分，并登记阻断报告发布的澄清候选。
13. 在 `CP-REVIEW` 检查点使用 `clarification-gate`；默认不触发，仅当用户确认后才能安全发布报告时提问。
14. 根据澄清会话、结构化需求模型、方法证据和覆盖审查结果，刷新最终“待确认问题”：移除已回答或已覆盖的问题，只保留未解决问题和暂不确认风险。
15. 如果质量门禁因输出质量失败，修正后重新审查；如果因需求信息缺失失败，保留刷新后的失败项并生成“待确认问题”。
16. 将最终报告写入 `outputs/test-points/<需求文件名>.test-points.md`。
17. 将测试点明细表单独写入 `outputs/testpoint-details/<需求文件名>.testpoint-details.md`，便于后续评审、导入表格或继续生成测试用例。

## 输出要求

- 使用 `templates/final-report-template.md`。
- 必须包含测试方法路由表，让评审者看到使用了哪些测试理论。
- 必须包含方法分析证据摘要，让评审者看到每种测试方法的分析过程。
- 必须包含交互澄清摘要；若未触发，写明“未触发交互澄清”和主要未触发原因。
- 如果触发过澄清，必须说明检查点、已确认答案、暂不确认风险和澄清会话产物路径。
- “待确认问题”必须在所有交互澄清完成后刷新，不得保留已回答或已被上下文覆盖的问题。
- 每条测试点必须在 `测试点` 描述中体现被测对象、特定场景和验证特性，并包含 `方法` 字段。
- 必须包含质量门禁结果、专家评分和 memory 更新建议。
- 必须额外生成仅包含测试点明细的独立 Markdown 文件，使用 `templates/testpoint-output-template.md`。

## 硬性约束

- 不生成测试用例。
- 不生成操作步骤。
- 不编造需求中没有的业务规则。
- `AskUserQuestion` 只在主会话中触发，不交给 subagent 内部触发。
- 多个环节只登记澄清候选，不直接向用户提问。
- 非 `Blocking` 或 `mustAsk` 不为 `是` 的问题，不触发 `AskUserQuestion`。
- 用户对澄清问题的回答默认只作用于本次分析。
- 未经用户明确确认，不写入 memory 源文件。
