from __future__ import annotations

from pathlib import Path
from urllib.request import Request

import pytest

from soulmap.devtools.checks import check_markdown_case, check_markdown_links
from soulmap.devtools.support.markdown import MarkdownReference


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


def test_case_checker_repo_filter_and_cli_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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
    monkeypatch: pytest.MonkeyPatch,
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
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


def test_link_checker_request_wrapper_handles_response_and_transport_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from email.message import Message
    from urllib.error import HTTPError, URLError

    requests: list[tuple[str, str, float]] = []

    class _Response:
        status = 201

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def successful_urlopen(request: Request, *, timeout: float) -> _Response:
        requests.append((request.full_url, request.get_method(), timeout))
        return _Response()

    monkeypatch.setattr(check_markdown_links, "urlopen", successful_urlopen)
    assert check_markdown_links._request_external_target(
        "https://example.com/path",
        method="HEAD",
        timeout=1.5,
    ) == (201, None)
    assert requests == [("https://example.com/path", "HEAD", 1.5)]

    http_error = HTTPError(
        "https://example.com",
        418,
        "teapot",
        hdrs=Message(),
        fp=None,
    )
    monkeypatch.setattr(
        check_markdown_links,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(http_error),
    )
    status, error = check_markdown_links._request_external_target(
        "https://example.com",
        method="GET",
        timeout=1.0,
    )
    assert status == 418
    assert error is http_error

    url_error = URLError("offline")
    monkeypatch.setattr(
        check_markdown_links,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(url_error),
    )
    status, error = check_markdown_links._request_external_target(
        "https://example.com",
        method="GET",
        timeout=1.0,
    )
    assert status is None
    assert error is url_error


def test_link_checker_handles_non_http_and_unknown_network_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "README.md"
    source.write_text("# Source\n", encoding="utf-8")

    assert (
        check_markdown_links._check_external_target(
            current_file=source,
            target="mailto:hello@example.com",
            line=1,
            timeout=1.0,
        )
        == []
    )

    monkeypatch.setattr(
        check_markdown_links,
        "_request_external_target",
        lambda *_args, **_kwargs: (None, None),
    )
    issues = check_markdown_links._check_external_target(
        current_file=source,
        target="https://example.com",
        line=1,
        timeout=1.0,
    )

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "request failed" in issues[0].message


def test_link_checker_skips_empty_reference_and_non_integer_response_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "README.md"
    source.write_text("# Source\n", encoding="utf-8")

    class _UnknownStatus:
        status = None

        def getcode(self) -> str:
            return "unknown"

    monkeypatch.setattr(
        check_markdown_links,
        "iter_markdown_references",
        lambda _lines: [
            MarkdownReference(1, "empty", ""),
        ],
    )

    assert check_markdown_links._http_status_from_response(_UnknownStatus()) is None
    assert (
        check_markdown_links.check_file_with_options(
            source,
            tmp_path,
            check_external=False,
            timeout=1.0,
        )
        == []
    )


def test_link_checker_wrapper_and_cli_cover_clean_and_error_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean = tmp_path / "clean.md"
    clean.write_text("# Clean\n", encoding="utf-8")

    assert check_markdown_links.check_file(clean, tmp_path) == []
    assert check_markdown_links.main(["--root", str(tmp_path), "clean.md"]) == 0

    broken = tmp_path / "broken.md"
    broken.write_text("[Missing](missing.md)\n", encoding="utf-8")

    assert check_markdown_links.main(["--root", str(tmp_path), "broken.md"]) == 1
    assert "broken.md:1: Broken local link: missing.md" in capsys.readouterr().out
