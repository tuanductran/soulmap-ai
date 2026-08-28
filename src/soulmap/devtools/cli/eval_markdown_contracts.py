"""Command-line entry point for the Markdown contract evaluation run.

This module only forwards to ``soulmap.devtools.evals.eval_markdown_contracts``, which owns the
behavior. Keep logic in that module rather than here.
"""

from __future__ import annotations

from soulmap.devtools.evals.eval_markdown_contracts import main

if __name__ == "__main__":
    raise SystemExit(main())
