# Runtime knowledge ownership follow-up (2026-11-13)

## Scope and source of truth

- Audited ref: `main` at `2fd59638d3cc3568ce3572fae490fed8ee65fd2b`.
- Current inventory: 75 Markdown files under `skills/**/*.md`.
- This is a focused follow-up to the October 2026 file-by-file audit. It verifies the current ownership split for the main runtime contracts and the behavior of both ownership audit commands.
- Evidence reviewed: `runtime_config.py`, the stage/orchestration/celebration knowledge loaders, `dependency_detector.py`, the corresponding Markdown sources, `audit/knowledge.py`, and `audit/ownership.py`.
- No runtime code, safety policy, or protected safety module/constant was changed.

## Current ownership principle

**Markdown carries semantic knowledge and human-readable guidance. Python owns executable configuration and enforcement.**

A Markdown table may still be parsed when it intentionally supplies semantic phrases or user-facing guidance. That does not make every scoring weight, threshold, routing priority, or policy switch Markdown-owned.

## Verified runtime split

| Domain | Markdown-owned knowledge | Python-owned configuration |
|---|---|---|
| Stage classification | Stage headings and names, semantic keyword signals, conversational roles, and recommendations from `skills/meta/stage-classifier.md` | Keyword weights, thresholds, recency multipliers, memory minimums, close-score delta, first-session limits, and anti-regression settings in `STAGE_CLASSIFIER_CONFIG` |
| Orchestration | Human-readable mode guidance from `skills/meta/orchestration.md`; the decision tree remains explanatory doctrine | Scalar policy values, primary/secondary routing priorities, and intensity fallbacks in `ORCHESTRATION_CONFIG` |
| Dependency detection | Semantic signal groups, regex expressions, context-exclusion cues, and response guidance from `skills/safety/dependency-detection.md` | Scoring weights and thresholds, context-exclusion policy switches, and clause-boundary rules |
| Celebration | Detection signal groups, negative overrides, confirmation signals, assistant anchors, and response guidance from `skills/frameworks/integration-celebration.md` | Celebration scoring weights and thresholds in `CELEBRATION_SCORING` |

The values in the Python configuration are not duplicated in the Markdown sources as the authoritative runtime configuration. Keep future edits on the correct side of this boundary.

## Audit command responsibilities

### `soulmap audit-knowledge`

The implementation in `src/soulmap/devtools/audit/knowledge.py`:

- inventories Python/Markdown phrase overlaps and detector/Markdown exact overlaps;
- reports Python configuration constants as active or orphaned based on static references;
- identifies implementation references in Markdown under `skills/`, `templates/`, and `frameworks/`;
- can enforce a maximum number of knowledge duplicates.

It is a configuration/phrase-drift audit. It is not the source-registry ownership audit.

### `soulmap audit-knowledge-ownership`

The implementation in `src/soulmap/devtools/audit/ownership.py`:

- requires `runtime_skill_path()` calls to use literal identifiers registered in `source_registry.py`;
- reports unregistered source identifiers;
- reports registry entries with no runtime consumer;
- reports direct `default_skill_path("skills/...")` calls that bypass the source registry.

It does not audit package membership or verify the complete contents of build artifacts. Those claims must be checked by the relevant packaging and artifact-verification tools.

## Safety boundary

Crisis detection remains a deliberate Python-owned exception. The per-language crisis packs and crisis detector use static, human-authored Python constants rather than Markdown-loaded phrase lists. This follow-up does not propose migrating or modifying those modules.

Do not modify `safety.py`, `crisis_detector.py`, `CRISIS_TIER1`, `CRISIS_TIER2`, or `GRANDIOSITY_SIGNALS` as part of an ownership-documentation cleanup. Preserve `MISALIGNMENT_SIGNALS`.

## Maintenance guidance

1. Read the current runtime consumer and loader before classifying a Markdown section as executable configuration.
2. Keep semantic phrases and AI-facing guidance in Markdown.
3. Keep scoring, thresholds, routing priorities, policy toggles, and implementation identifiers in Python.
4. Run both `uv run soulmap audit-knowledge` and `uv run soulmap audit-knowledge-ownership` after ownership changes.
5. Run the full CI and safety evaluation suite for behavior-affecting changes. Do not bulk-rewrite Markdown tables or move safety logic based on the historical October matrix.

## Limitations

This follow-up validates the current ownership split for the four domains above and the two audit commands. It is not a fresh reclassification of every one of the 75 skill files. The October file-by-file matrix remains a historical snapshot and should not be treated as current evidence for files not covered here.
