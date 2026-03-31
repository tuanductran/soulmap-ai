# Scripts

This folder contains bash helpers for contributor workflows.

The shell scripts here are thin macOS/Linux wrappers around the canonical Python entry
points in `src/soulmap_devtools/` and `src/soulmap_runtime/`.

## Common commands

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
bash scripts/format.sh
bash scripts/lint.sh
```

Cross-platform equivalents are the canonical Python entrypoints:

```bash
python -m soulmap_devtools.cli.format
python -m soulmap_devtools.cli.lint
python -m soulmap_runtime.guards.markdown_contract --root .
python -m soulmap_devtools.cli.check_markdown_links --root .
python -m soulmap_devtools.cli.check_markdown_case --root .
python -m soulmap_devtools.cli.build_skill
python -m soulmap_devtools.cli.build_skill --skill
python -m soulmap_devtools.cli.eval_groups
python -m soulmap_devtools.cli.eval_responses
python -m soulmap_devtools.cli.eval_markdown_contracts
```

If you edit public URLs in Markdown and want live external validation, run:

```bash
python -m soulmap_devtools.cli.check_markdown_links --root . --check-external
```

The repo's `pre-push` hook mirrors the local CI core with:

```bash
python -m soulmap_devtools.cli.lint --skip-tests
python -m pytest -n auto -q
```

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
