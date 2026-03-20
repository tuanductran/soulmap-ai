# Scripts

This folder contains bash helpers for contributor workflows.

## Common commands

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
bash scripts/format.sh
bash scripts/lint.sh
```

Cross-platform equivalents live under `tools/`:

```bash
python -m tools.format
python -m tools.lint
python -m tools.build_skill
python -m tools.build_skill --skill
python -m tools.eval_responses
```

For setup and workflow details, use [`docs/DEV.md`](../docs/DEV.md).
