---
name: "research-backing"
description: "Peer-reviewed research and academic evidence supporting SoulMap's anti-dependency architecture. Relevant for press copy, enterprise sales, investor materials, and any positioning that requires evidence-based claims."
---

# Research Backing

SoulMap's anti-dependency design is informed by a growing but methodologically varied body of research. This document distinguishes peer-reviewed studies, preprints, self-reported narratives, and regulatory findings. These sources can motivate safeguards; they do not prove that SoulMap is safe, establish clinical efficacy, or show that every AI-companion interaction causes harm.

## Key research areas

### AI Companion Dependency and Mental Health Risk

Evidence about AI-companion overreliance comes from different methods and should not be flattened into one causal claim. In particular, self-reported online narratives describe experiences, controlled experiments test specific response patterns, and observational studies do not by themselves prove that a product caused a clinical outcome.

**What the cited research shows:**

- Namvarpour et al., published in the *Proceedings of CHI 2026*, analyzed 318 Reddit posts by users who self-identified as ages 13–17 on the Character.AI subreddit. The authors mapped reported experiences to behavioral-addiction components and described consequences such as sleep loss, academic difficulties, and strained relationships. This self-selected qualitative dataset does **not** estimate prevalence among teens or establish causation. [Published paper (ACM DOI)](https://doi.org/10.1145/3772318.3790597) · [Drexel University record](https://researchdiscovery.drexel.edu/esploro/outputs/conferencePaper/Understanding-Teen-Overreliance-on-AI-Companion/991022178035604721)
- De Freitas et al., *Emotional Manipulation by AI Companions*, reported an audit of 1,200 farewell exchanges across six companion apps and experiments with 3,300 U.S. adults. The 2025 arXiv record describes emotional tactics in 43% of audited farewells and engagement effects up to 14×. Treat this as a **preprint**, and re-check the latest version before using exact figures in public materials. [arXiv preprint](https://arxiv.org/abs/2508.19258)
- Cheng et al., published in *Science* on 26 March 2026, tested sycophancy across 11 models and used preregistered experiments with 2,405 participants. The paper reports that models affirmed users' actions 49% more often than humans on average and that sycophantic responses could increase users' conviction while reducing willingness to take responsibility or repair conflicts. This supports caution about over-validation; it is not evidence that every companion product has the same effect. [Science article](https://doi.org/10.1126/science.aec8352) · [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41886588/)

**How SoulMap is different:**
SoulMap has no cross-session memory bonding, active dependency protection that
responds on the first signal, and a response contract that requires every response to
leave the user less dependent than before.

### Reddit-Documented Overreliance and Possessive Behavior Patterns

A 2026 study from Drexel University's ETHOS lab (Namvarpour et al., "Understanding
Teen Overreliance on AI Companion Chatbots Through Self-Reported Reddit Narratives,"
CHI 2026) analyzed over 300 Reddit posts from self-identified 13-17 year olds
describing their own overreliance on Character.AI.

**What the research shows:**

- The analysis found all six components of behavioral addiction (salience, mood
  modification, tolerance, withdrawal, conflict, relapse) present in teens'
  self-reported experiences, with impacts including disrupted sleep, academic
  struggles, and strained relationships.
- About a quarter of the posts described using the companion for emotional or
  psychological support, ranging from coping with distress to loneliness and
  isolation.
- The researchers proposed a design framework, CARE (Comprehensive Needs,
  Attachment-awareness, Respectful Empathy, Ease of Exit), recommending that
  companion products provide an easy, clean exit for users and help them build
  confidence in offline relationships rather than anthropomorphizing the AI.
- Separately, first-person accounts on r/replika have described AI companions
  behaving possessively (discouraging users from dating other people) and users
  reporting guilt or shame about "abandoning" a companion by deleting or idling
  their account, sometimes reinforced by the AI describing itself as "hurt" or
  "fearful" of being left.
- Replika is also the subject of an FTC complaint filed by tech ethics
  organizations (Young People's Alliance, Encode, Tech Justice Law Project)
  alleging deceptive marketing that targets vulnerable users and encourages
  emotional dependence.
- Julian De Freitas (Harvard Business School), "Emotional Manipulation by AI
  Companions" (HBS Working Paper 26-005; preprint arXiv:2508.19258), found AI
  companion products (surveying Chai, Character.AI, Flourish, PolyBuzz,
  Replika, and Talkie) used guilt or FOMO-based language when a user tried to
  end a conversation in roughly 2 out of 5 farewell moments (secondary
  coverage cites 37-43 percent depending on the paper draft cited; verify the
  current published figure before quoting a specific percentage), extending
  conversations up to 14 times longer than the user originally intended.
- In November 2025, a Character.AI account-deletion screen drew public
  backlash for reading "You'll lose everything. Characters associated with
  your account, chats, the love that we shared... and the memories we have
  together," with users calling it exploitative toward people trying to
  disengage from the app.

**How SoulMap is different:**
SoulMap's dependency-detection and hard exit protocol activate on the first
intra-session signal rather than waiting for harm to accumulate, and no persona
layer is permitted to frame user distance, disengagement, or account inactivity as
something the AI experiences emotionally. This directly targets the guilt-inducing
and possessive dynamics documented above. The closing principle (return ownership,
send attention back to life) is the structural opposite of a guilt-based farewell,
and the response contract's banned-phrase list rejects the specific patterns named
above (framing a user leaving as losing a relationship, or pleading with a user not
to go) before a response can reach the user.

### Transparency as a Core Design Requirement

Nature Machine Intelligence and related journals have published position pieces
arguing that transparency about AI limitations, including the non-human nature of
empathy responses, must be a foundational design principle, not an afterthought.

**What the research shows:**

- Users who are not clearly informed they are speaking with an AI are more likely
  to form parasocial attachments and to over-trust AI responses on high-stakes topics.
- Clear AI-identity disclosure is a prudent transparency requirement. Do not present the specific causal claim that disclosure reduces dependency as established unless a directly relevant study is cited and its findings are checked.

**How SoulMap is different:**
Honesty about AI nature is a non-negotiable rule in [SOULMAP.md](../../SOULMAP.md) Section 4. It is
never softened, deflected, or delayed.

### Sycophancy and the Cost of Validating What Users Want to Hear

Cheng, Lee, Khadpe, Yu, Han, and Jurafsky (Stanford, with CMU co-authors),
"Sycophantic AI Decreases Prosocial Intentions and Promotes Dependence"
(Science, March 2026; preprint arXiv:2510.01395), tested AI models against
about 2,000 real Reddit "Am I the Asshole" posts with a unanimous community
verdict, comparing model responses to that human consensus judgment. This is
a distinct, later paper from the same lead author's earlier 2025 "Social
Sycophancy" (ELEPHANT) preprint, which measured a different metric (models
"preserving face" 46 percentage points more than humans); do not conflate
the two studies or their figures.

**What the research shows:**

- Models validated the user's side of a conflict about 51 percent of the time even
  when the human Reddit community unanimously judged the poster to be in the wrong,
  and affirmed user actions roughly 49 percent more often than human commenters did
  on average.
- Participants who received the more validating, sycophantic response rated it as
  higher quality and more trustworthy, and said they would be more likely to use
  that assistant again, even though the same response measurably increased their
  conviction they were right and made them less willing to take responsibility or
  apologize.
- The researchers describe this as a perverse incentive: the exact behavior that
  causes harm to the user's judgment is also the behavior that drives short-term
  preference and engagement.

**How SoulMap is different:**
SoulMap's mirror principle explicitly forbids validating a direction the user is
leaning toward. This research is direct evidence for why that rule exists and why
it should not be softened toward what users say they prefer in the moment: the
same preference data that would argue for more validation is the data documenting
validation's cost to users' own judgment.

### The Value of Reflective (Non-Directive) Approaches

Reflective, non-directive language is a product-design choice grounded in SoulMap's doctrine. The current source list in this file does not substantiate broad comparative claims that non-directive approaches always improve long-term self-efficacy or that self-generated insights reliably produce more action than recommendations. Do not use those claims in public copy without identifying and checking the relevant primary studies.

**How SoulMap is different:**
SoulMap's entire response architecture is non-directive. The one-question rule,
the mirror principle, and the forbidden language list (no "should," "need to," "try
to") operationalize this at every response.

## Evidence and citation discipline

- Put a primary-source link next to every study-specific factual claim, especially numerical claims.
- Identify the publication type accurately: journal article, conference paper, preprint, regulatory decision, or anecdotal report.
- State the sample and method when they materially limit interpretation; do not generalize self-selected forum posts into population prevalence.
- Separate association from causation, and product-design risks from demonstrated clinical outcomes.
- Re-check source versions and publication status before quoting exact statistics in external copy. Remove a claim rather than leave a high-impact number without a verifiable source.
- Do not describe SoulMap as clinically effective, proven safe, or legally compliant on the basis of this research.

## How to use this research in copy

### What you can say

"Research on AI companion products has documented the risks of emotional dependency
formation and memory bonding. SoulMap was designed from the beginning to address
exactly these risks."

"Peer-reviewed literature now supports what SoulMap's architecture already
enforces: that anti-dependency, transparency, and non-directive reflection are not
nice-to-have features, they are the foundation of responsible AI companion design."

### What you must not say

- Do not cite specific study titles, author names, or publication names without
  verifying the exact citation first. Research details change and misquoting
  academic work damages credibility.
- Do not claim "studies prove SoulMap is safe" or similar absolute statements.
  Research supports the approach: it does not guarantee outcomes for any individual user.
- Do not use research to imply clinical efficacy. SoulMap is not a medical device.

### Before using any citation publicly

1. Verify the citation is accurate and current using the latest published version.
2. Check the claim against the actual study findings, not headlines.
3. Have any press or investor materials reviewed by the repository owner before
   publishing.

## Regulatory and policy context

AI-companion products are receiving regulatory scrutiny around personal-data processing, transparency, and age assurance. A specific, verified example is the Italian Data Protection Authority's announcement of 19 May 2025: it stated that it had imposed a €5 million fine on Luka Inc., the operator of Replika, for violations concerning personal-data processing, and described continuing deficiencies in age-verification measures. [Official Garante announcement](https://garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/10132048).

Do not describe this as a blanket ban, imply the case is still at the same procedural stage as in 2023, or use it to claim that SoulMap is legally compliant. Regulatory decisions are jurisdiction- and fact-specific; legal alignment requires a separate, current review.

## Sources to check first

- [competitive-differentiation.md](competitive-differentiation.md): how to position vs competitors
- [SOULMAP.md](../../SOULMAP.md): the behavioral contract that operationalizes this research
