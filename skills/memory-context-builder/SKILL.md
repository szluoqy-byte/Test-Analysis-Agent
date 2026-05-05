---
name: memory-context-builder
description: 每次需求分析开始前使用，用于从精简 memory 中选择相关项目上下文和测试经验，生成紧凑的本次上下文包，避免长期 memory 全量注入。
---

# 记忆上下文构建 Skill

本 skill 在每次分析开始时使用，目标是为当前需求挑选最相关的项目语境和项目测试经验。

## 输入

- 需求文档路径和需求标题。
- `memory/project-memory.md`。
- `memory/testing-experience-memory.md`。
- `templates/context-pack-template.md`。

## 选择规则

只选择与以下内容匹配的 memory：

- 需求模块、产品区域、用户角色或业务对象。
- 需求中出现的领域术语。
- 与相同流程、状态、权限、接口或数据对象相关的历史缺陷或反馈教训。
- 团队明确表达过的输出偏好。
- 关于测试点粒度或措辞的反馈教训。

## 输出

创建或刷新 `memory/latest-context-pack.md`，包含：

- 与本次需求相关的项目背景。
- 领域术语片段。
- 历史缺陷和风险模式。
- 已确认的项目测试经验。
- 输出偏好。
- 约束和非范围。

## 约束

- 不全量读取所有 memory。
- 不把 `knowledge/` 中已有的通用测试理论复制进 context pack。
- context pack 保持简洁、相关、有依据。
- 未经用户明确确认，不更新 memory 源文件。
