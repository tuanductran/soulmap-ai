from __future__ import annotations

from pathlib import Path

import pytest

from soulmap.devtools.checks import check_api_docs

_SELECTOR_RELATIVE_PATH = Path("src/soulmap/runtime/routing/framework_selector.py")
_DOC_RELATIVE_PATH = Path("docs/engineering/API.md")

_MATCHING_SELECTOR_SOURCE = """
def _simple_selection(framework, detector_result):
    return {
        "primary_framework": framework,
        "secondary_layer": None,
    }


async def select_framework_async(message, history, memory=None):
    if crisis_tier == 1:
        selection = {
            "primary_framework": "CRISIS",
            "secondary_layer": None,
        }
        return selection

    if res["shadow"].get("shadow_detected"):
        selection = _simple_selection("SHADOW", res["shadow"])
        return selection


if __name__ == "__main__":
    pass
"""


def _write_selector(repo_root: Path, source: str) -> None:
    path = repo_root / _SELECTOR_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def _write_doc(repo_root: Path, enum_values: str, extra_body: str = "") -> None:
    path = repo_root / _DOC_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# API Docs\n\n"
        "```bash\n"
        "python -m soulmap.runtime.routing.framework_selector\n"
        "```\n\n"
        "```json\n"
        f'{{"primary_framework": "{enum_values}"}}\n'
        "```\n"
        f"{extra_body}",
        encoding="utf-8",
    )


def test_matching_doc_and_source_have_no_issues(tmp_path: Path) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    _write_doc(tmp_path, "CRISIS|SHADOW")

    assert check_api_docs.check_repo(tmp_path) == []


def test_missing_api_doc_is_flagged(tmp_path: Path) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)

    issues = check_api_docs.check_repo(tmp_path)

    assert len(issues) == 1
    assert issues[0].path == _DOC_RELATIVE_PATH
    assert "does not exist" in issues[0].message


def test_stale_module_reference_is_flagged(tmp_path: Path) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    doc_path = tmp_path / _DOC_RELATIVE_PATH
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "# API Docs\n\n"
        "```bash\n"
        "python -m soulmap.runtime.routing.renamed_selector\n"
        "```\n\n"
        "```json\n"
        '{"primary_framework": "CRISIS|SHADOW"}\n'
        "```\n",
        encoding="utf-8",
    )

    issues = check_api_docs.check_repo(tmp_path)

    assert any("renamed_selector" in issue.message for issue in issues)
    assert any("does not exist" in issue.message for issue in issues)


def test_module_without_main_block_is_flagged(tmp_path: Path) -> None:
    _write_selector(
        tmp_path,
        _MATCHING_SELECTOR_SOURCE.replace('if __name__ == "__main__":\n    pass\n', ""),
    )
    _write_doc(tmp_path, "CRISIS|SHADOW")

    issues = check_api_docs.check_repo(tmp_path)

    assert any("no longer has" in issue.message for issue in issues)


def test_new_framework_missing_from_documented_enum_is_flagged(tmp_path: Path) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    _write_doc(tmp_path, "CRISIS")

    issues = check_api_docs.check_repo(tmp_path)

    assert any(
        "SHADOW" in issue.message and "not listed" in issue.message for issue in issues
    )


def test_removed_framework_still_documented_is_flagged(tmp_path: Path) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    _write_doc(tmp_path, "CRISIS|SHADOW|GHOST_FRAMEWORK")

    issues = check_api_docs.check_repo(tmp_path)

    assert any(
        "GHOST_FRAMEWORK" in issue.message and "no longer emits" in issue.message
        for issue in issues
    )


def test_detector_module_references_outside_soulmap_are_ignored(
    tmp_path: Path,
) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    doc_path = tmp_path / _DOC_RELATIVE_PATH
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "# API Docs\n\n"
        "```bash\n"
        "python -m soulmap.runtime.routing.framework_selector\n"
        "python -m pytest\n"
        "```\n\n"
        "```json\n"
        '{"primary_framework": "CRISIS|SHADOW"}\n'
        "```\n",
        encoding="utf-8",
    )

    assert check_api_docs.check_repo(tmp_path) == []


def test_main_returns_zero_when_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    _write_doc(tmp_path, "CRISIS|SHADOW")

    exit_code = check_api_docs.main(["--root", str(tmp_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_main_returns_one_and_prints_issues_when_drifted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_selector(tmp_path, _MATCHING_SELECTOR_SOURCE)
    _write_doc(tmp_path, "CRISIS")

    exit_code = check_api_docs.main(["--root", str(tmp_path)])

    assert exit_code == 1
    # str(Path(...)) renders native separators (docs\engineering\API.md on
    # Windows), so compare against the same rendering rather than a
    # hardcoded forward-slash literal.
    assert str(_DOC_RELATIVE_PATH) in capsys.readouterr().out
