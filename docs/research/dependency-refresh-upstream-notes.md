# Dependency refresh upstream notes

Research date: 2026-08-18.

The official uv documentation states that `uv lock --check` verifies whether the lockfile matches project metadata. A lockfile is not considered outdated merely because newer package releases exist; an explicit upgrade/refresh is required. Commands such as `uv run --locked` fail rather than silently updating a stale lockfile. [1]

GitHub's official Dependabot documentation distinguishes security updates from version updates. Security updates target known vulnerabilities, while version updates keep dependencies current even without a vulnerability. Dependabot version updates require a committed `dependabot.yml` configuration, and maintainers should review tests, changelogs and release notes before merging the generated pull request. [2]

Implication for SoulMap: the repository should keep its existing explicit uv lock/CI contracts and use a documented human review checklist. It should not assume that a new package release automatically requires a lock refresh, and it should not add Dependabot configuration or a new scanner without a repository-specific reason and a reviewed change proposal.

## References

[1]: https://docs.astral.sh/uv/concepts/projects/sync/ "uv locking and syncing"
[2]: https://docs.GitHub.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates "GitHub Dependabot version updates"
