"""Command-line entry point for the canonical-casing checker.

This module only forwards to ``soulmap.devtools.checks.check_markdown_case``, which owns the
behavior. Keep logic in that module rather than here.
"""

from __future__ import annotations

from soulmap.devtools.checks.check_markdown_case import main

if __name__ == "__main__":
    raise SystemExit(main())
