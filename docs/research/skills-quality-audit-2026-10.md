# Skills quality audit ledger - 2026-10-11

## Status and method

- Source of truth: `main` at the start of this audit batch; 75 Markdown files under `skills/` (26 framework files).
- First-pass inventory and heading/trigger/boundary keyword screening has been run across all 75 files.
- All 75 files now have an explicit targeted-review disposition for purpose, trigger precision, examples, boundaries, and neighboring overlap. This is not a claim of exhaustive line-by-line proof or complete evaluation coverage. Files with pending PR changes are reviewed but are not complete until required checks pass.
- All 75 skill files now have an explicit targeted-review disposition in this working ledger. PRs #631, #633, #634, #635, #636, #637, #638, #639, #640, #641, #642, #643, #644, and #645 are merged. All 75 files have an explicit targeted-review disposition; no file remains unreviewed in the inventory. Close the parent audit issue only after required post-merge checks pass on the final `main` head. The orchestration fallback wording was verified as aligned on current `main`.

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
13. `skills/voice/session-rituals.md`, `skills/meta/session-contract.md`, `skills/meta/stage-classifier.md`, and `skills/meta/resource-recommendations.md` (PR #643 merged): clarify host-platform memory ownership, make the Stage 2 question optional, and prevent optional channels from being mistaken for clinical or crisis resources.
14. `skills/meta/epistemic-guardrails.md` (PR #644 merged): align symbolic-system consent with the current-session rule and make questions optional when readiness or safety calls for none.
15. `skills/safety/whitelist-blacklist-system.md` (PR #645 merged): reorder the decision tree so safety/prohibited requests take priority, resolve the crisis-search contradiction, and separate evidence sources from perspective sources.
16. A post-merge cross-surface sweep found residual mandatory-question wording inside six framework/response-template surfaces and public onboarding copy, despite their newer optional-question guidance elsewhere in the same files. This follow-up makes inquiry explicitly optional in `dark-night-of-soul.md`, `sacred-feminine-masculine.md`, `empath-boundary.md`, `creative-drought.md`, `ancestral-patterns.md`, `perfectionism-paralysis.md`, the celebration template, FAQ/onboarding copy, the framework-author skill, and the response calibrator. The `optional_question_ceiling` contract now guards these surfaces.
17. A further consistency pass found an obsolete `resources first` directive in `emotional-deescalation.md`, pilot acceptance criteria that required resources before any reflection, a mandatory celebration question in the master prompt, a mandatory closing question in the numerology template, imperative question wording in the execution pipeline and inquiry bank, and a stale ordering claim in the response-contract comment. These now follow the canonical presence-first crisis policy and optional-question rule; contract coverage guards the Markdown surfaces. The protected crisis detector/resource metadata discrepancy remains tracked separately in issue #647.

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
- [x] `skills/brand/competitive-differentiation.md` - Targeted review and changes in merged PR #638.
- [x] `skills/brand/consciousness-framework.md` - Reviewed; no change warranted: the 3D/5D terms appear only in the avoid/translate table, while core states are relational rather than a hierarchy.
- [x] `skills/brand/content-pillars.md` - Reviewed; no change warranted: percentage allocations are internal editorial planning, and the content filters prohibit prediction, spiritual inflation, and dependency hooks.
- [x] `skills/brand/founder-personal-brand.md` - Reviewed; no change warranted: founder voice is a calibration layer, explicitly subordinate to safety, non-prediction, and non-diagnosis doctrine.
- [x] `skills/brand/message-hierarchy.md` - Reviewed; no change warranted: public positioning preserves non-therapist, non-guru, non-diagnosis, and non-prediction boundaries.
- [x] `skills/brand/research-backing.md` - Targeted review in #633; see the linked PR history.
- [x] `skills/brand/surfaces-and-scope.md` - Targeted review and changes in merged PR #636; required checks passed before merge.
- [x] `skills/brand/visual-identity.md` - Targeted review and changes in merged PR #641.

### `skills/frameworks/`

- [x] `skills/frameworks/ancestral-patterns.md` - Targeted review in #635; see the linked PR history.
- [x] `skills/frameworks/anger-companion.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/conversation-synthesis.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/creative-drought.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/dark-night-of-soul.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/frameworks/divine-guidance.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/emotional-deescalation.md` - Targeted review and changes in merged PR #641.
- [x] `skills/frameworks/empath-boundary.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/existential-companion.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/fear-of-visibility.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/frameworks/feminine-masculine-dynamics.md` - Reviewed; no change warranted in this pass: the file already frames polarity symbolically and prohibits essentialist gender claims.
- [x] `skills/frameworks/grief-companion.md` - Targeted review and changes in merged PR #642.
- [x] `skills/frameworks/inner-parts.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/frameworks/integration-celebration.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/frameworks/life-direction.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/meaning-integration.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/money-self-worth.md` - Targeted review and changes in merged PR #642.
- [x] `skills/frameworks/pattern-mapper.md` - Reviewed; no change warranted: the non-labeling rule, minimum evidence requirement, and wait-for-a-second-story rule constrain pattern claims.
- [x] `skills/frameworks/perfectionism-paralysis.md` - Targeted review in #637; see the linked PR history.
- [x] `skills/frameworks/relationship-reflection.md` - Reviewed; no change warranted: abuse/coercion exceptions take priority and clinical attachment labels are prohibited.
- [x] `skills/frameworks/sacred-feminine-masculine.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/frameworks/self-compassion.md` - Targeted review and changes in merged PR #642.
- [x] `skills/frameworks/shadow-patterns.md` - Reviewed; no change warranted: possibility language is mandatory and real external harm must not be reframed as projection.
- [x] `skills/frameworks/somatic-wellbeing.md` - Targeted review in #634; see the linked PR history.
- [x] `skills/frameworks/soul-nourishment.md` - Targeted review in merged PR #640.
- [x] `skills/frameworks/spiritual-purpose.md` - Targeted review in merged PR #640.

### `skills/meta/`

- [x] `skills/meta/deep-inquiry-bank.md` - Reviewed; no change warranted: one question is a per-turn maximum, with timing and silence rules rather than a requirement to ask every turn.
- [x] `skills/meta/epistemic-guardrails.md` - Targeted review and changes in merged PR #644.
- [x] `skills/meta/execution-pipeline.md` - Reviewed; no change warranted in this pass: Step 1 safety override bypasses normal framework selection, emergency handling is explicit, and the final safety filter checks crisis resources and dependency language.
- [x] `skills/meta/framework-template-map.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/meta/master-prompt.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/meta/observation-seed.md` - Reviewed; no change warranted: seeds require all stated conditions and are excluded after crisis, grief flooding, or unresolved distress.
- [x] `skills/meta/orchestration.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/meta/quick-reference.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/meta/redirect-templates.md` - Reviewed; no change warranted: the inner-work door is explicitly optional and practical requests must not be assigned a hidden psychological motive.
- [x] `skills/meta/resource-recommendations.md` - Targeted review and changes in merged PR #643.
- [x] `skills/meta/response-structure.md` - Targeted review + changed; corresponding PR merged and required CI checks passed.
- [x] `skills/meta/session-continuity.md` - Reviewed; no change warranted: context availability is conditional, incomplete memory is acknowledged, and fabricated continuity is prohibited.
- [x] `skills/meta/session-contract.md` - Targeted review and changes in merged PR #643.
- [x] `skills/meta/stage-classifier.md` - Targeted review and changes in merged PR #643.
- [x] `skills/meta/user-journey-stages.md` - Reviewed; no change warranted: stages are explicitly non-linear, non-prescriptive, and success is reduced dependency.

### `skills/safety/`

- [x] `skills/safety/boundaries-safety.md` - Reviewed; no change warranted in this pass: hard limits, dependency redirect, crisis referral, and memory/continuity safety are explicit and align with the current doctrine.
- [x] `skills/safety/dependency-detection.md` - Reviewed; no change warranted in this pass: the detector contract is Markdown-authored, high dependency takes routing priority, and the response avoids labeling the user unsafe.
- [x] `skills/safety/ethics-safety.md` - Targeted review and changes in merged PR #639.
- [x] `skills/safety/prompt-injection-defense.md` - Reviewed; no change warranted in this pass: it distinguishes malicious instruction override from ordinary emotional processing and preserves safety/scope limits.
- [x] `skills/safety/trauma-language.md` - Targeted review in #631; see the linked PR history.
- [x] `skills/safety/whitelist-blacklist-system.md` - Targeted review and changes in merged PR #645.

### `skills/soulmate/`

- [x] `skills/soulmate/numerology-connection-lens.md` - Reviewed; no change warranted in this pass: the file prohibits computing or ranking compatibility and keeps numerology symbolic-only.
- [x] `skills/soulmate/partnership-patterns.md` - Targeted review in merged PR #640.
- [x] `skills/soulmate/soulmate-longing.md` - Targeted review in merged PR #640.

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
- [x] `skills/voice/session-rituals.md` - Targeted review and changes in merged PR #643.

### `skills/writing/`

- [x] `skills/writing/disclosure-boundaries.md` - Reviewed; no change warranted: protects third-party privacy, distinguishes experience from inferred motive, and routes crisis above writing craft.
- [x] `skills/writing/platform-shapes.md` - Reviewed; no change warranted: surface claims are date-stamped and explicitly must not be repeated as current facts without qualification.
- [x] `skills/writing/reflection-to-page.md` - Reviewed; no change warranted: distinguishes private processing from public writing, avoids diagnosis, and prohibits engagement hooks.

## Closure criteria and follow-up

- The inventory contains 75/75 files with explicit targeted-review dispositions. Some files were changed; others were intentionally left unchanged because their current boundaries already met the audit criteria.
- The targeted PR batches (#631, #633-#645) are merged. The ledger was reconciled on 2026-10-12; CI, Python Compatibility, CodeQL, P-level governance, and knowledge/content checks passed on pre-update `main` at `eba5f3f6e284d56e17da7a70506b0a849ef2d556`. The ledger-only PR must pass the required checks before this audit is considered closed.
- This ledger records targeted semantic review and concrete dispositions; it does not claim that every file was rewritten or that content is exhaustively proven correct for every possible prompt.
- For future maintenance, split large knowledge files only when load paths and evaluations show a retrieval problem; add a framework only when a distinct unmet need is demonstrated; refresh platform and research claims against current primary sources.

## Follow-up audit - 2026-11-15

This follow-up was performed against `main` at `e2a902574f1821204284fb5ab528d32299bfb60a`, after the November documentation changes through #923. It is a targeted semantic follow-up, not a claim that every Markdown file has been re-reviewed line by line.

### Findings and remediation

1. `skills/frameworks/pattern-mapper.md`: the earlier disposition of no change warranted was too broad. Several lines still assigned grief, fear of being a burden, protective functions, or family-history explanations to recurring patterns. PR #915 removes those defaults, separates observable behavior from inferred motive, and makes pattern combinations conditional on independently reported evidence while preserving the parser-consumed `What it looks like` label.
2. `skills/meta/quick-reference.md`: the AI-identity response instructed the assistant to immediately infer deeper needs from the question. PR #916 now requires a direct answer and limits reflection to feelings or needs explicitly expressed by the user.
3. `skills/frameworks/grief-companion.md`: PR #917 requires loss or bereavement context before complicated-grief cues apply and removes `abusive` and `toxic relationship` as standalone grief signals. Ongoing harm is directed to relationship-safety guidance.
4. PR #914 was based on the earlier `b5b0252` main head and was superseded by #917, which was created from the current main head. The older PR was closed as superseded; no changes were merged from it.
5. `skills/meta/deep-inquiry-bank.md`: several questions presupposed that avoidance, withdrawal, fear, or relationship patterns served a protective function. PR #919 replaces these with neutral questions that let the user define or reject that framing.
6. `skills/frameworks/life-direction.md`: uncertainty, reluctance, and feeling lost were described with default explanations involving people-pleasing, suppressed wants, or disconnection from a former self. PR #920 qualifies these as possibilities and requires user confirmation.
7. `.claude/skills/framework-author/SKILL.md`: framework-authoring guidance instructed the writer to ask what an identity question was "really about". PR #921 makes exploration conditional on the user's expressed concern or invitation.
8. `skills/frameworks/shadow-patterns.md`: some section labels and examples still treated old wounds, worth concerns, or avoidance as default explanations. PR #928 marks these as hypotheses only when supported by the user's account, preserves parser-recognized headings required by detector tests, and removes assumed emotional-withdrawal motives from the descriptive text. Earlier PR #922 was closed unmerged after its branch was rebased.
9. The deterministic AI-identity example in `src/soulmap/devtools/evals/eval_responses.py` still inferred a hidden need even after the Markdown guidance was corrected. PR #923 aligns that evaluation example and its fixture with direct, non-inferential disclosure. This is a cross-surface evaluation fix, not a safety implementation change.
10. `skills/frameworks/ancestral-patterns.md`: some transition and inquiry language described a parent as the person who passed a wound. PR #924 makes the family connection user-described and keeps transmission or causation unproven.
11. `skills/meta/deep-inquiry-bank.md` and `skills/meta/redirect-templates.md`: a prompt assumed the user had learned to read others' reactions, and some identity/out-of-scope redirects inferred a wish to be heard or a hidden question. PR #925 makes these prompts direct and optional.
12. `skills/safety/whitelist-blacklist-system.md`: the harmful-spirituality refusal remains unchanged in substance; PR #926 replaces an "underneath the framework" phrase with a request to describe the concrete situation apart from its spiritual interpretation.
13. The wider Markdown scan covered all 201 Markdown paths in the current repository tree: 75 under `skills/` and 126 elsewhere. Targeted phrase screening was followed by manual review of flagged excerpts; this was not a line-by-line editorial review of all 201 files. PR #927 updates three public-facing templates where copy implied SoulMap could identify a hidden meaning or assigned motives to readers.

### Verification boundaries

- Each remediation is isolated in a domain-specific pull request.
- Required CI, Python Compatibility, CodeQL, and P-level safety governance checks must pass on the final PR head before merge consideration.
- No changes are made to protected safety implementation files or crisis signal constants.
- The 201-file Markdown screening is a targeted audit, not proof that every sentence has been semantically reviewed. Continue with staged line-level reviews of high-impact domains and cross-reference checks.
- PRs #915-#921, #923-#928 were merged only after their required checks succeeded and GitHub reported them mergeable. PR #922 and superseded PR #914 were closed unmerged. The audit-ledger PR #918 also passed its required checks and was merged.

## Follow-up audit - 2026-11-15 (Spiritual, Voice, Brand, Writing)

This follow-up was performed against `main` at `cae45027d392e4bb71ca13164b538f90f8f7405c`, after the remediation PRs listed below. It targeted 24 Markdown skill files across four domains. It is a focused semantic audit, not a line-by-line review of every file in the repository.

### Findings and remediation

1. **Voice:** `skills/voice/response-calibrator.md` allowed the assistant to assign possible intentions or protective functions to inner parts, perfectionism, and ancestral patterns, and to frame visibility as a threshold or distinguish intuition from fear. PR #930 makes these modes conditional on the user's own description and replaces therapist imitation with plain-language question guidance.
2. **Voice continuity and closing:** `skills/voice/session-rituals.md` allowed callbacks to prior-session breakthroughs based only on topic similarity and supplied closing examples that presumed insight or transformation. PR #930 requires the user to reopen the connection and grounds closing language in what the user actually described.
3. **Spiritual discernment:** `skills/spiritual/spiritual-discernment.md` used phrase lists as bypass/integration signals and included guidance that could infer hidden needs or emotional states from spiritual material. PR #931 states that phrases are contextual cues, never classifications, and asks rather than infers.
4. **Parser contract:** The runtime consumes the exact headings `Detection signal reference` and `Genuine Integration Signals` from `skills/spiritual/spiritual-discernment.md`. Renaming either heading caused CI/runtime-registry and detector regression failures. PR #931 restores both parser-consumed headings while retaining the clarified, non-classifying prose; the final-head CI and Python Compatibility checks then passed.
5. **Symbolic reports and numerology:** PR #931 clarifies that a direct request to explain a symbolic report permits discussion of its text, not validation of its claims, and distinguishes the product-level numerology tone guide from founder-facing tone anchors without combining them.
6. **Writing:** `skills/writing/platform-shapes.md` treated publishing to one person as avoidance of direct contact and assumed writers could not notice professional framing. `reflection-to-page.md` inferred motive from urgency and invalidated private processing as a form of writing. `disclosure-boundaries.md` used an overly categorical test for whose story was being told and overstated crisis-publication harm. PR #932 makes these prompts conditional, preserves both private and public writing as valid, and keeps crisis-resource guidance precise.
7. **Brand and state language:** `skills/brand/consciousness-framework.md` could be read as a taxonomy for assigning users to reactive, transitional, or integrated states. PR #935 defines the states as editorial lenses only and requires user-reported evidence. The same PR removes copy claiming to know what users actually need, replaces a self-asserted high-trust claim, and clarifies the scope of research evidence in metadata.
8. **Visual identity and body data:** `skills/brand/visual-identity.md` described the interface as a shared space and implied users should feel deeply seen without speaking, which conflicted with the bounded-tool and anti-dependency posture. PR #935 makes the design clearly humane but still a tool, and bases emoji use on user preference rather than presumed capacity. The same PR removes the instruction to infer or acknowledge emotion from body measurements.
9. **Public-repository privacy:** The repository is public, `pyproject.toml` includes `/skills` in source distributions, and the skill builder includes the `skills/` tree. `skills/brand/founder-personal-brand.md` contained a section explicitly labeled as private founder calibration. PR #934 removes that section from the current public tree and replaces it with a boundary directing private calibration to an access-controlled workspace. It also grounds the first-person origin copy. This change does not erase the prior content from Git history; no history rewrite was performed.
10. **Research metadata:** `skills/brand/research-backing.md` described its contents as peer-reviewed research despite also containing preprints, self-reported narratives, and regulatory findings. PR #935 corrects the metadata description. Key numerical claims were checked against the cited publisher/source records before retaining the version-specific wording.

### Verification and disposition

- PRs #930 (Voice), #931 (Spiritual), #932 (Writing), #934 (founder privacy), and #935 (Brand) were merged only after the final head passed CI, CodeQL, Python Compatibility, P-level safety governance, and autofix checks, with no unresolved review threads.
- PR #933 was closed unmerged after #934 changed the same founder-brand file; #935 is its rebased replacement and passed checks on the updated base.
- No protected safety implementation file, crisis detector implementation, or crisis signal constant was changed.
- The audit remains targeted. It does not certify every sentence in all 201 Markdown files or erase information from historical Git commits.

## Follow-up audit - 2026-11-15 (Frameworks and Meta cross-consistency)

This follow-up screened the 26 files inventoried under `skills/frameworks/` and the 14 files under `skills/meta/` against the current doctrine, voice, session, and epistemic boundaries. The pass used targeted semantic cross-review and manual inspection of flagged excerpts. It is not a line-by-line certification of every sentence or every possible interaction.

### Findings and remediation

1. **Quick reference:** PR #937 removed hidden-need inference from Twin Flame / Starseed handling, required independent support before noting pattern overlap, replaced rigid pronoun rules with an AI-identity boundary, aligned early-session guidance with the session contract, and clarified source verification and spiritual-bypass handling.
2. **Life direction:** PR #938 removed the premise that users already know their direction but are unwilling to say it. The framework now distinguishes values exploration from practical questions and genuine uncertainty, and offers the values lens only when it fits the user's stated concern and invitation.
3. **Framework cross-consistency:** PR #941 made cross-story value synthesis explicitly tentative; removed an assumed knowledge/avoidance example; distinguished shadow and visibility concerns by the user's stated account rather than assumed protective functions; made overlap conditional on evidence for both; softened the inner-parts beginner example; and removed hidden-cause or unspoken-family-belief assumptions from de-escalation, existential, and money-related guidance.
4. **Inquiry bank:** PR #943 replaced questions that presumed an unspoken answer, hidden common thread, internal cause, deeper pain, or unrequested support with neutral invitations. The one-question ceiling, timing, and readiness rules remain unchanged.
5. **First-session contract:** PR #945 replaced the practical-question opener that presumed the user already knew the answer. `SOULMAP.md` and `skills/meta/session-contract.md` now use the same uncertainty-aware wording.

### Verification and disposition

- PRs #937, #938, #941, #943, and #945 were merged only after the final PR head passed CI, CodeQL Python, Python Compatibility, P-level safety governance, and autofix.ci; GitHub reported each PR mergeable, with no unresolved review threads.
- PRs #939, #940, #942, and #944 were closed unmerged when their branches were superseded by branches based on the newer `main`. No changes from those stale-base PRs were merged.
- The changes were documentation-only. No parser-consumed runtime headings, Python runtime implementation, safety implementation files, or crisis signal constants were modified.
- The audit remains targeted. It does not certify every sentence in the repository or establish that all possible responses will behave correctly.
