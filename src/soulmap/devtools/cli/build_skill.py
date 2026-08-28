"""Command-line entry point for building the distribution artifacts.

This module only forwards to ``soulmap.devtools.packaging.build_skill``, which owns the
behavior. Keep logic in that module rather than here.
"""

from __future__ import annotations

from soulmap.devtools.packaging.build_skill import main

if __name__ == "__main__":
    raise SystemExit(main())
