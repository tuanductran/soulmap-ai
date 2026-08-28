"""Command-line entry point for the response-generation evaluation run.

This module only forwards to ``soulmap.devtools.evals.eval_responses``, which owns the
behavior. Keep logic in that module rather than here.
"""

from __future__ import annotations

from soulmap.devtools.evals.eval_responses import main

if __name__ == "__main__":
    raise SystemExit(main())
