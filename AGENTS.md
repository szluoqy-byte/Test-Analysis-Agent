# Test Analysis Agent 项目规则

本仓库是一个可移植的测试分析 Agent 包。核心流程应保持在 Markdown skills 和轻量 Python 校验脚本中，以便同时运行在 Claude Code、OpenCode 和其他 Agent 运行时中。

## 运行入口

- Claude Code 使用 `.claude-plugin/plugin.json` 和根目录 `skills/`。
- OpenCode 使用 `opencode.json`、`AGENTS.md`、`.opencode/commands/` 和 `.opencode/skills/`。
- 主流程入口是 `skills/analyze-requirement-testpoints/SKILL.md`。
- 不要重新引入插件级 `agents/`；角色化行为应放在 skills、knowledge 文件、templates 或 quality gates 中。

## Skill 事实源

- `skills/` 是唯一手工维护的 skill 源。
- `.opencode/skills/` 是供 OpenCode 发现 skill 的生成镜像。
- 修改任何 `skills/*/SKILL.md` 后，运行 `python bin/sync-opencode-skills.py`。
- 修改运行时 wiring 后，运行 `python bin/validate-agent-runtime.py`。

## 路径规则

- 所有 `skills/...`、`knowledge/...`、`templates/...`、`quality-gates/...`、`memory/...`、`bin/...` 和 `outputs/...` 路径都从仓库根目录解析。
- 不要基于 skill 目录、`.claude-plugin/`、`.opencode/` 或输入文件目录解析路径。
- 运行产物写入 `outputs/runs/<run-id>/`。
- 支持可选 `project-key`：确定后可扫描 `*/projects/<project-key>/**/*.md`；未唯一确定时不得读取所有项目目录正文。
- `knowledge/projects/<project-key>/` 和 `knowledge/user/` 只能作为测试知识补充，不得覆盖根目录 `knowledge/` 的核心标准、字段、类型、级别和质量门禁。
- 配置分为 `core / project / user` 三层：core 是仓库根目录稳定文件，project 位于 `*/projects/<project-key>/`，user 位于 `*/user/`。project 和 user 默认不提交 Git，只保留 README。
- user 层只能补充个人偏好和本地检查关注点，不得覆盖需求文档、project memory、核心输出契约或质量门禁。

## 测试分析流程

- 当用户要求从 Markdown 需求文档生成测试用例设计输入时，使用 `analyze-requirement-testpoints`。
- 阶段性动作依次使用 `memory-context-builder`、`requirement-testability`、`clarification-gate`、`testing-method-router`、路由选中的专项分析 skills、`testpoint-generation` 和 `coverage-review`。
- 不编造业务事实、状态、角色、接口契约、阈值或测试数据。
- 在认为报告完成前，运行 `bin/` 下的确定性检查。

## 校验命令

- Runtime wiring：`python bin/validate-agent-runtime.py`
- OpenCode skill 镜像：`python bin/sync-opencode-skills.py --check`
- 示例输出 smoke 检查：`python bin/smoke-test-analysis.py`
