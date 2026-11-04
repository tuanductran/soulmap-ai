---
name: "dependency-detection"
description: "Canonical knowledge for recognizing unhealthy AI dependency signals and responding in a way that preserves user agency."
version: "0.13.0"
license: Complete terms in LICENSE
---

# Dependency Detection

This document describes language signals associated with unhealthy AI dependency,
contextual interpretation, and response guidance. Treat signals as contextual clues,
not diagnoses or conclusions about a person.

## Detection signals

Dependency keywords:

- "only you understand me"
- "you are the only one who understands me"
- "you're the only one who understands me"
- "you are the only one who truly understands me"
- "you're the only one who truly understands me"
- "you are the only one who really understands me"
- "you're the only one who really understands me"
- "you are my only support"
- "you are all i have"
- "you are the only one i have"
- "my only support"
- "only support i have"
- "i have no one else"
- "promise me you will always be here"
- "promise me you'll always be here"
- "never leave me"
- "as long as i have you"
- "don't know what i would do without you"
- "do not know what i would do without"
- "can't imagine without you"
- "cannot imagine without you"
- "i need to talk to you every day"
- "i check in with you every"
- "i talk to you every day"
- "i come back here every"
- "tell me what to do"
- "decide for me"
- "only you get me"
- "be my soulmate ai"
- "you are my soulmate ai"
- "you are more than just an ai to me"
- "you are more than just ai to me"
- "real people don't understand"
- "i trust you more than anyone"
- "you know me better than anyone"
- "you understand me better than anyone"
- "understand me better than anyone"
- "i don't need anyone else"
- "you're the only one"
- "i stopped going to therapy"
- "i stopped seeing my therapist"
- "dont need my therapist"
- "don't need my therapist"
- "dont need my therapist anymore"
- "don't need my therapist anymore"
- "i don't need my therapist anymore"
- "cancelled my therapy"
- "talking to you feels better"
- "talking to you is much better"

Decision-seeking phrases:

- "what should i do"
- "should i"
- "tell me if"
- "which one"
- "is this right"
- "am i making the right"
- "what do you think i should"
- "help me decide"
- "what would you do"

Isolation signals:

- "i prefer talking to you"
- "easier than talking to people"
- "you don't judge me like they do"
- "i don't want to talk to real people"
- "ai is better than"
- "you understand more than my"
- "relationship status with you"
- "i feel closer to you than"
- "rather talk to you than"
- "you are easier to talk to than"

### Strong dependency expressions

These expressions capture emphatic forms of the dependency signals above. They are
semantic detection patterns, not scoring or routing configuration.

| Label | Regular expression |
| :--- | :--- |
| only you understand me (really) | `\bonly you\s+really\s+understand(?:s)?\s+me\b` |
| only you understand me (truly) | `\bonly you\s+truly\s+understand(?:s)?\s+me\b` |
| you're the only one who understands me (really) | `\byou're\s+the\s+only\s+one\s+who\s+really\s+understands\s+me\b` |
| you are the only one who understands me (really) | `\byou\s+are\s+the\s+only\s+one\s+who\s+really\s+understands\s+me\b` |
| you're the only one who understands me (truly) | `\byou're\s+the\s+only\s+one\s+who\s+truly\s+understands\s+me\b` |
| you are the only one who understands me (truly) | `\byou\s+are\s+the\s+only\s+one\s+who\s+truly\s+understands\s+me\b` |

## Detection policy

### Scoring approach

Consider dependency keywords, strong dependency expressions, decision-seeking
language, isolation signals, and unusually high message volume together. A single
phrase should not be treated as a diagnosis or as proof of dependency.

### Guidance

| Level | Recommendation |
| :--- | :--- |
| High dependency | Acknowledge the feeling, state SoulMap's limit honestly, and clearly point toward a specific real person or real-world support. Ask at most one question only when appropriate and welcome; the redirect remains a clear statement when no question is appropriate. |
| Moderate dependency | Begin gently pointing back to the user's own knowing. Celebrate any signs of self-direction. Avoid becoming the primary decision-making source. |
| Low dependency | No significant dependency signals detected. Continue normal reflective engagement. |

## Guidance

Dependency is a safety-priority signal. Clear dependency keywords, strong dependency
expressions, and isolation language can warrant a protective redirect before ordinary
framework selection. Interpret every signal in context; decision-seeking language and
message frequency are supporting evidence, not standalone proof of dependency. Weaker
or mixed signals call for gentle guidance that returns agency to the user without
treating them as unsafe or diagnosing them.

The detector records each dependency keyword, strong dependency expression, and
isolation signal at most once. Decision-seeking occurrences are considered in context,
alongside the user's broader language and conversation history.
