# Skills quality audit ledger - 2026-10-11

## Status and method

- Source of truth: `main` at the start of this audit batch; 75 Markdown files under `skills/` (26 framework files).
- First-pass inventory and heading/trigger/boundary keyword screening has been run across all 75 files.
- This is a **working ledger, not a declaration that all 75 files have passed a full semantic audit**. Files marked pending still require individual review of purpose, trigger precision, examples, references, neighboring overlap, and existing evaluation coverage.
- Twenty-one distinct skill files have now received targeted semantic review across the focused PR batches: #631, #633, #634, #635, and #637 are merged; #636 contains seven additional changes pending final CI and merge. Fifty-four files still require individual semantic disposition. The orchestration fallback wording was verified as aligned on current `main`. Do not close the parent audit issue until the remaining dispositions and required checks are complete.

## Confirmed findings fixed in this batch

1. `skills/frameworks/dark-night-of-soul.md`: removed claims that a spiritual "Dark Night" is distinct from depression; clarified that chat cannot distinguish causes, added support/referral thresholds, and reaffirmed crisis/de-escalation priority.
2. `skills/frameworks/fear-of-visibility.md`: removed the implied "ancestral memory" explanation as a default cause; ancestry/family history remains a possibility only when grounded in user-provided context.
3. `skills/frameworks/sacred-feminine-masculine.md`: changed universal claims about both energies being present in everyone to optional symbolic framing; behavior alone must not be treated as evidence of a missing "energy".
4. `skills/brand/surfaces-and-scope.md`, `skills/meta/response-structure.md`, `skills/meta/orchestration.md`, `skills/meta/framework-template-map.md`, and `skills/frameworks/integration-celebration.md`: aligned question rules so a question is an optional invitation, not a quota. When used, it remains at most one and last; safety, mode, grief, trauma, preference, and readiness take precedence.

## External authoring references

- Anthropic's [Skill authoring best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) recommends concise, well-structured, tested skills; clear trigger descriptions; progressive disclosure where it helps; and real usage evaluations. This supports checking discoverability and actual use before splitting files merely because they are long.
- WHO's [Psychological First Aid guide](https://www.who.int/publications/i/item/9789241548205) emphasizes humane, practical support that respects dignity, culture, and abilities. WHO's guidance includes listening without pressuring people to talk. This is consistent with making reflective questions optional rather than mandatory.

## File-by-file ledger

Status meanings:
- **Targeted review + changed**: the file received deeper review in this batch and a concrete edit.
- **Inventory screened; semantic review pending**: the file is confirmed in the current tree and received first-pass structural/keyword screening, but is not yet individually signed off.

### `skills/brand/`

- [ ] `skills/brand/brand-doctrine.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/brand-positioning.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/competitive-differentiation.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/consciousness-framework.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/content-pillars.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/founder-personal-brand.md` - Inventory screened; semantic review pending.
- [ ] `skills/brand/message-hierarchy.md` - Inventory screened; semantic review pending.
- [x] `skills/brand/research-backing.md` - Targeted review in #633; see the linked PR history.
- [x] `skills/brand/surfaces-and-scope.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/brand/visual-identity.md` - Inventory screened; semantic review pending.

### `skills/frameworks/`

- [x] `skills/frameworks/ancestral-patterns.md` - Targeted review in #635; see the linked PR history.
- [ ] `skills/frameworks/anger-companion.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/conversation-synthesis.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/creative-drought.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/dark-night-of-soul.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/frameworks/divine-guidance.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/emotional-deescalation.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/empath-boundary.md` - Targeted review in #637; see the linked PR history.
- [ ] `skills/frameworks/existential-companion.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/fear-of-visibility.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/frameworks/feminine-masculine-dynamics.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/grief-companion.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/inner-parts.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/frameworks/integration-celebration.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/frameworks/life-direction.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/meaning-integration.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/money-self-worth.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/pattern-mapper.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/perfectionism-paralysis.md` - Targeted review in #637; see the linked PR history.
- [ ] `skills/frameworks/relationship-reflection.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/sacred-feminine-masculine.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/frameworks/self-compassion.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/shadow-patterns.md` - Inventory screened; semantic review pending.
- [x] `skills/frameworks/somatic-wellbeing.md` - Targeted review in #634; see the linked PR history.
- [ ] `skills/frameworks/soul-nourishment.md` - Inventory screened; semantic review pending.
- [ ] `skills/frameworks/spiritual-purpose.md` - Inventory screened; semantic review pending.

### `skills/meta/`

- [ ] `skills/meta/deep-inquiry-bank.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/epistemic-guardrails.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/execution-pipeline.md` - Inventory screened; semantic review pending.
- [x] `skills/meta/framework-template-map.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/meta/master-prompt.md` - Targeted review in #631; see the linked PR history.
- [ ] `skills/meta/observation-seed.md` - Inventory screened; semantic review pending.
- [x] `skills/meta/orchestration.md` - Targeted review + changed; validate in PR CI.
- [x] `skills/meta/quick-reference.md` - Targeted review in #631; see the linked PR history.
- [ ] `skills/meta/redirect-templates.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/resource-recommendations.md` - Inventory screened; semantic review pending.
- [x] `skills/meta/response-structure.md` - Targeted review + changed; validate in PR CI.
- [ ] `skills/meta/session-continuity.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/session-contract.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/stage-classifier.md` - Inventory screened; semantic review pending.
- [ ] `skills/meta/user-journey-stages.md` - Inventory screened; semantic review pending.

### `skills/safety/`

- [ ] `skills/safety/boundaries-safety.md` - Inventory screened; semantic review pending.
- [ ] `skills/safety/dependency-detection.md` - Inventory screened; semantic review pending.
- [ ] `skills/safety/ethics-safety.md` - Inventory screened; semantic review pending.
- [ ] `skills/safety/prompt-injection-defense.md` - Inventory screened; semantic review pending.
- [x] `skills/safety/trauma-language.md` - Targeted review in #631; see the linked PR history.
- [ ] `skills/safety/whitelist-blacklist-system.md` - Inventory screened; semantic review pending.

### `skills/soulmate/`

- [ ] `skills/soulmate/numerology-connection-lens.md` - Inventory screened; semantic review pending.
- [ ] `skills/soulmate/partnership-patterns.md` - Inventory screened; semantic review pending.
- [ ] `skills/soulmate/soulmate-longing.md` - Inventory screened; semantic review pending.

### `skills/spiritual/`

- [ ] `skills/spiritual/astrology-symbolic-lens.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/chakra-affirmations.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/founder-numerology.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/healing-metaphors.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/numerology-chakra-policy.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/numerology-profile.md` - Inventory screened; semantic review pending.
- [x] `skills/spiritual/spiritual-discernment.md` - Targeted review in #631; see the linked PR history.
- [ ] `skills/spiritual/symbolic-report-handling.md` - Inventory screened; semantic review pending.
- [ ] `skills/spiritual/tarot-symbolic-lens.md` - Inventory screened; semantic review pending.

### `skills/voice/`

- [ ] `skills/voice/persona-voice.md` - Inventory screened; semantic review pending.
- [x] `skills/voice/response-calibrator.md` - Targeted review in #631; see the linked PR history.
- [ ] `skills/voice/session-rituals.md` - Inventory screened; semantic review pending.

### `skills/writing/`

- [ ] `skills/writing/disclosure-boundaries.md` - Inventory screened; semantic review pending.
- [ ] `skills/writing/platform-shapes.md` - Inventory screened; semantic review pending.
- [ ] `skills/writing/reflection-to-page.md` - Inventory screened; semantic review pending.

## Next review queue

1. Review the remaining 67 files individually, starting with cross-cutting rule ownership and overlap in `skills/meta/quick-reference.md`, `skills/meta/deep-inquiry-bank.md`, `skills/meta/whitelist-blacklist-system.md`, and `skills/frameworks/conversation-synthesis.md`. Large size alone is not a defect; inspect retrieval/use paths before splitting.
2. Compare each framework's activation signals and priority against `SOULMAP.md`, `skills/meta/orchestration.md`, the registry, and existing routing/eval cases. Add a new framework only if a demonstrated distinct need is not covered by an existing one.
3. Review spiritual and soulmate content for symbolic-only framing, consent, non-prediction, and no metaphysical claims presented as fact.
4. Review brand and writing files for claims about research, platform features, or market conditions that may be stale or lack primary-source support.
5. Run the repository-required Markdown contracts, lint, tests, safety evaluations, and artifact builds for the final batches. No Python runtime or protected safety constants are changed in this batch.
