# Scripts

This folder contains bash helpers for contributor workflows.

The shell scripts here are thin macOS/Linux wrappers around the canonical Python entry
points in `src/soulmap/devtools/` and `src/soulmap/runtime/`.

## Common commands

```bash
bash scripts/bootstrap_venv.sh
bash scripts/format.sh
bash scripts/lint.sh
```

Cross-platform equivalents are the canonical Python entrypoints:

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap build
uv run soulmap build --skill
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap eval-markdown-contracts
```

If you edit public URLs in Markdown and want live external validation, run:

```bash
uv run soulmap check-links --root . --check-external
```

Before pushing, mirror the local CI core with:

```bash
uv run soulmap lint --skip-tests
uv run soulmap test -n auto -q
```

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
