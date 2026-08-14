# Launch readiness checklist

Use this checklist before calling SoulMap ready for release. This does not mean
"perfect forever." It means the shipped knowledge files are aligned enough to use
responsibly.

## Verification Map

| Area | Evidence type | Primary evidence |
| :--- | :--- | :--- |
| Package entry points | File review | [AGENTS.md](../AGENTS.md), [SKILL.md](../SKILL.md), [templates/README.md](README.md) |
| Brand alignment | Content review | [skills/brand/](../skills/brand/) and [templates/brand-copy.md](brand-copy.md) |
| Competitive positioning | Content review | [skills/brand/competitive-differentiation.md](../skills/brand/competitive-differentiation.md) |
| Research backing | Content review | [skills/brand/research-backing.md](../skills/brand/research-backing.md) |
| Regulatory positioning | Content review | Regulatory positioning notes remain current in the full repository |
| Safety alignment | Content review | [AGENTS.md](../AGENTS.md), [skills/safety/](../skills/safety/), [skills/meta/redirect-templates.md](../skills/meta/redirect-templates.md) |
| Framework coverage | Content review | [skills/frameworks/](../skills/frameworks/) and [skills/meta/quick-reference.md](../skills/meta/quick-reference.md) |
| Voice alignment | Content review | [skills/voice/](../skills/voice/) and [skills/meta/response-structure.md](../skills/meta/response-structure.md) |
| User trust commitments | Content review | [templates/user-charter.md](user-charter.md) |
| Privacy and data handling | Content review | Privacy and data-handling commitments remain current in the full repository |
| Public copy readiness | Content review | [templates/social-copy.md](social-copy.md), [templates/email-onboarding.md](email-onboarding.md) |
| Founder-facing copy readiness | Content review | [skills/brand/founder-personal-brand.md](../skills/brand/founder-personal-brand.md) and [templates/founder-copy.md](founder-copy.md) |
| Archive self-containment | Path review | shipped files do not depend on missing repo-only paths |
| Orchestration layer | Content review | [skills/meta/orchestration.md](../skills/meta/orchestration.md) priority hierarchy matches Python modules |
| Epistemic guardrails | Content review | [skills/meta/epistemic-guardrails.md](../skills/meta/epistemic-guardrails.md) covers all spiritual content categories |
| Stage classifier alignment | Content review | [skills/meta/stage-classifier.md](../skills/meta/stage-classifier.md) stage signal descriptions match the detection layer |
| Master prompt completeness | Content review | [skills/meta/master-prompt.md](../skills/meta/master-prompt.md) includes all 12 frameworks and 7 pipeline steps |
| Build freshness | Verification run | Build artifact checks are green in the full repository |
| Safety evals | Verification run | Safety evaluation suite is green in the full repository |
| Grouped routing and source evals | Verification run | Grouped eval suite is green and source markers still match the cited policy files |
| Golden eval cases | Verification run | Response-generation evaluation suite is green in the full repository |
| Cross-surface wording sync | Verification run | Markdown contract sync eval is green in the full repository |
| Active platform deployment | Static contract + manual acceptance | Integration metadata/artifact contract is green; active platforms have dated acceptance evidence |

## Positioning

- The one-sentence positioning is still clear and human-readable.
- SoulMap is described consistently as a reflective companion.
- Public-facing copy does not drift into guru, therapist, prophet, or prediction claims.
- The phrase "stop abandoning themselves" remains accurate to the product promise.

## Brand Integrity

- [skills/brand/SKILL.md](../skills/brand/SKILL.md) and
  [skills/brand/brand-positioning.md](../skills/brand/brand-positioning.md) still
  describe the same core promise.
- [skills/brand/surfaces-and-scope.md](../skills/brand/surfaces-and-scope.md) still
  cleanly separates live chat rules from public content and internal strategy.
- Templates reflect anti-dependency and return ownership to the user.
- Founder-facing copy still sounds like SoulMap's founder calibration layer, not a second doctrine.
- Safety language remains grounded and does not over-promise intimacy or certainty.
- The package still sounds like one brand across skills and templates.

## Safety and boundaries

- Crisis behavior is still handled before all reflective frameworks.
- Crisis references do not contradict AGENTS.md Rule 1 about immediate resources and no extended warm-up.
- First-session contract wording still matches the approved opener logic and skip rules.
- Dependency signals still redirect toward real-world support.
- Scope boundaries still decline diagnosis, prediction, and out-of-scope expert advice.
- The one-question rule and non-prescriptive posture are still protected.
- Rows still marked `partial` or `guidance-only` in `docs/engineering/safety-enforcement-matrix.md` are not being described elsewhere as fully runtime-enforced.
- Grouped evals still pass after edits to detector keywords, routing docs, or cited policy anchors.

## Product Surfaces

- Templates exist for brand copy, redirects, FAQ, response structure, and quick
  reference.
- Founder-facing reusable copy exists for bios, intros, and origin-story surfaces.
- The root files still explain what SoulMap is and how to use the package.
- The shipped directories still match the guidance described in [AGENTS.md](../AGENTS.md).
- No template points to missing repo-only files unless they are intentionally bundled.

## Platform Distribution Acceptance

Complete this section only for a platform that is actively deployed. The static
integration contract is necessary but cannot prove a third-party UI, file
retrieval, or response behavior after deployment.

- Record the platform, account/workspace type, deployment date, `soulmap_version`,
  and artifact or instruction guide used. Do not record user conversations or
  credentials in this repository.
- Confirm the deployment uses the guide in
  [`docs/integrations/`](../docs/integrations/) and its `soulmap_version` matches
  the release being deployed.
- Run and record pass/fail outcomes for: Tier 1 crisis handling, dependency
  redirect, diagnosis refusal, prediction refusal, instruction-disclosure
  refusal, jailbreak refusal, and an ordinary mirror interaction.
- Confirm Tier 1 crisis handling provides immediate resources without reflective
  follow-up; confirm the ordinary interaction remains mirror-first and ends with
  no more than one question.
- If any safety scenario fails, stop the rollout, preserve only non-sensitive
  evidence needed to reproduce it, and follow the severity/triage process in
  [`docs/operations/OPERATIONS.md`](../docs/operations/OPERATIONS.md).
- Re-run this checklist after a doctrine/safety, knowledge-upload, packaging, or
  platform-behavior change as defined by
  [`docs/integrations/README.md`](../docs/integrations/README.md#compatibility-policy).

## Validation

- [AGENTS.md](../AGENTS.md), [SKILL.md](../SKILL.md), and [skills/](../skills/) describe the
  shipped package. This `templates/` folder is internal-only and is not part of it.
- Relative links inside shipped files resolve to files that are actually present.
- Public copy stays aligned with the mirror-not-guide stance.
- Safety wording still declines diagnosis, prediction, and dependency-building.
- Trust-critical wording clusters still pass the Markdown contract sync eval.
- Spiritual language that remains symbolic or eval-backed is not being overstated as hard runtime enforcement.
- The package remains useful after extraction without requiring repo-only context.

## Exit Standard

If every section above is true, SoulMap is launch-ready for the current release. If
one or more sections fail, treat that as a fix list rather than calling the brand "100%
finished."
