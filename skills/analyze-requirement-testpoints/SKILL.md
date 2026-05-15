---
name: analyze-requirement-testpoints
description: 当用户要求基于单个 Markdown 需求文档生成后续独立测试设计项目可消费的测试用例设计输入时使用。该 skill 是主入口，负责串联记忆上下文、需求结构化、交互澄清、测试方法路由、场景化测试点生成、覆盖审查和设计输入输出；入参来自 $ARGUMENTS。
---

# 需求测试点分析主入口

本 skill 是完整链路入口。目标是从 `$ARGUMENTS` 指定的一份 Markdown 需求文档生成 `测试用例设计输入`，作为后续独立测试设计项目的直接输入。

Analysis 项目与后续 Design 项目相互独立；主交付物必须自包含到足以支撑后续用例设计，不假设后续项目能读取原始需求、Analysis 的 knowledge、memory、context-pack、方法证据或过程报告。

过程分析报告可以作为 Analysis 内部审查和追溯产物保留，但主交付物必须是场景化的设计输入文件，而不是扁平测试点明细。

## 必需输入

- `$ARGUMENTS`：一个 `.md` 需求文档路径。

## 职责边界

- 本 skill 只负责编排完整分析链路和写出本次运行产物。
- 业务术语、设计约束和项目偏好来自 `memory-context-builder` 生成的上下文包，不在本 skill 内重复维护。
- 通用测试理论、分析维度、标准类型、标准方法、风险规则和专家审查规则来自 `knowledge/`；测试分析与测试设计边界以 `knowledge/test-analysis-methodology.md` 为准。
- 设计输入结构来自 `templates/testcase-design-input-template.md`，过程分析报告结构来自 `templates/final-report-template.md`，质量判定来自 `quality-gates/` 和 `coverage-review`。
- 场景、场景测试条件、测试点和测试用例的边界以 `knowledge/test-scenario-point-case-boundary.md` 为准；设计输入中的测试类型以 `knowledge/basic-test-types.md` 为准。
- 专项分析 skill 只产出方法证据和测试点候选；最终由 `testpoint-generation` 统一合并为测试场景、场景测试条件、场景测试点、接口测试清单和接口测试点。
- 主设计输入是唯一跨项目交接物；凡是后续设计可执行用例必须知道的业务规则、角色、入口、数据因子、接口契约、约束和未确认问题，都必须进入主设计输入，不得只留在过程报告或原始需求里。

## 项目根目录与输出路径

在生成任何运行产物前，必须先固定 `PROJECT_ROOT`：

1. `PROJECT_ROOT` 等于用户启动 Claude Code 或当前 Claude Code 会话所在的工作目录。
2. `$ARGUMENTS` 只用于定位需求文档；不得从需求文档路径向上反推 `PROJECT_ROOT`。
3. 如果 `$ARGUMENTS` 是相对路径，只按 `PROJECT_ROOT` 解析为绝对路径。
4. 禁止把 skill 文件所在目录、插件缓存目录、`.claude-plugin/` 或 Claude Code 的内部 skill 工作目录当作 `PROJECT_ROOT`。
5. 如果当前工作目录明显是上述禁止目录，必须先向用户确认正确工作目录，不得继续生成报告。

所有运行产物必须写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/` 下的固定类别目录，具体契约见 `docs/output-artifact-contract.md`。报告中可以展示相对路径 `outputs/runs/<run-id>/...`，但实际写文件时必须使用基于 `PROJECT_ROOT` 的绝对路径。

`run-id` 只在一次新的完整分析开始时生成一次。同一轮分析内的后续修正、澄清回答处理、质量门禁重跑和报告刷新，必须复用已经创建的运行目录。如果用户明确要求“继续上次结果修改”或提供了已有运行目录，优先复用该目录；只有用户要求重新分析或无法确认已有运行目录属于当前需求时，才创建新的 `run-id`。

## 执行流程

1. 校验输入必须是单个 Markdown 文件。
2. 将当前 Claude Code 会话工作目录固定为 `PROJECT_ROOT`，生成本次运行 ID：`<YYYYMMDD-HHMMSS>-<需求文件名安全短名>-<短哈希>`，并创建 `${PROJECT_ROOT}/outputs/runs/<run-id>/deliverables/`、`process/`、`reports/` 和按需 `legacy/`。
3. 使用 `memory-context-builder` 生成本次运行的 `${PROJECT_ROOT}/outputs/runs/<run-id>/process/context-pack.md`，并登记可能的 memory 澄清候选。
4. 在 `CP-MEMORY` 检查点使用 `clarification-gate`；memory 冲突影响需求理解时优先触发 `AskUserQuestion`。
5. 使用 `requirement-testability` 生成结构化需求模型，并按 `knowledge/test-analysis-methodology.md` 标记需求片段涉及的测试分析维度，登记业务规则、状态、权限、边界和接口契约澄清候选。
6. 在 `CP-REQUIREMENT` 检查点必须使用 `clarification-gate`；这是主要澄清点，必须形成候选队列、触发决策和未触发原因。若存在 `P0/P1` 的 `MustAsk` 或 `ShouldAsk`，必须在主会话触发 `AskUserQuestion`。
7. 使用 `testing-method-router` 先判断每个需求片段涉及的分析维度，再选择适用测试方法，并登记影响方法必要性的澄清候选。
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
12. 使用 `testpoint-generation` 基于方法证据生成场景化测试用例设计输入：先识别测试场景，再补齐场景测试条件、场景测试点、接口测试清单和接口测试点；原则上不在本阶段打断用户，缺口写为待确认风险点。
13. 使用 `coverage-review` 执行覆盖审查、质量门禁和专家评分，并登记阻断报告发布的澄清候选。
14. 在 `CP-REVIEW` 检查点使用 `clarification-gate`；默认不触发，仅当用户确认后才能安全发布报告时提问，并记录未触发原因。
15. 根据澄清会话、结构化需求模型、方法证据和覆盖审查结果，刷新最终“待确认问题”：移除已回答或已覆盖的问题，只保留未解决问题和暂不确认风险。
16. 如果质量门禁因输出质量失败，修正后重新审查；如果因需求信息缺失失败，保留刷新后的失败项并生成“待确认问题”。
17. 将主输出写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/deliverables/testcase-design-input.md`，使用 `templates/testcase-design-input-template.md`，供后续独立测试设计项目直接消费。
18. 如需保留过程审查信息，将分析报告写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/reports/test-analysis-report.md`，报告中可包含方法路由、方法证据、覆盖审查、质量门禁、专家评分和 memory 更新建议。

## 阶段产物契约

| 阶段 | 必须产出 | 交给下一阶段 |
|---|---|---|
| `memory-context-builder` | `process/context-pack.md`、memory 澄清候选 | 需求可测性、澄清闸门 |
| `requirement-testability` | 结构化需求模型、可测性结论、需求澄清候选 | 方法路由、澄清闸门 |
| `testing-method-router` | 分析维度覆盖表、方法路由表、方法范围澄清候选 | 专项方法 skill、测试点生成 |
| 专项方法 skill | `ME-*` 方法证据、测试点候选、方法缺口候选 | 测试点生成、澄清闸门 |
| `testpoint-generation` | 测试用例设计输入、场景化测试点、接口测试点、待确认风险点 | 覆盖审查 |
| `coverage-review` | 门禁结果、专家评分、阻断项和修正建议 | 设计输入和过程报告刷新 |

## 输出要求

- 主输出使用 `templates/testcase-design-input-template.md`。
- 主输出必须包含：需求信息、测试场景清单、测试场景详情、接口测试清单、接口测试详情、待确认信息和输入完整性自检。
- 主输出必须自包含：不能用“见原始需求”“按需求实现”“同上”等占位替代业务规则、数据因子、接口契约或范围边界。
- 主输出必须先按业务/系统行为拆分 `SC-*` 测试场景，再在每个场景下提供可供后续设计用例的共用条件。
- 主输出必须体现测试分析维度的结果：场景承接流程维度，场景条件承接角色、数据、状态、规则和接口上下文，测试点承接规则、风险、契约和质量属性。
- 每个场景的 `必填条件` 必须包含 `场景入口/触发方式`、`执行用户/角色`、`前置条件`、`测试数据因子`、`业务设计约束`。
- 场景测试点必须使用 `测试点 ID | 测试点 | 大类 | 子类 | 级别 | 风险/备注`，接口测试点必须使用 `测试点 ID | 测试点 | 大类 | 子类 | 风险/备注`。
- `大类/子类`、`场景测试类型` 和 `接口测试类型` 必须从 `knowledge/basic-test-types.md` 中选择；优先使用需求明确触发的类型，不为凑覆盖虚构专项类型。
- 主输出不得包含 `方法`、`需求依据`、`方法路由`、`方法证据`、`质量门禁`、`专家评分` 或 `建议沉淀的记忆更新` 等过程字段。
- “待确认信息”必须在所有交互澄清完成后刷新，只保留后续设计可执行用例时必须知道的问题；没有待确认问题时写“本次无待确认信息。”，不要保留空问题行。
- 如保留过程分析报告，使用 `templates/final-report-template.md`，并在报告中记录 `PROJECT_ROOT`、`run-id`、运行目录、设计输入路径、分析报告路径、澄清会话路径和上下文包路径。
- 默认不生成独立测试点明细；如旧流程明确需要，只能写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/legacy/testpoint-details.md`。

## 硬性约束

- 不生成测试用例。
- 不生成操作步骤。
- 不编造需求中没有的业务规则。
- 不把“回读原始需求、过程报告或 Analysis 项目文件”作为后续设计的前提。
- 不直接覆盖历史运行产物；所有本次运行产物必须写入同一个 `${PROJECT_ROOT}/outputs/runs/<run-id>/` 目录，并使用固定文件名。
- 不允许在 `skills/`、`.claude-plugin/`、插件缓存目录或 skill 工作目录下创建 `outputs/runs/`。
- 后续阶段不得重新解析、搜索或修正 `PROJECT_ROOT`；只能使用主入口固定后的值。
- `AskUserQuestion` 只在主会话中触发，不交给 subagent 内部触发。
- 多个环节只登记澄清候选，不直接向用户提问。
- `AskUserQuestion` 按优先级触发：`P0/MustAsk` 必问，`P1/ShouldAsk` 应问，`P2/P3` 默认进入待确认或忽略。
- 复杂需求的整次分析目标是累计 5 到 10 个确认项；简单需求可以少问或不问，但必须在澄清会话产物中说明原因。
- 用户对澄清问题的回答默认只作用于本次分析。
- 未经用户明确确认，不写入 memory 源文件。
- 不把中间候选表或扁平测试点表直接当作最终设计输入；最终设计输入必须经过 `testpoint-generation` 场景化合并和 `coverage-review` 审查。
