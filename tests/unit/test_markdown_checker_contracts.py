from __future__ import annotations

from pathlib import Path

from soulmap.devtools.checks import check_markdown_case, check_markdown_links


def test_case_checker_skips_code_and_prevents_overlapping_term_reports(
    tmp_path: Path,
) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "soulmap ai is written incorrectly.\n"
        "`github` should be ignored inline.\n"
        "```text\nruff and pyright should be ignored in a fence.\n```\n",
        encoding="utf-8",
    )

    issues = check_markdown_case.check_file(source, tmp_path)

    assert len(issues) == 1
    assert issues[0].line == 1
    assert (
        issues[0].message
        == "Canonical case mismatch: found 'soulmap ai', expected 'SoulMap AI'"
    )


def test_case_checker_repo_filter_and_cli_failure(tmp_path: Path, capsys) -> None:
    source = tmp_path / "guide.md"
    source.write_text("github is not canonical.\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("SoulMap AI\n", encoding="utf-8")

    issues = check_markdown_case.check_repo(tmp_path, ["guide.md"])

    assert len(issues) == 1
    assert check_markdown_case.main(["--root", str(tmp_path), "guide.md"]) == 1
    assert "guide.md:1: Canonical case mismatch" in capsys.readouterr().out


def test_link_checker_flags_all_local_target_failures(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"png")
    source = tmp_path / "README.md"
    source.write_text(
        "# Source\n\n"
        "[Empty]()\n"
        "[Unsafe](javascript:alert)\n"
        "[Windows](docs\\guide.md)\n"
        "[Self](#missing)\n"
        "[Escape](../outside.md)\n"
        "[Directory](docs/#anchor)\n"
        "[Image](image.png#detail)\n"
        "[Cross](docs/guide.md#missing)\n",
        encoding="utf-8",
    )

    messages = [
        issue.message
        for issue in check_markdown_links.check_file_with_options(
            source,
            tmp_path,
            check_external=False,
            timeout=1.0,
        )
    ]

    assert "Disallowed link scheme: javascript:alert" in messages
    assert "Unsupported local path pattern: docs\\guide.md" in messages
    assert "Broken anchor link: #missing" in messages
    assert "Link escapes repo root: ../outside.md" in messages
    assert "Cannot resolve anchor against directory target: docs/#anchor" in messages
    assert (
        "Cannot resolve anchor against non-Markdown target: image.png#detail"
        in messages
    )
    assert "Broken cross-file anchor: docs/guide.md#missing" in messages


def test_link_checker_external_checks_handle_fallback_statuses_and_errors(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "README.md"
    source.write_text("[External](https://example.com)\n", encoding="utf-8")
    calls: list[str] = []

    def fake_request(
        _target: str, *, method: str, timeout: float
    ) -> tuple[int | None, Exception | None]:
        _ = timeout
        calls.append(method)
        if method == "HEAD":
            return 405, None
        return 200, None

    monkeypatch.setattr(check_markdown_links, "_request_external_target", fake_request)

    assert check_markdown_links.check_repo(tmp_path, check_external=True) == []
    assert calls == ["HEAD", "GET"]

    monkeypatch.setattr(
        check_markdown_links,
        "_request_external_target",
        lambda *_args, **_kwargs: (403, None),
    )
    warnings = check_markdown_links.check_repo(tmp_path, check_external=True)
    assert len(warnings) == 1
    assert warnings[0].severity == "warning"
    assert "HTTP 403" in warnings[0].message

    monkeypatch.setattr(
        check_markdown_links,
        "_request_external_target",
        lambda *_args, **_kwargs: (None, RuntimeError("offline")),
    )
    transient = check_markdown_links.check_repo(tmp_path, check_external=True)
    assert len(transient) == 1
    assert transient[0].severity == "warning"
    assert "offline" in transient[0].message


def test_link_checker_response_status_and_warning_cli_behavior(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    class _Response:
        status = None

        def getcode(self) -> int:
            return 204

    assert check_markdown_links._http_status_from_response(_Response()) == 204
    assert check_markdown_links._http_status_from_response(object()) is None

    source = tmp_path / "README.md"
    source.write_text("[External](https://example.com)\n", encoding="utf-8")
    monkeypatch.setattr(
        check_markdown_links,
        "_request_external_target",
        lambda *_args, **_kwargs: (429, None),
    )

    assert (
        check_markdown_links.main(
            ["--root", str(tmp_path), "--check-external", "README.md"]
        )
        == 0
    )
    assert "WARNING: External link returned HTTP 429" in capsys.readouterr().out
    assert (
        check_markdown_links.main(
            [
                "--root",
                str(tmp_path),
                "--check-external",
                "--fail-on-warning",
                "README.md",
            ]
        )
        == 1
    )
