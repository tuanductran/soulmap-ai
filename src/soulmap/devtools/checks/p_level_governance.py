"""Safety-governance metadata check for P-level pull requests.

A pull request whose title carries a P-level tag must declare its priority,
whether it preserves or changes a safety boundary, the validation evidence
behind it, and how to roll it back. A pull request that changes a safety
boundary must additionally carry the full evidence section, so an ADR and
regression evidence exist before the change merges.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

P_LEVEL_TITLE = re.compile(r"^\[(P[0-3])\]\s+")
METADATA_FIELD = re.compile(
    r"^- \*\*(Priority|Safety boundary|Evidence|Rollback):\*\*\s*(.+?)\s*$",
    re.MULTILINE,
)
REQUIRED_FIELDS = frozenset({"Priority", "Safety boundary", "Evidence", "Rollback"})
VALID_BOUNDARIES = frozenset({"preserved", "changed"})
CHANGE_EVIDENCE_MARKERS = (
    "## Safety change evidence",
    "- **ADR:**",
    "- **Positive regression:**",
    "- **Near-miss regression:**",
    "- **Safety matrix:**",
)


def p_level_from_title(title: str) -> str | None:
    """Read the P-level tag from a pull-request title.

    Args:
        title: Pull-request title.

    Returns:
        The P-level, such as ``"P1"``, or None when the title carries no tag.
        An untagged pull request is outside this check rather than a failure.
    """
    match = P_LEVEL_TITLE.match(title)
    return match.group(1) if match else None


def metadata_from_body(body: str) -> dict[str, str]:
    """Extract the governance metadata fields from a pull-request body.

    Args:
        body: Pull-request body in Markdown.

    Returns:
        A mapping of field name to value for every recognized field present.
        Missing fields are simply absent rather than empty.
    """
    return {field: value.strip() for field, value in METADATA_FIELD.findall(body)}


def validate_pull_request(title: str, body: str) -> list[str]:
    """Return deterministic governance errors for a P-level pull request."""
    priority = p_level_from_title(title)
    if priority is None:
        return []

    metadata = metadata_from_body(body)
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS.difference(metadata))
    if missing:
        errors.append(
            "P-level pull requests require metadata fields: " + ", ".join(missing) + "."
        )
        return errors

    if metadata["Priority"] != priority:
        errors.append(
            f"Priority metadata must match the title: expected {priority}, "
            f"found {metadata['Priority']}."
        )

    boundary = metadata["Safety boundary"].lower()
    if boundary not in VALID_BOUNDARIES:
        errors.append("Safety boundary must be exactly `preserved` or `changed`.")

    if metadata["Evidence"].lower() in {"n/a", "none", "not applicable"}:
        errors.append(
            "Evidence must name the validation that supports this P-level task."
        )

    if "revert" not in metadata["Rollback"].lower():
        errors.append("Rollback must state how the change can be reverted.")

    if boundary == "changed":
        for marker in CHANGE_EVIDENCE_MARKERS:
            if marker not in body:
                errors.append(
                    "Safety-boundary changes require the Safety change evidence section, "
                    f"including `{marker}`."
                )

    return errors


def pull_request_from_event(payload: Mapping[str, Any]) -> tuple[str, str]:
    """Pull the title and body out of a GitHub event payload.

    Args:
        payload: Parsed GitHub webhook event.

    Returns:
        A ``(title, body)`` pair. A pull request with no body yields an empty
        string, which then fails the metadata check with a specific error
        rather than a parse failure.

    Raises:
        ValueError: If the payload carries no pull request, or its title or
            body has an unexpected type.
    """
    pull_request = payload.get("pull_request")
    if not isinstance(pull_request, Mapping):
        raise ValueError("GitHub event does not contain a pull_request payload.")

    title = pull_request.get("title")
    body = pull_request.get("body")
    if not isinstance(title, str):
        raise ValueError("Pull request title is missing or invalid.")
    if body is None:
        body = ""
    if not isinstance(body, str):
        raise ValueError("Pull request body is invalid.")
    return title, body


def main(argv: list[str] | None = None) -> int:
    """Validate a pull request's governance metadata from an event file.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when the metadata is valid or the pull request carries no P-level
        tag, 1 when a governance rule fails, and 2 when the event file cannot
        be read or parsed.
    """
    parser = argparse.ArgumentParser(
        description="Validate P-level pull-request safety governance metadata."
    )
    parser.add_argument("--event-path", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        payload = json.loads(args.event_path.read_text(encoding="utf-8"))
        title, body = pull_request_from_event(payload)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Unable to read pull-request event: {error}", file=sys.stderr)
        return 2

    priority = p_level_from_title(title)
    if priority is None:
        print("P-level governance: skipped (title has no [P0]-[P3] prefix).")
        return 0

    errors = validate_pull_request(title, body)
    if errors:
        print(
            f"P-level governance failed for {priority} pull request:", file=sys.stderr
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"P-level governance passed for {priority} pull request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
