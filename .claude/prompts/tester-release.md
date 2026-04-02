# Tester Release Prompt

Use this prompt for tester-style release readiness passes.

- Audit the repo as a product system, not only as Python code.
- Prioritize safety, response quality, Markdown source-of-truth integrity, packaging, and CI.
- Check `.github/workflows/` alongside docs and tests.
- Prefer focused runtime tests, focused evals, build smoke, and targeted exploratory
  charters.
- Add only the smallest regression protection that closes a real gap.
- Treat `CHANGELOG.md` and other release-facing Markdown as release-critical inputs, not
  passive docs.
- Verify that any manual release path still runs
  `uv run soulmap lint` before tagging or publishing artifacts.
