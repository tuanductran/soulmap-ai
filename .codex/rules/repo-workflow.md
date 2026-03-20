# Codex Repo Workflow

Use these rules when Codex is working inside this repository.

## Source of truth

- `AGENTS.md` is the baseline SoulMap doctrine, safety contract, and shipped package guide.
- `docs/repo-contract.md` is the structural contract.
- `docs/maintenance-boundary.md` is the scope-control document.
- `docs/content-contract.md` is the Markdown contract.

## Working style

- Make the smallest correct change first.
- Prefer updating existing files over adding parallel ones.
- Do not expand product scope just because a new surface is possible.
- Keep local Codex files supplemental to `AGENTS.md`, not competitive with it.

## Quality checks

After meaningful edits, run:

```bash
python3 -m tools.format
python3 -m tools.lint
python3 -m pytest -q
```

If packaging or release behavior changed, also run:

```bash
python3 -m tools.build_skill
python3 -m tools.build_skill --skill
```

For behavior and content validation, run when relevant:

```bash
python3 -m tools.eval_responses
python3 tests/test_safety_evals.py
python3 -m modules.markdown_contract --root .
```
