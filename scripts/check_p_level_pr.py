"""Shell entry point for the P-level governance check.

Forwards to ``soulmap.devtools.checks.p_level_governance``, which owns the
behavior. This wrapper exists so CI can call the check by path without
depending on the installed console script.
"""

from __future__ import annotations

from soulmap.devtools.checks.p_level_governance import main

if __name__ == "__main__":
    raise SystemExit(main())
