# Python actionlint action

Runs pinned actionlint through a Python Docker action.

```yaml
- name: Validate GitHub Actions workflows
  uses: ./.github/actions/actionlint/python
```

GitHub does not provide a native `runs.using: python` action runtime, so the Python implementation is packaged as a Docker container action. Docker container actions package their runtime and dependencies with the action. citeturn1search7turn1search1
