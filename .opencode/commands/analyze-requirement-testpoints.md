---
description: Generate test case design input from a Markdown requirement
agent: build
---

Use the repository skill `analyze-requirement-testpoints`.

Treat the command arguments below as the skill `$ARGUMENTS`:

```text
$ARGUMENTS
```

Keep `PROJECT_ROOT` fixed to the current repository root. Write outputs under `outputs/runs/<run-id>/`, run the deterministic checks from `bin/`, and report the design input path, process report path, check result, and unresolved confirmation questions.
