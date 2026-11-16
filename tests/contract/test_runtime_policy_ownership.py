"""Protect the boundary between semantic Markdown and Python runtime policy."""

import re
from pathlib import Path

from soulmap.runtime.knowledge.runtime_config import FRAMEWORK_TEMPLATE_ROWS

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_skill(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_detector_markdown_does_not_duplicate_numeric_policy_tables() -> None:
    """Keep executable detector weights and thresholds in Python configuration."""
    detector_sources = (
        "skills/frameworks/anger-companion.md",
        "skills/frameworks/ancestral-patterns.md",
        "skills/frameworks/creative-drought.md",
        "skills/frameworks/dark-night-of-soul.md",
        "skills/frameworks/divine-guidance.md",
        "skills/frameworks/emotional-deescalation.md",
        "skills/frameworks/empath-boundary.md",
        "skills/frameworks/existential-companion.md",
        "skills/frameworks/fear-of-visibility.md",
        "skills/frameworks/grief-companion.md",
        "skills/frameworks/inner-parts.md",
        "skills/frameworks/meaning-integration.md",
        "skills/frameworks/perfectionism-paralysis.md",
        "skills/soulmate/partnership-patterns.md",
        "skills/frameworks/pattern-mapper.md",
        "skills/frameworks/sacred-feminine-masculine.md",
        "skills/frameworks/shadow-patterns.md",
        "skills/frameworks/somatic-wellbeing.md",
        "skills/soulmate/soulmate-longing.md",
        "skills/frameworks/soul-nourishment.md",
        "skills/spiritual/spiritual-discernment.md",
        "skills/frameworks/spiritual-purpose.md",
        "skills/frameworks/life-direction.md",
        "skills/frameworks/conversation-synthesis.md",
    )
    numeric_policy_row = re.compile(r"^\|\s*[^|]+\s*\|\s*\d+\s*\|\s*$", re.MULTILINE)

    for relative_path in detector_sources:
        content = _read_skill(relative_path)
        assert numeric_policy_row.search(content) is None, (
            f"{relative_path} duplicates a Python-owned numeric policy table"
        )


def test_acute_grief_question_timing_is_python_owned_and_readiness_gated() -> None:
    """Keep the acute-grief timing policy executable and qualitative in Markdown."""
    rule = next(row for row in FRAMEWORK_TEMPLATE_ROWS if row[0] == "Grief (acute)")
    assert "initial acute-grief period" in rule[3].lower()
    assert "readiness" in rule[3].lower()

    documentation = (
        "skills/frameworks/grief-companion.md",
        "skills/voice/response-calibrator.md",
        "skills/meta/deep-inquiry-bank.md",
        "skills/meta/master-prompt.md",
        "skills/meta/framework-template-map.md",
    )
    for relative_path in documentation:
        content = _read_skill(relative_path).lower()
        assert "first 2-3 exchanges" not in content, (
            f"{relative_path} duplicates a fixed exchange-count window"
        )
        assert "initial acute-grief period" in content
        assert "readiness" in content


def test_stage_and_orchestration_markdown_do_not_duplicate_numeric_thresholds() -> None:
    """Keep stage and routing thresholds in Python, not portable guidance."""
    checks = {
        "skills/meta/stage-classifier.md": (
            r"most recent\s+\d+\s+user messages",
            r"within\s+\d+\s+points",
            r"session count.{0,40}\d+",
            r"first session.{0,100}(?:default|maximum|higher than)\s+stage\s+\d+",
        ),
        "skills/meta/orchestration.md": (
            r"default to stage\s+1",
            r"dependency score\s*>=\s*\d+",
            r"repeat signals across\s+\d+\+\s+stories",
            r"stage\s+\d+ or above",
        ),
    }
    for relative_path, patterns in checks.items():
        content = _read_skill(relative_path)
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE) is None, (
                f"{relative_path} duplicates Python-owned runtime policy: {pattern}"
            )
