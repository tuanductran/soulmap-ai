# Security Policy

If you discover a security issue, please do not open a public issue.

## Reporting

Use GitHub's private vulnerability reporting:

1. Go to the repository **Security** tab
2. Click **Report a vulnerability**
3. Fill in reproduction steps, impact, and suggested fixes

If you cannot use GitHub private reporting, contact the repository owner directly
via the profile linked on the repository page.

Do not disclose publicly until the issue has been reviewed and resolved.

## Scope

This repository contains content and local scripts. No deployed services by default.
The following are in scope:

- Prompt injection vectors in skills, templates, or response logic
- Unsafe subprocess invocation in `tools/` or `scripts/`
- Mishandling of user-provided data in local modules
- Hardcoded credentials, keys, or secrets committed to the repository
- Dependencies with known critical vulnerabilities (CVE)

## Response

The repository owner will acknowledge within 7 days and provide a resolution timeline.
