# Privacy

SoulMap AI is a reflective companion delivered as a knowledge base and local tooling.
This document describes what data is and is not handled by this project.

## What this repository is

SoulMap is a Markdown knowledge base, a set of local Python packages, and a packaged
Agent Skills archive. It is a content and logic layer, not a deployed service.

There is no SoulMap AI server. There is no SoulMap AI account system. There is no
SoulMap AI backend that receives or stores your conversations.

## Where your conversations go

When you use SoulMap AI, you are using it through a separate AI platform (for example,
Claude.ai, an API integration, or a product built on top of these). The platform you
are using governs how your conversation data is handled. SoulMap AI has no visibility
into and no control over that data.

Consult the privacy policy of the platform you are using for the applicable data
practices.

## What this repository does handle

If you run SoulMap AI's local Python tooling, inputs handled by the local command are
processed on your machine. The project does not send conversation inputs to a
SoulMap-operated server because no such server exists.

Some explicitly networked operations do contact third-party endpoints. Examples include
opt-in external link checking, package installation, and GitHub Actions or API operations.
Those requests serve the selected operation; they are not a SoulMap conversation-storage
service. Review the relevant third-party service's current terms and privacy policy when
using those features.

Evaluation tooling (`uv run soulmap eval-responses`) uses synthetic test cases defined
in `evals/`. It does not use real user data.

## Dependencies

SoulMap AI's Python dependencies are listed in `pyproject.toml`. This repository does
not implement a SoulMap-operated telemetry or conversation-upload service. This
statement is not a certification of every third-party dependency's telemetry or network
behavior; consult the relevant tool and service documentation for its current settings
and practices.

## Security

If you discover a security concern, including prompt injection vectors or unsafe
handling of user-provided data, use the repository's private vulnerability reporting
flow on GitHub. In a full repository checkout, see `SECURITY.md` for the detailed
disclosure process.

## Questions

Open an issue in the GitHub repository or contact the repository owner directly.
