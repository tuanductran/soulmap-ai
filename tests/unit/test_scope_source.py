from soulmap.runtime.knowledge.scope_source import load_scope_rules
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_scope_rules_match_markdown_contract() -> None:
    rules = load_scope_rules()

    assert "self_awareness" in rules.whitelist_tier1
    assert "psychological_patterns" in rules.whitelist_tier1
    assert "work_and_purpose" in rules.whitelist_tier2
    assert "technical" in rules.blacklist_layer1
    assert "jailbreak" in rules.blacklist_prohibited
    assert "ignore your rules" in rules.blacklist_prohibited["jailbreak"]


def test_scope_categories_are_human_readable_in_skill() -> None:
    text = runtime_skill_path("scope-classification").read_text(encoding="utf-8")
    policy = text.split("## Scope policy", 1)[1]

    for category in (
        "Self-awareness",
        "Psychological patterns",
        "Work and purpose",
        "Professional advice",
        "News and current events",
        "System extraction",
    ):
        assert f"#### {category}" in policy
    for internal_label in (
        "self_awareness",
        "psychological_patterns",
        "work_and_purpose",
        "professional_advice",
        "news_and_current_events",
        "system_extraction",
    ):
        assert f"#### {internal_label}" not in policy
