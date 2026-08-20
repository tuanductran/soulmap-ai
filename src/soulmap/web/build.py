"""Deterministic helpers for reusable SoulMap website static builds."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

MANIFEST_VERSION = 1
EXPORTER_VERSION = "1"
MANIFEST_FILENAME = "manifest.json"


@dataclass(frozen=True)
class BuildKey:
    """Inputs that must match before a previous static output can be reused."""

    fingerprint: str
    base_path: str
    exporter_version: str = EXPORTER_VERSION

    def as_dict(self) -> dict[str, str]:
        return {
            "fingerprint": self.fingerprint,
            "base_path": self.base_path,
            "exporter_version": self.exporter_version,
        }


def repository_root() -> Path:
    """Return the source checkout root when running from a checkout."""
    module_root = Path(__file__).resolve().parents[3]
    if (module_root / "src" / "soulmap").is_dir():
        return module_root
    return Path.cwd().resolve()


def _iter_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def build_inputs(root: Path | None = None) -> tuple[Path, ...]:
    """Return source files that can change a public static export."""
    checkout = (root or repository_root()).resolve()
    candidates = [
        *_iter_files(checkout / "src" / "soulmap" / "web"),
        *_iter_files(checkout / "skills"),
    ]
    for filename in ("pyproject.toml", "uv.lock"):
        path = checkout / filename
        if path.is_file():
            candidates.append(path)
    return tuple(sorted(set(candidates)))


def source_fingerprint(
    root: Path | None = None, inputs: tuple[Path, ...] | None = None
) -> str:
    """Hash source paths and bytes so build reuse is content-addressed."""
    checkout = (root or repository_root()).resolve()
    hasher = sha256()
    for path in inputs or build_inputs(checkout):
        relative = path.resolve().relative_to(checkout).as_posix()
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def build_key(base_path: str, root: Path | None = None) -> BuildKey:
    """Create the deterministic key for a public export."""
    return BuildKey(source_fingerprint(root), base_path)


def _manifest_path(cache_dir: Path) -> Path:
    return cache_dir / MANIFEST_FILENAME


def load_reusable_output(
    cache_dir: Path, output: Path, key: BuildKey
) -> list[Path] | None:
    """Return prior output files when manifest, key and files all match."""
    manifest_path = _manifest_path(cache_dir)
    if not manifest_path.is_file() or not output.is_dir():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return None
    if (
        manifest.get("version") != MANIFEST_VERSION
        or manifest.get("key") != key.as_dict()
    ):
        return None
    relative_files = manifest.get("files")
    if not isinstance(relative_files, list) or not relative_files:
        return None
    output_root = output.resolve()
    paths: list[Path] = []
    for relative in relative_files:
        if not isinstance(relative, str):
            return None
        path = (output_root / relative).resolve()
        if output_root not in path.parents or not path.is_file():
            return None
        paths.append(path)
    return paths


def write_manifest(
    cache_dir: Path, output: Path, key: BuildKey, files: list[Path]
) -> None:
    """Atomically persist a successful export manifest outside the public site."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    relative_files = sorted(
        path.resolve().relative_to(output.resolve()).as_posix() for path in files
    )
    payload = {
        "version": MANIFEST_VERSION,
        "key": key.as_dict(),
        "files": relative_files,
    }
    target = _manifest_path(cache_dir)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(target)
