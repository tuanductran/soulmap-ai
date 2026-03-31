# Security Hardening Prompt

Use this prompt for practical security and operational-hardening passes in SoulMap AI.

- Start from `AGENTS.md`, `docs/operations/OPERATIONS.md`, `docs/operations/PRIVACY.md`, and `SECURITY.md`.
- Audit `src/`, `scripts/`, and `.github/workflows/` for shell safety, path safety, and least-privilege permissions.
- Check docs for overclaims about privacy, disclosure, incident handling, or runtime safeguards.
- Focus on concrete risks such as secrets exposure, unsafe subprocess patterns, and packaging leaks.
- Prefer the smallest direct hardening fix over abstract security commentary.
- Run the relevant repo checks after meaningful edits.
