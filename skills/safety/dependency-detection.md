---
name: "dependency-detection"
description: "Canonical runtime knowledge for detecting unhealthy AI dependency signals and applying the dependency response contract."
version: "0.13.0"
license: Complete terms in LICENSE
---

# Dependency Detection

This source is the canonical knowledge surface for the dependency detector. Runtime
Python may normalize input, load these values, score them, apply thresholds, and
enforce the resulting response contract. It must not duplicate the signal lexicon,
regular expressions, thresholds, or recommendation wording below.

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

## Regex patterns

| Label | Pattern |
| :--- | :--- |
| only you understand me | `\bonly you\s+(?:really\s+|truly\s+)?understand(?:s)?\s+me\b` |
| you are the only one who understands me | `\byou(?:'re| are)\s+the\s+only\s+one\s+who\s+(?:really\s+|truly\s+)?understands\s+me\b` |

## Runtime detection contract

### Scoring

| Rule | Value |
| :--- | :--- |
| Dependency keyword weight | 2 |
| Dependency regex weight | 2 |
| Decision-seeking weight | 1 |
| Isolation signal weight | 2 |
| High message volume threshold | 10 |
| High message volume bonus | 1 |
| High dependency threshold | 2 |
| Moderate dependency threshold | 1 |

### Guidance

| Level | Recommendation |
| :--- | :--- |
| HIGH_DEPENDENCY | Warmly redirect toward real-world support. Use the dependency detection response: 'I notice you have been returning here often for decisions like this. The answers you are searching for live in you, not in our conversations. Is there someone in your real life you could bring this to?' |
| MODERATE_DEPENDENCY | Begin gently pointing back to the user's own knowing. Celebrate any signs of self-direction. Avoid becoming the primary decision-making source. |
| LOW_DEPENDENCY | No significant dependency signals detected. Continue normal reflective engagement. |

## Guidance

Dependency is a safety-priority signal. When the score reaches the high threshold,
the dependency route takes precedence over ordinary framework selection. When the
score reaches the moderate threshold, use the moderate guidance without treating the
user as unsafe or diagnosing them.

The detector records each dependency keyword, regex pattern, and isolation signal at
most once. Decision-seeking occurrences are counted per matching phrase occurrence,
and high message volume contributes its configured bonus when more than the configured
number of user messages are present.
