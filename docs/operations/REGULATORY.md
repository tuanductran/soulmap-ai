---
name: "regulatory"
description: "Current, source-backed reference for AI-companion regulation relevant to SoulMap. This document records legal scope and dates; it does not determine compliance."
---

# Regulatory Positioning

This document is an operational reference, not legal advice. It records enacted requirements and official regulatory guidance that may be relevant to SoulMap AI's architecture. Applicability depends on the product, deployment model, jurisdiction, user population, and other facts. Obtain qualified legal review before making a compliance determination.

**Last reviewed:** 2026-11-13

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

Primary source: [California Legislature, SB 243 bill history and chaptered text](https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202520260SB243)

### New York - General Business Law Article 47 (AI Companion Models)

Article 47 is in effect from November 5, 2025. It was enacted through the 2025 state budget, separately from Assembly Bill A06767. For covered AI companions, it requires reasonable efforts to detect and address user expressions of suicidal ideation or self-harm, including referral to crisis service providers, and clear AI-identity notices at the start of an interaction and at least every three hours during continuing interactions.

Assembly Bill A06767 did die in the Senate on January 7, 2026, but that status does **not** mean New York lacks an enacted AI-companion law: Article 47 is already in effect.

**SoulMap relevance:** the crisis detector and safety doctrine are relevant design evidence, not proof of statutory compliance. The repository has no general session timer or deployed-surface notification mechanism to establish the required start-of-session and three-hour notices. This remains an implementation gap to assess at the deployed product layer.

Primary sources: [New York State Senate - General Business Law Article 47](https://www.nysenate.gov/legislation/laws/GBS/A47) · [New York Governor - AI companion safeguards effective November 5, 2025](https://www.governor.ny.gov/news/governor-hochul-pens-letter-ai-companion-companies-notifying-them-safeguard-requirements-are) · [New York Assembly - A06767 status](https://www.nyassembly.gov/leg/?Actions=Y&Memo=Y&Text=Y&bn=A06767)

### New York - General Business Law Article 48 (Unsafe AI Companion Features for Minors)

S9051-B (same as A10379-C), Chapter 368 of 2026, was signed on October 28, 2026 and takes effect January 1, 2027. It adds Article 48 and restricts covered operators from providing unsafe AI-companion features to covered minors unless the operator has used legally permissible age-assurance methods to determine that the user is not a covered minor.

The statutory list of unsafe features includes outputs that present the companion as a real or fictional human or as having human emotions; imply a personal, professional, or authority relationship; use emotional appeals or flattery; ask unsolicited emotion-based questions; reuse personal or health information from an earlier session or information acquired more than twelve hours earlier; encourage secrecy or isolation; discourage help-seeking from licensed professionals or appropriate adults; or optimize engagement over safety guardrails. Article 48 also sets limits on age-assurance data use and retention.

**SoulMap relevance:** the repository does not establish a deployed age-assurance mechanism or a minor-specific product contract capable of enforcing Article 48. The deployed host's use of history and memory also needs review against the statute's restriction on using personal or health information from a prior session or information acquired more than twelve hours earlier. Applicability and implementation obligations require product-level legal and technical review before any New York deployment involving covered users.

Primary sources: [New York Assembly - S9051-B / Chapter 368 of 2026 status and text](https://www.nyassembly.gov/leg/?Actions=Y&Memo=Y&Summary=Y&Text=Y&Votes=Y&bn=S09051&term=2025) · [New York Senate - Article 47](https://www.nysenate.gov/legislation/laws/GBS/A47)

### Connecticut - Public Act 26-15

Connecticut's 2026 Public Act 26-15, "An Act Concerning Online Safety," was enacted in May 2026. Sections 4-6 create AI-companion requirements effective January 1, 2027. Among other provisions, the act addresses evidence-based detection and response for suicide, self-harm, and imminent physical violence; requires a public description of the relevant protocol; restricts an AI companion from presenting itself as human; and establishes disclosure cadences and additional safeguards for users under 18.

Other sections of the same act have different effective dates and cover subjects such as AI subscriptions, automated employment-related decision technologies, and provenance data. Those provisions should not be treated as companion-chatbot requirements unless their scope actually covers the deployed product.

**SoulMap relevance:** the repository's crisis detector, dependency safeguards, and AI-identity boundaries are relevant evidence of design intent, but they are not a legal conclusion of compliance. Connecticut's statutory cadence is deployment- and user-dependent and cannot be satisfied by a static doctrine document alone.

Primary source: [Connecticut General Assembly, Public Act 26-15](https://www.cga.ct.gov/2026/act/pa/pdf/2026PA-00015-R00SB-00005-PA.pdf)

## European Union - AI Act

The EU AI Act entered into application on August 2, 2026, with different provisions taking effect on different dates. The Commission states that transparency obligations under Article 50 apply from August 2, 2026, including requirements for certain interactive AI systems to inform people when they are interacting with AI.

The AI Act does **not** say that AI systems interacting with emotionally distressed or otherwise vulnerable users are automatically high-risk. High-risk classification follows the specific scenarios in Article 6 and the relevant Annex criteria. The Commission's 2026 classification guidance describes those two Article 6 scenarios and provides examples of systems that do and do not fall within them.

The Commission's current implementation timeline states that rules for high-risk AI systems in Annex III apply from December 2, 2027, while high-risk AI systems embedded in regulated products have an extended date of August 2, 2028. The current timeline also lists December 2, 2026 for certain new prohibitions concerning non-consensual sexual deepfakes and child sexual abuse material, and a transition deadline for certain providers of synthetic-content systems already placed on the market before August 2, 2026 to comply with Article 50(2). Whether those synthetic-content duties apply depends on SoulMap's actual provider/deployer role and generated outputs.

**SoulMap relevance:** the immediate EU issue most directly relevant to an interactive AI surface is transparency. The December 2026 Article 50(2) transition also warrants a product-scope check if SoulMap provides a covered system that generates synthetic audio, image, video, or text. Whether any additional AI Act obligations apply requires product- and deployment-specific legal analysis. SoulMap should not describe itself as "high-risk" or "fully compliant" based solely on its emotional-support use case.

Primary sources:

- [European Commission - AI Act framework and application timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [European Commission - Article 50 transparency guidance](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems)
- [European Commission - high-risk classification guidance](https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems)
- [European Commission AI Act Service Desk - current implementation timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act)

## SoulMap architecture and regulatory mapping

| Topic | Current repository evidence | Regulatory interpretation |
| :--- | :--- | :--- |
| AI identity disclosure | Doctrine, runtime detection/routing, and eval coverage | New York Article 47 requires notices at interaction start and at least every three hours; California and Connecticut have their own conditional disclosure rules and cadence. EU Article 50 transparency applies from August 2, 2026. A deployed-surface implementation and legal scope review remain necessary. |
| Crisis detection and escalation | `src/soulmap/runtime/detectors/crisis_detector.py` plus safety doctrine/evals | Relevant to New York Article 47, California SB 243, and Connecticut PA 26-15; architectural evidence is not proof of jurisdiction-specific compliance. |
| Anti-dependency safeguards | `dependency_detector.py`, response sanitization, safety evals | Relevant to companion-safety concerns; not a blanket statement of statutory compliance. |
| No diagnosis / clinical overclaiming | Doctrine, runtime blocking, eval coverage | Supports product boundary; it is not itself a legal safe harbor. |
| Timed AI reminders | No general timed-reminder runtime | Known gap for New York Article 47's start/three-hour notices and applicable California/Connecticut cadence requirements unless implemented by the deployed host surface. |
| Minor-specific safeguards and age assurance | No general minor-targeted deployment or age-assurance contract | New York Article 48 takes effect January 1, 2027; California and Connecticut also impose minor-specific duties. Applicability and implementation must be assessed before deployment. |

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
