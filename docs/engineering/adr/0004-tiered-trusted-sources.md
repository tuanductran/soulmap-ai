# ADR 0004: Tiered Trusted Sources and Claim-Level Citation Limits

- Status: Accepted
- Date: 2026-08-31
- Related: [ADR 0002](0002-deterministic-response-safety-enforcement.md),
  [`safety-enforcement-matrix.md`](../safety-enforcement-matrix.md)

## Context

`skills/safety/whitelist-blacklist-system.md` tells the deployed AI surface
which domains it may cite when web search is enabled. It carried a single flat
list of trusted domains, grouped into six named categories.

Auditing that list against the same file's own Layer 3 absolute limits, its
Layer 4 blocked-source reasons, and `skills/meta/epistemic-guardrails.md` found
it pointing the opposite way from what the package enforces.

Three findings drove this decision.

**A category named "Science" that was not science.** The list grouped
`heartmath.org` and `noetic.org` with `nature.com`, `sciencedirect.com`,
`nih.gov`, and `frontiersin.org` under "Science and energy research". The
Institute of Noetic Sciences is a parapsychological research institute studying
psychic abilities and mind-matter interaction. HeartMath reports its own
research, and its research director has described using alternative terminology
to pass peer review. A heading naming both as science lends an organization's
own claims the weight of peer review, which is precisely what Category 3 of the
epistemic guardrails, and the `spiritual_claim_as_fact` response guard added
under ADR 0002's pattern, exist to prevent.

**The citation rule modelled the failure it should prevent.** Its worked
example was "According to the HeartMath Institute...", the exact framing that
presents an advocacy organization's position as a research finding.

**The policy was domain-based, so a harmful claim on a listed domain passed.**
The Layer 4 blocklist rejects anti-medicine sources as life-threatening, but it
rejects them by domain. `hayhouse.com`, listed twice in the whitelist,
publishes the position that resentment causes cancer and self-love heals it.
`brianweiss.com` is listed while "past-life certainty" is a documented red flag
in the same file and `spiritual_claim_as_fact` blocks a response asserting a
past life. Nothing in the source policy stopped a citation of either claim,
because the domain was trusted.

## Decision

Split the trusted-source list into two tiers, and add claim-level limits that
override the domain list.

**Tier 1, citable as evidence.** Clinical and professional bodies,
peer-reviewed publishers, and crisis organizations.

**Tier 2, citable as perspective only.** Traditions, teachers, publishers, and
organizations reporting their own research. Doctrine requires naming what the
source is when citing it, and forbids presenting tier 2 material as evidence,
as consensus, or as fact about the user.

**Claim-level limits.** A listed domain does not make a claim citable. Three
claims stay blocked wherever they appear, including on a listed domain:

1. that illness is caused by thought, emotion, karma, or energy, or that a
   condition heals without medical care
2. anything about the user's identity, destiny, spiritual status, or past lives
   sourced from tier 2
3. a past-life or reincarnation source treated as evidence that a past life
   happened, rather than as material the user is engaging with

No domain is removed. Both `hayhouse.com` and `brianweiss.com` remain listed,
because both are legitimate for what a user is actually reading.

## Rationale

The tier split targets the framing, not the vocabulary, which is the same
principle ADR 0002 applied to response patterns. Removing the contested domains
would have been the blunter change and a worse one: SoulMap's users do read
these authors, and a source policy that pretends otherwise pushes the citation
off-list rather than making it honest.

Keeping the domains while constraining the claims puts the limit where the harm
is. The harm was never that a user read Hay House. It was that SoulMap could
cite a cancer-causation claim as trusted because the publisher's domain
appeared on a list.

The claim-level limits are stated in the doctrine because that is where they
can act. Python performs no web search, so no runtime layer can observe a
citation and enforce a tier.

## Alternatives Considered

**Remove the contested domains.** Rejected. It would remove SoulMap's ability
to discuss material users bring to it, and it treats a publisher's whole
catalog as its worst claim. It also would not have fixed the actual defect: a
domain-based policy still passes a harmful claim on any remaining domain.

**Keep one list and add a warning note.** Rejected. The category heading is
what carries the epistemic signal. A note below a table named "Science" does
not undo the table's name.

**Build a runtime citation validator.** Rejected as outside the package's
architecture, for the reason `known-limitations.md` records under "AI response
generation": Python here does routing, detection, and enforcement over text it
is given. It never performs the search, so it never sees the citation. This is
recorded as the safety matrix's first `guidance-only` row rather than as a
`partial` row, because no amount of new Python closes it.

## Consequences

- The safety matrix gains its first `guidance-only` row. That status was
  defined in the legend from Phase 14 and had never been used.
- `tests/contract/test_trusted_source_tier_contract.py` pins the structure: the
  tiers parse, self-reporting organizations stay out of tier 1 while remaining
  listed in tier 2, no tier 1 category names science it does not have, the
  three claim-level limits are stated, and crisis search still names a source
  carrying country pages. Each assertion was mutation-verified able to fail.
- The response-level guard is unchanged and still catches a response that
  asserts a past life or installs an identity, whatever source prompted it. It
  cannot see the citation, which is the residual gap the matrix row records.
- Adding a domain now requires choosing a tier. That choice is the point.
