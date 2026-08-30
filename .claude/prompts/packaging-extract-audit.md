# Packaging Extract Audit Prompt

Use this prompt for packaging and extracted-bundle honesty passes in SoulMap AI.

- Start from `SOULMAP.md`, `docs/engineering/repo-contract.md`, `docs/operations/UPLOAD.md`, and `src/soulmap/devtools/packaging/build_skill.py`.
- Audit `.distignore`, build scripts, and artifact contents together.
- Verify shipped docs do not assume repo-only files exist after extraction.
- Prioritize `dist/soulmap-ai.zip` and `dist/soulmap-ai.skill` self-containment over convenience wording.
- Prefer fixing source-of-truth docs or build inputs over adding workaround files.
- Rebuild both artifacts after meaningful edits.
