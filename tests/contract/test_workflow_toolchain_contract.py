"""Keep GitHub Actions toolchain pins and audit permissions consistent."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ROOT = REPO_ROOT / ".github" / "workflows"


def test_setup_uv_is_sha_pinned_and_uses_one_consistent_version() -> None:
    """Prevent workflow drift in the uv action revision and installed version."""
    action_refs: list[str] = []
    uv_versions: list[str] = []

    for path in sorted(WORKFLOW_ROOT.glob("*.yml")):
        content = path.read_text(encoding="utf-8")
        action_refs.extend(
            re.findall(
                r"^\s*uses:\s*astral-sh/setup-uv@([^\s#]+)",
                content,
                re.MULTILINE,
            )
        )
        uv_versions.extend(
            re.findall(
                r"^\s*version:\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)",
                content,
                re.MULTILINE,
            )
        )

    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
    assert uv_versions
    assert len(set(uv_versions)) == 1


def test_dependency_detector_baseline_workflow_is_read_only() -> None:
    """Keep the dependency baseline audit from acquiring unnecessary write access."""
    content = (
        WORKFLOW_ROOT / "dependency-detector-baseline.yml"
    ).read_text(encoding="utf-8")
    match = re.search(
        r"^permissions:\n(?P<body>(?:[ \t]+[^\n]*\n)+)",
        content,
        re.MULTILINE,
    )

    assert match is not None
    assert match.group("body").strip() == "contents: read"
