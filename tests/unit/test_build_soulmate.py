from pathlib import Path

from scripts.build_soulmate import DEFAULT_STAGE, REPO_ROOT, stage_package


def test_default_soulmate_stage_is_outside_repository() -> None:
    assert REPO_ROOT not in DEFAULT_STAGE.parents


def test_stage_package_uses_only_explicit_package_inputs(tmp_path: Path) -> None:
    stage_dir = tmp_path / "stage"

    stage_package(stage_dir)

    assert (stage_dir / "pyproject.toml").is_file()
    assert (stage_dir / "README.md").is_file()
    assert (stage_dir / "LICENSE").is_file()
    assert (stage_dir / "src" / "soulmate" / "__init__.py").is_file()
    assert not (stage_dir / ".gitignore").exists()
    assert not (stage_dir / "src" / "soulmap").exists()
