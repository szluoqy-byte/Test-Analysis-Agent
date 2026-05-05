---
name: risk-based-test-analysis
description: 当需要按产品、业务、数据、权限、集成、运维和历史缺陷风险来识别重点覆盖区域和测试点级别时使用。
---

# 风险驱动测试分析 Skill

本 skill 用来判断“哪里失败代价最高，哪里应该优先测”。

## 输入

- 结构化需求模型。
- 记忆上下文包。
- `knowledge/expert-rules.md`。
- `knowledge/defect-patterns.md`。
- `knowledge/testpoint-standard.md`。
- `knowledge/risk-level-rules.md`。

## 风险识别方式

- 使用 `knowledge/expert-rules.md` 判断风险覆盖方向。
- 使用 `knowledge/defect-patterns.md` 匹配通用缺陷模式。
- 使用 `memory/latest-context-pack.md` 中的项目历史缺陷和项目风险模式修正关注点。
- 使用 `knowledge/risk-level-rules.md` 判断建议级别，级别定义仍以 `knowledge/testpoint-standard.md` 为准。

## 级别规则

级别定义以 `knowledge/testpoint-standard.md` 为准；本 skill 只负责根据风险原因建议级别。

## 输出

先输出方法分析证据：

| 证据ID | 方法 | 风险点/失败模式 | 分析结论 | 关联测试点/待确认 |
|---|---|---|---|---|

再输出风险登记表：

| 模块 | 风险点 | 风险原因 | 建议级别 | 关联需求依据 |
|---|---|---|---|---|

## 约束

- 风险可以将测试点调整为更高重要级别，但不能创造需求中没有的业务规则。
- 合理但未明确的风险，标记为“待确认”或“风险确认点”。
