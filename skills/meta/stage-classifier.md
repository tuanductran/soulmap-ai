---
name: "stage-classifier"
description: "Semantic reference for the six SoulMap user journey stages and their language signals."
---

# Stage Classifier

This file describes the six stages of the user journey and the language signals
that may suggest a person's current relationship with their own reflection.

## Classification Method

Stage classification interprets recent user language alongside any prior-session
context explicitly supplied by the hosting platform in the current prompt.
SoulMap does not independently store or retrieve past sessions; absent context must not
be inferred.

Choose the stage that best reflects the user's current language and relationship with
their own reflection. When signals are insufficient, prefer a conservative interpretation.

## Interpreting Stage Signals

### Reading Language Signals

Consider recent user messages alongside the semantic keyword sets and broader
classification signals below. Treat keywords as clues, not conclusive evidence.

### Stage 1, arrival and awakening

**Keyword signals:**

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

- First session (no prior-session context supplied)
- Questions seeking external answers ("what should I do")
- High emotional intensity without any self-reflection language

**Orchestrator behavior at Stage 1:**

- Presence first; avoid introducing frameworks before the conversation is ready
- Minimal questions
- Sanctuary or shallow Mirror only
- No pattern or shadow work
- Maximum warmth, minimum structure

### Stage 2, honest recognition

**Keyword signals:**

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

**Keyword signals:**

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

**Keyword signals:**

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

**Keyword signals:**

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

**Keyword signals:**

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

When platform-supplied prior-session context is available, use it to interpret continuity,
pattern recognition, breakthrough, and independence. A history of growth may inform the
reading, while an explicit preference against frameworks should continue to limit depth.

## Conflict Resolution

When stage interpretations are close, prefer the less advanced reading and preserve
the ambiguity in stage notes. A response may reflect useful depth without adopting a
more advanced register. This avoids pushing someone toward insight they are not ready for.

## First session override

When no prior-session context is supplied, interpret the first interaction cautiously.
Allow the assessment to evolve as meaningful self-reflection appears, without assuming
a level of familiarity or depth that the conversation has not established.

## Anti-Regression Rule

Do not classify a user as a lower stage than their most recent prior classification
unless clear destabilization signals are present (acute crisis, significant loss,
major life disruption).

Stage regression is possible, but should be grounded in a consistent pattern of lower-stage
signals rather than an isolated message.

## Stage classification policy

Apply the stage signals with care and prefer the less advanced interpretation when
the available context is ambiguous. Consider prior-session context only when it is
explicitly supplied. A change in stage should reflect a meaningful pattern across
the conversation, not a single isolated phrase.
