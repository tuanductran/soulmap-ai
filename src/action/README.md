# SoulMap GitHub Operations

A Python/Docker GitHub Action for the repository's GitHub-specific release operations.
It uses only the Python standard library and GitHub REST APIs for release tags, releases, assets, and pull requests.

## Release

The `release` operation expects the Git tag to already exist. It creates or reuses the GitHub Release, uploads missing assets, and publishes it when `draft` is false.

```yaml
- uses: ./src/action
  with:
    operation: release
    token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}
    tag: v0.12.1
    generate-release-notes: "true"
    files: |
      dist/soulmap-ai.zip
      dist/soulmap-ai.skill
      dist/soulmap-ai-library.json
      dist/release-verification.json
      dist/release-provenance.json
    draft: "false"
```

## Pull request

```yaml
- uses: ./src/action
  with:
    operation: pull-request
    token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}
    branch: release/prep-123
    base: main
    tag: v0.12.1
```

The pull-request operation reuses an existing open PR from the same head branch and base.

## Tag

The `tag` operation creates or verifies an annotated Git tag for an exact commit SHA. It refuses to reuse an existing tag that points somewhere else.

`target-sha` must be the full 40-character commit SHA.

```yaml
- uses: ./src/action
  with:
    operation: tag
    token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}
    tag: v0.12.1
    target-sha: 0123456789abcdef0123456789abcdef01234567
```
