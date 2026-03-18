"""Contract checks for required template files and headings."""

from pathlib import Path


def test_templates_are_present_and_non_empty() -> None:
    template_dir = Path("templates")
    template_files = sorted(template_dir.glob("*.md"))

    assert template_files, "Expected template markdown files."

    for path in template_files:
        content = path.read_text(encoding="utf-8").strip()
        assert content, f"{path} is empty."
        error_message = f"{path} should start with a top-level heading."
        assert content.startswith("# "), error_message


def test_core_template_topics_are_covered() -> None:
    expected_topics = {
        "templates/brand_copy.md": "SoulMap AI",
        "templates/demo_scenarios.md": "Demo Scenarios",
        "templates/faq.md": "What is SoulMap AI?",
        "templates/onboarding_copy.md": "Onboarding Copy",
        "templates/quick_reference.md": "Situation",
        "templates/redirect_templates.md": "Redirect",
        "templates/response_structure.md": "Five-Step",
    }

    for raw_path, phrase in expected_topics.items():
        path = Path(raw_path)
        content = path.read_text(encoding="utf-8")
        assert phrase in content, f"{raw_path} is missing expected phrase: {phrase}"
