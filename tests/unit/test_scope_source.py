from soulmap.runtime.knowledge.scope_source import load_scope_rules


def test_scope_rules_match_markdown_contract() -> None:
    rules = load_scope_rules()

    assert "self_awareness" in rules.whitelist_tier1
    assert "psychological_patterns" in rules.whitelist_tier1
    assert "work_and_purpose" in rules.whitelist_tier2
    assert "technical" in rules.blacklist_layer1
    assert "jailbreak" in rules.blacklist_prohibited
    assert "ignore your rules" in rules.blacklist_prohibited["jailbreak"]
