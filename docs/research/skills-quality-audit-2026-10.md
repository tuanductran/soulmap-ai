# Skills quality audit ledger - 2026-10-11

## Status and method

- Source of truth: `main` at the start of this audit batch; 75 Markdown files under `skills/` (26 framework files).
- First-pass inventory and heading/trigger/boundary keyword screening has been run across all 75 files.
- This is a **working ledger, not a declaration that all 75 files have passed a full semantic audit**. Files marked pending still require individual review of purpose, trigger precision, examples, references, neighboring overlap, and existing evaluation coverage.
- All 75 skill files now have an explicit targeted-review disposition in this working ledger. PRs #631, #633, #634, #635, #637, #638, #639, #640, #641, and #642 are merged; #636, #643, #644, and #645 contain reviewed changes pending final CI and merge. No skill file remains without a review disposition, but the final safety-policy change and other open PRs must pass required checks before the audit can close. The orchestration fallback wording was verified as aligned on current `main`.

## Confirmed findings across the current audit batches

1. `skills/frameworks/dark-night-of-soul.md`: removed claims that a spiritual "Dark Night" is distinct from depression; clarified that chat cannot distinguish causes, added support/referral thresholds, and reaffirmed crisis/de-escalation priority.
2. `skills/frameworks/fear-of-visibility.md`: removed the implied "ancestral memory" explanation as a default cause; ancestry/family history remains a possibility only when grounded in user-provided context.
3. `skills/frameworks/sacred-feminine-masculine.md`: changed universal claims about both energies being present in everyone to optional symbolic framing; behavior alone must not be treated as evidence of a missing "energy".
4. `skills/brand/surfaces-and-scope.md`, `skills/meta/response-structure.md`, `skills/meta/orchestration.md`, `skills/meta/framework-template-map.md`, and `skills/frameworks/integration-celebration.md`: aligned question rules so a question is an optional invitation, not a quota. When used, it remains at most one and last; safety, mode, grief, trauma, preference, and readiness take precedence.
5. `skills/frameworks/creative-drought.md` and `skills/frameworks/perfectionism-paralysis.md`: removed predictive growth language and overconfident causal claims; explanations remain tentative and user-grounded.
6. `skills/frameworks/empath-boundary.md`: treats "absorbing emotions" as the user's description of an experience, not proof of literal emotional or energy transfer.
7. `skills/frameworks/conversation-synthesis.md`: makes the closing question optional when readiness, safety, or closure calls for none.
8. `skills/brand/competitive-differentiation.md` (PR #638 merged): replaces broad competitor assertions with sourced, dated statements from official product/privacy documentation.
9. `skills/safety/ethics-safety.md` (PR #639 merged): separates privacy/governance requirements from unverified claims about current operations and host-platform data handling.
10. Ten additional files in PR #640 align framework-specific closing-question instructions with the canonical readiness-aware rule; the PR is merged after all required checks passed.
11. `skills/frameworks/emotional-deescalation.md` and `skills/brand/visual-identity.md` (PR #641 merged): add a medical triage gate before grounding and remove unsupported claims that specific sound frequencies heal or ground.
12. `skills/frameworks/self-compassion.md`, `skills/frameworks/money-self-worth.md`, and `skills/frameworks/grief-companion.md` (PR #642 merged): qualify assumed protective motives and causal stories about money, and avoid assuming every grief relationship was loving.
13. `skills/voice/session-rituals.md`, `skills/meta/session-contract.md`, `skills/meta/stage-classifier.md`, and `skills/meta/resource-recommendations.md` (PR #643 pending): clarify host-platform memory ownership, make the Stage 2 question optional, and prevent optional channels from being mistaken for clinical or crisis resources.
14. `skills/meta/epistemic-guardrails.md` (PR #644 pending): align symbolic-system consent with the current-session rule and make questions optional when readiness or safety calls for none.
15. `skills/safety/whitelist-blacklist-system.md` (PR #645 pending): reorder the decision tree so safety/prohibited requests take priority, resolve the crisis-search contradiction, and separate evidence sources from perspective sources.

## External authoring references

- Anthropic's [Skill authoring best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) recommends concise, well-structured, tested skills; clear trigger descriptions; progressive disclosure where it helps; and real usage evaluations. This supports checking discoverability and actual use before splitting files merely because they are long.
- WHO's [Psychological First Aid guide](https://www.who.int/publications/i/item/9789241548205) emphasizes humane, practical support that respects dignity, culture, and abilities. WHO's guidance includes listening without pressuring people to talk. This is consistent with making reflective questions optional rather than mandatory.

## File-by-file ledger

Status meanings:

- **Targeted review + changed**: the file received deeper review and a concrete edit in a listed PR.
- **Inventory screened; semantic review pending**: the file is confirmed in the current tree and received first-pass structural/keyword screening, but is not yet individually signed off.

### `skills/brand/`

- [x] `skills/brand/brand-doctrine.md` - Reviewed; no change warranted: this is normative brand doctrine and the promise is phrased as a design aim, not a guarantee.
- [x] `skills/brand/brand-positioning.md` - Reviewed; no change warranted: explicitly excludes prediction, diagnosis, and spiritual authority; promises are bounded.
- [x] `skills/brand/competitive-differentiation.md` - Targeted review and changes in PR #638; pending CI/merge.
- [x] `skills/brand/consciousness-framework.md` - Reviewed; no change warranted: the 3D/5D terms appear only in the avoid/translate table, while core states are relational rather than a hierarchy.
- [x] `skills/brand/content-pillars.md` - Reviewed; no change warranted: percentage allocations are internal editorial planning, and the content filters prohibit prediction, spiritual inflation, and dependency hooks.
- [x] `skills/brand/founder-personal-brand.md` - Reviewed; no change warranted: founder voice is a calibration layer, explicitly subordinate to safety, non-prediction, and non-diagnosis doctrine.
- [x] `skills/brand/message-hierarchy.md` - Reviewed; no change warranted: public positioning preserves non-therapist, non-guru, non-diagnosis, and non-prediction boundaries.
- [x] `skills/brand/research-backing.md` - Targeted review in #633; see the linked PR history.
- [x] `skills/brand/surfaces-and-scope.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/brand/visual-identity.md` - Targeted review and changes in merged PR #641.

### `skills/frameworks/`

- [x] `skills/frameworks/ancestral-patterns.md` - Targeted review in #635; see the linked PR history.
- [x] `skills/frameworks/anger-companion.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/conversation-synthesis.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/creative-drought.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/dark-night-of-soul.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/frameworks/divine-guidance.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/frameworks/emotional-deescalation.md` - Targeted review and changes in PR #641; pending CI/merge.
- [x] `skills/frameworks/empath-boundary.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/existential-companion.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/frameworks/fear-of-visibility.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/frameworks/feminine-masculine-dynamics.md` - Reviewed; no change warranted in this pass: the file already frames polarity symbolically and prohibits essentialist gender claims.
- [x] `skills/frameworks/grief-companion.md` - Targeted review and changes in merged PR #642.
- [x] `skills/frameworks/inner-parts.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/frameworks/integration-celebration.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/frameworks/life-direction.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/frameworks/meaning-integration.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/frameworks/money-self-worth.md` - Targeted review and changes in PR #642; pending CI/merge.
- [x] `skills/frameworks/pattern-mapper.md` - Reviewed; no change warranted: the non-labeling rule, minimum evidence requirement, and wait-for-a-second-story rule constrain pattern claims.
- [x] `skills/frameworks/perfectionism-paralysis.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/relationship-reflection.md` - Reviewed; no change warranted: abuse/coercion exceptions take priority and clinical attachment labels are prohibited.
- [x] `skills/frameworks/sacred-feminine-masculine.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/frameworks/self-compassion.md` - Targeted review and changes in PR #642; pending CI/merge.
- [x] `skills/frameworks/shadow-patterns.md` - Reviewed; no change warranted: possibility language is mandatory and real external harm must not be reframed as projection.
- [x] `skills/frameworks/somatic-wellbeing.md` - Targeted review in #634; see the linked PR history.
- [x] `skills/frameworks/soul-nourishment.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/frameworks/spiritual-purpose.md` - Targeted review in #640 pending CI/merge.

### `skills/meta/`

- [x] `skills/meta/deep-inquiry-bank.md` - Reviewed; no change warranted: one question is a per-turn maximum, with timing and silence rules rather than a requirement to ask every turn.
- [x] `skills/meta/epistemic-guardrails.md` - Targeted review and changes in PR #644; pending CI/merge.
- [x] `skills/meta/execution-pipeline.md` - Reviewed; no change warranted in this pass: Step 1 safety override bypasses normal framework selection, emergency handling is explicit, and the final safety filter checks crisis resources and dependency language.
- [x] `skills/meta/framework-template-map.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/meta/master-prompt.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/meta/observation-seed.md` - Reviewed; no change warranted: seeds require all stated conditions and are excluded after crisis, grief flooding, or unresolved distress.
- [x] `skills/meta/orchestration.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/meta/quick-reference.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/meta/redirect-templates.md` - Reviewed; no change warranted: the inner-work door is explicitly optional and practical requests must not be assigned a hidden psychological motive.
- [x] `skills/meta/resource-recommendations.md` - Targeted review and changes in PR #643; pending CI/merge.
- [x] `skills/meta/response-structure.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/meta/session-continuity.md` - Reviewed; no change warranted: context availability is conditional, incomplete memory is acknowledged, and fabricated continuity is prohibited.
- [x] `skills/meta/session-contract.md` - Targeted review and changes in PR #643; pending CI/merge.
- [x] `skills/meta/stage-classifier.md` - Targeted review and changes in PR #643; pending CI/merge.
- [x] `skills/meta/user-journey-stages.md` - Reviewed; no change warranted: stages are explicitly non-linear, non-prescriptive, and success is reduced dependency.

### `skills/safety/`

- [x] `skills/safety/boundaries-safety.md` - Reviewed; no change warranted in this pass: hard limits, dependency redirect, crisis referral, and memory/continuity safety are explicit and align with the current doctrine.
- [x] `skills/safety/dependency-detection.md` - Reviewed; no change warranted in this pass: the detector contract is Markdown-authored, high dependency takes routing priority, and the response avoids labeling the user unsafe.
- [x] `skills/safety/ethics-safety.md` - Targeted review and changes in PR #639; pending CI/merge.
- [x] `skills/safety/prompt-injection-defense.md` - Reviewed; no change warranted in this pass: it distinguishes malicious instruction override from ordinary emotional processing and preserves safety/scope limits.
- [x] `skills/safety/trauma-language.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/safety/whitelist-blacklist-system.md` - Targeted review and changes in PR #645; pending CI/merge.

### `skills/soulmate/`

- [x] `skills/soulmate/numerology-connection-lens.md` - Reviewed; no change warranted in this pass: the file prohibits computing or ranking compatibility and keeps numerology symbolic-only.
- [x] `skills/soulmate/partnership-patterns.md` - Targeted review in #640 pending CI/merge.
- [x] `skills/soulmate/soulmate-longing.md` - Targeted review in #640 pending CI/merge.

### `skills/spiritual/`

- [x] `skills/spiritual/astrology-symbolic-lens.md` - Reviewed; no change warranted in this pass: symbolic-only use, no horoscope generation, prediction, diagnosis, or compatibility verdict.
- [x] `skills/spiritual/chakra-affirmations.md` - Reviewed; no change warranted in this pass: explicit consent, symbolic framing, and no healing/destiny promises are already required.
- [x] `skills/spiritual/founder-numerology.md` - Reviewed; no change warranted in this pass: numbers-only handling and no personal identifiers are explicit.
- [x] `skills/spiritual/healing-metaphors.md` - Reviewed; no change warranted in this pass: metaphors are prompts for curiosity, not diagnosis or causal explanation.
- [x] `skills/spiritual/numerology-chakra-policy.md` - Reviewed; no change warranted in this pass: symbolic-only limits, consent, data minimization, and safety overrides are explicit.
- [x] `skills/spiritual/numerology-profile.md` - Reviewed; no change warranted in this pass: profile is explicitly non-evidential and cannot establish mission, rank, identity, or future.
- [x] `skills/spiritual/spiritual-discernment.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/spiritual/symbolic-report-handling.md` - Reviewed; no change warranted in this pass: report claims are separated from evidence, with consent, data minimization, and no prediction/prescription.
- [x] `skills/spiritual/tarot-symbolic-lens.md` - Reviewed; no change warranted in this pass: no card assignment, prediction, diagnosis, or compatibility verdict.

### `skills/voice/`

- [x] `skills/voice/persona-voice.md` - Reviewed; no change warranted: question ceiling, grief/crisis restraint, and anti-dependency closing rules are explicit.
- [x] `skills/voice/response-calibrator.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/voice/session-rituals.md` - Targeted review and changes in PR #643; pending CI/merge.

### `skills/writing/`

- [x] `skills/writing/disclosure-boundaries.md` - Reviewed; no change warranted: protects third-party privacy, distinguishes experience from inferred motive, and routes crisis above writing craft.
- [x] `skills/writing/platform-shapes.md` - Reviewed; no change warranted: surface claims are date-stamped and explicitly must not be repeated as current facts without qualification.
- [x] `skills/writing/reflection-to-page.md` - Reviewed; no change warranted: distinguishes private processing from public writing, avoids diagnosis, and prohibits engagement hooks.

## Next review queue

1. Review the remaining 67 files individually, starting with cross-cutting rule ownership and overlap in `skills/meta/quick-reference.md`, `skills/meta/deep-inquiry-bank.md`, `skills/meta/whitelist-blacklist-system.md`, and `skills/frameworks/conversation-synthesis.md`. Large size alone is not a defect; inspect retrieval/use paths before splitting.
2. Compare each framework's activation signals and priority against `SOULMAP.md`, `skills/meta/orchestration.md`, the registry, and existing routing/eval cases. Add a new framework only if a demonstrated distinct need is not covered by an existing one.
3. Review spiritual and soulmate content for symbolic-only framing, consent, non-prediction, and no metaphysical claims presented as fact.
4. Review brand and writing files for claims about research, platform features, or market conditions that may be stale or lack primary-source support.
5. Run the repository-required Markdown contracts, lint, tests, safety evaluations, and artifact builds for the final batches. No Python runtime or protected safety constants are changed in this batch.
