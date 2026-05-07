---
name: analyze-requirement-testpoints
description: 当用户要求基于单个 Markdown 需求文档生成测试点分析报告时使用。该 skill 是主入口，负责串联记忆上下文、需求结构化、交互澄清、测试方法路由、测试点生成、覆盖审查和最终报告输出；入参来自 $ARGUMENTS。
---

# 需求测试点分析主入口

本 skill 是完整链路入口。目标是从 `$ARGUMENTS` 指定的一份 Markdown 需求文档生成测试点分析报告。

## 必需输入

- `$ARGUMENTS`：一个 `.md` 需求文档路径。

## 职责边界

- 本 skill 只负责编排完整分析链路和写出本次运行产物。
- 业务术语、设计约束和项目偏好来自 `memory-context-builder` 生成的上下文包，不在本 skill 内重复维护。
- 通用测试理论、标准类型、标准方法、风险规则和专家审查规则来自 `knowledge/`。
- 报告结构来自 `templates/`，质量判定来自 `quality-gates/` 和 `coverage-review`。
- 专项分析 skill 只产出方法证据和测试点候选；最终测试点表由 `testpoint-generation` 统一合并。

## 项目根目录与输出路径

在生成任何运行产物前，必须先解析 `PROJECT_ROOT`：

1. 如果 `$ARGUMENTS` 是绝对路径，从需求文档所在目录向上查找项目根标识。
2. 如果 `$ARGUMENTS` 是相对路径，先按用户当前会话工作目录解析为绝对路径，再向上查找项目根标识。
3. 项目根标识优先级为 `.claude-plugin/plugin.json`、`memory/project-memory.md`、`.git/`。
4. 禁止把 skill 文件所在目录、插件缓存目录或 Claude Code 的内部 skill 工作目录当作 `PROJECT_ROOT`。
5. 如果无法定位 `PROJECT_ROOT`，必须先向用户确认项目根目录，不得继续生成报告。

所有运行产物必须写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/`。报告中可以展示相对路径 `outputs/runs/<run-id>/...`，但实际写文件时必须使用基于 `PROJECT_ROOT` 的绝对路径。

`run-id` 只在一次新的完整分析开始时生成一次。同一轮分析内的后续修正、澄清回答处理、质量门禁重跑和报告刷新，必须复用已经创建的运行目录。如果用户明确要求“继续上次结果修改”或提供了已有运行目录，优先复用该目录；只有用户要求重新分析或无法确认已有运行目录属于当前需求时，才创建新的 `run-id`。

## 执行流程

1. 校验输入必须是单个 Markdown 文件。
2. 解析 `PROJECT_ROOT`，生成本次运行 ID：`<YYYYMMDD-HHMMSS>-<需求文件名安全短名>-<短哈希>`，并创建 `${PROJECT_ROOT}/outputs/runs/<run-id>/`。
3. 使用 `memory-context-builder` 生成本次运行的 `${PROJECT_ROOT}/outputs/runs/<run-id>/context-pack.md`，并登记可能的 memory 澄清候选。
4. 在 `CP-MEMORY` 检查点使用 `clarification-gate`；memory 冲突影响需求理解时优先触发 `AskUserQuestion`。
5. 使用 `requirement-testability` 生成结构化需求模型，并登记业务规则、状态、权限、边界和接口契约澄清候选。
6. 在 `CP-REQUIREMENT` 检查点必须使用 `clarification-gate`；这是主要澄清点，必须形成候选队列、触发决策和未触发原因。若存在 `P0/P1` 的 `MustAsk` 或 `ShouldAsk`，必须在主会话触发 `AskUserQuestion`。
7. 使用 `testing-method-router` 判断每个需求片段适用的测试方法，并登记影响方法必要性的澄清候选。
8. 在 `CP-ROUTING` 检查点使用 `clarification-gate`；性能、安全、兼容等高优先范围问题应作为 `ShouldAsk` 提问，除非已有明确依据或已被用户回答。
9. 按方法路由调用必要的专项 skill：
   - `risk-based-test-analysis`
   - `boundary-equivalence-analysis`
   - `state-transition-analysis`
   - `decision-table-analysis`
   - `scenario-flow-analysis`
   - `permission-role-analysis`
   - `interface-contract-analysis`
   - `data-consistency-analysis`
   - `combinatorial-compatibility-analysis`
10. 汇总专项 skill 产出的 `ME-*` 方法分析证据，并登记专项方法缺口澄清候选。
11. 在 `CP-METHOD` 检查点使用 `clarification-gate`；优先确认会导致决策表、状态图、权限矩阵或接口契约失真的缺口。
12. 使用 `testpoint-generation` 基于方法证据生成测试点明细；原则上不在本阶段打断用户，缺口写为待确认风险点。
13. 使用 `coverage-review` 执行覆盖审查、质量门禁和专家评分，并登记阻断报告发布的澄清候选。
14. 在 `CP-REVIEW` 检查点使用 `clarification-gate`；默认不触发，仅当用户确认后才能安全发布报告时提问，并记录未触发原因。
15. 根据澄清会话、结构化需求模型、方法证据和覆盖审查结果，刷新最终“待确认问题”：移除已回答或已覆盖的问题，只保留未解决问题和暂不确认风险。
16. 如果质量门禁因输出质量失败，修正后重新审查；如果因需求信息缺失失败，保留刷新后的失败项并生成“待确认问题”。
17. 将最终报告写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/<需求文件名安全短名>.test-points.md`。
18. 将测试点明细表单独写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/<需求文件名安全短名>.testpoint-details.md`，便于后续评审、导入表格或继续生成测试用例。

## 阶段产物契约

| 阶段 | 必须产出 | 交给下一阶段 |
|---|---|---|
| `memory-context-builder` | `context-pack.md`、memory 澄清候选 | 需求可测性、澄清闸门 |
| `requirement-testability` | 结构化需求模型、可测性结论、需求澄清候选 | 方法路由、澄清闸门 |
| `testing-method-router` | 方法路由表、方法范围澄清候选 | 专项方法 skill、测试点生成 |
| 专项方法 skill | `ME-*` 方法证据、测试点候选、方法缺口候选 | 测试点生成、澄清闸门 |
| `testpoint-generation` | 标准测试点表、独立明细表内容、待确认风险点 | 覆盖审查 |
| `coverage-review` | 门禁结果、专家评分、阻断项和修正建议 | 最终报告刷新 |

## 输出要求

- 使用 `templates/final-report-template.md`。
- 必须在报告中记录 `PROJECT_ROOT`、`run-id`、运行目录、完整报告路径、测试点明细路径和澄清会话路径。
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
- 不直接覆盖历史运行产物；所有本次运行产物必须写入同一个 `${PROJECT_ROOT}/outputs/runs/<run-id>/` 目录。
- 不允许在 `skills/`、`.claude-plugin/`、插件缓存目录或 skill 工作目录下创建 `outputs/runs/`。
- `AskUserQuestion` 只在主会话中触发，不交给 subagent 内部触发。
- 多个环节只登记澄清候选，不直接向用户提问。
- `AskUserQuestion` 按优先级触发：`P0/MustAsk` 必问，`P1/ShouldAsk` 应问，`P2/P3` 默认进入待确认或忽略。
- 复杂需求的整次分析目标是累计 5 到 10 个确认项；简单需求可以少问或不问，但必须在澄清会话产物中说明原因。
- 用户对澄清问题的回答默认只作用于本次分析。
- 未经用户明确确认，不写入 memory 源文件。
- 不把中间候选表直接当作最终测试点输出；最终测试点必须经过 `testpoint-generation` 合并和 `coverage-review` 审查。
