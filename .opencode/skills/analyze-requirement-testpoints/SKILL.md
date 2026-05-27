---
name: analyze-requirement-testpoints
description: 当用户要求基于单个 Markdown 需求文档生成后续独立测试设计项目可消费的测试用例设计输入时使用。该 skill 是主入口，负责串联记忆上下文、需求结构化、待确认问题治理、测试方法路由、场景化测试点生成、覆盖审查和设计输入输出；入参来自 $ARGUMENTS。
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

1. `PROJECT_ROOT` 等于用户启动 Claude Code、OpenCode 或当前 agent 会话所在的工作目录。
2. `$ARGUMENTS` 只用于定位需求文档；不得从需求文档路径向上反推 `PROJECT_ROOT`。
3. 如果 `$ARGUMENTS` 是相对路径，只按 `PROJECT_ROOT` 解析为绝对路径。
4. 禁止把 skill 文件所在目录、插件缓存目录、`.claude-plugin/`、`.opencode/` 或宿主内部 skill 工作目录当作 `PROJECT_ROOT`。
5. 如果当前工作目录明显是上述禁止目录，必须先向用户确认正确工作目录，不得继续生成报告。

所有运行产物必须写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/` 下的固定类别目录，具体契约见 `docs/output-artifact-contract.md`。报告中可以展示相对路径 `outputs/runs/<run-id>/...`，但实际写文件时必须使用基于 `PROJECT_ROOT` 的绝对路径。

`run-id` 只在一次新的完整分析开始时生成一次。同一轮分析内的后续修正、待确认问题刷新、质量门禁重跑和报告刷新，必须复用已经创建的运行目录。如果用户明确要求“继续上次结果修改”或提供了已有运行目录，优先复用该目录；只有用户要求重新分析或无法确认已有运行目录属于当前需求时，才创建新的 `run-id`。

## 项目化上下文发现

本流程按 `core / project / user` 三层读取配置。core 层是随 Agent 包发布的根目录文件；project 层是 `*/projects/<project-key>/**/*.md`；user 层是 `*/user/**/*.md`。project 和 user 层默认不提交 Git，只作为本地 overlay。

本流程支持可选 `project-key`，用于发现项目化 memory、knowledge、templates 和 quality gates。`project-key` 不改变 `PROJECT_ROOT`，也不能从需求文件路径反推项目根目录。

`project-key` 按以下顺序确定：

1. 用户在命令参数或当前请求中显式提供 `--project <project-key>`、`project=<project-key>` 或“项目：<project-key>”。
2. 需求 Markdown frontmatter 中存在 `project` 或 `project_key`。
3. `memory/projects/` 或 `knowledge/projects/` 下存在唯一目录名，且该目录名、目录 README、项目标题或关键词与需求标题、模块或正文显式匹配。

项目化文件发现范围：

- `memory/projects/<project-key>/project-memory.md`
- `memory/projects/<project-key>/testing-experience-memory.md`
- `memory/projects/<project-key>/domains/**/*.md`
- `memory/projects/<project-key>/**/*.md`
- `knowledge/projects/<project-key>/**/*.md`
- `templates/projects/<project-key>/**/*.md`
- `quality-gates/projects/<project-key>/**/*.md`
- `memory/user/**/*.md`
- `knowledge/user/**/*.md`
- `templates/user/**/*.md`
- `quality-gates/user/**/*.md`

如果无法唯一确定 `project-key`，不得全量读取所有项目目录正文；继续使用 core 层和 user 层，并把项目归属问题登记到最终“待确认信息”。project/user 层只能补充项目风险画像、覆盖策略、术语映射、路由说明、测试 oracle、模板说明或附加门禁，不得覆盖 core 层中的核心标准、字段、类型、级别、输出契约和质量门禁。user 层也不得覆盖需求文档或 project memory。

## 渐进式披露与按源补读

本流程必须遵循渐进式披露：先由 `memory-context-builder` 读取目录、README、frontmatter、文件名和标题结构，生成最小 `context-pack.md`；后续阶段默认消费当前 run 的 context pack 和 core 标准。

当专项 skill 发现 context pack 缺少完成当前分析所需的 project/user 信息时，可以按源补读，但必须受控：

- 优先读取 context pack 已列出的来源文件、章节、关键词或“后续补读建议”。
- 如果当前需求明确指向某个 project/user 文件，也可以读取该对应文件。
- 不得自行全目录搜索 project/user，也不得把大文件整份复制进过程产物。
- 读取结果直接进入当前 skill 的方法证据、风险备注或过程报告，不要求刷新 `context-pack.md`。

超过 50KB 的 project/user Markdown 不要求提供 `index.md`。读取大文件时先看文件名、frontmatter、标题结构或目录，再按命中的标题、关键词或表格片段读取必要内容；如果仍无法定位，转为待确认候选或风险备注。

## 执行流程

1. 校验输入必须是单个 Markdown 文件。
2. 将当前 agent 会话工作目录固定为 `PROJECT_ROOT`，生成本次运行 ID：`<YYYYMMDD-HHMMSS>-<需求文件名安全短名>-<短哈希>`，并创建 `${PROJECT_ROOT}/outputs/runs/<run-id>/deliverables/`、`process/`、`reports/` 和按需 `legacy/`。
3. 解析可选 `project-key`，使用 `memory-context-builder` 扫描 core、project 和 user 三层配置，生成本次运行的 `${PROJECT_ROOT}/outputs/runs/<run-id>/process/context-pack.md`，并登记可能的 memory 或项目归属待确认候选。
4. 在 `CP-MEMORY` 检查点使用 `clarification-gate`；memory 冲突影响需求理解时登记为待确认候选，不中途提问。
5. 使用 `requirement-testability` 生成结构化需求模型，并按 `knowledge/test-analysis-methodology.md` 标记需求片段涉及的测试分析维度，登记业务规则、状态、权限、边界和接口契约待确认候选。
6. 在 `CP-REQUIREMENT` 检查点必须使用 `clarification-gate`；这是主要待确认收集点，必须形成候选队列、去重排序结果和最终保留原因。即使存在 `P0/P1` 问题，也不得中途打断用户。
7. 使用 `testing-method-router` 先判断每个需求片段涉及的分析维度，再选择适用测试方法，并登记影响方法必要性的待确认候选。
8. 在 `CP-ROUTING` 检查点使用 `clarification-gate`；性能、安全、兼容等高优先范围问题如果缺少依据，进入最终待确认候选。
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
10. 汇总专项 skill 产出的 `ME-*` 方法分析证据，并登记专项方法缺口待确认候选。
11. 如果任一阶段发现 context pack 不足，可按上述受控规则补读对应来源文件；补读仍不足时转为待确认候选或风险备注。
12. 在 `CP-METHOD` 检查点使用 `clarification-gate`；会导致决策表、状态图、权限矩阵或接口契约失真的缺口必须进入最终待确认候选。
13. 使用 `testpoint-generation` 基于方法证据生成场景化测试用例设计输入：先识别测试场景，再补齐场景测试条件、场景测试点、接口测试清单和接口测试点；原则上不在本阶段打断用户，缺口写为待确认风险点。
14. 使用 `coverage-review` 执行覆盖审查、质量门禁和专家评分，并登记阻断报告发布的待确认候选。
15. 在 `CP-REVIEW` 检查点使用 `clarification-gate`；对仍会影响交付可用性的缺口做最终收口，不提问、不暂停。
16. 根据待确认候选、结构化需求模型、方法证据和覆盖审查结果，刷新最终“待确认问题”：移除已覆盖和重复的问题，只保留后续用例设计必须知道的未解决问题。
17. 如果质量门禁因输出质量失败，修正后重新审查；如果因需求信息缺失失败，保留刷新后的失败项并生成“待确认问题”。
18. 将主输出写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/deliverables/testcase-design-input.md`，使用 `templates/testcase-design-input-template.md`，供后续独立测试设计项目直接消费。
19. 如需保留过程审查信息，将分析报告写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/reports/test-analysis-report.md`，报告中可包含方法路由、方法证据、覆盖审查、质量门禁、专家评分和 memory 更新建议。

## 阶段产物契约

| 阶段 | 必须产出 | 交给下一阶段 |
|---|---|---|
| `memory-context-builder` | `process/context-pack.md`、memory 待确认候选 | 需求可测性、待确认治理 |
| `requirement-testability` | 结构化需求模型、可测性结论、需求待确认候选 | 方法路由、待确认治理 |
| `testing-method-router` | 分析维度覆盖表、方法路由表、方法范围待确认候选 | 专项方法 skill、测试点生成 |
| 专项方法 skill | `ME-*` 方法证据、测试点候选、方法缺口候选、按源补读记录 | 测试点生成、待确认治理 |
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
- “待确认信息”必须在最终输出前刷新，只保留后续设计可执行用例时必须知道的问题；没有待确认问题时写“本次无待确认信息。”，不要保留空问题行。
- 如保留过程分析报告，使用 `templates/final-report-template.md`，并在报告中记录 `PROJECT_ROOT`、`run-id`、运行目录、设计输入路径、分析报告路径、待确认治理记录路径和上下文包路径。
- 默认不生成独立测试点明细；如旧流程明确需要，只能写入 `${PROJECT_ROOT}/outputs/runs/<run-id>/legacy/testpoint-details.md`。

## 硬性约束

- 不生成测试用例。
- 不生成操作步骤。
- 不编造需求中没有的业务规则。
- 不把“回读原始需求、过程报告或 Analysis 项目文件”作为后续设计的前提。
- 不直接覆盖历史运行产物；所有本次运行产物必须写入同一个 `${PROJECT_ROOT}/outputs/runs/<run-id>/` 目录，并使用固定文件名。
- 不允许在 `skills/`、`.claude-plugin/`、插件缓存目录或 skill 工作目录下创建 `outputs/runs/`。
- 后续阶段不得重新解析、搜索或修正 `PROJECT_ROOT`；只能使用主入口固定后的值。
- 全流程不调用用户交互能力。
- 多个环节只登记待确认候选，不直接向用户提问，不暂停主流程。
- `P0/P1` 问题默认进入最终 `## 6. 待确认信息`；`P2` 视影响范围进入待确认信息或风险备注；`P3` 默认只保留在过程记录。
- 复杂需求可以保留多个待确认项，但必须去重、合并同类项，并说明影响场景或测试点。
- 未经用户明确确认，不写入 memory 源文件。
- 不把中间候选表或扁平测试点表直接当作最终设计输入；最终设计输入必须经过 `testpoint-generation` 场景化合并和 `coverage-review` 审查。
