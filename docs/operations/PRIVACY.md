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

If you run SoulMap AI's local Python tooling (`python -m soulmap_runtime.experimental.soulmap_demo`),
any input you provide is processed locally on your machine. Nothing is transmitted to
any SoulMap AI server, because there is none.

Evaluation tooling (`python -m soulmap_devtools.cli.eval_responses`) uses synthetic test cases defined
in `evals/`. It does not use real user data.

## Biometric and Wearable Data

`src/soulmap_runtime/experimental/biometric_ingest.py` contains logic for parsing wearable data if you choose
to provide it. Any such data is processed locally within a single session and is not
stored or transmitted by the SoulMap AI codebase.

## Dependencies

SoulMap AI's Python dependencies are listed in `pyproject.toml`. No dependency sends
telemetry or user data as part of this project's usage. All tools (Ruff, Pyright,
pytest) operate entirely locally.

## Security

If you discover a security concern, including prompt injection vectors or unsafe
handling of user-provided data, use the repository's private vulnerability reporting
flow on GitHub. In a full repository checkout, see `SECURITY.md` for the detailed
disclosure process.

## Questions

Open an issue in the GitHub repository or contact the repository owner directly.
