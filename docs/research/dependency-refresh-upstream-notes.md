# Dependency refresh upstream notes

Research date: 2026-11-17.

The official uv documentation states that `uv lock --check` verifies whether the lockfile matches project metadata. A lockfile is not considered outdated merely because newer package releases exist; an explicit upgrade/refresh is required. Commands such as `uv run --locked` fail rather than silently updating a stale lockfile. [1]

GitHub's official Dependabot documentation lists `uv` as a supported package ecosystem. Astral's integration guide confirms that Dependabot can update `uv.lock`. Dependabot is therefore the sole owner of the Python project dependency surface in this repository. [2] [3]

Renovate's PEP 621 manager can update `pyproject.toml` dependencies and work with `uv.lock`, including lockfile maintenance. Enabling it alongside Dependabot's `uv` ecosystem would create overlapping ownership. Renovate is consequently restricted to GitHub Actions and Dockerfile managers; Dependabot is restricted to `uv`. [4] [5]

GitHub recommends disabling an existing dependency-management integration before enabling Dependabot for the same dependency surface. The repository's explicit split follows that principle: one bot per ecosystem, no automatic merge, and maintainer review of release notes, compatibility, lock changes and CI evidence.

## References

[1]: https://docs.astral.sh/uv/concepts/projects/sync/ "uv locking and syncing"
[2]: https://docs.GitHub.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories "Dependabot supported ecosystems"
[3]: https://docs.astral.sh/uv/guides/integration/dependabot/ "Using uv with Dependabot"
[4]: https://docs.renovatebot.com/modules/manager/pep621/ "Renovate PEP 621 manager"
[5]: https://docs.astral.sh/uv/guides/integration/dependency-bots/ "Using uv with Renovate"
