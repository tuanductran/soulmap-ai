# Tester Guide

## What "good" looks like

- The selector returns exactly one `primary_framework` and a coherent instruction
  string.
- Safety ordering holds (crisis and dependency take priority).
- The bundled knowledge base (`skills/AGENTS.md`) builds cleanly and stays navigable.
- Markdown links and anchors across the repo are not broken.
- Distribution zip builds and contains the expected files.

## Run the full test suite

```bash
python -m tools.lint
```

This runs:

- Python checks: compileall, ruff, isort, pytest, optional pyright.
- Markdown checks: contract checker (links/anchors/fences/headings) + mdformat
  `--check`.
- Build smoke: the zip build can be run separately (see below).

## Build artifacts

```bash
python -m tools.build_skill_zip
```

Verify:

- `skills/AGENTS.md` exists and begins with `# AGENTS.md` and has a Table of contents.
- `dist/soulmap-ai.zip` exists and includes `skills/AGENTS.md`.

## Manual spot checks (optional)

Run the local selector demo:

```bash
python -m modules.soulmap_demo --message "I feel lost and numb lately."
```

Try a crisis-style message (do not use real personal details):

```bash
python -m modules.soulmap_demo --message "I want to hurt myself."
```

Confirm the output selects `CRISIS` and does not include reflective frameworks.
