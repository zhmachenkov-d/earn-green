# EarnGreen product repo

This repository is the **product package** checkout (`earngreen` Python package, CLI, Action). It is not the BMAD planning workspace.

## Planning / BMad

- Canonical BMad install and ticket store live in the parent polyrepo workspace: `earn-green.specs` (`_bmad/`, `_bmad-output/`).
- Start the AI tool from that workspace root, not from this folder alone.
- Do not install BMad (`_bmad/`, `.agents/` skills) in this repository — it breaks polyrepo project-root resolution.
- Specs and stories that change this code must name project `earn-green`.

See parent `AGENTS.md`, parent `README.md`, and architecture AD-13 / AD-14.

## Design principles

Code in this package must follow **SOLID**, **DRY**, **KISS**, and the **Pythonic Way** (PEP 20 / idiomatic Python):

- **SOLID** — single responsibility per module/type; open for extension via clear seams, closed for careless edits; depend on abstractions at package boundaries (core vs adapters/surfaces), not on concrete I/O.
- **DRY** — one source of truth for a rule or mapping; extract shared logic when duplication would drift, not prematurely.
- **KISS** — prefer the simplest design that meets the story; no speculative layers, frameworks, or configurability.
- **Pythonic Way** — clear over clever; explicit over implicit; prefer stdlib and language idioms (`with`, comprehensions where readable, EAFP where natural, dataclasses/`Enum`/`Path` as fit) over Java-style boilerplate or reinvented patterns. Readability counts; when in doubt, match existing module style and PEP 8 via Ruff.

When a change pulls against these (e.g. a shortcut that duplicates policy or bloated “future-proof” APIs), choose the principle-aligned option and say so briefly in the PR/commit context.

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
