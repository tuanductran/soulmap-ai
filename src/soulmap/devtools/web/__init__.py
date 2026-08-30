"""Static website generator for the public SoulMap site.

This package reads canonical repository files and writes static HTML. It never
writes to `skills/`, never executes `soulmap.runtime`, and never serves a
request. See `docs/web/ARCHITECTURE.md` for the boundary this package works
inside, and `docs/web/CONTENT-MODEL.md` for the allowlist that decides what may
become public.
"""

from __future__ import annotations
