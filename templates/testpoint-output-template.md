# 兼容测试点明细模板

> 说明：该模板仅用于兼容旧的过程审查或表格导入场景。当前主输出应使用 `templates/testcase-design-input-template.md` 生成 `deliverables/testcase-design-input.md`。

```markdown
# <需求名称> 测试点明细

- 输入文档：
- 运行 ID：
- 来源报告：
- 生成时间：
- 说明：本文件仅保存测试点明细，不包含覆盖审查、质量门禁、专家评分和记忆更新建议。

## 测试点明细

| ID | 模块 | 测试点 | 类型 | 方法 | 需求依据 | 级别 | 风险/备注 |
|---|---|---|---|---|---|---|---|
| TP-001 |  | 验证... | 功能正确性 | 风险驱动 |  | Level 1 |  |
```

## 字段规则

- `ID`：`TP-001` 格式，按顺序递增。
- `模块`：需求模块或业务区域。
- `测试点`：按 `knowledge/testpoint-standard.md` 的表达结构描述验证目标。
- `类型`：来自 `knowledge/testpoint-standard.md` 的标准分类。
- `方法`：使用的测试理论或启发式方法。
- `需求依据`：需求标题、表格行、段落摘要或明确的风险确认点。
- `级别`：取值以 `knowledge/testpoint-standard.md` 为准。
- `风险/备注`：简洁说明风险、不确定性或评审备注。

## 落盘规则

- 主输出路径：`${PROJECT_ROOT}/outputs/runs/<run-id>/deliverables/testcase-design-input.md`。
- 如需兼容旧流程，可额外生成独立明细，固定路径为 `${PROJECT_ROOT}/outputs/runs/<run-id>/legacy/testpoint-details.md`，不得替代主输出。
- 兼容明细文件必须能追溯到主输出中的场景测试点和接口测试点，不得与主输出冲突。
