from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from soulmap.devtools.packaging import build_skill

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "verify_extracted_artifacts.py"
)


def _write(root: Path, relative_path: str, content: str = "content\n") -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def _build_valid_repo(root: Path) -> None:
    for name in ("LICENSE", "SOULMAP.md", "SKILL.md"):
        _write(root, name)
    _write(root, "skills/public.md")
    _write(root, ".claude-plugin/marketplace.json", "{}\n")
    build_skill.build_zip(root)
    build_skill.build_skill(root)


def test_verifier_accepts_both_valid_artifacts(tmp_path: Path) -> None:
    _build_valid_repo(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 0
    assert "PASS extracted artifact boundary: dist/soulmap-ai.zip" in result.stdout
    assert "PASS extracted artifact boundary: dist/soulmap-ai.skill" in result.stdout
    assert result.stderr == ""


def test_verifier_rejects_missing_artifact(tmp_path: Path) -> None:
    _build_valid_repo(tmp_path)
    (tmp_path / "dist" / "soulmap-ai.skill").unlink()

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "artifact not found" in result.stderr


def test_verifier_rejects_internal_reference_in_shipped_skill(tmp_path: Path) -> None:
    _build_valid_repo(tmp_path)
    _write(
        tmp_path,
        "skills/public.md",
        "This must not mention src/soulmap/runtime internals.\n",
    )
    build_skill.build_zip(tmp_path)
    build_skill.build_skill(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "forbidden shipped references" in result.stderr
