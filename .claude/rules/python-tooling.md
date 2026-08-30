---
paths:
  - src/**/*.py
  - tests/**/*.py
  - scripts/**/*.py
  - pyproject.toml
---

# Python and tooling rules

Use the repo's Python tooling contract when changing code or developer workflows.

- keep Python 3.11 compatibility
- keep `pyproject.toml` as the source of truth for Python tooling
- prefer Ruff as the single Python lint, format, and import-sorting tool unless the
  repo has a proven gap it cannot cover
- keep Pyright aligned with `[tool.pyright]`
- prefer typed changes that continue to pass Pyright in `standard` mode

## Docstrings and annotations

Ruff enforces `D` (pydocstyle, Google convention) and `ANN` (annotations) across
`src/`, `tests/`, and `scripts/`. Both are contracts, not style preferences, so a
new function needs its docstring and its annotations before it lands.

- write Google-style docstrings: a one-line summary, a blank line, then the body
- document `Args:`, `Returns:`, `Yields:`, and `Raises:` when they carry information
  a reader cannot get from the signature
- do not restate the signature in prose, explain the contract and the reason instead
- for a detector or guard, say which Markdown file owns the phrases it reads, so the
  knowledge-first boundary stays visible from the Python side
- annotate every argument and return, including test helpers and fixtures
  (`monkeypatch: pytest.MonkeyPatch`, `capsys: pytest.CaptureFixture[str]`)
- prefer a precise type over `Any`, a context manager returns `Iterator[None]`
  rather than `Any`

Test functions are exempt from the missing-docstring rules (`D100` to `D104`) because
the test name carries the meaning. Keep writing a docstring when a test encodes a
doctrine rule that the name alone cannot explain, and quote the rule it protects.

- update tests when a tooling or contract change affects observable behavior
- prefer shared helpers in `src/soulmap/runtime/io/cli_payload.py` for stdin parsing, JSON error output, and common payload extraction
- prefer shared helpers in `src/soulmap/runtime/io/text_normalization.py` for message cleanup instead of re-implementing quote and whitespace normalization per detector
- prefer package-first commands rooted in `src/soulmap/devtools/` and `src/soulmap/runtime/`
- keep `.venv` editable install aligned with `scripts/bootstrap_venv.sh` and `pyproject.toml`
- if subprocess tests need repo-local imports, pass `PYTHONPATH=src` explicitly rather than reviving root-level shim packages
- for pure helpers such as text normalization, JSON parsing, and small contract utilities, prefer adding compact property-based tests when that catches more edge cases than example-only tests
- do not create a new helper when a call site has a materially different contract or would become less clear than the local explicit code
- `vulture` runs in CI at `min_confidence = 80`; that is a false-positive floor for
  automated gating, not proof nothing real hides below it. For a focused dead-code
  pass, see `../skills/code-quality-review/SKILL.md`'s "Dead code and unused-import
  audits" section for the manual low-confidence sweep and how to triage it
