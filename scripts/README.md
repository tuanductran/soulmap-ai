# Scripts

This folder contains shell and Python helpers for contributor workflows and CI.

The shell scripts here are thin macOS/Linux wrappers around the canonical Python entry
points in `src/soulmap/devtools/` and `src/soulmap/runtime/`.

## Common commands

```bash
bash scripts/bootstrap_venv.sh
bash scripts/format.sh
bash scripts/lint.sh
```

Activating `.venv` is optional when you use `uv run ...`. To activate it in the
current shell, source this helper rather than running it:

```bash
source scripts/activate_venv.sh
```

Cross-platform equivalents are the canonical Python entrypoints:

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap check-api-docs --root .
uv run soulmap build
uv run soulmap build --skill
uv run soulmap library-manifest
uv run python scripts/verify_artifact_hashes.py
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

CI and release verification use the reproducibility helper to record an explicit
pytest-randomly seed and preserve a serial reproduction command when parallel tests fail:

```bash
uv run python scripts/pytest_diagnostics.py
```

After building the Library artifacts, verify their recorded size and SHA-256 values
without network access:

```bash
uv run soulmap library-manifest
uv run python scripts/verify_artifact_hashes.py
```

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
