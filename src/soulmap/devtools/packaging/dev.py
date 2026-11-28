"""Build, verify, audit, and watch local SoulMap sources during development.

By default this command stays alive and rebuilds verified artifacts when watched
source files change. Pass ``--once`` for a single build-and-audit cycle.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
import zipfile
from collections.abc import Callable
from pathlib import Path

from soulmap.devtools.packaging import build_skill
from soulmap.devtools.packaging.members import is_safe_member_path, source_members
from soulmap.devtools.support.repo import REPO_ROOT

IGNORED_PARTS = frozenset(
    {
        ".git", ".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache",
        ".hypothesis", "__pycache__", "dist", "build", ".soulmap",
        "node_modules", ".uv-cache", ".cache",
    }
)
WATCH_ROOTS = (
    "skills", "templates", "src", "tests", "evals", "docs", "scripts",
    ".claude", ".claude-plugin", ".github", "schemas",
)
WATCH_FILES = frozenset(
    {
        "AGENTS.md", "SOULMAP.md", "SKILL.md", "README.md", "CONTRIBUTING.md",
        "CHANGELOG.md", "pyproject.toml", "uv.lock", ".distignore", ".gitignore",
        ".pymarkdown.json", "ruff.toml", "pytest.ini",
    }
)
WATCH_SUFFIXES = frozenset(
    {
        ".md", ".markdown", ".py", ".toml", ".json", ".json5", ".jsonl",
        ".yaml", ".yml", ".txt", ".sh", ".bash", ".zsh", ".ini", ".cfg", ".lock",
    }
)


def _is_watched(path: Path, root: Path) -> bool:
    """Return whether a path can affect builds, docs, QA, or repository audits."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if any(part in IGNORED_PARTS for part in relative.parts) or not path.is_file():
        return False
    relative_name = relative.as_posix()
    if relative_name in WATCH_FILES:
        return True
    if relative.parts and relative.parts[0] in WATCH_ROOTS:
        return path.suffix.lower() in WATCH_SUFFIXES or path.name in WATCH_FILES
    return len(relative.parts) == 1 and (
        path.suffix.lower() in WATCH_SUFFIXES or path.name.startswith(".")
    )


def _snapshot(root: Path) -> dict[str, tuple[int, int]]:
    """Capture size and modification time for every watched source file."""
    snapshot: dict[str, tuple[int, int]] = {}
    for path in root.rglob("*"):
        if path.is_symlink() or not _is_watched(path, root):
            continue
        try:
            stat = path.stat()
        except OSError:
            # Editors may replace or delete a file during enumeration.
            continue
        snapshot[path.relative_to(root).as_posix()] = (
            stat.st_mtime_ns,
            stat.st_size,
        )
    return snapshot


def _watch(
    repo_root: Path,
    *,
    interval: float,
    debounce: float,
    run_cycle: Callable[[Path], int],
    snapshot: Callable[[Path], dict[str, tuple[int, int]]] = _snapshot,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> int:
    """Watch source snapshots and rebuild once an edit batch has settled."""
    print("SoulMap dev watcher ready. Press Ctrl+C to stop.")
    print(f"Watching repository sources under {repo_root}")
    previous = snapshot(repo_root)
    try:
        while True:
            sleep(interval)
            current = snapshot(repo_root)
            if current == previous:
                continue
            quiet_since = monotonic()
            while True:
                sleep(interval)
                latest = snapshot(repo_root)
                if latest != current:
                    current = latest
                    quiet_since = monotonic()
                if monotonic() - quiet_since >= debounce:
                    break
            changed = sorted(
                path
                for path in previous.keys() | current.keys()
                if previous.get(path) != current.get(path)
            )
            print("\n" + "-" * 72)
            print("Detected source changes:")
            for path in changed[:30]:
                print(f"  - {path}")
            if len(changed) > 30:
                print(f"  ... and {len(changed) - 30} more")
            try:
                run_cycle(repo_root)
            except Exception as exc:
                print(
                    f"ERROR (dev rebuild): {type(exc).__name__}: {exc}",
                    file=sys.stderr,
                )
                print("Watcher remains active. Fix the source and save again.")
            previous = current
    except KeyboardInterrupt:
        print("\nSoulMap dev watcher stopped.")
        return 0


def _verify_archive(
    archive_path: Path, expected_members: set[str], source_root: Path
) -> None:
    """Reject corrupt, stale, unexpected, or unsafe archive contents."""
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"Archive contains duplicate members: {archive_path}")
        unsafe = [name for name in names if not is_safe_member_path(name)]
        if unsafe:
            raise ValueError(
                f"Archive contains unsafe member paths in {archive_path}: {unsafe[:5]}"
            )
        actual_members = set(names)
        missing = sorted(expected_members - actual_members)
        unexpected = sorted(actual_members - expected_members)
        if missing or unexpected:
            raise ValueError(
                f"Archive member mismatch for {archive_path}: "
                f"missing={missing[:5]}, unexpected={unexpected[:5]}"
            )
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise ValueError(
                f"Archive CRC check failed for {archive_path}: {corrupt_member}"
            )
        stale_members = [
            name
            for name in names
            if archive.read(name) != (source_root / name).read_bytes()
        ]
        if stale_members:
            raise ValueError(
                f"Archive content differs from source for {archive_path}: "
                f"{stale_members[:5]}"
            )


def _extract_verified(archive_path: Path, destination: Path, source_root: Path) -> int:
    """Verify and atomically replace an extracted tree using a staging directory."""
    include_plugin = archive_path.name == "soulmap-ai.skill"
    expected_members = source_members(source_root, include_plugin=include_plugin)
    _verify_archive(archive_path, expected_members, source_root)

    staging = destination.with_name(f"{destination.name}.staging")
    backup = destination.with_name(f"{destination.name}.previous")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(staging)
        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if not destination.exists() and backup.exists():
            backup.replace(destination)
        raise
    print(f"OK (dev extract): {archive_path.name} -> {destination}")
    return len(expected_members)


def _build_and_refresh(repo_root: Path) -> int:
    """Build and verify both distribution archives and extracted trees."""
    archives = build_skill.build_all(repo_root)
    output_root = repo_root / ".soulmap"
    total_files = 0
    for archive_path, output_name in zip(archives, ("zip", "skill"), strict=True):
        total_files += _extract_verified(
            archive_path, output_root / output_name, repo_root
        )
    print(f"OK (dev): {total_files} packaged file entries verified under {output_root}")
    return total_files


def _run_audits(repo_root: Path) -> int:
    """Run existing Python and resource inventories as advisory reports."""
    from scripts.audit_python_reachability import main as python_audit_main
    from scripts.audit_resource_inventory import main as resource_audit_main

    print("\n=== Python module reachability (review candidates only) ===")
    python_status = python_audit_main(["--root", str(repo_root)])
    print("\n=== Knowledge and documentation resource inventory ===")
    resource_status = resource_audit_main(["--root", str(repo_root)])
    if python_status:
        print(f"NOTICE: Python reachability audit exited with status {python_status}")
    if resource_status:
        print(f"NOTICE: Resource inventory exited with status {resource_status}")
    print("No source or documentation files are removed by dev audits.")
    return 0


def _run_cycle(repo_root: Path, *, audit: bool = True) -> int:
    """Run a verified build and optionally report reachability findings."""
    _build_and_refresh(repo_root)
    if audit:
        _run_audits(repo_root)
    return 0




def main(argv: list[str] | None = None) -> int:
    """Run an initial build/audit cycle, then watch until interrupted by default."""
    parser = argparse.ArgumentParser(
        prog="soulmap dev",
        description=(
            "Build and verify artifacts, audit unused-code/resource candidates, and "
            "watch source changes. Use --once for one cycle."
        ),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Build, verify, extract, and audit once without starting a watcher.",
    )
    parser.add_argument(
        "--no-audit", action="store_true",
        help="Skip Python and resource reachability reports.",
    )
    parser.add_argument(
        "--interval", type=float, default=0.5,\n        help="Polling interval in seconds (default: 0.5).",\n    )\n    parser.add_argument(\n        "--debounce", type=float, default=0.8,
        help="Quiet period after the last file change before rebuilding (default: 0.8s).",
    )
    args = parser.parse_args(argv)
    if args.interval <= 0 or args.debounce < 0:
        parser.error("--interval must be positive and --debounce cannot be negative")

    repo_root = REPO_ROOT
    _run_cycle(repo_root, audit=not args.no_audit)
    if args.once:
        return 0
    return _watch(
        repo_root,
        interval=args.interval,
        debounce=args.debounce,
        run_cycle=lambda root: _run_cycle(root, audit=not args.no_audit),
    )


if __name__ == "__main__":
    raise SystemExit(main())
