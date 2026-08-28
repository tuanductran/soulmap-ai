"""Command-line entry point for the repository formatter.

This module only forwards to ``soulmap.devtools.quality.format``, which owns the
behavior. Keep logic in that module rather than here.
"""

from __future__ import annotations

from soulmap.devtools.quality.format import main

if __name__ == "__main__":
    raise SystemExit(main())
