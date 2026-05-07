---
name: memory-context-builder
description: 每次需求分析开始前使用，用于从精简 memory 中选择相关项目上下文和测试经验，生成紧凑的本次上下文包，避免长期 memory 全量注入。
---

# 记忆上下文构建 Skill

本 skill 在每次分析开始时使用，目标是为当前需求挑选最相关的项目语境和项目测试经验。

## 输入

- 需求文档路径和需求标题。
- `memory/project-memory.md`，包括全局内容和业务域索引。
- 与当前需求匹配的 `memory/domains/*.md` 业务域分片。
- `memory/testing-experience-memory.md`。
- `templates/context-pack-template.md`。

## 选择规则

先读取 `memory/project-memory.md`，根据“业务域索引”选择可能相关的 `memory/domains/*.md` 分片，再只选择与以下内容匹配的 memory：

- 需求模块、产品区域、用户角色或业务对象。
- 需求中出现的领域术语。
- 需求中出现的接口、数据对象、状态、配置、规则或设计约束。
- 与相同流程、状态、权限、接口或数据对象相关的历史缺陷或反馈教训。
- 团队明确表达过的输出偏好。
- 关于测试点粒度或措辞的反馈教训。

## 输出

创建或刷新 `memory/latest-context-pack.md`，包含：

- 与本次需求相关的项目背景。
- 领域术语片段。
- 相关业务域分片和命中原因。
- 历史缺陷和风险模式。
- 已确认的项目测试经验。
- 输出偏好。
- 约束和非范围。
- memory 澄清候选问题，仅限业务域命中冲突或 memory 与当前需求明显冲突的情况。

同时将本次运行实际使用的上下文包复制到 `outputs/runs/<run-id>/context-pack.md`，作为不可覆盖的运行产物。

## 约束

- 不全量读取所有业务域分片。
- 未登记到 `memory/project-memory.md` 业务域索引的分片，不作为稳定 memory 来源。
- 不把 `knowledge/` 中已有的通用测试理论复制进 context pack。
- context pack 保持简洁、相关、有依据。
- 未经用户明确确认，不更新 memory 源文件。
- 本 skill 不直接触发 `AskUserQuestion`；只向 `clarification-gate` 提供候选。
- `memory/latest-context-pack.md` 可被后续运行刷新，不能作为历史运行追溯的唯一来源。
