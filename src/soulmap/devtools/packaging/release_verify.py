"""Verify release artifacts and cross-platform integration contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any

from soulmap.devtools.packaging.library import build_library
from soulmap.devtools.support.repo import REPO_ROOT

INTEGRATION_GUIDES = (
    Path("docs/integrations/README.md"),
    Path("docs/integrations/chatgpt-instructions.md"),
    Path("docs/integrations/gemini-instructions.md"),
    Path("docs/integrations/poe-system-prompt.md"),
)
CORE_FILES = {"LICENSE", "SOULMAP.md", "SKILL.md"}
PLUGIN_PREFIX = ".claude-plugin/"


class ReleaseVerificationError(ValueError):
    """Raised when a release contract is violated."""


def _project_version(repo_root: Path) -> str:
    with (repo_root / "pyproject.toml").open("rb") as handle:
        payload = tomllib.load(handle)
    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise ReleaseVerificationError("pyproject.toml must define project.version")
    return version


def _front_matter(content: str, path: Path) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    if match is None:
        raise ReleaseVerificationError(f"{path}: missing YAML front matter")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            continue
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _verify_integrations(repo_root: Path, version: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for relative_path in INTEGRATION_GUIDES:
        path = repo_root / relative_path
        if not path.is_file():
            raise ReleaseVerificationError(f"integration guide is missing: {relative_path}")
        front_matter = _front_matter(path.read_text(encoding="utf-8"), relative_path)
        if front_matter.get("doctrine_source") != "SOULMAP.md":
            actual = front_matter.get("doctrine_source", "<missing>")
            raise ReleaseVerificationError(
                f"{relative_path}: doctrine_source must be SOULMAP.md, got {actual}"
            )
        if front_matter.get("soulmap_version") != version:
            actual = front_matter.get("soulmap_version", "<missing>")
            raise ReleaseVerificationError(
                f"{relative_path}: soulmap_version must be {version}, got {actual}"
            )
        results.append(
            {
                "path": relative_path.as_posix(),
                "doctrine_source": "SOULMAP.md",
                "soulmap_version": version,
            }
        )
    return results


def _version_markers(repo_root: Path) -> list[Path]:
    paths = [repo_root / "SKILL.md"]
    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        paths.extend(sorted(skills_root.glob("*/SKILL.md")))
    return paths


def _verify_version_markers(repo_root: Path, version: str) -> list[str]:
    checked: list[str] = []
    for path in _version_markers(repo_root):
        if not path.is_file():
            raise ReleaseVerificationError(f"version marker is missing: {path.relative_to(repo_root)}")
        front_matter = _front_matter(path.read_text(encoding="utf-8"), path.relative_to(repo_root))
        actual = front_matter.get("version")
        if actual != version:
            raise ReleaseVerificationError(
                f"{path.relative_to(repo_root)}: version must be {version}, got {actual or '<missing>'}"
            )
        checked.append(path.relative_to(repo_root).as_posix())

    marketplace = repo_root / ".claude-plugin" / "marketplace.json"
    if not marketplace.is_file():
        raise ReleaseVerificationError(f"version marker is missing: {marketplace.relative_to(repo_root)}")
    payload = json.loads(marketplace.read_text(encoding="utf-8"))
    if payload.get("version") != version:
        raise ReleaseVerificationError(
            f".claude-plugin/marketplace.json: version must be {version}, got {payload.get('version', '<missing>')}"
        )
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        raise ReleaseVerificationError(".claude-plugin/marketplace.json: plugins must be a list")
    for plugin in plugins:
        if not isinstance(plugin, dict) or plugin.get("version") != version:
            raise ReleaseVerificationError(
                ".claude-plugin/marketplace.json: every plugin version must match "
                f"{version}"
            )
    checked.append(marketplace.relative_to(repo_root).as_posix())
    return checked


def _source_members(repo_root: Path, *, include_plugin: bool) -> set[str]:
    paths: set[Path] = set()
    for name in CORE_FILES:
        path = repo_root / name
        if path.is_file():
            paths.add(path)
    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        paths.update(path for path in skills_root.rglob("*") if path.is_file())
    if include_plugin:
        plugin_root = repo_root / ".claude-plugin"
        if plugin_root.is_dir():
            paths.update(path for path in plugin_root.rglob("*") if path.is_file())
    return {path.relative_to(repo_root).as_posix() for path in paths}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_archive(
    repo_root: Path, path: Path, *, include_plugin: bool
) -> dict[str, Any]:
    if not path.is_file():
        raise ReleaseVerificationError(f"artifact is missing: {path.relative_to(repo_root)}")
    try:
        with zipfile.ZipFile(path) as archive:
            actual = set(archive.namelist())
            if any(name.startswith("/") or ".." in Path(name).parts for name in actual):
                raise ReleaseVerificationError(f"{path.name}: unsafe archive member path")
            expected = _source_members(repo_root, include_plugin=include_plugin)
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            if missing:
                raise ReleaseVerificationError(
                    f"{path.name}: missing shipped members: {missing}"
                )
            if unexpected:
                raise ReleaseVerificationError(
                    f"{path.name}: unexpected members: {unexpected}"
                )
            if not actual >= CORE_FILES:
                raise ReleaseVerificationError(
                    f"{path.name}: missing one or more core files: {sorted(CORE_FILES)}"
                )
            has_plugin = any(name.startswith(PLUGIN_PREFIX) for name in actual)
            if has_plugin != include_plugin:
                expectation = "include" if include_plugin else "exclude"
                raise ReleaseVerificationError(
                    f"{path.name}: must {expectation} .claude-plugin/"
                )
    except zipfile.BadZipFile as exc:
        raise ReleaseVerificationError(f"{path.name}: invalid ZIP archive") from exc

    return {
        "filename": path.name,
        "path": path.relative_to(repo_root).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def verify_release(repo_root: Path) -> dict[str, Any]:
    """Build and verify release artifacts and integration contracts."""
    version = _project_version(repo_root)
    integrations = _verify_integrations(repo_root, version)
    version_markers = _verify_version_markers(repo_root, version)

    dist = repo_root / "dist"
    for filename in (
        "soulmap-ai.zip",
        "soulmap-ai.skill",
        "soulmap-ai-library.json",
        "release-verification.json",
    ):
        path = dist / filename
        if path.exists():
            path.unlink()

    manifest_path = build_library(repo_root)
    zip_path = dist / "soulmap-ai.zip"
    skill_path = dist / "soulmap-ai.skill"
    artifacts = [
        _verify_archive(repo_root, zip_path, include_plugin=False),
        _verify_archive(repo_root, skill_path, include_plugin=True),
    ]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != version:
        raise ReleaseVerificationError(
            f"library manifest version must be {version}, got {manifest.get('version')}"
        )
    manifest_artifacts = manifest.get("artifacts")
    if not isinstance(manifest_artifacts, list):
        raise ReleaseVerificationError("library manifest must contain artifacts")
    for artifact in artifacts:
        matching = next(
            (entry for entry in manifest_artifacts if entry.get("filename") == artifact["filename"]),
            None,
        )
        if matching is None:
            raise ReleaseVerificationError(
                f"library manifest is missing {artifact['filename']}"
            )
        if matching.get("size_bytes") != artifact["size_bytes"]:
            raise ReleaseVerificationError(
                f"library manifest size drift for {artifact['filename']}"
            )
        if matching.get("sha256") != artifact["sha256"]:
            raise ReleaseVerificationError(
                f"library manifest SHA-256 drift for {artifact['filename']}"
            )

    return {
        "status": "pass",
        "version": version,
        "doctrine_source": "SOULMAP.md",
        "version_markers": version_markers,
        "integrations": integrations,
        "artifacts": artifacts,
        "manifest": manifest_path.relative_to(repo_root).as_posix(),
    }


def main(argv: list[str] | None = None) -> int:
    """Run release verification and write a machine-readable summary."""
    parser = argparse.ArgumentParser(
        description="Build and verify SoulMap release artifacts and integration contracts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: project root)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON summary path (default: dist/release-verification.json)",
    )
    args = parser.parse_args(argv)
    repo_root = args.root.resolve()
    output = (args.output or repo_root / "dist" / "release-verification.json").resolve()

    try:
        summary = verify_release(repo_root)
    except (OSError, ReleaseVerificationError, json.JSONDecodeError) as exc:
        failure = {"status": "fail", "error": str(exc)}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2), file=sys.stderr)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
