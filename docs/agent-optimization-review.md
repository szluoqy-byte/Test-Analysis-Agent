# Agent 优化评审记录

## 目标

持续优化 Test Analysis Agent，使其更接近测试专家的工作方式：能够选择合适的测试理论方法，基于需求生成风险驱动的测试点，并对自身输出做质量评审。

## 第 0 轮问题

| 领域 | 发现 | 风险 |
|---|---|---|
| 入口 | 缺少面向用户的端到端主入口 skill | 用户可能直接调用窄能力，绕过 memory、方法路由和审查 |
| 测试理论 | 只有边界、状态、权限、接口，缺少决策表、场景流、数据一致性和组合兼容 | 复杂业务规则容易退化成泛化测试点 |
| 方法路由 | 没有显式机制为需求片段选择测试方法 | Agent 可能声称使用专家能力，但没有真正应用方法 |
| 输出结构 | 测试点没有体现由哪种测试方法产生 | 评审者无法判断测试理论是否被应用 |
| 质量门禁 | 只检查结构和追踪，缺少方法应用和风险级别检查 | 弱输出也可能通过 |
| 专家评审 | 没有评分标准 | 没有判断“足够好”的迭代终点 |

## 第 1 轮优化

- 新增 `skills/analyze-requirement-testpoints/SKILL.md` 作为主流程入口。
- 新增 `skills/testing-method-router/SKILL.md` 和 `knowledge/test-method-routing-matrix.md`。
- 新增专项测试理论 skill：
  - `decision-table-analysis`
  - `scenario-flow-analysis`
  - `data-consistency-analysis`
  - `combinatorial-compatibility-analysis`
- 新增专家知识：
  - `coverage-taxonomy.md`
  - `test-oracle-heuristics.md`
  - `expert-review-rubric.md`
- 新增质量门禁：
  - `method-application-check.md`
  - `risk-priority-check.md`
- 更新模板，使每条测试点包含 `方法` 列。
- 新增 `bin/lint-testpoint-report.py`，用于确定性检查报告结构和非用例化约束。

## 第 2 轮样例自测

| 样例 | 结果 | 说明 |
|---|---|---|
| `examples/outputs/sample-requirement.test-points.md` | 预期警告 | 需求未明确客服审核状态规则，报告保留待确认问题 |
| `examples/outputs/complex-promotion-requirement.test-points.md` | 目标通过 | 覆盖边界/等价类、决策表、状态迁移、权限矩阵、接口契约、数据一致性、组合兼容和风险驱动 |

## 第 3 轮 lint 反馈

第一次确定性 lint 过严，把审查说明中提到的 `预期结果` 误判为违规。现在脚本只检查表格列名和测试点表达，允许质量门禁说明引用禁用词。

当前确定性 lint 结果：

| 报告 | 校验结果 |
|---|---|
| `examples/outputs/sample-requirement.test-points.md` | 通过 |
| `examples/outputs/complex-promotion-requirement.test-points.md` | 通过 |

## 第 4 轮中文化优化

- 将所有 `SKILL.md` 的触发描述、输入、流程、输出和约束改为中文测试专家表达。
- 将 Agent 角色定义、knowledge、templates、quality gates、memory 文档改为中文逻辑。
- 将报告中的状态值由 `PASS/WARN/FAIL` 改为 `通过/警告/失败`。
- 保留文件名和 skill 名的英文标识，便于 Claude Code / OpenClaw 适配和工具引用。

## 第 5 轮设计文档结构优化

- 重构 `docs/test-analysis-agent-design.md`，从组件清单式文档调整为系统架构设计文档。
- 新增系统上下文、分层架构、主运行流程、Agent 协作、测试方法路由、记忆注入、数据产物流和质量闭环等架构视图。
- 使用 Mermaid 图表达关键流程，便于后续实现者理解端到端链路。
- 将组件职责、输出契约、验收标准和当前假设集中到文档后半部分，降低阅读成本。

## 第 6 轮独立测试点明细产物

- 增加独立测试点明细落盘要求：`outputs/testpoint-details/<需求文件名>.testpoint-details.md`。
- 该轮完整报告仍保留 `## 6. 测试点明细`，独立明细文件仅保留测试点表和必要元信息；第 12 轮引入方法证据摘要后，测试点明细调整为 `## 7. 测试点明细`。
- 更新主入口 skill、编排 Agent、测试点生成 skill、覆盖审查 skill、模板、质量门禁和设计文档。
- 扩展确定性 lint，使其同时支持完整报告和独立测试点明细文件。

## 第 7 轮测试点定义收敛

- 采纳测试点定义：测试点是对验证特性的细化，用直观、明确、无歧义的语言描述被测对象在特定场景下的某一功能、规则或行为。
- 不新增 `被测对象`、`场景`、`验证特性` 三个表格列，避免明细表过重。
- 将该定义作为 `测试点` 字段的描述规范，写入测试点标准、生成 skill、质量门禁、模板和设计文档。
- lint 保持原有表格字段，只对明显空泛或疑似步骤化的测试点描述给出提示。

## 第 8 轮级别体系调整

- 将测试点级别调整为 `Level 0` 到 `Level 4`。
- 将测试点表头调整为 `级别`。
- 写入 Level 0 到 Level 4 的完整定义，覆盖核心、关键、重要、一般和生僻五类。
- 更新风险驱动分析、测试点标准、模板、质量门禁、设计文档、lint 脚本和示例产物。

## 第 9 轮 Memory 精简设计

- 将 memory 从 `global/project/context-packs` 多层结构收敛为 `project-memory.md`、`testing-experience-memory.md` 和 `latest-context-pack.md`。
- 明确 Memory 的定义：经人工确认、会影响后续分析的项目上下文和测试经验。
- 明确 Memory 不保存通用测试理论、未确认业务规则和单次运行完整中间产物。
- 更新 `memory-context-builder`，只从两个长期 memory 文件中筛选相关内容，运行时只注入 `latest-context-pack.md`。
- 更新记忆更新建议模板和示例报告中的写入位置。

## 第 10 轮 Knowledge / Skills / Memory 边界清理

- 明确 `knowledge` 保存稳定测试知识和标准，`skills` 保存分析动作流程，`memory` 保存经确认的项目上下文和项目经验。
- 将 `context-pack-template.md` 从 `knowledge/` 移到 `templates/`，避免知识层混入模板职责。
- 清理 `memory/testing-experience-memory.md` 中的通用缺陷模式和通用测试启发，统一归属到 `knowledge/`。
- 压缩 `risk-based-test-analysis`、`testing-method-router`、`testpoint-generation` 中重复的级别定义、路由规则和类型枚举，改为引用 `knowledge/`。
- 新增 `docs/knowledge-skill-memory-boundaries.md` 作为后续归档和扩展的边界判定依据。

## 第 11 轮可执行评测闭环

- 新增 `bin/semantic-testpoint-check.py`，用于启发式检查必选方法覆盖、类型方法匹配、需求依据粒度、风险备注和级别分布。
- 新增 `bin/smoke-test-analysis.py`，用于对示例需求执行完整报告 lint、独立明细 lint、语义检查和明细一致性比对。
- 新增 `quality-gates/semantic-quality-check.md`，将语义启发式检查纳入质量门禁。
- 新增 `examples/evaluation-matrix.md`，记录已覆盖样例和后续应补齐的需求类型。
- 更新覆盖审查 skill 和设计文档，使质量闭环从结构 lint 扩展为结构检查、语义检查和示例 smoke 回归。

## 第 12 轮方法证据链优化

- 新增 `knowledge/method-evidence-standard.md`，定义 `ME-*` 方法分析证据字段和质量要求。
- 新增 `templates/method-analysis-template.md`，要求专项测试方法先输出证据，再生成测试点候选。
- 新增 `knowledge/risk-level-rules.md`，将 Level 0 到 Level 4 的风险判定规则从 skill 中抽离到知识层。
- 将 `knowledge/defect-patterns.md` 重构为结构化缺陷模式卡片，包含触发信号、典型风险、推荐方法、测试点表达建议和待确认问题。
- 为测试方法路由表补充 `置信度` 字段，帮助评审者判断方法选择是否可靠。
- 更新所有专项方法 skill，使其输出方法证据并关联 `TP-*` 或 `Q-*`。
- 更新测试点生成 skill，使测试点来源于方法路由和方法证据，而不是直接泛化生成。
- 更新覆盖审查和质量门禁，使缺少方法证据且无待确认解释的必选方法无法通过。
- 扩展 `bin/lint-testpoint-report.py` 和 `bin/semantic-testpoint-check.py`，机械检查方法证据表、路由置信度、质量门禁结果和专家评分。
- 更新示例报告，补齐方法分析证据摘要和新版章节顺序。
- 更新设计文档，补充 Claude Code 插件兼容性、方法证据链、Knowledge / Skills / Memory 边界和产物流视图。

## 当前验收标准

- 最终报告包含测试方法路由表。
- 测试方法路由表包含 `必要性` 和 `置信度`。
- 每个 `必选` 方法至少生成一条 `ME-*` 方法分析证据，并关联测试点或待确认问题。
- 每个 `必选` 方法至少生成一个测试点，或输出一个明确解释缺口的待确认问题。
- 每条测试点包含类型、方法、依据、级别和风险备注。
- 测试点级别必须是 `Level 0`、`Level 1`、`Level 2`、`Level 3` 或 `Level 4`。
- 没有测试点写成测试用例。
- 质量门禁不能存在阻断性失败；警告项必须在覆盖审查中说明。
- 专家评分总分至少 `10/12`，且任一维度不得为 `0`；若阻塞来自需求缺失，必须输出待确认问题。
- 示例集必须通过 `bin/smoke-test-analysis.py`。

## 剩余注意事项

- 当前仓库仍是 Markdown-first 的 Agent 包，不是独立 CLI 产品。
- memory 源文件仅在用户明确确认后更新。
- 确定性 lint 和语义启发式检查不替代人工专家评审，但可作为回归底线。
