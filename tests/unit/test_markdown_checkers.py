from __future__ import annotations

from pathlib import Path

from soulmap.devtools.checks import check_markdown_case, check_markdown_links


def test_markdown_link_checker_accepts_valid_local_links(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    target = tmp_path / "docs" / "guide.md"
    target.write_text("# Guide\n\n## Details\n\nContent\n", encoding="utf-8")
    source = tmp_path / "README.md"
    source.write_text(
        "[Guide](docs/guide.md)\n[Details](docs/guide.md#details)\n[Here](#local-anchor)\n\n## Local anchor\n",
        encoding="utf-8",
    )

    assert check_markdown_links.check_repo(tmp_path) == []


def test_markdown_link_checker_flags_missing_file_and_anchor(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "[Missing](docs/missing.md)\n[Broken](#missing-anchor)\n",
        encoding="utf-8",
    )

    issues = check_markdown_links.check_repo(tmp_path)

    assert any(
        "Broken local link: docs/missing.md" in issue.message for issue in issues
    )
    assert any(
        "Broken anchor link: #missing-anchor" in issue.message for issue in issues
    )


def test_markdown_link_checker_handles_duplicate_heading_suffixes(
    tmp_path: Path,
) -> None:
    target = tmp_path / "guide.md"
    target.write_text(
        "# Repeat\n\n## Same heading\n\nText\n\n## Same heading\n\nMore text\n",
        encoding="utf-8",
    )
    source = tmp_path / "README.md"
    source.write_text("[Anchor](guide.md#same-heading-1)\n", encoding="utf-8")

    assert check_markdown_links.check_repo(tmp_path) == []


def test_markdown_link_checker_accepts_root_relative_and_image_links(
    tmp_path: Path,
) -> None:
    (tmp_path / "skills").mkdir()
    (tmp_path / "assets").mkdir()
    target = tmp_path / "skills" / "guide.md"
    target.write_text("# Skill guide\n", encoding="utf-8")
    image = tmp_path / "assets" / "logo.png"
    image.write_bytes(b"png")
    source = tmp_path / "README.md"
    source.write_text(
        "[Skill](/skills/guide.md#skill-guide)\n![Logo](assets/logo.png)\n[Site](https://example.com)\n",
        encoding="utf-8",
    )

    assert check_markdown_links.check_repo(tmp_path) == []


def test_markdown_link_checker_flags_anchor_on_non_markdown_target(
    tmp_path: Path,
) -> None:
    image = tmp_path / "logo.png"
    image.write_bytes(b"png")
    source = tmp_path / "README.md"
    source.write_text("[Logo](logo.png#detail)\n", encoding="utf-8")

    issues = check_markdown_links.check_repo(tmp_path)

    assert any("non-Markdown target" in issue.message for issue in issues)


def test_markdown_link_checker_ignores_external_links_by_default(
    tmp_path: Path,
) -> None:
    source = tmp_path / "README.md"
    source.write_text("[Site](https://example.com)\n", encoding="utf-8")

    assert check_markdown_links.check_repo(tmp_path) == []


def test_markdown_link_checker_can_fail_on_external_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "README.md"
    source.write_text("[Site](https://example.com)\n", encoding="utf-8")

    def fake_request(
        target: str, *, method: str, timeout: float
    ) -> tuple[int | None, Exception | None]:
        assert target == "https://example.com"
        assert timeout == 2.5
        return (404, None)

    monkeypatch.setattr(check_markdown_links, "_request_external_target", fake_request)

    issues = check_markdown_links.check_repo(
        tmp_path,
        check_external=True,
        timeout=2.5,
    )

    assert any("HTTP 404" in issue.message for issue in issues)
    assert all(issue.severity == "error" for issue in issues)


def test_markdown_link_checker_warning_exit_is_opt_in(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "README.md"
    source.write_text("[Site](https://example.com)\n", encoding="utf-8")

    def fake_request(
        target: str, *, method: str, timeout: float
    ) -> tuple[int | None, Exception | None]:
        return (429, None)

    monkeypatch.setattr(check_markdown_links, "_request_external_target", fake_request)

    assert (
        check_markdown_links.main(
            ["--root", str(tmp_path), "--check-external", str(source)]
        )
        == 0
    )
    assert (
        check_markdown_links.main(
            [
                "--root",
                str(tmp_path),
                "--check-external",
                "--fail-on-warning",
                str(source),
            ]
        )
        == 1
    )


def test_markdown_case_checker_accepts_canonical_terms(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "SoulMap AI uses Markdown docs, GitHub workflows, Ruff, Pyright, Hypothesis, lefthook, Claude, and Codex.\n",
        encoding="utf-8",
    )

    assert check_markdown_case.check_repo(tmp_path) == []


def test_markdown_case_checker_flags_wrong_case(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "soulmap ai uses github workflows with ruff and pyright.\n",
        encoding="utf-8",
    )

    issues = check_markdown_case.check_repo(tmp_path)

    assert any("expected 'SoulMap AI'" in issue.message for issue in issues)
    assert any("expected 'GitHub'" in issue.message for issue in issues)
    assert any("expected 'Ruff'" in issue.message for issue in issues)
    assert any("expected 'Pyright'" in issue.message for issue in issues)


def test_markdown_case_checker_skips_exempt_paths(tmp_path: Path) -> None:
    source = tmp_path / "CHANGELOG.md"
    source.write_text("soulmap ai github ruff pyright\n", encoding="utf-8")

    assert check_markdown_case.check_repo(tmp_path) == []


def test_markdown_case_checker_skips_claude_entrypoint(tmp_path: Path) -> None:
    source = tmp_path / "CLAUDE.md"
    source.write_text(
        "# CLAUDE\n\nThis file points Claude Code at repo guidance.\n", encoding="utf-8"
    )

    assert check_markdown_case.check_repo(tmp_path) == []
