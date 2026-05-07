# Knowledge / Skills / Memory 边界说明

## 一句话边界

```text
Knowledge = 稳定测试知识和标准
Skills = 使用知识完成分析动作的流程
Memory = 经确认的项目上下文和项目历史经验
```

## 归属规则

| 内容类型 | 放置位置 | 原因 |
|---|---|---|
| 测试点定义、字段、类型、方法、级别 | `knowledge/testpoint-standard.md` | 稳定标准，所有 skill 共用 |
| 风险优先、异常优先、状态优先等专家原则 | `knowledge/expert-rules.md` | 通用测试专家规则 |
| 空值、重复提交、越权、幂等等通用缺陷模式 | `knowledge/defect-patterns.md` | 跨项目缺陷启发 |
| 需求文档、需求依据、方法证据、记忆上下文包等框架术语 | `knowledge/domain-glossary.md` | 稳定分析术语，所有 skill 共用 |
| 需求信号到测试方法的映射 | `knowledge/test-method-routing-matrix.md` | 稳定路由知识 |
| Level 0 到 Level 4 的判定规则 | `knowledge/risk-level-rules.md` | 级别标准应全局一致 |
| 方法分析证据字段和质量要求 | `knowledge/method-evidence-standard.md` | 证明测试理论被实际应用的统一标准 |
| 某个测试方法的执行步骤 | `skills/*/SKILL.md` | 过程性动作，不是事实库 |
| 输入、输出、约束、质量门禁调用顺序 | `skills/*/SKILL.md` | Agent 运行流程 |
| 项目全局事实、全局约束、输出偏好和项目专属术语覆盖 | `memory/project-memory.md` | 项目专属且经确认 |
| 不同业务域的业务术语、角色权限、接口约定、数据约定和设计约束 | `memory/domains/*.md` | 用户自定义扩展区，自动扫描并按需匹配 |
| 项目真实历史缺陷、复盘教训、团队测试习惯 | `memory/testing-experience-memory.md` | 项目专属经验 |
| 本次运行筛选出的少量上下文 | `${PROJECT_ROOT}/outputs/runs/<run-id>/context-pack.md` | 运行产物，不是长期事实源 |
| 报告、中间产物和运行产物的 Markdown 结构 | `templates/*.md` | 模板层只定义形状和占位，不维护另一套标准 |
| 输出是否通过的检查项、失败条件和字段校验 | `quality-gates/*.md` | 质量门禁层负责判定，不产生新知识 |
| 可机械执行的结构、语义和回归检查 | `bin/*.py` | 脚本层只做确定性校验 |

## 禁止重复

- `skills/` 不重复维护测试点类型、方法枚举、级别定义和通用缺陷模式，只引用 `knowledge/`。
- `skills/` 不把方法证据写成自由发挥的叙述，统一引用 `knowledge/method-evidence-standard.md` 和 `templates/method-analysis-template.md`。
- `memory/` 不保存通用测试理论、通用缺陷模式、通用级别定义和方法步骤。
- `memory/` 不重复维护框架术语定义；框架术语归属 `knowledge/domain-glossary.md`，memory 只记录项目专属术语或覆盖。
- `knowledge/` 不保存项目事实、用户临时偏好、单次运行结果和未确认假设。
- `memory/domains/*.md` 不需要登记索引；新增分片应自带清晰标题、适用范围、关键词或术语，便于自动匹配。
- `context-pack.md` 只摘录与本次需求相关的 memory，不复制整份长期 memory，也不放在 `memory/` 下。
- `templates/` 可以列出字段、占位和最小示例，但字段含义、类型、方法、级别等标准必须引用 `knowledge/`。
- `quality-gates/` 可以重复列出允许值用于校验，但必须以 `knowledge/` 的标准为来源，不维护独立定义。
- `bin/` 中的枚举和章节列表必须服务于机械校验；如果标准变化，应同步来自 `knowledge/`、`templates/` 或 `quality-gates/` 的权威来源。

## 冲突处理

当信息冲突时，按以下顺序处理：

1. 当前用户明确指令。
2. 当前需求文档中的明确规则。
3. 经确认的项目 memory。
4. `knowledge/` 中的通用测试知识。
5. skill 的流程性默认动作。

如果 memory 或 knowledge 与需求文档冲突，不直接覆盖需求；输出待确认问题。
