# Claude Code 项目规则

本仓库同时是 Claude Code plugin 和 OpenCode 兼容 Agent 包。

请遵循 `AGENTS.md` 中的同一套项目规则。简版如下：

- Claude Code 加载 `.claude-plugin/plugin.json` 和根目录 `skills/`。
- 主流程入口是 `skills/analyze-requirement-testpoints/SKILL.md`。
- `skills/` 是唯一手工维护的 skill 源。
- `.opencode/skills/` 由 `skills/` 生成，不要直接编辑。
- 修改 skills 后，运行 `python bin/sync-opencode-skills.py`。
- 修改运行时 wiring 后，运行 `python bin/validate-agent-runtime.py`。
- 从仓库根目录解析路径，不要从 `.claude-plugin/`、`.opencode/`、skill 目录或输入文件目录解析。
- 已确定 `project-key` 时可扫描 `*/projects/<project-key>/**/*.md`；未唯一确定时不要读取所有项目目录正文。
- 配置按 `core / project / personal` 三层处理；personal 当前兼容目录是 `*/user/`，project 和 personal 层默认本地化，不提交 Git。
- project 和 personal 是当前 run 的一等输入源，命中、未采用和补读建议必须记录到 `process/context-pack.md`。
- 每次 run 必须维护 `process/task-list.md`，用于约束阶段顺序和状态。
- 不要重新引入插件级 `agents/`；角色化行为应放在 skills、knowledge 文件、templates 或 quality gates 中。
