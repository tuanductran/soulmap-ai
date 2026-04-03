from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from soulmap.devtools.support.markdown import (
    extract_heading_anchors,
    is_external_markdown_target,
    iter_markdown_references,
    resolve_local_markdown_target,
    resolve_markdown_inputs,
    split_markdown_link_target,
)


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str
    severity: str = "error"


_WARNING_HTTP_STATUSES = {403, 429}
_HEAD_FALLBACK_HTTP_STATUSES = {400, 403, 405, 429, 500, 501, 502, 503}


def _format_external_issue(
    current_file: Path,
    line: int,
    target: str,
    message: str,
    *,
    severity: str = "error",
) -> Issue:
    return Issue(
        current_file,
        line,
        f"External link {message}: {target}",
        severity=severity,
    )


def _http_status_from_response(response: object) -> int | None:
    status = getattr(response, "status", None)
    if isinstance(status, int):
        return status
    getcode = getattr(response, "getcode", None)
    if callable(getcode):
        code = getcode()
        if isinstance(code, int):
            return code
    return None


def _request_external_target(
    target: str,
    *,
    method: str,
    timeout: float,
) -> tuple[int | None, Exception | None]:
    request = Request(
        target,
        headers={"User-Agent": "SoulMap-AI-Markdown-Link-Checker/1.0"},
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return _http_status_from_response(response), None
    except HTTPError as exc:
        return exc.code, exc
    except (URLError, TimeoutError, ValueError) as exc:
        return None, exc


def _check_external_target(
    *,
    current_file: Path,
    target: str,
    line: int,
    timeout: float,
) -> list[Issue]:
    issues: list[Issue] = []
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"}:
        return issues

    status, error = _request_external_target(target, method="HEAD", timeout=timeout)
    if status in _HEAD_FALLBACK_HTTP_STATUSES or (status is None and error is not None):
        status, error = _request_external_target(target, method="GET", timeout=timeout)

    if status is not None:
        if 200 <= status < 400:
            return issues
        if status in _WARNING_HTTP_STATUSES:
            issues.append(
                _format_external_issue(
                    current_file,
                    line,
                    target,
                    f"returned HTTP {status}",
                    severity="warning",
                )
            )
            return issues
        issues.append(
            _format_external_issue(
                current_file,
                line,
                target,
                f"returned HTTP {status}",
            )
        )
        return issues

    reason = str(error) if error is not None else "request failed"
    issues.append(
        _format_external_issue(
            current_file,
            line,
            target,
            reason,
            severity="warning",
        )
    )
    return issues


def _check_local_target(
    *,
    repo_root: Path,
    current_file: Path,
    target: str,
    line: int,
) -> list[Issue]:
    issues: list[Issue] = []
    file_part, fragment = split_markdown_link_target(target)

    if "\\" in file_part:
        return [Issue(current_file, line, f"Unsupported local path pattern: {target}")]

    if file_part == "" and fragment is not None:
        anchors = {
            anchor.slug
            for anchor in extract_heading_anchors(
                current_file.read_text(encoding="utf-8").splitlines()
            )
        }
        if fragment not in anchors:
            issues.append(Issue(current_file, line, f"Broken anchor link: #{fragment}"))
        return issues

    try:
        resolved = resolve_local_markdown_target(
            repo_root=repo_root,
            current_file=current_file,
            target_path=file_part,
        )
        resolved.relative_to(repo_root)
    except ValueError:
        return [Issue(current_file, line, f"Link escapes repo root: {target}")]

    if not resolved.exists():
        return [Issue(current_file, line, f"Broken local link: {file_part}")]

    if fragment is None:
        return issues

    if resolved.is_dir():
        return [
            Issue(
                current_file,
                line,
                f"Cannot resolve anchor against directory target: {target}",
            )
        ]

    if resolved.suffix.lower() != ".md":
        return [
            Issue(
                current_file,
                line,
                f"Cannot resolve anchor against non-Markdown target: {target}",
            )
        ]

    anchors = {
        anchor.slug
        for anchor in extract_heading_anchors(
            resolved.read_text(encoding="utf-8").splitlines()
        )
    }
    if fragment not in anchors:
        issues.append(
            Issue(
                current_file, line, f"Broken cross-file anchor: {file_part}#{fragment}"
            )
        )
    return issues


def check_file(path: Path, repo_root: Path) -> list[Issue]:
    return check_file_with_options(
        path,
        repo_root,
        check_external=False,
        timeout=5.0,
    )


def check_file_with_options(
    path: Path,
    repo_root: Path,
    *,
    check_external: bool,
    timeout: float,
) -> list[Issue]:
    issues: list[Issue] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for reference in iter_markdown_references(lines):
        target = reference.target.strip()
        if not target:
            continue
        if is_external_markdown_target(target):
            if check_external:
                issues.extend(
                    _check_external_target(
                        current_file=path,
                        target=target.strip().strip("<>").strip(),
                        line=reference.line,
                        timeout=timeout,
                    )
                )
            continue
        if target.startswith(("javascript:", "data:", "file:")):
            issues.append(
                Issue(path, reference.line, f"Disallowed link scheme: {target}")
            )
            continue
        issues.extend(
            _check_local_target(
                repo_root=repo_root,
                current_file=path,
                target=target,
                line=reference.line,
            )
        )

    return issues


def check_repo(
    repo_root: Path,
    inputs: list[str] | None = None,
    *,
    check_external: bool = False,
    timeout: float = 5.0,
) -> list[Issue]:
    issues: list[Issue] = []
    for path in resolve_markdown_inputs(repo_root, inputs):
        issues.extend(
            check_file_with_options(
                path,
                repo_root,
                check_external=check_external,
                timeout=timeout,
            )
        )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulmap check-links")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo root (default: current directory).",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        help="Also validate external http/https links with live network requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Per-request timeout in seconds for external link checks (default: 5.0).",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat external-link warnings such as 403/429 or transient network failures as errors.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional Markdown files or directories to check.",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    issues = check_repo(
        repo_root,
        args.paths,
        check_external=args.check_external,
        timeout=args.timeout,
    )
    if not issues:
        return 0

    for issue in issues:
        rel = issue.path.resolve().relative_to(repo_root)
        prefix = f"{issue.severity.upper()}: " if issue.severity != "error" else ""
        print(f"{rel}:{issue.line}: {prefix}{issue.message}")
    if any(issue.severity == "error" for issue in issues):
        return 1
    return 1 if args.fail_on_warning else 0


if __name__ == "__main__":
    raise SystemExit(main())
