"""Build the isolated Soulmate package from the monorepo source boundary."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "packages" / "soulmate"
SOURCE_ROOT = REPO_ROOT / "src" / "soulmate"
DEFAULT_STAGE = REPO_ROOT / "dist" / ".soulmate-build"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "soulmate"


class SoulmateBuildError(RuntimeError):
    """Raised when the isolated Soulmate package cannot be staged."""


def package_version() -> str:
    """Read the package version from the Soulmate package manifest."""

    with (PACKAGE_ROOT / "pyproject.toml").open("rb") as handle:
        metadata = tomllib.load(handle)
    version = metadata.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise SoulmateBuildError("Soulmate package manifest has no valid version")
    return version


def _copy_required_file(name: str, destination: Path) -> None:
    source = PACKAGE_ROOT / name
    if not source.is_file():
        raise SoulmateBuildError(f"Missing Soulmate package file: {source}")
    shutil.copy2(source, destination / name)


def stage_package(stage_dir: Path) -> Path:
    """Create a clean, explicitly allow-listed build directory."""

    if not SOURCE_ROOT.is_dir():
        raise SoulmateBuildError(f"Missing Soulmate source directory: {SOURCE_ROOT}")

    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)

    _copy_required_file("pyproject.toml", stage_dir)
    _copy_required_file("README.md", stage_dir)
    _copy_required_file("LICENSE", stage_dir)
    shutil.copytree(SOURCE_ROOT, stage_dir / "src" / "soulmate")
    return stage_dir


def build_package(stage_dir: Path, output_dir: Path) -> tuple[Path, Path]:
    """Build wheel and sdist from the isolated staging directory."""

    stage_package(stage_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    uv = shutil.which("uv")
    if uv is None:
        raise SoulmateBuildError("uv is required to build the Soulmate package")

    subprocess.run(
        [
            uv,
            "build",
            "--directory",
            str(stage_dir),
            "--out-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    version = package_version()
    wheel = output_dir / f"soulmate_ai-{version}-py3-none-any.whl"
    sdist = output_dir / f"soulmate_ai-{version}.tar.gz"
    if not wheel.is_file() or not sdist.is_file():
        raise SoulmateBuildError(
            f"Expected Soulmate artifacts were not created in {output_dir}"
        )
    return wheel, sdist


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the isolated Soulmate wheel and source distribution."
    )
    parser.add_argument("--stage-dir", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args(argv)

    if args.print_version:
        print(package_version())
        return 0

    wheel, sdist = build_package(args.stage_dir.resolve(), args.output_dir.resolve())
    print(f"OK (wheel): {wheel}")
    print(f"OK (sdist): {sdist}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SoulmateBuildError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
