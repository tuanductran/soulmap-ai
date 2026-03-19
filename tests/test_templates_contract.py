"""Contract checks for required template files and headings."""

from pathlib import Path


def _strip_leading_metadata(content: str) -> str:
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return stripped
    # Strip YAML front matter (--- ... ---) only.
    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return stripped
    end_idx = None
    for i in range(1, min(len(lines), 80)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return stripped
    return "\n".join(lines[end_idx + 1 :]).lstrip()


def test_templates_are_present_and_non_empty() -> None:
    template_dir = Path("templates")
    template_files = sorted(template_dir.glob("*.md"))

    assert template_files, "Expected template markdown files."

    for path in template_files:
        content = _strip_leading_metadata(path.read_text(encoding="utf-8")).strip()
        assert content, f"{path} is empty."
        error_message = f"{path} should start with a top-level heading."
        assert content.startswith("# "), error_message


def test_core_template_topics_are_covered() -> None:
    expected_topics = {
        "templates/brand-copy.md": "SoulMap AI",
        "templates/demo-scenarios.md": "Demo Scenarios",
        "templates/faq.md": "What is SoulMap AI?",
        "templates/onboarding-copy.md": "Onboarding Copy",
        "templates/quick-reference.md": "Situation",
        "templates/redirect-templates.md": "Redirect",
        "templates/response-structure.md": "Five-Step",
    }

    for raw_path, phrase in expected_topics.items():
        path = Path(raw_path)
        content = path.read_text(encoding="utf-8")
        assert phrase in content, f"{raw_path} is missing expected phrase: {phrase}"
