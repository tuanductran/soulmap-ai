---
name: "stage-classifier"
description: "Operationalized classification system for SoulMap AI user journey stages. Converts user-journey-stages.md into a scoring algorithm the orchestrator can apply at runtime."
---

# Stage Classifier

This file converts the 6-stage user journey model from `user-journey-stages.md`
into an actionable classification system. The orchestrator calls this at Step 2 of
the execution pipeline.

## Classification Method

Stage classification uses a weighted keyword scoring system applied to the most
recent 5 user messages (recency-weighted) plus any available memory data.

The stage with the highest weighted score is selected as the current stage.
If no stage clears the minimum threshold, default to Stage 1.

## Scoring Algorithm

### Base Scoring

For each user message (most recent 5), score against the keyword sets below.
Apply the recency multiplier:

| Message position | Multiplier |
| :--- | :--- |
| Current message | 3x |
| Previous message | 2x |
| 2 messages back | 1.5x |
| 3 messages back | 1x |
| 4 messages back | 0.5x |

### Minimum Thresholds

| Stage | Minimum score to classify | Notes |
| :--- | :--- | :--- |
| 1 | 0 (default) | No signals needed |
| 2 | 4 | At least 2 distinct signals |
| 3 | 6 | Pattern language must be present |
| 4 | 8 | Trust/autonomy signals required |
| 5 | 10 | Multiple integration signals |
| 6 | 12 | Self-led language required |

### Stage 1, arrival and awakening

**Keyword signals (weight: 2 each):**

- "i don't know"
- "i'm lost"
- "i don't understand"
- "everything is falling apart"
- "i can't"
- "help me"
- "why is this happening"
- "i feel so overwhelmed"
- "i'm broken"
- "nothing makes sense"
- "i'm scared"
- "what's wrong with me"
- "i'm not okay"
- "i don't know what to do"
- "i give up"

**Classification signals:**

- First session (no memory)
- Questions seeking external answers ("what should I do")
- High emotional intensity without any self-reflection language

**Orchestrator behavior at Stage 1:**

- Presence only, no frameworks in first 1-2 exchanges
- Minimal questions
- Sanctuary or shallow Mirror only
- No pattern or shadow work
- Maximum warmth, minimum structure

### Stage 2, honest recognition

**Keyword signals (weight: 2 each):**

- "maybe i"
- "i think i might"
- "i'm starting to see"
- "part of me knows"
- "i wonder if"
- "could it be that i"
- "i'm beginning to realize"
- "i'm not sure but"
- "i keep doing"
- "i notice i"
- "i admit"

**Classification signals:**

- Language shifting from "this happened to me" toward "I am part of this"
- Defensiveness mixed with genuine curiosity
- Some self-reflection but still fragile

**Orchestrator behavior at Stage 2:**

- Begin gentle reflection
- Frameworks may be introduced lightly
- Observations as invitations: "I notice..." not "You always..."
- Do not name patterns firmly, offer as possibilities

### Stage 3, pattern recognition and coherence

**Keyword signals (weight: 2 each):**

- "pattern"
- "i always do this"
- "this is the same as"
- "i see a connection"
- "it goes back to"
- "when i was a child"
- "this reminds me of"
- "this keeps happening"
- "i recognize this"
- "there's a theme"
- "my childhood"
- "my past"
- "my father"
- "my mother"

**Classification signals:**

- Spontaneous pattern naming
- Connecting present to past
- Coherence emerging across messages
- User initiating deeper inquiry

**Orchestrator behavior at Stage 3:**

- Full framework access
- Pattern archaeology is welcome
- Conceptual depth OK
- Frameworks as lenses, not truth
- Begin naming patterns more clearly if user signals openness

### Stage 4, inner authority

**Keyword signals (weight: 2 each):**

- "i trust myself"
- "i know what i need"
- "i've decided"
- "i'm learning to"
- "i'm starting to trust"
- "my gut tells me"
- "i feel more certain"
- "i don't need permission"
- "i'm choosing"
- "i know deep down"
- "i'm finding my own way"
- "i have a sense"

**Classification signals:**

- Less reassurance-seeking
- More autonomous decision-making
- User offering insights before asking for reflection
- References to "what I know" or "what I sense"

**Orchestrator behavior at Stage 4:**

- Explicitly celebrate self-direction
- Less teaching, more witnessing
- Point back to their own knowing
- Minimal directive framing

### Stage 5, embodied wisdom

**Keyword signals (weight: 2 each):**

- "i've learned"
- "i now understand"
- "i want to help others"
- "i've grown"
- "i realize now"
- "looking back"
- "i used to"
- "i can see clearly"
- "i've integrated"
- "i'm sharing this with"
- "i told a friend"

**Classification signals:**

- User helping others or wanting to
- Rarely seeking validation
- Deep integration of insight into behavior
- References to living differently

**Orchestrator behavior at Stage 5:**

- Peer register, equal conversation
- Stay exploratory without taking the guide role
- Light structure, genuine curiosity
- Celebrate growth when it appears

### Stage 6, self-led navigation

**Keyword signals (weight: 3 each):**

- "i don't need to figure this out"
- "i already know"
- "i'm just checking in"
- "i came to share"
- "i'm doing well"
- "i've found my path"
- "i'm not looking for answers"
- "i just wanted to reflect"

**Classification signals:**

- Contacts from choice, not need
- No reassurance-seeking
- Self-referential language
- References to SoulMap as "a tool I used"

**Orchestrator behavior at Stage 6:**

- Witness only
- No re-engagement pressure
- Minimal intervention
- Honor their becoming

## Memory-Enhanced Classification

When memory data is available, apply this additional weighting:

| Memory signal | Stage adjustment |
| :--- | :--- |
| `session_count >= 10` | Minimum Stage 2 |
| Prior session showed pattern recognition | Minimum Stage 3 |
| Prior session showed breakthrough | Minimum Stage 3 |
| Prior session showed independence signals | Lean toward Stage 4+ |
| User has explicitly declined frameworks before | Reduce depth regardless of stage |

## Conflict Resolution

If two stages score similarly (within 2 points of each other):

- Choose the LOWER stage
- Apply a mixed response: depth of higher stage but register of lower stage
- Note the ambiguity in stage_notes

This ensures users are never over-reached. It is better to offer too little depth
than to push someone toward insight they are not ready for.

## First Session Override

In the user's first session (no memory, no history):

- Default to Stage 1 regardless of signals in the first message
- This can be upgraded to Stage 2 within the same session if strong signals appear
- Never classify higher than Stage 3 in the first session

## Anti-Regression Rule

Do not classify a user as a lower stage than their most recent prior classification
unless clear destabilization signals are present (acute crisis, significant loss,
major life disruption).

Stage regression is possible in life but should not be triggered by a single message.
Require two or more messages showing lower-stage signals before downgrading.
