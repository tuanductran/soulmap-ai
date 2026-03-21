"""Contract checks for the local `.codex/` helper layer."""

from pathlib import Path


def test_codex_readme_preserves_agents_precedence() -> None:
    content = Path(".codex/README.md").read_text(encoding="utf-8")

    for phrase in [
        "`AGENTS.md`",
        "supplemental local layer",
        "Do not assume every editor or AI tool will automatically prioritize `.codex/`.",
    ]:
        assert phrase in content


def test_repo_docs_acknowledge_codex_as_optional_local_layer() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    contract = Path("docs/repo-contract.md").read_text(encoding="utf-8")

    assert ".codex/" in readme
    assert ".codex/" in contract
    assert "subordinate to `AGENTS.md`" in contract


def test_codex_source_character_rule_exists() -> None:
    assert Path(".codex/rules/source-character-safety.md").is_file()
