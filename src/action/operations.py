"""Top-level handlers for each supported GitHub Action operation."""

from __future__ import annotations

from urllib.parse import quote

from client import GitHubClient
from errors import GitHubActionError
from inputs import (
    asset_paths,
    boolean,
    env,
    read_body,
    repository_parts,
    summary,
    write_output,
)
from refs import create_branch, create_tag, ensure_tag_exists
from releases import (
    create_release,
    finalize_release,
    get_release,
    update_release_metadata,
    upload_assets,
)


def run_branch(client: GitHubClient) -> None:
    """Create or verify the release branch for an exact commit."""
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    branch = env("INPUT_BRANCH")
    target_sha = env("INPUT_TARGET_SHA")
    create_branch(client, owner, repo, branch, target_sha)
    write_output("branch-name", branch)
    summary(f"## SoulMap release branch\n\n- Branch: {branch}\n- Commit: {target_sha}")


def run_tag(client: GitHubClient) -> None:
    """Create or verify the release tag for an exact commit."""
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    tag = env("INPUT_TAG")
    target_sha = env("INPUT_TARGET_SHA")
    create_tag(client, owner, repo, tag, target_sha)
    write_output("tag-name", tag)
    summary(f"## SoulMap release tag\n\n- Tag: {tag}\n- Commit: {target_sha}")


def run_release(client: GitHubClient) -> None:
    """Execute the complete release publication workflow."""
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    tag = env("INPUT_TAG")
    ensure_tag_exists(client, owner, repo, tag)
    release = get_release(client, owner, repo, tag)
    if release is None:
        release = create_release(
            client,
            owner,
            repo,
            tag,
            env("INPUT_RELEASE_NAME", required=False, default=tag),
            read_body(),
            boolean("INPUT_PRERELEASE"),
            boolean("INPUT_GENERATE_RELEASE_NOTES"),
        )
    else:
        release = update_release_metadata(client, owner, repo, release)
    upload_assets(client, release, asset_paths())
    release = get_release(client, owner, repo, tag) or release
    release = finalize_release(
        client,
        owner,
        repo,
        release,
        boolean("INPUT_DRAFT"),
        boolean("INPUT_PRERELEASE"),
    )
    release_id, release_url = release.get("id"), release.get("html_url")
    if (
        not isinstance(release_id, int)
        or not isinstance(release_url, str)
        or not release_url
    ):
        raise GitHubActionError("GitHub release response is missing outputs.")
    write_output("release-id", release_id)
    write_output("release-url", release_url)
    write_output("tag-name", tag)
    summary(f"## SoulMap release published\n\n- Tag: {tag}\n- URL: {release_url}")


def run_pull_request(client: GitHubClient) -> None:
    """Create or reuse the release preparation pull request."""
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    branch = env("INPUT_BRANCH")
    base = env("INPUT_BASE", required=False, default="main")
    tag = env("INPUT_TAG", required=False)
    title = env(
        "INPUT_TITLE",
        required=False,
        default=f"chore(release): {tag}" if tag else "chore(release)",
    )
    body = read_body() or f"Automated release preparation for {tag}."
    existing = client.paginated(
        f"/repos/{quote(owner)}/{quote(repo)}/pulls",
        params={
            "state": "open",
            "head": f"{owner}:{branch}",
            "base": base,
        },
    )
    prs = [item for item in existing if isinstance(item, dict)]
    if len(prs) > 1:
        raise GitHubActionError(
            f"GitHub returned multiple open release PRs for {owner}:{branch} -> {base}."
        )
    pr = prs[0] if prs else None
    if pr is None:
        created = client.api(
            "POST",
            f"/repos/{quote(owner)}/{quote(repo)}/pulls",
            payload={"base": base, "head": branch, "title": title, "body": body},
        )
        if not isinstance(created, dict):
            raise GitHubActionError("GitHub did not return a pull request object.")
        pr = created
    url = pr.get("html_url")
    number = pr.get("number")
    if not isinstance(url, str) or not url or not isinstance(number, int):
        raise GitHubActionError("GitHub did not return complete pull request metadata.")
    write_output("pull-request-url", url)
    write_output("pull-request-number", number)
    summary(f"## SoulMap release pull request\n\n- URL: {url}\n- Number: {number}")
