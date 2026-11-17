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

from pathlib import Path

from soulmap.devtools.packaging.build_skill import _iter_inputs
from soulmap.devtools.support.markdown import (
    is_external_markdown_target,
    iter_markdown_references,
    resolve_local_markdown_target,
    split_markdown_link_target,
)
from soulmap.devtools.support.repo import REPO_ROOT


def _shipped_relative_paths(repo_root: Path = REPO_ROOT) -> set[str]:
    """Return every shipped file as a POSIX path relative to the repo root."""
    return {path.relative_to(repo_root).as_posix() for path in _iter_inputs(repo_root)}


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


def _broken_links(repo_root: Path = REPO_ROOT) -> list[str]:
    """Return a description of every shipped Markdown link that would not resolve."""
    files = _shipped_relative_paths(repo_root)
    directories = _shipped_directories(files)
    broken: list[str] = []

    for name in sorted(files):
        if not name.endswith(".md"):
            continue
        current_file = repo_root / name
        lines = current_file.read_text(encoding="utf-8").splitlines(keepends=True)
        for reference in iter_markdown_references(lines):
            target_path, _fragment = split_markdown_link_target(reference.target)
            if not target_path or is_external_markdown_target(target_path):
                continue
            resolved = resolve_local_markdown_target(
                repo_root=repo_root,
                current_file=current_file,
                target_path=target_path,
            )
            try:
                relative = resolved.relative_to(repo_root.resolve()).as_posix()
            except ValueError:
                broken.append(
                    f"{name}:{reference.line}: [{reference.label}] escapes the "
                    f"shipped package: {reference.target}"
                )
                continue
            if relative not in files and relative not in directories:
                broken.append(
                    f"{name}:{reference.line}: [{reference.label}] does not resolve "
                    f"to {relative}"
                )
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


def test_shipped_link_audit_parses_reference_links_and_nested_destinations(
    tmp_path: Path,
) -> None:
    """Reference-style links and nested destinations must be checked as well as inline links."""
    (tmp_path / "LICENSE").write_text("license\n", encoding="utf-8")
    (tmp_path / "SOULMAP.md").write_text("# Doctrine\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text(
        "# Skill\n\n"
        "[Guide][guide]\n"
        "[Missing][missing]\n"
        "[Nested](skills/assets/logo_(dark).png)\n"
        "![Absent](skills/assets/missing_(dark).png)\n\n"
        "[guide]: skills/guide.md\n"
        "[missing]: skills/not-present.md\n",
        encoding="utf-8",
    )
    (tmp_path / "skills" / "assets").mkdir(parents=True)
    (tmp_path / "skills" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "skills" / "assets" / "logo_(dark).png").write_bytes(b"image")

    findings = _broken_links(tmp_path)

    assert len(findings) == 2
    assert any("skills/not-present.md" in finding for finding in findings)
    assert any("missing_(dark).png" in finding for finding in findings)


def test_shipped_link_audit_rejects_targets_that_escape_package_root(
    tmp_path: Path,
) -> None:
    (tmp_path / "LICENSE").write_text("license\n", encoding="utf-8")
    (tmp_path / "SOULMAP.md").write_text("# Doctrine\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text("[Outside](../outside.md)\n", encoding="utf-8")

    findings = _broken_links(tmp_path)

    assert len(findings) == 1
    assert "escapes the shipped package" in findings[0]


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
        lines = (REPO_ROOT / name).read_text(encoding="utf-8").splitlines(keepends=True)
        for reference in iter_markdown_references(lines):
            target, _fragment = split_markdown_link_target(reference.target)
            target = target.strip().lstrip("./")
            if target.startswith(internal_roots):
                offenders.append(
                    f"{name}:{reference.line}: links to internal path {reference.target!r}"
                )

    assert not offenders, "\n".join(offenders)
