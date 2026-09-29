#!/usr/bin/env python3
"""Backfill empty GitHub release notes using GitHub's generated release notes API."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OWNER = "tuanductran"
REPO = "soulmap-ai"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
TOKEN = os.environ["SOULMAP_RELEASE_TOKEN"]
RELEASES = [
    "v0.2.0", "v0.3.0", "v0.4.0", "v0.4.1", "v0.5.0", "v0.5.1",
    "v0.6.0", "v0.7.0", "v0.8.0", "v0.9.0", "v0.9.1", "v0.10.0",
    "v0.11.0", "v0.12.0", "v0.12.1", "v0.13.0",
]


def request(method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        API + path,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2026-03-10",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path}: HTTP {exc.code}: {detail}") from exc


def main() -> None:
    releases = request("GET", "/releases?per_page=100")
    by_tag = {item["tag_name"]: item for item in releases}

    for index, tag in enumerate(RELEASES):
        release = by_tag.get(tag)
        if release is None:
            raise RuntimeError(f"Release not found: {tag}")
        if release.get("body"):
            print(f"skip {tag}: body already exists")
            continue

        previous_tag = RELEASES[index - 1] if index else "v0.1.0"
        generated = request(
            "POST",
            "/releases/generate-notes",
            {
                "tag_name": tag,
                "previous_tag_name": previous_tag,
            },
        )
        body = generated.get("body", "").strip()
        if not body:
            raise RuntimeError(f"Generated release notes are empty: {tag}")

        request(
            "PATCH",
            f"/releases/{release['id']}",
            {"body": body},
        )
        print(f"updated {tag} from {previous_tag}")


if __name__ == "__main__":
    main()
