---
name: memory-context-builder
description: 每次需求分析开始前使用，用于从精简 memory 中选择相关项目上下文和测试经验，生成紧凑的本次上下文包，避免长期 memory 全量注入。
---

# 记忆上下文构建 Skill

本 skill 在每次分析开始时使用，目标是为当前需求挑选最相关的项目语境和项目测试经验。

## 输入

- 需求文档路径、需求标题和主入口解析出的 `PROJECT_ROOT`。
- `memory/project-memory.md`，包括全局项目事实、全局约束和输出偏好。
- 自动扫描得到的、与当前需求匹配的 `memory/domains/*.md` 业务域分片。
- `memory/testing-experience-memory.md`。
- `templates/context-pack-template.md`。

## 选择规则

先读取 `memory/project-memory.md`，再自动扫描 `memory/domains/*.md` 业务域分片并跳过 `README.md`。分片不需要在 `project-memory.md` 中登记。根据文件名、标题、适用范围、关键词、领域术语、角色、接口、状态、数据对象和以下内容选择相关 memory：

- 需求模块、产品区域、用户角色或业务对象。
- 需求中出现的领域术语。
- 需求中出现的接口、数据对象、状态、配置、规则或设计约束。
- 与相同流程、状态、权限、接口或数据对象相关的历史缺陷或反馈教训。
- 团队明确表达过的输出偏好。
- 关于测试点粒度或措辞的反馈教训。

## 输出

创建或刷新 `${PROJECT_ROOT}/outputs/runs/<run-id>/context-pack.md`，包含：

- 与本次需求相关的项目背景。
- 领域术语片段。
- 相关业务域分片和命中原因。
- 历史缺陷和风险模式。
- 已确认的项目测试经验。
- 输出偏好。
- 约束和非范围。
- memory 澄清候选问题，仅限业务域命中冲突或 memory 与当前需求明显冲突的情况。

## 约束

- 不把所有业务域分片全量注入 context pack；可以扫描文件元信息和标题结构，但只摘取与本次需求相关的片段。
- 新增 `memory/domains/*.md` 分片无需登记索引；但分片内容必须自带清晰的标题、适用范围、关键词或术语，便于自动匹配。
- 不把 `knowledge/` 中已有的通用测试理论复制进 context pack。
- context pack 保持简洁、相关、有依据。
- 未经用户明确确认，不更新 memory 源文件。
- 本 skill 不直接触发 `AskUserQuestion`；只向 `clarification-gate` 提供候选。
- `context-pack.md` 是当前 run 的运行产物，不写入 `memory/`，也不作为长期 memory 源文件。
- 不允许在 skill 文件目录、插件缓存目录或 `.claude-plugin/` 目录下创建 `outputs/runs/`。
