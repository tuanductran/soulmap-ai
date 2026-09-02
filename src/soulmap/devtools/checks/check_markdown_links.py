"""Markdown link checker.

Verifies that local links resolve to a real file and that anchors match a real
heading. External links are checked only when explicitly requested, since that
mode depends on live network responses.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from soulmap.devtools.support.markdown import (
    extract_heading_anchors,
    is_external_markdown_target,
    iter_disallowed_markdown_references,
    iter_markdown_references,
    resolve_local_markdown_target,
    resolve_markdown_inputs,
    split_markdown_link_target,
)


@dataclass(frozen=True)
class Issue:
    """One link problem.

    Attributes:
        path: File the link was found in.
        line: 1-indexed line the link is on.
        message: Description naming the destination and what is wrong.
        severity: ``"error"`` for a broken local link, or ``"warning"`` for an
            external response that may be bot protection or rate limiting
            rather than a genuinely dead link.
    """

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


def _is_shipped_markdown(repo_root: Path, path: Path) -> bool:
    """Report whether a Markdown file is part of the shipped knowledge package.

    Args:
        repo_root: Repository root.
        path: File being checked.

    Returns:
        True for the root manifests and anything under ``skills/``.
    """
    try:
        relative = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return False
    return relative in {"SKILL.md", "SOULMAP.md"} or relative.startswith("skills/")


def _check_link_label(
    *,
    repo_root: Path,
    current_file: Path,
    label: str,
    target: str,
    line: int,
) -> list[Issue]:
    """Flag shipped link text that spells a path instead of naming a file.

    ``[../safety/ethics-safety.md](../safety/ethics-safety.md)`` reads as a
    path, but the ``../`` prefix describes where the link starts from. That
    means nothing to a reader and changes with whichever file does the linking.
    Written as ``[ethics-safety.md](../safety/ethics-safety.md)`` the text names
    the destination and stays correct wherever it is quoted.

    Scoped to shipped content on purpose. Inside ``docs/`` a label like
    ``skills/meta/master-prompt.md`` tells a maintainer where the file lives in
    the repository, which is useful and true. The same label inside ``skills/``
    describes a layout the reader of an extracted package does not have.

    Only labels that are themselves a path form are flagged, so a prose label
    such as ``[the safety rules](../safety/ethics-safety.md)`` stays untouched.

    Args:
        repo_root: Repository root, used to decide whether the file ships.
        current_file: File the link was found in.
        label: Link text exactly as written.
        target: Link destination exactly as written.
        line: 1-indexed source line.

    Returns:
        One issue when a shipped label spells a path, otherwise an empty list.
    """
    if not _is_shipped_markdown(repo_root, current_file):
        return []

    stripped = label.strip()
    if not stripped.startswith(("../", "./", "skills/")):
        return []

    file_part, _ = split_markdown_link_target(target)
    expected = file_part.rstrip("/").rsplit("/", 1)[-1]
    if file_part.endswith("/"):
        expected += "/"
    if not expected or stripped == expected:
        return []

    return [
        Issue(
            current_file,
            line,
            f"Link text should name the file, not the path: "
            f"use [{expected}] instead of [{stripped}]",
        )
    ]


def _check_local_target(
    *,
    repo_root: Path,
    current_file: Path,
    target: str,
    line: int,
) -> list[Issue]:
    issues: list[Issue] = []
    file_part, fragment = split_markdown_link_target(target)

    if "\\" in unquote(file_part):
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
    """Check one Markdown file's local links.

    External links are skipped. Call :func:`check_file_with_options` to
    include them.

    Args:
        path: Markdown file to check.
        repo_root: Repository root, which root-relative links resolve against.

    Returns:
        Every link problem found, in line order.
    """
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
    """Check one Markdown file's links, with external checking optional.

    Args:
        path: Markdown file to check.
        repo_root: Repository root, which root-relative links resolve against.
        check_external: Whether to make network requests for external links.
        timeout: Seconds to wait per external request.

    Returns:
        Every link problem found, in line order. External responses that
        commonly indicate bot protection or rate limiting are reported as
        warnings rather than errors.
    """
    issues: list[Issue] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for reference in iter_disallowed_markdown_references(lines):
        target = reference.target.strip()
        if target:
            issues.append(
                Issue(path, reference.line, f"Disallowed link scheme: {target}")
            )

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
        issues.extend(
            _check_local_target(
                repo_root=repo_root,
                current_file=path,
                target=target,
                line=reference.line,
            )
        )
        if not reference.is_image:
            issues.extend(
                _check_link_label(
                    repo_root=repo_root,
                    current_file=path,
                    label=reference.label,
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
    """Check Markdown files for link problems.

    Args:
        repo_root: Repository root.
        inputs: Files or directories to check, or None for the whole
            repository.
        check_external: Whether to make network requests for external links.
        timeout: Seconds to wait per external request.

    Returns:
        Every link problem found across the checked files.
    """
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
    """Run the link check from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when no error-severity problem is found, 1 otherwise. Warnings alone
        fail the run only when the caller passes the fail-on-warning flag.
    """
    parser = argparse.ArgumentParser(prog="soulmap check-links")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
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
