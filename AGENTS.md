# EarnGreen product repo

This repository is the **product package** checkout (`earngreen` Python package, CLI, Action). It is not the BMAD planning workspace.

## Planning / BMad

- Canonical BMad install and ticket store live in the parent polyrepo workspace: `earn-green.specs` (`_bmad/`, `_bmad-output/`).
- Start the AI tool from that workspace root, not from this folder alone.
- Do not install BMad (`_bmad/`, `.agents/` skills) in this repository — it breaks polyrepo project-root resolution.
- Specs and stories that change this code must name project `earn-green`.

See parent `AGENTS.md`, parent `README.md`, and architecture AD-13 / AD-14.

## Python lint, format, and types

Ruff is the only linter and formatter. Mypy is the type checker. Config for both lives in `pyproject.toml` (`[tool.ruff]`, `[tool.mypy]`). Do not add Black, isort, Flake8, pyright, or parallel formatters/type checkers.

After changing Python under `src/` or `tests/`:

```bash
uv sync --group dev
uv run ruff check --fix .
uv run ruff format .
uv run mypy
uv run pytest
```

- Prefer auto-fixes from `ruff check --fix` over hand-editing style.
- Change Ruff/Mypy rule sets only in `pyproject.toml`; do not sprinkle `# noqa` / `# type: ignore` unless a false positive needs a one-line exception with a short reason.
- Ruff `target-version` and Mypy `python_version` are `3.12` (matches `requires-python`).
- Mypy runs in `strict` mode; keep public APIs annotated.
