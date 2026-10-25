# SoulMap Skills Runtime Ownership Audit (2026-10)

## Scope and source of truth

- Audited ref: `main` at `62670446f53acd2f225dbed448c739cbc0391bd5`.
- Inventory: 75 Markdown files under `skills/**/*.md`.
- This is a read-only ownership audit and inventory change only. It does not alter runtime behavior, skill content, safety policy, routing, or protected safety modules/constants.
- Classification describes how a file is used by the repository, not whether its prose is good or bad.

## Classification rules

1. **Runtime-parsed contract** - Python reads structured content and turns it into runtime configuration, thresholds, patterns, or routing decisions. This is data for Python even though the source format is Markdown.
2. **Runtime knowledge source** - a runtime detector or knowledge loader reads the file, typically extracting domain signal groups, labels, patterns, or scoring inputs.
3. **Structure / build / prompt source** - the file is consumed by packaging, skill composition, source mapping, or as an AI-facing instruction; it is not confirmed here as a Python-parsed decision table.
4. **Knowledge-only candidate** - no direct runtime consumer was identified in the inspected source registry/runtime loaders. This does not mean the file is unused by Claude, packaging, tests, or other tools.

## Confirmed architecture findings

### Structured Markdown is currently executable runtime configuration

- `skills/meta/stage-classifier.md` is parsed by `src/soulmap/runtime/knowledge/stage_classifier.py`. The parser reads stage headings, keyword lists, thresholds, recency multipliers, and the "Runtime enforcement contract" settings/role/recommendation tables.
- `skills/meta/orchestration.md` is parsed by `src/soulmap/runtime/knowledge/orchestration_source.py`. It reads scalar settings, runtime instructions, primary/secondary priority tables, and intensity fallbacks.
- `skills/safety/dependency-detection.md` supplies regex patterns and context-exclusion rows consumed by `src/soulmap/runtime/detectors/dependency_detector.py`.
- `skills/frameworks/integration-celebration.md` supplies score weights consumed by `src/soulmap/runtime/knowledge/celebration_source.py`.
- `skills/meta/framework-template-map.md` is consumed by the framework/template routing source.
- Additional detector-specific Markdown files are loaded through the runtime knowledge/source registry; see the per-file matrix below.

**Interpretation:** these files are not "pure prose" from Python's perspective. Their content is part of the runtime interface. A table heading, row label, threshold, regex, or setting can be a de-facto schema/identifier when code looks it up by that exact text. The Markdown format itself is not the problem; the ownership contract is.

### Not every underscore or code-looking phrase is a Python key

The audit must distinguish:

- natural-language semantic labels used by a skill as ordinary content;
- placeholders intended for AI-facing templates, such as `{theme}` or `{guidance}`;
- parser section names and table labels that Python explicitly consumes;
- implementation identifiers that should be owned by Python rather than copied into a skill.

A global deletion/rewrite of underscores, placeholders, or all structured tables would break valid knowledge and may change routing or safety behavior. No blanket normalization is recommended.

### Safety boundary

No changes were made to `safety.py`, `crisis_detector.py`, `CRISIS_TIER1`, `CRISIS_TIER2`, or `GRANDIOSITY_SIGNALS`. `MISALIGNMENT_SIGNALS` is not modified. This audit does not recommend moving or weakening crisis-response safety rules as part of a content cleanup.

## File-by-file matrix (75 files)

Legend:

- **R-CONTRACT**: confirmed Python-parsed runtime contract / structured runtime data.
- **R-SOURCE**: runtime knowledge source or detector input; Python consumer is known from the source registry or detector/loader.
- **AI/BUILD**: primarily AI-facing instruction or packaging/composition source; no Python decision-table consumer confirmed in this audit.
- **CONTENT**: knowledge content; no direct Python runtime data consumer confirmed in this audit.
- **REVIEW**: content has structured material or likely indirect use; inspect before moving/rewriting. Classification is intentionally conservative.

| Skill Markdown | Classification | Ownership note |
|---|---|---|
| `skills/brand/brand-doctrine.md` | CONTENT | Brand doctrine; no direct runtime data consumer confirmed. |
| `skills/brand/brand-positioning.md` | CONTENT | Brand positioning content. |
| `skills/brand/competitive-differentiation.md` | CONTENT | Brand strategy content. |
| `skills/brand/consciousness-framework.md` | CONTENT | Conceptual framework content. |
| `skills/brand/content-pillars.md` | CONTENT | Content strategy. |
| `skills/brand/founder-personal-brand.md` | CONTENT | Founder-brand guidance. |
| `skills/brand/message-hierarchy.md` | CONTENT | Messaging guidance. |
| `skills/brand/research-backing.md` | CONTENT | Research and evidence guidance. |
| `skills/brand/surfaces-and-scope.md` | CONTENT | Product/content scope guidance. |
| `skills/brand/visual-identity.md` | CONTENT | Visual identity guidance. |
| `skills/frameworks/ancestral-patterns.md` | R-SOURCE | Detector-specific knowledge source; preserve semantic signal meaning. |
| `skills/frameworks/anger-companion.md` | R-SOURCE | Detector/knowledge loader consumes structured signal/scoring content. |
| `skills/frameworks/conversation-synthesis.md` | R-SOURCE | Synthesis knowledge source; preserve topic/semantic labels. |
| `skills/frameworks/creative-drought.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/dark-night-of-soul.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/divine-guidance.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/emotional-deescalation.md` | R-SOURCE | Registered runtime detection source; safety-adjacent, so preserve semantics. |
| `skills/frameworks/empath-boundary.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/existential-companion.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/fear-of-visibility.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/feminine-masculine-dynamics.md` | CONTENT | Framework guidance; no direct Python data consumer confirmed. |
| `skills/frameworks/grief-companion.md` | R-SOURCE | Detector-specific knowledge source; preserve grief-language nuance. |
| `skills/frameworks/inner-parts.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/integration-celebration.md` | R-CONTRACT | Celebration weights/configuration are parsed by Python. |
| `skills/frameworks/life-direction.md` | R-SOURCE | Direction detector/knowledge loader consumes structured signal content. |
| `skills/frameworks/meaning-integration.md` | R-SOURCE | Registered runtime detection source. |
| `skills/frameworks/money-self-worth.md` | CONTENT | Framework guidance; no direct Python data consumer confirmed. |
| `skills/frameworks/pattern-mapper.md` | R-SOURCE | Python extracts structured pattern knowledge/sections. |
| `skills/frameworks/perfectionism-paralysis.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/relationship-reflection.md` | CONTENT | Framework guidance; no direct Python data consumer confirmed. |
| `skills/frameworks/sacred-feminine-masculine.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/self-compassion.md` | R-SOURCE | Registered runtime detection signal source; no separate contract/guidance section is registered. |
| `skills/frameworks/shadow-patterns.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/somatic-wellbeing.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/soul-nourishment.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/frameworks/spiritual-purpose.md` | R-SOURCE | Detector-specific knowledge source. |
| `skills/meta/deep-inquiry-bank.md` | AI/BUILD | Prompt/question bank; no Python decision-table consumer confirmed. |
| `skills/meta/epistemic-guardrails.md` | AI/BUILD | AI-facing epistemic guidance. |
| `skills/meta/execution-pipeline.md` | AI/BUILD | Process/instruction content; verify build references before relocation. |
| `skills/meta/framework-template-map.md` | R-CONTRACT | Python uses framework/template mapping for routing. |
| `skills/meta/master-prompt.md` | AI/BUILD | AI-facing prompt composition. |
| `skills/meta/observation-seed.md` | AI/BUILD | Observation seed content. |
| `skills/meta/orchestration.md` | R-CONTRACT | Python parses routing priorities, scalar settings, fallbacks, and runtime instructions. |
| `skills/meta/quick-reference.md` | AI/BUILD | Quick-reference content. |
| `skills/meta/redirect-templates.md` | AI/BUILD | Response templates; placeholders are valid unless runtime treats them as code keys. |
| `skills/meta/resource-recommendations.md` | AI/BUILD | Recommendation guidance. |
| `skills/meta/response-structure.md` | AI/BUILD | Response structure guidance. |
| `skills/meta/session-continuity.md` | AI/BUILD | Session continuity guidance. |
| `skills/meta/session-contract.md` | REVIEW | Contract-like content; verify exact runtime/build consumer before editing. |
| `skills/meta/stage-classifier.md` | R-CONTRACT | Python parses stage keywords, weights, thresholds, recency multipliers, memory rules, and stage mappings. |
| `skills/meta/user-journey-stages.md` | AI/BUILD | AI-facing journey-stage guidance; do not assume same role as executable classifier. |
| `skills/safety/boundaries-safety.md` | REVIEW | Safety guidance; preserve semantics and safety boundaries. |
| `skills/safety/dependency-detection.md` | R-CONTRACT | Regex patterns and context-exclusion table are parsed by Python. |
| `skills/safety/ethics-safety.md` | REVIEW | Safety/ethics guidance; no blanket edits. |
| `skills/safety/prompt-injection-defense.md` | REVIEW | Security guidance; preserve exact behavioral protections. |
| `skills/safety/trauma-language.md` | REVIEW | Safety-adjacent language guidance. |
| `skills/safety/whitelist-blacklist-system.md` | R-CONTRACT | Registered source for Python's runtime classification contract; preserve safety semantics. |
| `skills/soulmate/numerology-connection-lens.md` | CONTENT | Domain knowledge; no direct Python data consumer confirmed. |
| `skills/soulmate/partnership-patterns.md` | R-SOURCE | Partnership-pattern detector/knowledge source. |
| `skills/soulmate/soulmate-longing.md` | R-SOURCE | Soulmate-longing detector/knowledge source. |
| `skills/spiritual/astrology-symbolic-lens.md` | CONTENT | Symbolic lens content. |
| `skills/spiritual/chakra-affirmations.md` | CONTENT | Affirmation content. |
| `skills/spiritual/founder-numerology.md` | CONTENT | Numerology content. |
| `skills/spiritual/healing-metaphors.md` | CONTENT | Metaphor guidance. |
| `skills/spiritual/numerology-chakra-policy.md` | REVIEW | Policy-like content; inspect any downstream consumer before changing. |
| `skills/spiritual/numerology-profile.md` | CONTENT | Numerology profile guidance. |
| `skills/spiritual/spiritual-discernment.md` | R-SOURCE | Spiritual-discernment knowledge source. |
| `skills/spiritual/symbolic-report-handling.md` | REVIEW | Report-handling guidance; verify packaging/runtime references. |
| `skills/spiritual/tarot-symbolic-lens.md` | CONTENT | Symbolic lens content. |
| `skills/voice/persona-voice.md` | AI/BUILD | Voice/persona guidance. |
| `skills/voice/response-calibrator.md` | REVIEW | Calibration guidance; verify if any runtime consumes structured thresholds. |
| `skills/voice/session-rituals.md` | AI/BUILD | Session ritual guidance. |
| `skills/writing/disclosure-boundaries.md` | REVIEW | Disclosure constraints; preserve claims and safety semantics. |
| `skills/writing/platform-shapes.md` | CONTENT | Platform writing guidance. |
| `skills/writing/reflection-to-page.md` | CONTENT | Writing guidance. |

## Minimal remediation plan

Do not bulk-rewrite all Skills and do not remove every underscore or placeholder. The smallest safe sequence is:

1. **Define the boundary explicitly:** Skills contain AI-facing knowledge and natural-language guidance. They must not contain implementation identifiers whose only purpose is to satisfy Python lookups, nor executable code snippets intended to be copied into runtime.
2. **Move only implementation-owned binding names to one central Python-owned registry/schema.** Human-readable section titles can remain if they are part of a deliberate document contract; opaque runtime keys should not be duplicated in prose.
3. **Separate prose from runtime configuration where the user requires Skills to be pure content.** The confirmed candidates are the executable portions of `orchestration.md`, `stage-classifier.md`, `dependency-detection.md`, `integration-celebration.md`, and `framework-template-map.md`. Do this in a dedicated behavior-preserving change, not a bulk cleanup. Preserve all existing rule values, regexes, thresholds, ordering, and routing outcomes.
4. **Add contract tests** that fail if a new Python-owned identifier or executable implementation block is introduced into `skills/**/*.md`, while allowing natural-language semantic labels and valid AI-facing placeholders.
5. **Prove equivalence before merging:** compare current vs refactored outputs for stage classification, framework selection, dependency detection, and celebration scoring; run the complete CI/safety suite and request CodeRabbit review. No merge until checks and review are clean.

## Explicitly not recommended

- Do not treat every snake_case token as a code key.
- Do not remove AI-facing placeholders such as `{theme}` or `{guidance}` without proving they are runtime identifiers.
- Do not change crisis/safety constants or weaken safety rules as part of this audit.
- Do not modify `main` directly.
- Do not claim the files marked CONTENT are unused overall; the classification only means no direct Python runtime data consumer was confirmed.

## Audit limitation

The 75-file inventory is complete. Direct consumers and executable contracts are marked where established from the runtime source registry and loader implementations. Entries marked REVIEW are intentionally conservative: before any move, inspect the relevant packager, prompt composer, tests, and any non-Python consumer so that valid AI-facing content is not mistaken for runtime configuration.
