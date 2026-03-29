# Security Hardening Prompt

Use this prompt for practical security and operational-hardening passes in SoulMap AI.

- Start from `AGENTS.md`, `docs/OPERATIONS.md`, `docs/PRIVACY.md`, and `SECURITY.md`.
- Audit `tools/`, `scripts/`, and `.github/workflows/` for shell safety, path safety, and least-privilege permissions.
- Check docs for overclaims about privacy, disclosure, incident handling, or runtime safeguards.
- Focus on concrete risks such as secrets exposure, unsafe subprocess patterns, and packaging leaks.
- Prefer the smallest direct hardening fix over abstract security commentary.
- Run the relevant repo checks after meaningful edits.
