# Test Analysis Agent Project Rules

This repository is a portable test analysis agent package. Keep the core workflow in Markdown skills and lightweight Python validation scripts so it can run in Claude Code, OpenCode, and other agent runtimes.

## Runtime Entry Points

- Claude Code uses `.claude-plugin/plugin.json` and the root `skills/` directory.
- OpenCode uses `opencode.json`, `AGENTS.md`, `.opencode/commands/`, and `.opencode/skills/`.
- The main workflow is `skills/analyze-requirement-testpoints/SKILL.md`.
- Do not reintroduce plugin-level `agents/`; role-specific behavior belongs in skills, knowledge files, templates, or quality gates.

## Skill Source Of Truth

- Treat `skills/` as the only manually edited skill source.
- Treat `.opencode/skills/` as a generated mirror for OpenCode discovery.
- After changing any `skills/*/SKILL.md`, run `python bin/sync-opencode-skills.py`.
- After changing runtime wiring, run `python bin/validate-agent-runtime.py`.

## Path Rules

- Resolve all `skills/...`, `knowledge/...`, `templates/...`, `quality-gates/...`, `memory/...`, `bin/...`, and `outputs/...` paths from the repository root.
- Do not resolve paths relative to a skill directory, `.claude-plugin/`, `.opencode/`, or an input file directory.
- Runtime outputs belong under `outputs/runs/<run-id>/`.

## Test Analysis Workflow

- For requests to generate test case design input from a Markdown requirement, use `analyze-requirement-testpoints`.
- Use `memory-context-builder`, `requirement-testability`, `clarification-gate`, `testing-method-router`, the routed analysis skills, `testpoint-generation`, and `coverage-review` as the staged skill actions.
- Do not invent business facts, states, roles, API contracts, thresholds, or test data.
- Run deterministic checks from `bin/` before considering generated reports complete.

## Validation Commands

- Runtime wiring: `python bin/validate-agent-runtime.py`
- OpenCode skill mirror: `python bin/sync-opencode-skills.py --check`
- Example output smoke test: `python bin/smoke-test-analysis.py`
