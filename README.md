# EarnGreen

Green tests can lie. EarnGreen verifies that green was earned — Hollow Trust Card, Gate A, and Weekly integrity for AI-written tests (pytest beachhead).

## Repo role

This is the **product package** git repository (architecture AD-13): one installable `earngreen` package, CLI, and GitHub Action.

Planning, BMad, and the initiative / ticket store live in the BMAD polyrepo workspace [`earn-green.specs`](https://github.com/zhmachenkov-d/earn-green.specs) (architecture AD-14). Clone that workspace with `--recurse-submodules` and start agents from its root.

```text
earn-green.specs/          # workspace + planning (start AI here)
└── earn-green/            # this repo (submodule)
```

## Install and run

From this repository (or the `earn-green/` submodule in the workspace):

```bash
uv sync --group dev
uv run earngreen --help
uv run earngreen --version
```

Scaffold CLI only — `--help` and `--version`. Run smoke tests with `uv run pytest`.
