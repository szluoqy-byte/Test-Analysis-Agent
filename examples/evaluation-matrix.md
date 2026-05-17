# 示例评测矩阵

本文件用于规划测试分析 Agent 的回归样例。每个样例都应包含输入需求，以及 `examples/outputs/runs/<stem>-run/` 下固定命名的测试用例设计输入、过程上下文、过程报告和测试点明细，并通过 `bin/smoke-test-analysis.py`。

## 已覆盖样例

| 样例 | 主要能力 | 状态 |
|---|---|---|
| `sample-requirement.md` | 状态迁移、权限矩阵、数据一致性、接口契约、待确认问题 | 已覆盖，固定 run：`examples/outputs/runs/sample-requirement-run/` |
| `complex-promotion-requirement.md` | 边界值、等价类、决策表、状态迁移、权限矩阵、接口契约、数据一致性、组合兼容、风险驱动 | 已覆盖，固定 run：`examples/outputs/runs/complex-promotion-requirement-run/` |

## 待补充样例

| 样例方向 | 必须覆盖的方法 | 目标风险 |
|---|---|---|
| 审批流和撤回 | 状态迁移、权限矩阵、场景流 | 非法迁移、越权审批、终态修改 |
| 批量导入和部分失败 | 边界值、等价类、数据一致性、错误推测 | 批量上限、重复数据、部分成功回滚 |
| 多租户数据隔离 | 权限矩阵、数据一致性、安全风控 | 跨租户访问、数据泄露、权限缓存 |
| 外部系统回调 | 接口契约、状态迁移、数据一致性 | 重复回调、乱序回调、超时补偿 |
| 配置开关灰度发布 | 组合兼容、场景流、风险驱动 | 新老版本差异、开关回滚、降级行为 |

## 样例验收

- 测试用例设计输入通过 `bin/lint-testcase-design-input.py`。
- 固定 run 目录通过 `bin/check-artifact-consistency.py`。
- 过程报告通过 `bin/lint-testpoint-report.py`。
- 独立测试点明细通过 `bin/lint-testpoint-report.py`。
- 过程报告通过 `bin/semantic-testpoint-check.py`。
- 过程报告与独立测试点明细中的测试点表完全一致，且不与测试用例设计输入冲突。
