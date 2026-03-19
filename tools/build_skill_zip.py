from __future__ import annotations

import fnmatch
from pathlib import Path
import zipfile

from tools._repo import REPO_ROOT


def _load_distignore(repo_root: Path) -> list[str]:
    distignore = repo_root / ".distignore"
    if not distignore.is_file():
        return []
    patterns: list[str] = []
    for raw in distignore.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _is_ignored(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)


def _iter_zip_inputs(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for name in ["LICENSE"]:
        candidate = repo_root / name
        if candidate.is_file():
            paths.append(candidate)

    claude_plugin = repo_root / ".claude-plugin" / "marketplace.json"
    if claude_plugin.is_file():
        paths.append(claude_plugin)

    for folder in ["skills", "templates"]:
        base = repo_root / folder
        for path in base.rglob("*"):
            if path.is_file():
                paths.append(path)
    return sorted(set(paths))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    repo_root = REPO_ROOT

    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_zip = out_dir / "soulmap-ai.zip"

    patterns = _load_distignore(repo_root)
    inputs = _iter_zip_inputs(repo_root)

    if out_zip.exists():
        out_zip.unlink()

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            rel = path.relative_to(repo_root).as_posix()
            if _is_ignored(rel, patterns):
                continue
            archive.write(path, arcname=rel)

    print(f"OK: {out_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
