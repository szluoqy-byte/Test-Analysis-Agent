# 测试分析任务清单

## 运行标识

- 需求文档：examples/requirements/complex-promotion-requirement.md
- run-id：complex-promotion-requirement-run
- PROJECT_ROOT：examples fixture
- 生成时间：fixture

## 任务列表

| 序号 | 阶段 | 负责 skill | 必须产物/检查点 | 状态 | 证据/路径 |
|---|---|---|---|---|---|
| 1 | 固定 PROJECT_ROOT 与运行目录 | analyze-requirement-testpoints | outputs/runs/complex-promotion-requirement-run/ | done | examples/outputs/runs/complex-promotion-requirement-run/ |
| 2 | 构建上下文包 | memory-context-builder | process/context-pack.md | done | process/context-pack.md |
| 3 | 需求可测性分析 | requirement-testability | 结构化需求模型、需求待确认候选 | done | reports/test-analysis-report.md |
| 4 | 待确认治理 | clarification-gate | CP-MEMORY、CP-REQUIREMENT、CP-ROUTING、CP-METHOD、CP-REVIEW | done | deliverables/testcase-design-input.md#6-待确认信息 |
| 5 | 方法路由 | testing-method-router | 分析维度覆盖表、方法路由表 | done | reports/test-analysis-report.md |
| 6 | 专项方法分析 | selected method skills | ME-* 方法证据、测试点候选、方法缺口候选 | done | reports/test-analysis-report.md |
| 7 | 按源补读 | selected method skills | 按需补读记录、来源说明 | skipped | 示例 fixture 未触发 project/user 按源补读 |
| 8 | 设计输入生成 | testpoint-generation | deliverables/testcase-design-input.md | done | deliverables/testcase-design-input.md |
| 9 | 覆盖审查 | coverage-review | 门禁结果、专家评分、阻断项 | done | reports/test-analysis-report.md |
| 10 | 确定性校验 | coverage-review / bin | lint、consistency、semantic 检查结果 | done | bin/smoke-test-analysis.py |
| 11 | 输出收口 | analyze-requirement-testpoints | 主交付件路径、过程报告路径、最终待确认信息 | done | deliverables/testcase-design-input.md |
