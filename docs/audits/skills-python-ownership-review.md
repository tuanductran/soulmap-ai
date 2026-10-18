# Read-only audit: Python-specific configuration in shipped skills

Tracking issue: [#714](https://github.com/tuanductran/soulmap-ai/issues/714)

## Scope and constraints

This document requests a **repository-wide, read-only CodeRabbit review**. It does not authorize edits to shipped skills, Python modules, tests, or runtime behavior. The purpose is to determine whether any content under `skills/**/*.md` stores Python-only keys, parser directives, implementation details, runtime configuration, or duplicate registry data that belongs to one canonical owner.

Do not treat structured Markdown, technical identifiers, metadata, or a mention of Python as leakage by itself. Markdown remains authoritative for product knowledge and behavioral doctrine. Python may own executable routing, enforcement, runtime-only configuration, and technical registries where repository contracts explicitly assign ownership. Do not move product knowledge into Python merely for uniformity.

## Required repository context

Read the current `main` HEAD, `AGENTS.md`, `SOULMAP.md`, `docs/engineering/repo-contract.md`, `docs/engineering/knowledge-architecture.md`, `docs/engineering/known-limitations.md`, relevant ADRs, `docs/ROADMAP.md`, current ownership audits/tests, and relevant packaging checks.

Inspect full diffs and rationale for the migration history, then follow later changes on current `main`:

- [#476: remove Python implementation leakage from skills](https://github.com/tuanductran/soulmap-ai/commit/2a10a47c5d65aaf301a5a489e647c801f8709ce6)
- [#481: enforce Markdown-native runtime contracts](https://github.com/tuanductran/soulmap-ai/commit/7504c80d3d990661007f9ddaaef43ec9a013d81a)
- [#483: knowledge-first orchestration boundaries](https://github.com/tuanductran/soulmap-ai/commit/89d6e84ed3ab638b0eba36d42e4adab05aba83d4)
- [#499: close Markdown architecture drift audit gaps](https://github.com/tuanductran/soulmap-ai/commit/616d7ca089f3c896222832afd8184bd4d0de7799)
- [#539/#541: move runtime source registry out of the skills tree](https://github.com/tuanductran/soulmap-ai/commit/1916b59d0b9215785aafc492754a42b164bd16a5)
- [later knowledge/runtime contract hardening and reverted/deferred migrations](https://github.com/tuanductran/soulmap-ai/commit/6e821bcd30d0cc83e6495481166068e0dd6fa198)

Do not repeat a previously rejected or reverted migration without new evidence. Do not assume these references exhaust the history.

## Review tasks

Audit all shipped `skills/**/*.md` and relevant metadata/entrypoint files. Trace each suspected key or value to its real consumer in `src/soulmap/runtime/`, `src/soulmap/devtools/`, tests, and packaging.

Classify each candidate as:

1. Canonical product knowledge - keep in Markdown.
2. Runtime-owned configuration/contract - possible Python/runtime owner only if supported by current contracts/history.
3. Technical identifier or portable interface - not automatically leakage; justify why it exists.
4. Duplicated or stale knowledge/runtime metadata - identify all copies and the authoritative owner.
5. Intentional exception / false positive - explain why it is valid.

Look for Python-only schemas/directives, duplicate defaults/mappings/thresholds/selector labels/registry entries, runtime code consuming implementation-only skill metadata, obsolete paths/contracts from migrations, and gaps or false positives in ownership tests and packaging validation.

For each finding report exact path and line/heading, classification, consuming code, tests, history/ADR evidence, severity, canonical owner, shipped/package impact, migration risk, and a minimal recommendation. Distinguish proven defects from preferences. Explicitly name clean areas and intentional exceptions. If evidence is insufficient, state the open question rather than guessing.

## Non-negotiable limits

- **Do not edit any file as part of this review.**
- Do not create follow-up branches or PRs from this review.
- Do not change detector semantics or weaken safety checks.
- Do not perform broad refactors or mass migrations.
- Recommend a follow-up implementation PR only if a concrete defect is proven and a minimal safe plan with regression guards is provided. Await maintainer approval before implementing it.

Return a findings-first report tied to the current `main` HEAD and the exact files/history actually inspected.
