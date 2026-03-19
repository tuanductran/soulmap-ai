# Tester Guide

## What "good" looks like

- The selector returns exactly one `primary_framework` and a coherent instruction
  string.
- Safety ordering holds (crisis and dependency take priority).
- Local `.claude/` workflow docs and skills match the current repo structure.
- Markdown links and anchors across the repo are not broken.
- Distribution zip builds and contains the expected files.

## Run the full test suite

```bash
python -m tools.lint
```

This runs:

- Python checks: compileall, ruff, isort, pytest, optional pyright.
- Local workflow contract checks, including `tests/test_claude_contract.py`.
- Markdown checks: contract checker (links/anchors/fences/headings/metadata) +
  `pymarkdown` across repo docs, `skills/`, and `templates/` while preserving YAML
  front matter.
- Build smoke: the zip build can be run separately (see below).

Use these docs as review references when verifying release readiness:

- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
- [`../templates/launch-readiness-checklist.md`](../templates/launch-readiness-checklist.md)

## Build artifacts

```bash
python -m tools.build_skill_zip
```

Verify:

- `dist/soulmap-ai.zip` exists and includes files under `skills/` and `templates/`.

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
