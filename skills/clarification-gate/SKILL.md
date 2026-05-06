---
name: clarification-gate
description: 在需求结构化后、测试方法路由前使用。用于识别会影响测试点正确性的阻塞级疑问，并优先通过 Claude Code 的 AskUserQuestion 进行交互澄清。
---

# 交互澄清闸门 Skill

本 skill 用于决定“是否必须先问用户，再继续生成测试点”。它只处理会影响测试分析正确性的关键疑问，不把所有不完整信息都变成阻塞。

## 输入

- 结构化需求模型。
- `memory/latest-context-pack.md`。
- 需求模型中的待确认问题。
- `templates/clarification-template.md`。

## 触发时机

在 `requirement-testability` 输出结构化需求模型之后、`testing-method-router` 之前执行。

## 阻塞级问题判定

以下情况优先标记为 `Blocking`：

- 多条件业务规则缺失，例如优惠叠加、审批优先级、互斥分支或规则优先级。
- 状态迁移不完整，例如终态是否可回退、取消后是否释放资源、失败后是否补偿。
- 权限边界不清，例如角色、租户、归属、数据范围或审批权限不同。
- 金额、数量、时间、次数、配额、阈值等边界缺失。
- 接口失败、超时、重试、幂等、回调或错误码规则缺失。
- 当前需求与 `memory/latest-context-pack.md` 中已确认事实冲突。
- 需求只出现“合理、快速、稳定、优化”等不可验证表达，且影响核心验收。

以下情况通常不阻塞：

- 只影响措辞、报告组织或补充说明的问题。
- 可作为风险确认点继续分析的问题。
- 不影响核心测试点生成的非关键边界。

## AskUserQuestion 使用规则

如果存在 `Blocking` 问题，优先使用 Claude Code 的 `AskUserQuestion` 交互能力，而不是只输出 Markdown 文本。

- 只在主入口 skill 或主会话编排中触发，不交给 subagent 内部触发。
- 每轮最多提出 1 到 4 个问题；复杂需求优先一次只问最关键的 1 到 3 个。
- 每个问题提供 2 到 4 个明确选项。
- 选项必须包含一个可继续推进的保守选项，例如“暂不确认，作为待确认风险点继续”。
- 宿主 UI 应保留自定义回答入口；用户自定义回答只作用于本次分析，除非后续明确确认写入 memory。
- 用户选择“暂不确认”时，不编造业务规则；把对应内容标记为待确认风险点继续。

## 问题输出字段

每个问题应包含：

| 字段 | 说明 |
|---|---|
| 问题ID | 使用 `CQ-001` 递增 |
| header | 12 个字以内，用于交互问题标题 |
| question | 面向用户的清晰问题 |
| why | 为什么必须确认 |
| options | 2 到 4 个选项 |
| blockingLevel | `Blocking`、`Important` 或 `Optional` |
| relatedRequirement | 关联需求依据 |
| memoryConflict | 如有冲突，说明冲突的 memory 来源 |

## 会话产物

创建或更新 `outputs/clarifications/<需求文件名>.clarification-session.md`，记录：

- 澄清问题队列。
- 用户回答。
- 回答是否进入本次上下文。
- 是否建议沉淀到长期 memory。

该文件是运行产物，不是长期 memory。

## 输出

如果无 `Blocking` 问题：

- 输出“无需交互澄清”。
- 将 `Important` 和 `Optional` 问题保留为后续报告中的待确认问题或风险确认点。

如果存在 `Blocking` 问题：

1. 调用 `AskUserQuestion` 询问用户。
2. 将用户回答写入澄清会话产物。
3. 将已确认答案作为本次运行上下文合并进结构化需求模型。
4. 对选择“暂不确认”的问题，作为待确认风险点继续，不写成已确认规则。

## 约束

- 不生成测试点。
- 不生成测试用例或操作步骤。
- 不把用户本次回答自动写入 `memory/project-memory.md`、`memory/domains/*.md` 或 `memory/testing-experience-memory.md`。
- 不为了追求覆盖率而提出无关问题。
- 不把合理推测伪装成用户确认。
