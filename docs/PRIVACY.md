# Privacy

SoulMap AI is a reflective companion delivered as a knowledge base and local tooling.
This document describes what data is and is not handled by this project.

## What This Repository Is

SoulMap AI is a Markdown knowledge base, a set of local Python modules, and a packaged
Agent Skills archive. It is a content and logic layer -- not a deployed service.

There is no SoulMap AI server. There is no SoulMap AI account system. There is no
SoulMap AI backend that receives or stores your conversations.

## Where Your Conversations Go

When you use SoulMap AI, you are using it through a separate AI platform (for example,
Claude.ai, an API integration, or a product built on top of these). The platform you
are using governs how your conversation data is handled. SoulMap AI has no visibility
into and no control over that data.

Consult the privacy policy of the platform you are using for the applicable data
practices.

## What This Repository Does Handle

If you run SoulMap AI's local Python tooling (`python -m modules.soulmap_demo`),
any input you provide is processed locally on your machine. Nothing is transmitted to
any SoulMap AI server, because there is none.

Evaluation tooling (`python -m tools.eval_responses`) uses synthetic test cases defined
in `evals/`. It does not use real user data.

## Biometric and Wearable Data

`modules/biometric_ingest.py` contains logic for parsing wearable data if you choose
to provide it. Any such data is processed locally within a single session and is not
stored or transmitted by the SoulMap AI codebase.

## Dependencies

SoulMap AI's Python dependencies are listed in `pyproject.toml`. No dependency sends
telemetry or user data as part of this project's usage. All tools (ruff, pyright,
pytest) operate entirely locally.

## Security

If you discover a security concern -- including prompt injection vectors or unsafe
handling of user-provided data -- see `SECURITY.md` for the disclosure process.

## Questions

Open an issue in the GitHub repository or contact the repository owner directly.
