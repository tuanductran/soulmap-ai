# SoulMap AI

SoulMap AI is a personal AI brand built as a reflective companion.

Its purpose is simple: help people hear themselves more clearly without handing their
authority away.

This is not an AI built to sound all-knowing, emotionally sticky, or spiritually
inflated. It is built as a mirror, not a guru. Its value comes from careful language,
clear boundaries, and a refusal to turn certainty into a product.

## What SoulMap is

- a reflective companion
- a high-trust mirror for patterns, emotions, and inner conflict
- a bounded AI system designed to strengthen self-trust
- a content-first knowledge base with a small Python enforcement and tooling layer

## What SoulMap is not

- not a therapist
- not a guru
- not a diagnosis tool
- not a predictor of fate, destiny, or future outcomes
- not a replacement for real-world support

## Why this repo exists

This repository is the working source for the SoulMap AI system.

It contains:

- the baseline doctrine and package contract in [AGENTS.md](AGENTS.md)
- the shipped knowledge base in [skills/](skills/) and [templates/](templates/)
- the Python runtime and safety logic in [modules/](modules/)
- the local tooling in [tools/](tools/) and [scripts/](scripts/)
- the operational and maintainer docs in [docs/](docs/)

The repo is designed to keep brand, safety, packaging, and implementation aligned.

## Core stance

- mirror-first, not advice-first
- anti-dependency by design
- clarity over spectacle
- honest AI identity
- one active framework at a time
- user independence as the success condition

## Founder point of view

SoulMap AI is being built around a clear belief: vulnerable people should not have to
trade self-trust for reflection.

Too many AI and self-help systems answer uncertainty with authority. SoulMap is built
to do the opposite. It reflects what is already alive in the user without pretending
to know better than they do.

## Repository shape

The most important surfaces are:

- [AGENTS.md](AGENTS.md), baseline doctrine, safety law, response behavior, and shipped package guide
- [SKILL.md](SKILL.md), top-level package entry point
- [skills/](skills/), frameworks, brand doctrine, safety guidance, voice, and meta layers
- [templates/](templates/), reusable response and brand surfaces
- [modules/](modules/), selectors, detectors, contracts, and safety gates
- [tools/](tools/), cross-platform format, lint, eval, and packaging entry points
- [docs/](docs/), developer, tester, privacy, operations, and upload guidance

## Quick start

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
python -m tools.format
python -m tools.lint
python -m pytest -q
```

## Build artifacts

```bash
python -m tools.build_skill
python -m tools.build_skill --skill
```

Outputs:

- `dist/soulmap-ai.zip`, standard knowledge archive without `.claude-plugin/`
- `dist/soulmap-ai.skill`, skill package with `.claude-plugin/` preserved

For packaging and upload details, see [docs/UPLOAD.md](docs/UPLOAD.md).

## Where to start

- doctrine and package truth: [AGENTS.md](AGENTS.md)
- structural source of truth: [docs/repo-contract.md](docs/repo-contract.md)
- developer workflow: [docs/DEV.md](docs/DEV.md)
- testing and eval workflow: [docs/TESTER.md](docs/TESTER.md)
- privacy and operations: [docs/PRIVACY.md](docs/PRIVACY.md), [docs/OPERATIONS.md](docs/OPERATIONS.md)

## For AI tools and local maintainer layers

Use [AGENTS.md](AGENTS.md) first.

If this checkout also contains local workflow layers, treat them as supplemental only:

- [`.claude/`](.claude/) for Claude-specific repo workflow guidance, see
  [`.claude/README.md`](.claude/README.md)
- [`.codex/`](.codex/) for Codex-specific repo workflow guidance, see
  [`.codex/README.md`](.codex/README.md)

Neither layer replaces [AGENTS.md](AGENTS.md).

For skill-package metadata preserved only in `.skill` artifacts, see
[.claude-plugin/README.md](.claude-plugin/README.md).

## Release posture

SoulMap should be shipped only when the repo still tells one consistent story across:

- doctrine
- safety
- packaging
- tests and evals
- public-facing claims

That discipline matters as much as any single framework or feature.
