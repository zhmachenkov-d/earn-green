# EarnGreen product repo

This repository is the **product package** checkout (`earngreen` Python package, CLI, Action). It is not the BMAD planning workspace.

## Planning / BMad

- Canonical BMad install and ticket store live in the parent polyrepo workspace: `earn-green.specs` (`_bmad/`, `_bmad-output/`).
- Start the AI tool from that workspace root, not from this folder alone.
- Do not install BMad (`_bmad/`, `.agents/` skills) in this repository — it breaks polyrepo project-root resolution.
- Specs and stories that change this code must name project `earn-green`.

See parent `AGENTS.md`, parent `README.md`, and architecture AD-13 / AD-14.
