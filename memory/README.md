# Memory 模块说明

Memory 是 Agent 在多次需求分析之间保留的、经人工确认的项目上下文和测试经验。它的目标是让测试点分析更贴近当前项目，而不是替代需求文档、测试理论或专家知识库。

## 文件

| 文件 | 定义 | 使用方式 |
|---|---|---|
| `project-memory.md` | 项目 Memory 入口索引、全局项目事实、全局约束和输出偏好 | 作为项目语境入口 |
| `domains/*.md` | 按业务域拆分的项目事实、术语、角色权限、接口/数据约定和设计约束 | 由 `project-memory.md` 索引，按需注入 |
| `testing-experience-memory.md` | 项目历史缺陷、项目风险模式、评审反馈、团队测试习惯 | 作为项目测试经验来源 |

运行时上下文包不保存在 `memory/` 下；每次分析写入 `outputs/runs/<run-id>/context-pack.md`。

## 运行产物

| 文件 | 定义 | 使用方式 |
|---|---|---|
| `outputs/runs/<run-id>/context-pack.md` | 本次运行筛选出的相关 memory 摘要 | 当前 run 内注入和追溯 |

## 使用流程

1. `memory-context-builder` 先读取 `project-memory.md` 的全局内容和业务域索引。
2. 根据需求标题、模块、角色、业务对象、状态、接口和关键词，选择相关 `domains/*.md` 分片。
3. 同时读取 `testing-experience-memory.md` 中与本次需求相关的项目经验。
4. 只选择与本次需求直接相关的条目，生成 `outputs/runs/<run-id>/context-pack.md`。
5. 后续需求分析、方法路由、测试点生成和覆盖审查只读取当前 run 的 `context-pack.md`。
6. 最终报告给出“建议沉淀的 Memory 更新”。
7. 用户确认后，才把建议追加到对应长期 memory 文件或业务域分片。

## 写入边界

- 写入 memory 的内容必须有证据，来源可以是需求文档、用户反馈、评审结论或真实缺陷复盘。
- 通用测试理论、通用缺陷模式和通用级别定义不写入 memory，应放在 `knowledge/`。
- 未确认的业务规则不写入 memory，应放在待确认问题。
- 单次运行的完整中间产物不写入 memory，应保存在 `outputs/`。
- 业务域分片必须登记到 `project-memory.md` 的“业务域索引”，否则不会被稳定选中。
- `context-pack.md` 是运行产物，不是全局 memory 文件。
