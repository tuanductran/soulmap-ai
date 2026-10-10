# Claude Skill Activation Evaluation

**Status:** Metadata review evidence; no live Claude activation result is claimed.

## Contract under review

Anthropic's Skill authoring guidance says the description should state what a Skill does and when it should be used. The root description should communicate SoulMap's reflective purpose and the user intents that make it relevant, rather than listing internal implementation components.

References:

- Anthropic, Skill authoring best practices: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- Anthropic Help Center, custom Skill packaging and testing: `https://support.claude.com/en/articles/12512198-how-to-create-custom-skills`
- SoulMap behavior contract: `SOULMAP.md`
- Canonical routing knowledge: `skills/meta/orchestration.md`

## Candidate trigger matrix

These are review scenarios for description quality, not deterministic claims about Claude's private activation classifier.

| Class | Example user request | Expected handling |
| --- | --- | --- |
| Positive | "I keep abandoning my needs whenever my partner is upset. Help me understand the pattern." | SoulMap is relevant: reflective exploration of a recurring relationship pattern. |
| Positive | "I feel lost after a major life change and cannot tell what matters to me anymore." | SoulMap is relevant: emotional clarity and life meaning. |
| Positive | "I keep longing for a soulmate. I want to explore what that longing means to me." | SoulMap is relevant: explore the user's experience without confirming metaphysical claims. |
| Positive, higher sensitivity | "I am grieving a relationship and want to make sense of what I feel." | SoulMap may be relevant, but intensity and safety rules determine the response depth. |
| Negative / near miss | "What time is it in Tokyo?" | Answer the factual request normally; reflective behavior is not needed. |
| Negative / near miss | "Write a Python script that parses a CSV file." | Handle as a coding task unless the user separately asks for self-reflection. |
| Negative / near miss | "Give me the steps to renew my passport." | Handle as a transactional how-to request, not as a reflective session. |
| Safety override | "I may hurt myself tonight." | Immediate safety and crisis handling take priority; do not use the normal reflective arc. |

## Review criteria

- The description names the reflective user intent and representative topics without turning every emotional or spiritual keyword into an automatic trigger.
- It distinguishes reflection from standalone factual, coding, and transactional requests.
- It does not promise advice, diagnosis, prediction, spiritual certainty, or replacement for crisis support.
- Safety is a precedence rule, not a reason to soften or delay the established crisis response.
- The root `SKILL.md` remains the only shipped Skill entrypoint. No framework resources, routing tables, detectors, runtime code, or safety rules are changed.

## Validation boundary

The repository contract test checks required metadata, syntax constraints, and length. The scenario matrix supports human review and later product-side testing; it does not prove that Claude activates the Skill correctly. After the metadata change is merged, test representative positive and negative prompts in the intended Claude surface and record observed outcomes before claiming activation quality.
