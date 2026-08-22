from pathlib import Path

import pytest

from soulmap.runtime.knowledge import pattern_source
from soulmap.runtime.knowledge.keyword_lists import default_skill_path
from soulmap.runtime.knowledge.pattern_source import (
    default_pattern_mapper_path,
    parse_pattern_mapper,
)


def test_default_skill_path_prefers_existing_environment_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    expected = tmp_path / "skills" / "custom.md"
    expected.parent.mkdir(parents=True)
    expected.write_text("# custom\n", encoding="utf-8")
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(tmp_path))

    assert default_skill_path("skills/custom.md") == expected


def test_default_skill_path_raises_for_missing_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match=r"Could not locate missing\.md"):
        default_skill_path("missing.md")


def test_pattern_mapper_path_prefers_existing_environment_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    expected = tmp_path / "skills" / "frameworks" / "pattern-mapper.md"
    expected.parent.mkdir(parents=True)
    expected.write_text("# patterns\n", encoding="utf-8")
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(tmp_path))

    assert default_pattern_mapper_path() == expected


def test_pattern_mapper_path_raises_when_no_checkout_is_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        pattern_source,
        "_RELATIVE_MARKDOWN_PATH",
        Path("skills/frameworks/does-not-exist.md"),
    )

    with pytest.raises(FileNotFoundError, match="Could not locate skills/frameworks"):
        default_pattern_mapper_path()


def test_pattern_parser_handles_wrapped_quotes_and_unquoted_cycle_fallback() -> None:
    text = """## Pattern 1: Avoidance Loop
**What it looks like:** I keep delaying the same decision.
**Detection signals:**
- \"a wrapped detection
  phrase\"
**Cycle phrases:**
- circling the same question
**Reflection language:**
- \"I can name the loop\"
**SoulMap role:** Mirror the repeated choice.

## Pattern 2: Clear Loop
**What it looks like:** A second pattern body.
**Detection signals:**
- \"another signal\"
**Cycle phrases:**
- \"another quoted phrase\"
"""

    signals = parse_pattern_mapper(text)

    assert set(signals) == {"avoidance_loop", "clear_loop"}
    assert signals["avoidance_loop"].keywords == ("a wrapped detection phrase",)
    assert signals["avoidance_loop"].cycle_phrases == ("circling the same question",)
    assert signals["avoidance_loop"].reflection_language == ("I can name the loop",)
    assert signals["clear_loop"].cycle_phrases == ("another quoted phrase",)
    assert signals["clear_loop"].description == "A second pattern body."


def test_pattern_parser_ignores_text_before_first_pattern_heading() -> None:
    signals = parse_pattern_mapper("intro\n**Detection signals:**\n- ignored\n")

    assert signals == {}
