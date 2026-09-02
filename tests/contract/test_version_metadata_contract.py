"""Every shipped skill and marketplace plugin declares the package version.

A consumer who installs a skill or a plugin has no other way to tell which
release of SoulMap the content belongs to. `cz bump` keeps the declarations in
step through `version_files` in `pyproject.toml`, and this contract is what
makes a missed entry fail rather than drift quietly: a new skill directory
whose `SKILL.md` has no `version`, or a bump that reaches `pyproject.toml`
while leaving a plugin behind.

Versions move in lockstep with the package on purpose. A skill is not
independently released, so an independent version would imply a guarantee the
release process does not make.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

_FRONTMATTER_VERSION_RE = re.compile(r'^version:\s*"([^"]+)"\s*$', re.MULTILINE)


def _package_version() -> str:
    """Return the single source of truth for the release version."""
    with PYPROJECT.open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def _skill_manifests() -> list[Path]:
    """Return the root manifest plus every shipped skill's manifest."""
    return [REPO_ROOT / "SKILL.md", *sorted(REPO_ROOT.glob("skills/*/SKILL.md"))]


def _declared_version(manifest: Path) -> str | None:
    """Return the version declared in a manifest's front matter, if any."""
    text = manifest.read_text(encoding="utf-8")
    header = text.split("---", 2)[1] if text.startswith("---") else ""
    match = _FRONTMATTER_VERSION_RE.search(header)
    return match.group(1) if match else None


def test_the_manifest_discovery_is_not_silently_matching_nothing() -> None:
    """A glob returning nothing would make every assertion below vacuous."""
    manifests = _skill_manifests()

    assert len(manifests) >= 8, f"expected root plus 7 skills, found {len(manifests)}"
    for manifest in manifests:
        assert manifest.is_file(), manifest


def test_every_skill_manifest_declares_the_package_version() -> None:
    """A skill claiming no version, or an older one, misinforms its consumer."""
    expected = _package_version()

    mismatched = {
        str(manifest.relative_to(REPO_ROOT)): _declared_version(manifest)
        for manifest in _skill_manifests()
        if _declared_version(manifest) != expected
    }

    assert not mismatched, (
        f"skill manifests out of step with pyproject ({expected}): {mismatched}. "
        f"`cz bump` should carry these; check the version_files globs."
    )


def test_the_marketplace_and_every_plugin_declare_the_package_version() -> None:
    """The marketplace and its plugins are versioned by the same release."""
    expected = _package_version()
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

    assert data.get("version") == expected, (
        f"marketplace version {data.get('version')!r} != pyproject {expected!r}"
    )

    plugins = data["plugins"]
    assert len(plugins) >= 7, f"expected the full plugin set, found {len(plugins)}"

    mismatched = {
        plugin.get("name", "<unnamed>"): plugin.get("version")
        for plugin in plugins
        if plugin.get("version") != expected
    }
    assert not mismatched, (
        f"plugins out of step with pyproject ({expected}): {mismatched}"
    )


def test_every_shipped_skill_directory_has_a_versioned_manifest() -> None:
    """A new skill directory must not ship without a manifest to version.

    Without this, adding `skills/newthing/` with content but no `SKILL.md`
    would leave it unversioned and unnoticed, since the checks above only
    look at manifests that already exist.
    """
    directories = sorted(
        path for path in (REPO_ROOT / "skills").iterdir() if path.is_dir()
    )

    assert directories, "no skill directories found, check the path"
    missing = [
        str(directory.relative_to(REPO_ROOT))
        for directory in directories
        if not (directory / "SKILL.md").is_file()
    ]
    assert not missing, f"skill directories without a SKILL.md manifest: {missing}"
