# 输出产物契约

## 目标

`outputs/` 只保存运行产物。每次分析创建一个独立 run 目录，目录内按产物类别固定命名，避免不同模型、语言环境或需求文件名处理方式导致下游无法稳定定位文件。

## 目录结构

```text
outputs/
└── runs/
    └── <run-id>/
        ├── deliverables/
        │   └── testcase-design-input.md
        ├── process/
        │   ├── task-list.md
        │   ├── context-pack.md
        │   └── clarification-session.md
        ├── reports/
        │   └── test-analysis-report.md
        └── legacy/                  # 按需
            └── testpoint-details.md
```

## 产物分类

| 类别 | 路径 | 是否默认生成 | 说明 |
|---|---|---|---|
| 主交付件 | `deliverables/testcase-design-input.md` | 是 | 唯一跨项目交接物，供后续独立测试设计项目消费 |
| 任务清单 | `process/task-list.md` | 是 | 当前 run 的阶段顺序、状态和证据路径，是流程控制事实源 |
| 过程上下文 | `process/context-pack.md` | 是 | 当前 run 筛选出的 memory、project/personal 补充和项目上下文快照 |
| 待确认治理记录 | `process/clarification-session.md` | 有待确认候选时生成 | 记录候选问题、去重降级结果和最终待确认问题；最终展示以主交付件 `## 6. 待确认信息` 为准 |
| 过程报告 | `reports/test-analysis-report.md` | 可选 | Analysis 内部审查、追溯和质量门禁报告 |
| 兼容明细 | `legacy/testpoint-details.md` | 默认不生成 | 仅为旧流程、表格导入或人工审查兼容保留 |

## 命名规则

- run 目录名使用 `<YYYYMMDD-HHMMSS>-<需求文件名安全短名>-<短哈希>`。
- run 目录内文件名固定，不再使用需求文件名作为产物文件名前缀。
- 下游只读取 `outputs/runs/<run-id>/deliverables/testcase-design-input.md`。
- 不再默认生成 `<需求文件名安全短名>.test-points.md` 或 `<需求文件名安全短名>.testpoint-details.md`。
- 如需兼容旧流程，独立明细只写入 `legacy/testpoint-details.md`，不得替代主交付件。

## 精简原则

- 主交付件必须自包含，不能要求后续项目读取 `process/` 或 `reports/`。
- `process/task-list.md` 必须在创建 run 目录后立即生成，最终输出前所有必选阶段应为 `done`，可选阶段可为 `skipped` 并说明原因。
- `process/context-pack.md` 必须记录 project/personal 的绑定结果、已扫描来源、命中来源、未采用来源、冲突处理和后续补读建议。即使没有命中正文，也要说明未命中或未采用原因。
- 如果 context pack 命中了 `*/projects/<project-key>/` 或 `*/user/`，后续设计需要知道的项目风险、覆盖策略、术语映射、个人关注点或判定依据必须上收到主交付件，不能要求后续项目回读 project/personal 本地补充。
- `process/context-pack.md` 是本次运行的初始上下文快照和来源地图，不要求在后续按源补读时反复刷新；补读来源和结论记录在方法证据、风险备注或过程报告中。
- 过程报告中可以包含方法路由、方法证据、覆盖审查和专家评分，因此不再另行生成多份过程类 Markdown。
- `process/` 只保留运行恢复和追溯必需文件。
- `legacy/` 只在用户明确要求或旧工具链需要时生成。

## 示例回归

- 示例 fixtures 固定放在 `examples/outputs/runs/<stem>-run/`，目录内部仍使用本契约的 `deliverables/`、`process/`、`reports/`、`legacy/` 分类和固定文件名。
- `bin/smoke-test-analysis.py` 只读取固定 run fixtures，不再依赖 `<需求文件名安全短名>.test-points.md` 或 `<需求文件名安全短名>.testpoint-details.md`。
- `bin/check-artifact-consistency.py <run-dir>` 用于检查固定运行目录、主交付件、过程报告和兼容明细之间的 `TP-*` / `ITP-*` 一致性。
