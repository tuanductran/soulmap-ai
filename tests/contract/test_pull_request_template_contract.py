"""The pull-request template must stay in step with the governance check.

`p-level-governance` rejects a P-level pull request whose body is missing any
of nine exact strings. Nothing helped an author produce them, so the contract
lived in whoever remembered it. This template carries it instead.

Two properties matter, and they pull against each other:

- the template must contain every string the check looks for, so filling it in
  is enough
- the template's own placeholder values must be rejected, so submitting it
  unedited cannot satisfy a safety contract with junk

A template that only satisfied the first would be worse than none: it would
turn a real check into a shape an author can pattern-match past.
"""

from __future__ import annotations

from pathlib import Path

from soulmap.devtools.checks.p_level_governance import (
    CHANGE_EVIDENCE_MARKERS,
    REQUIRED_FIELDS,
    validate_pull_request,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / ".github" / "pull_request_template.md"

_TAGGED_TITLE = "[P1] fix(safety): example"


def _template() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _filled() -> str:
    """Return the template with every placeholder replaced by real content."""
    return (
        _template()
        .replace("P0 | P1 | P2 | P3", "P1")
        .replace("preserved | changed", "changed")
        .replace("- **Evidence:** n/a", "- **Evidence:** full suite green")
        .replace(
            "- **Rollback:** how to undo this", "- **Rollback:** revert this commit"
        )
        .replace("- **ADR:**", "- **ADR:** 0004")
        .replace("- **Positive regression:**", "- **Positive regression:** test_x")
        .replace("- **Near-miss regression:**", "- **Near-miss regression:** test_y")
        .replace("- **Safety matrix:**", "- **Safety matrix:** unchanged")
    )


def test_the_template_exists_where_github_looks_for_it() -> None:
    assert TEMPLATE.is_file(), f"missing {TEMPLATE.relative_to(REPO_ROOT)}"


def test_the_template_carries_every_string_the_check_requires() -> None:
    """A field the checker wants but the template omits is a trap for authors."""
    text = _template()

    missing = [f"- **{field}:**" for field in sorted(REQUIRED_FIELDS)]
    missing = [marker for marker in missing if marker not in text]
    assert not missing, f"template is missing required fields: {missing}"

    absent = [marker for marker in CHANGE_EVIDENCE_MARKERS if marker not in text]
    assert not absent, f"template is missing safety-change markers: {absent}"


def test_the_unedited_template_cannot_satisfy_a_p_level_pull_request() -> None:
    """Submitting the template as-is must fail, not pass with placeholder text.

    This is the property that keeps the template from weakening the check it
    encodes. Every placeholder is chosen to be rejected: a priority that cannot
    match any title, a boundary that is neither value, an evidence line the
    checker explicitly refuses, and a rollback line with no `revert` in it.
    """
    errors = validate_pull_request(_TAGGED_TITLE, _template())

    assert len(errors) >= 4, f"placeholders were accepted: {errors}"


def test_a_filled_template_passes() -> None:
    """Filling it in is sufficient, so the template is actually usable."""
    assert validate_pull_request(_TAGGED_TITLE, _filled()) == []


def test_the_template_is_inert_for_an_untagged_pull_request() -> None:
    """Most pull requests carry no P-level, and must not be blocked by it."""
    assert validate_pull_request("fix(safety): example", _template()) == []


def test_deleting_the_evidence_section_still_fails_a_boundary_change() -> None:
    """The template must not let an author drop the section it exists to carry."""
    body = _filled().split("## Safety change evidence")[0]

    errors = validate_pull_request(_TAGGED_TITLE, body)

    assert len(errors) == len(CHANGE_EVIDENCE_MARKERS)
