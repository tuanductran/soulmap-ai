import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCKFILE = REPO_ROOT / "uv.lock"

PYPROJECT = REPO_ROOT / "pyproject.toml"
README = REPO_ROOT / "README.md"
UPLOAD = REPO_ROOT / "docs" / "operations" / "UPLOAD.md"
LIBRARY = REPO_ROOT / "docs" / "operations" / "LIBRARY.md"
KNOWN_LIMITATIONS = REPO_ROOT / "docs" / "engineering" / "known-limitations.md"
ROADMAP = REPO_ROOT / "docs" / "ROADMAP.md"
REPO_CONTRACT = REPO_ROOT / "docs" / "engineering" / "repo-contract.md"


def test_project_version_matches_lockfile() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project_version = project["project"]["version"]
    lock_text = LOCKFILE.read_text(encoding="utf-8")
    match = re.search(
        r'(?ms)^name = "soulmap-ai"$\nversion = "(?P<version>[^"]+)"',
        lock_text,
    )

    assert match is not None
    assert match.group("version") == project_version


def test_python_distribution_is_local_tooling_only() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")

    assert "classifiers = [" in text
    assert '"Private :: Do Not Upload"' in text
    assert 'license = "MIT"' in text
    assert 'license-files = ["LICENSE"]' in text
    assert 'authors = [{ name = "Tuan Duc Tran" }]' in text
    assert "[project.urls]" in text


def test_sdist_excludes_local_only_layers() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    include_block = text.split("[tool.hatch.build.targets.sdist]", 1)[1].split("]", 1)[
        0
    ]

    assert '"/.claude"' not in include_block
    assert '"/.claude-plugin"' not in include_block
    assert '"/.github"' not in include_block


def test_docs_direct_ai_imports_to_custom_artifacts() -> None:
    for path in (README, UPLOAD, LIBRARY, REPO_CONTRACT):
        text = path.read_text(encoding="utf-8")
        assert "dist/soulmap-ai.skill" in text
        assert "dist/soulmap-ai.zip" in text

    readme = README.read_text(encoding="utf-8")
    upload = UPLOAD.read_text(encoding="utf-8")
    assert "local developer/test tooling" in readme
    assert "not standalone" in readme
    assert "soulmap-with-soulmate-ai" in readme
    assert "soulmate-ai" in readme
    assert "uv run soulmap build-composed" in readme
    assert "scripts/build_soulmate_skills.py" in readme
    assert "dist/soulmate-ai/soulmate-ai.skill" in readme
    assert "Python wheel and source distribution are for local development" in upload
    assert "artifacts to import into an AI tool" in upload.replace("\n", " ")
    library = LIBRARY.read_text(encoding="utf-8")
    assert "standalone SoulMap Framework" in library
    assert "not silently added to the standalone Library manifest" in library


def test_active_packaging_truth_surfaces_describe_composition() -> None:
    for path in (README, LIBRARY, KNOWN_LIMITATIONS, ROADMAP, REPO_CONTRACT):
        text = path.read_text(encoding="utf-8")
        assert "soulmap-with-soulmate-ai" in text
        assert "soulmate-ai" in text
        assert "exactly two" not in text.lower()
        assert "two-artifact model" not in text.lower()
