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
- the shipped knowledge base in [skills/](skills/)
- the canonical Python runtime and safety logic in [src/soulmap/runtime/](src/soulmap/runtime/)
- the canonical local tooling in [src/soulmap/devtools/](src/soulmap/devtools/) and
  convenience wrappers in [scripts/](scripts/)
- the operational and maintainer docs in [docs/](docs/)
- the framework-neutral Soulmate foundation library in [src/soulmate/](src/soulmate/)
- the standalone Soulmate package and AI foundation-skill source in
  [packages/soulmate/](packages/soulmate/)

The repo is designed to keep brand, safety, packaging, and implementation aligned.
Soulmate is the reusable foundation layer; SoulMap remains the opinionated reflective
framework built on top of it.

## Soulmate foundation library

Soulmate is an independent, framework-neutral foundation for future consumers such as
SoulMap. Its public Python source lives in `src/soulmate/`, while standalone package
metadata and Soulmate-only AI foundation skills live under `packages/soulmate/`.
SoulMap may import approved public Soulmate APIs, but Soulmate never imports SoulMap or
its product doctrine, routing state, safety policy, voice, brand, or spiritual content.

The standalone `soulmate-ai` Python wheel and source distribution, currently marked
`Private :: Do Not Upload`, are local pre-release developer and review surfaces. The
Soulmate AI skill archive is built separately from the package-owned allow-list and is
not part of the root `dist/soulmap-ai.zip` or `dist/soulmap-ai.skill` artifacts. See the
[repository contract](docs/engineering/repo-contract.md) and [Soulmate release
checklist](docs/operations/SOULMATE-RELEASE-CHECKLIST.md) for the exact boundaries.

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
- [skills/](skills/), frameworks, brand doctrine, safety guidance, voice, and meta layers (including
  the shipped response and redirect templates in skills/meta/)
- [src/soulmap/runtime/](src/soulmap/runtime/), selectors, detectors, guards, and runtime support
- [src/soulmap/devtools/](src/soulmap/devtools/), canonical format, lint, eval, and packaging entry points
- [docs/](docs/), developer, tester, privacy, operations, and upload guidance

## Quick start

```bash
uv python install 3.11
bash scripts/bootstrap_venv.sh
uv run soulmap format
uv run soulmap lint
uv run soulmap test -n auto -q
```

`bash scripts/bootstrap_venv.sh` now syncs the local environment from `uv.lock` and
targets Python 3.11 explicitly.

## Run the website

```bash
uv run soulmap web
```

The local Python website defaults to `http://127.0.0.1:8765`. To export static files
for GitHub Pages, use `uv run soulmap web --export-static --output site --base-path /soulmap-ai`.
For repeated local edits, add `--incremental` to reuse a verified export when the web,
public Skill, lockfile and exporter inputs are unchanged.
See [docs/product/WEBSITE.md](docs/product/WEBSITE.md) for routes, responsive behavior,
workflow boundaries, and its deliberate separation from the shipped AI artifacts.

## Build artifacts

```bash
uv run soulmap build
uv run soulmap build --skill
```

Outputs:

- `dist/soulmap-ai.zip`, standard knowledge archive without `.claude-plugin/`
- `dist/soulmap-ai.skill`, skill package with `.claude-plugin/` preserved

For packaging and upload details, see [docs/operations/UPLOAD.md](docs/operations/UPLOAD.md).

## Distribution boundary

The Python wheel and source distribution are local developer/test tooling surfaces. They
provide the `soulmap` CLI and repository validation code, but they are not standalone
knowledge-base runtimes and do not replace the repository's `skills/` source tree.

For use in AI tools, import the generated `dist/soulmap-ai.skill` or
`dist/soulmap-ai.zip` artifact. Those artifacts are the supported distribution surface for
SoulMap doctrine and package knowledge; the Python distribution is not an AI Skill installer.

## Where to start

- doctrine and package truth: [AGENTS.md](AGENTS.md)
- structural source of truth: [docs/engineering/repo-contract.md](docs/engineering/repo-contract.md)
- safety architecture, end to end: [docs/engineering/safety-architecture.md](docs/engineering/safety-architecture.md)
- intentional architecture limitations: [docs/engineering/known-limitations.md](docs/engineering/known-limitations.md)
- Library vs Framework boundary: [docs/engineering/library-vs-framework.md](docs/engineering/library-vs-framework.md)
- project roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)
- developer workflow: [docs/engineering/DEV.md](docs/engineering/DEV.md)
- testing and eval workflow: [docs/engineering/TESTER.md](docs/engineering/TESTER.md)
- privacy and operations: [docs/operations/PRIVACY.md](docs/operations/PRIVACY.md), [docs/operations/OPERATIONS.md](docs/operations/OPERATIONS.md)

## For AI tools and local maintainer layers

Use [AGENTS.md](AGENTS.md) first.

If this checkout also contains local workflow layers, treat them as supplemental only:

- [`.claude/`](.claude/) for the local Claude workflow layer, see
  [`.claude/README.md`](.claude/README.md)

This layer does not replace [AGENTS.md](AGENTS.md).

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
