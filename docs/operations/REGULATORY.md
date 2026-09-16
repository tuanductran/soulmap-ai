---
name: "regulatory"
description: "Current, source-backed reference for AI-companion regulation relevant to SoulMap. This document records legal scope and dates; it does not determine compliance."
---

# Regulatory Positioning

This document is an operational reference, not legal advice. It records enacted requirements and official regulatory guidance that may be relevant to SoulMap AI's architecture. Applicability depends on the product, deployment model, jurisdiction, user population, and other facts. Obtain qualified legal review before making a compliance determination.

**Last reviewed:** 2026-09-17

## Important distinction

Do not treat an AI-companion safety rule, a transparency obligation, and a high-risk AI classification as interchangeable concepts.

- **Transparency:** some laws require users to be told that they are interacting with AI.
- **Safety obligations:** some companion-chatbot laws impose crisis, anti-dependency, minor-safety, or content safeguards.
- **High-risk classification:** the EU AI Act uses specific Article 6 and Annex criteria. Emotional distress or interaction with a vulnerable person does **not**, by itself, establish that a system is high-risk under the AI Act.

## United States

### California - SB 243 / Business and Professions Code §§ 22601-22606

California SB 243 (Chapter 677, Statutes of 2025) became effective January 1, 2026. It regulates defined "companion chatbots" and requires, among other things:

- a clear and conspicuous AI disclosure when a reasonable person would otherwise be misled into believing they are interacting with a human;
- a maintained protocol addressing production of suicidal ideation, suicide, or self-harm content, including crisis-service referral when a user expresses such risk, with protocol details published on the operator's website;
- additional safeguards for users the operator knows are minors, including AI disclosure, at-least-every-three-hours break/AI reminders during continuing interactions, and measures concerning sexually explicit content;
- annual reporting beginning July 1, 2027 on specified crisis-referral and protocol information.

**SoulMap relevance:** the crisis and AI-identity architecture is relevant, but the repository does not currently establish that a deployed product satisfies every California statutory requirement. In particular, the repository has no general timed-reminder runtime and does not assume a minor-targeted deployment.

Primary source: California Legislature, SB 243 bill history and chaptered text: https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202520260SB243

### New York

New York Assembly Bill A06767 (2025-2026) proposed requirements for AI companions, including crisis protocols and notices concerning the non-human nature of the system. The bill **died in the Senate on January 7, 2026**; it should therefore not be described as an enacted New York companion-chatbot requirement in this document.

**SoulMap relevance:** retain New York as a legislative-watch item rather than an active compliance requirement unless a later enacted measure is identified and verified.

Primary source: New York State Assembly bill status: https://assembly.ny.gov/leg/?Actions=Y&Memo=Y&Summary=Y&Text=Y&Votes=Y&bn=A06767&term=

### Connecticut - Public Act 26-15

Connecticut's 2026 Public Act 26-15, "An Act Concerning Online Safety," was enacted in May 2026. Sections 4-6 create AI-companion requirements effective January 1, 2027. Among other provisions, the act addresses evidence-based detection and response for suicide, self-harm, and imminent physical violence; requires a public description of the relevant protocol; restricts an AI companion from presenting itself as human; and establishes disclosure cadences and additional safeguards for users under 18.

Other sections of the same act have different effective dates and cover subjects such as AI subscriptions, automated employment-related decision technologies, and provenance data. Those provisions should not be treated as companion-chatbot requirements unless their scope actually covers the deployed product.

**SoulMap relevance:** the repository's crisis detector, dependency safeguards, and AI-identity boundaries are relevant evidence of design intent, but they are not a legal conclusion of compliance. Connecticut's statutory cadence is deployment- and user-dependent and cannot be satisfied by a static doctrine document alone.

Primary source: Connecticut General Assembly, Public Act 26-15: https://www.cga.ct.gov/2026/act/pa/pdf/2026PA-00015-R00SB-00005-PA.pdf

## European Union - AI Act

The EU AI Act entered into application on August 2, 2026, with different provisions taking effect on different dates. The Commission states that transparency obligations under Article 50 apply from August 2, 2026, including requirements for certain interactive AI systems to inform people when they are interacting with AI.

The AI Act does **not** say that AI systems interacting with emotionally distressed or otherwise vulnerable users are automatically high-risk. High-risk classification follows the specific scenarios in Article 6 and the relevant Annex criteria. The Commission's 2026 classification guidance describes those two Article 6 scenarios and provides examples of systems that do and do not fall within them.

The Commission currently states that the rules for high-risk AI systems in Annex III apply from December 2, 2027, while high-risk AI systems embedded in regulated products have an extended date of August 2, 2028.

**SoulMap relevance:** the immediate EU issue most directly relevant to an interactive AI surface is transparency. Whether any additional AI Act obligations apply requires a product- and deployment-specific legal analysis. SoulMap should not describe itself as "high-risk" or "fully compliant" based solely on its emotional-support use case.

Primary sources:

- European Commission - AI Act framework and application timeline: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- European Commission - Article 50 transparency guidance: https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems
- European Commission - high-risk classification guidance: https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems

## SoulMap architecture and regulatory mapping

| Topic | Current repository evidence | Regulatory interpretation |
| :--- | :--- | :--- |
| AI identity disclosure | Doctrine, runtime detection/routing, and eval coverage | Relevant to enacted transparency/disclosure requirements, but deployed-surface wording and cadence remain deployment-specific. |
| Crisis detection and escalation | `src/soulmap/runtime/detectors/crisis_detector.py` plus safety doctrine/evals | Strong architectural evidence, but jurisdiction-specific legal sufficiency requires separate review. |
| Anti-dependency safeguards | `dependency_detector.py`, response sanitization, safety evals | Relevant to companion-safety concerns; not a blanket statement of statutory compliance. |
| No diagnosis / clinical overclaiming | Doctrine, runtime blocking, eval coverage | Supports product boundary; it is not itself a legal safe harbor. |
| Timed AI reminders | No general timed-reminder runtime | Known gap for laws that require periodic notices in particular deployments. |
| Minor-specific safeguards | No general minor-targeted deployment contract | Scope must be established before claiming that minor-specific statutory duties apply or are satisfied. |
| Backend storage | See `docs/operations/PRIVACY.md` | Privacy and data-protection obligations require separate jurisdictional analysis. |

## What this means for product and communications

The repository can document technical safeguards and design intent. It must not convert those facts into a legal compliance claim.

Preferred wording:

> SoulMap AI was designed with explicit AI-identity, crisis, anti-dependency, and non-clinical boundaries. Jurisdiction-specific compliance depends on the deployed product, users, and applicable law and requires legal review.

Do not claim:

> "SoulMap AI is fully compliant with [specific law]."

Do not describe a proposed bill as enacted law. Do not describe an AI system as EU AI Act high-risk solely because it interacts with users experiencing emotional distress.

## Source-maintenance rule

When updating this document:

1. Prefer enacted statutory text or the responsible regulator's official guidance.
2. Record the exact jurisdiction, instrument, provision, status, and effective date.
3. Separate enacted requirements from proposed legislation and general policy direction.
4. Avoid legal conclusions that are not supported by a product-specific legal analysis.
5. Update the **Last reviewed** date whenever a tracked law or official guidance is re-verified.
