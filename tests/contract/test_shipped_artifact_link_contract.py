"""Every link inside the shipped package must resolve inside the shipped package.

`skills/` content ships standalone. A relative link that points at a
repository-only path resolves to nothing once the archive is extracted, which
is the failure the shipped-package boundary rule exists to prevent.

`test_epistemic_guardrail_boundary_contract.py` already forbids repository-only
substrings, but it scans `skills/` only. The archive also carries the root
`SKILL.md` and `SOULMAP.md`, so a broken link in either shipped without any
check seeing it. This closes that gap.

It checks link *targets* rather than raw substrings on purpose. `SOULMAP.md`
legitimately names `templates/` and `.claude/` in prose, precisely to explain
that they are internal-only and do not ship. Naming a directory to say it is
absent is correct content; linking to it is the defect. A substring rule cannot
tell those apart, and would have to either fail on correct prose or carry a
per-file exemption.

The shipped set comes from the packager's own `_iter_inputs`, so this follows
the real boundary rather than restating it. If the packager starts shipping
another file, that file is checked here automatically.
"""

from __future__ import annotations

import posixpath
import re

from soulmap.devtools.packaging.build_skill import _iter_inputs
from soulmap.devtools.support.repo import REPO_ROOT

# Inline links only. Reference-style definitions and bare autolinks are not
# used in the shipped files today; if that changes, this pattern needs to grow
# and the anti-vacuous test below is what will show it has not.
_INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def _shipped_relative_paths() -> set[str]:
    """Return every shipped file as a POSIX path relative to the repo root."""
    return {path.relative_to(REPO_ROOT).as_posix() for path in _iter_inputs(REPO_ROOT)}


def _shipped_directories(files: set[str]) -> set[str]:
    """Return every directory implied by the shipped files.

    An archive stores files, not directories, but a link to `skills/safety/`
    resolves fine once extracted. Every ancestor counts, not just the immediate
    parent, so a link to `skills/` resolves too.
    """
    directories: set[str] = set()
    for name in files:
        parts = name.split("/")[:-1]
        for depth in range(1, len(parts) + 1):
            directories.add("/".join(parts[:depth]))
    return directories


def _broken_links() -> list[str]:
    """Return a description of every shipped link that would not resolve."""
    files = _shipped_relative_paths()
    directories = _shipped_directories(files)
    broken: list[str] = []

    for name in sorted(files):
        if not name.endswith(".md"):
            continue
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        for raw_target in _INLINE_LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith(_EXTERNAL_PREFIXES):
                continue
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), target)
            )
            if resolved not in files and resolved not in directories:
                broken.append(f"{name}: [{raw_target}] does not resolve to {resolved}")
    return broken


def test_the_shipped_set_includes_the_root_manifests_and_the_skills_tree() -> None:
    """Anti-vacuous guard, and a check that the boundary is what we think.

    If `_iter_inputs` ever stopped returning the root manifests, the link check
    below would pass by simply not looking at them, which is the exact gap this
    file was written to close.
    """
    files = _shipped_relative_paths()

    assert "SKILL.md" in files, "the root manifest is no longer in the shipped set"
    assert "SOULMAP.md" in files, "the doctrine file is no longer in the shipped set"
    assert sum(1 for name in files if name.startswith("skills/")) >= 70

    markdown = [name for name in files if name.endswith(".md")]
    assert len(markdown) >= 70, f"only {len(markdown)} shipped markdown files parsed"


def test_no_shipped_file_links_to_something_that_does_not_ship() -> None:
    """A link that dies on extraction is the shipped-package boundary failing."""
    broken = _broken_links()

    assert not broken, "links that break once the archive is extracted:\n" + "\n".join(
        broken
    )


def test_internal_only_directories_never_appear_as_a_link_target() -> None:
    """Naming an internal directory in prose is fine; linking to it is not.

    `SOULMAP.md` explains that `templates/` and `.claude/` are internal and do
    not ship. That prose is correct and must stay allowed. A link into either
    one is a different thing: it would resolve to nothing for every reader of
    the extracted package.
    """
    internal_roots = (
        "templates/",
        ".claude/",
        ".github/",
        "docs/",
        "tests/",
        "scripts/",
        "src/",
        "library/",
    )
    offenders: list[str] = []

    for name in sorted(_shipped_relative_paths()):
        if not name.endswith(".md"):
            continue
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        for raw_target in _INLINE_LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].strip().lstrip("./")
            if target.startswith(internal_roots):
                offenders.append(f"{name}: links to internal path {raw_target!r}")

    assert not offenders, "\n".join(offenders)
