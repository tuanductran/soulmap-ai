"""GitHub operations used by SoulMap workflows."""
from __future__ import annotations
import json, mimetypes, os, sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
USER_AGENT = "soulmap-github-action"

class GitHubActionError(RuntimeError):
    """Raised when an action operation cannot be completed safely."""

class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def request(self, method: str, url: str, *, payload: dict[str, object] | None = None,
                data: bytes | None = None, content_type: str | None = None) -> dict[str, object] | list[object] | None:
        body = data if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }
        if body is not None:
            headers["Content-Length"] = str(len(body))
        if content_type:
            headers["Content-Type"] = content_type
        try:
            with urlopen(Request(url, data=body, method=method, headers=headers), timeout=60) as response:
                if response.status == 204:
                    return None
                raw = response.read()
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubActionError(f"GitHub API {method} {url} failed with HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise GitHubActionError(f"GitHub API {method} {url} failed: {exc.reason}") from exc

    def api(self, method: str, path: str, *, payload: dict[str, object] | None = None) -> dict[str, object] | list[object] | None:
        return self.request(method, f"{API_ROOT}{path}", payload=payload)

    def upload(self, upload_url: str, *, name: str, content: bytes, content_type: str) -> dict[str, object] | list[object] | None:
        base = upload_url.split("{", 1)[0]
        return self.request("POST", f"{base}?{urlencode({'name': name})}", data=content, content_type=content_type)

def env(name: str, *, required: bool = True, default: str = "") -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise GitHubActionError(f"Missing required action input: {name}")
    return value

def boolean(name: str, default: bool = False) -> bool:
    value = env(name, required=False, default="true" if default else "false").strip().lower()
    if value not in {"true", "false"}:
        raise GitHubActionError(f"Input {name!r} must be true or false.")
    return value == "true"

def repository_parts(repository: str) -> tuple[str, str]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise GitHubActionError(f"Invalid GitHub repository: {repository!r}")
    return owner, name

def write_output(name: str, value: object) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with Path(output_file).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}<<SOULMAP_EOF\n{value}\nSOULMAP_EOF\n")

def summary(message: str) -> None:
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with Path(summary_file).open("a", encoding="utf-8") as handle:
            handle.write(f"{message.rstrip()}\n")

def read_body() -> str:
    body = env("INPUT_BODY", required=False)
    body_path = env("INPUT_BODY_PATH", required=False)
    if body_path:
        path = Path(body_path)
        if not path.is_file():
            raise GitHubActionError(f"Body file does not exist: {path}")
        body = path.read_text(encoding="utf-8")
    return body

def asset_paths() -> list[Path]:
    paths = []
    for item in env("INPUT_FILES", required=False).splitlines():
        item = item.strip()
        if item:
            path = Path(item)
            if not path.is_file():
                raise GitHubActionError(f"Release asset does not exist: {path}")
            paths.append(path)
    return paths

def get_release(client: GitHubClient, owner: str, repo: str, tag: str) -> dict[str, object] | None:
    path = f"/repos/{quote(owner)}/{quote(repo)}/releases/tags/{quote(tag, safe='')}"
    try:
        response = client.api("GET", path)
    except GitHubActionError as exc:
        if "HTTP 404" in str(exc):
            return None
        raise
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub returned an invalid release object.")
    return response

def create_release(client: GitHubClient, owner: str, repo: str, tag: str, name: str, body: str,
                   prerelease: bool, generate_notes: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "tag_name": tag,
        "name": name or tag,
        "body": body,
        "draft": True,
        "prerelease": prerelease,
        "generate_release_notes": generate_notes,
    }
    response = client.api("POST", f"/repos/{quote(owner)}/{quote(repo)}/releases", payload=payload)
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return a release object.")
    return response

def upload_assets(client: GitHubClient, release: dict[str, object], paths: list[Path]) -> None:
    upload_url = release.get("upload_url")
    if not isinstance(upload_url, str):
        raise GitHubActionError("Release response lacks upload metadata.")
    assets = release.get("assets", [])
    existing = {asset.get("name") for asset in assets if isinstance(asset, dict)}
    missing = [path.name for path in paths if path.name not in existing]
    if not release.get("draft", False) and missing:
        raise GitHubActionError("Published release is immutable and is missing assets: " + ", ".join(missing))
    for path in paths:
        if path.name in existing:
            print(f"Release asset already present: {path.name}")
            continue
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        print(f"Uploading release asset: {path}")
        client.upload(upload_url, name=path.name, content=path.read_bytes(), content_type=content_type)

def finalize_release(client: GitHubClient, owner: str, repo: str, release: dict[str, object],
                     draft: bool, prerelease: bool) -> dict[str, object]:
    if release.get("draft") is not True:
        return release
    release_id = release.get("id")
    if not isinstance(release_id, int):
        raise GitHubActionError("Release response lacks a valid release ID.")
    response = client.api("PATCH", f"/repos/{quote(owner)}/{quote(repo)}/releases/{release_id}",
                          payload={"draft": draft, "prerelease": prerelease})
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return the updated release.")
    return response

def run_release(client: GitHubClient) -> None:
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    tag = env("INPUT_TAG")
    release = get_release(client, owner, repo, tag)
    if release is None:
        release = create_release(
            client, owner, repo, tag,
            env("INPUT_RELEASE_NAME", required=False, default=tag),
            read_body(),
            boolean("INPUT_PRERELEASE"),
            boolean("INPUT_GENERATE_RELEASE_NOTES"),
        )
    upload_assets(client, release, asset_paths())
    release = get_release(client, owner, repo, tag) or release
    release = finalize_release(client, owner, repo, release, boolean("INPUT_DRAFT"), boolean("INPUT_PRERELEASE"))
    release_id, release_url = release.get("id"), release.get("html_url")
    if release_id is None or not isinstance(release_url, str):
        raise GitHubActionError("GitHub release response is missing outputs.")
    write_output("release-id", release_id)
    write_output("release-url", release_url)
    write_output("tag-name", tag)
    summary(f"## SoulMap release published\n\n- Tag: {tag}\n- URL: {release_url}")

def run_pull_request(client: GitHubClient) -> None:
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    branch = env("INPUT_BRANCH")
    base = env("INPUT_BASE", required=False, default="main")
    tag = env("INPUT_TAG", required=False)
    title = env("INPUT_TITLE", required=False, default=f"chore(release): {tag}" if tag else "chore(release)")
    body = read_body() or f"Automated release preparation for {tag}."
    query = urlencode({"state": "open", "head": f"{owner}:{branch}", "base": base})
    existing = client.api("GET", f"/repos/{quote(owner)}/{quote(repo)}/pulls?{query}")
    pr = existing[0] if isinstance(existing, list) and existing and isinstance(existing[0], dict) else None
    if pr is None:
        created = client.api("POST", f"/repos/{quote(owner)}/{quote(repo)}/pulls",
                             payload={"base": base, "head": branch, "title": title, "body": body})
        if not isinstance(created, dict):
            raise GitHubActionError("GitHub did not return a pull request object.")
        pr = created
    url = pr.get("html_url")
    if not isinstance(url, str) or not url:
        raise GitHubActionError("GitHub did not return a pull request URL.")
    write_output("pull-request-url", url)
    summary(f"## SoulMap release pull request\n\n- URL: {url}")

def main() -> int:
    try:
        operation = env("INPUT_OPERATION").strip().lower()
        client = GitHubClient(env("INPUT_TOKEN"))
        if operation == "release":
            run_release(client)
        elif operation == "pull-request":
            run_pull_request(client)
        else:
            raise GitHubActionError(f"Unsupported operation {operation!r}; expected release or pull-request.")
    except GitHubActionError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
