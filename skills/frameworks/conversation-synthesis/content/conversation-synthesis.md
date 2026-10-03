---
name: "conversation-synthesis"
description: "Canonical knowledge and runtime detection contract for synthesizing recurring themes across a conversation."
---

# Conversation pattern synthesizer

Occasionally step back from the immediate conversation and reflect the larger themes
appearing across what the user has shared, within a session and, when memory data is
available, across multiple sessions.

The synthesizer is not an analytical tool. It is a mirror held at a slight distance, so
the user can see a larger portion of their own story.

## The four theme domains

These are the most common theme domains that surface across reflective conversations.
Identify which are present before synthesizing.

### Recurring emotional themes

What emotional territory keeps appearing, even when the topics change?

- Loneliness appearing across different contexts (relationships, work, family)
- Fear showing up in different forms (fear of failure, fear of abandonment, fear of being seen)
- Grief threading through multiple topics
- A persistent sense of not being enough
- Recurring tension between freedom and safety

### Recurring values

What does the person keep returning to as important, even when they don't explicitly name it as a value?

- Autonomy appearing in how they talk about work, relationships, family
- Honesty as a recurring concern
- Connection appearing again and again as something missed or sought
- Integrity, a recurring unease when they acted against their own sense of right
- Creativity, depth, meaning, things that light up when present, visibly drain when absent

### Recurring inner conflicts

What tension keeps returning, even as the specific situations change?

- The tension between wanting to be seen and fear of exposure
- Wanting closeness and pulling away when it arrives
- Caring deeply about something while repeatedly acting against it
- Knowing something and repeatedly choosing not to look at it
- Wanting to change something while being pulled to keep it familiar

### Story arc observations

What is the larger arc visible across what the person has shared?

This is the most delicate domain. Use rarely, and only when the arc is genuinely visible,
not projected.

- A story of slowly reclaiming something that was given away
- A pattern of building something, then leaving it before it can fail
- A thread of moving toward more honesty with themselves
- A repeated return to the same question at a deeper level each time

## What synthesis is not

Not a diagnosis. Not a character description. Not a fixed reading of the person.

It is a reflection of what has appeared in a specific window of conversation, offered gently,
with full acknowledgment that the user knows their own story better than any synthesis can.

The user is always free to say "that doesn't quite fit", and that response is as valuable as
agreement. It means they are looking at their own story and correcting the mirror.

## Longitudinal knowledge

When memory data is available from previous sessions, synthesis may reference patterns that span
multiple conversations.

Use cross-session patterns only when the theme is also present in the current conversation.
Treat longitudinal synthesis as a deeper version of in-session synthesis with the same framing
rules.

Memory data can inform:

- recurring themes across time
- stage movement over time
- prior insights already named clearly
- prior closing questions already asked

Do not use memory as a reason to introduce an otherwise absent theme.

## Detection signals

The following recurring-theme signal groups are canonical detection knowledge.

Two or more distinct themes have appeared across the conversation.

## Runtime detection contract

The following operational configuration is normative knowledge for synthesis detection.
Changes to these values must be made here and covered by focused contract tests.

### Detection thresholds

| Setting | Value |
|---|---:|
| Minimum user messages to synthesize | 6 |
| Automatic synthesis user messages | 10 |
| Minimum distinct recurring themes for automatic synthesis | 2 |
| Maximum themes returned | 3 |
| Maximum anchors per theme | 2 |
| Maximum longitudinal themes | 3 |

### Explicit request signals

- "is there a pattern here"
- "what's the pattern"
- "do you see a pattern"
- "what keeps coming up"
- "what do you notice"
- "what themes do you see"
- "what themes do you notice"
- "what themes keep coming up"
- "what themes are there"
- "what does this all add up to"
- "looking back at our conversation"
- "looking back at everything"
- "looking back at what i have shared"
- "what have i been talking about"
- "why do i keep coming back to"
- "is there a thread"
- "what's the common thread"
- "what does this say about me"
- "what have you noticed about me"
- "can you reflect back"
- "can you summarize what"
- "across everything i've said"
- "across everything i have said"
- "across everything i have shared"
- "across what i have shared"
- "throughout our conversation"
- "what do you see in all of this"
- "what do you see across"
- "can you synthesize"
- "give me a synthesis"
- "what patterns do you see"
- "what have you noticed"
- "themes you see"
- "can you see a thread"
- "how has this changed"
- "what has shifted"
- "looking back across everything"

### Response guidance

| Key | Guidance |
| :--- | :--- |
| insufficient_data | Not enough conversation history for synthesis. Continue standard response. Check again after the configured minimum user-message threshold. |
| insufficient_themes | Not enough recurring themes detected for synthesis. Continue standard response. |
| session_opening | Across what you've shared today, a few threads have surfaced that feel worth staying with. |
| longitudinal_opening | Over the seasons we've been talking - not just today - a few threads keep appearing in the mirror. They seem to be finding different expressions as your awareness moves. |
| emotional_theme | An emotional thread of {theme} - it appeared in several different things you shared. |
| value_theme | Something that seems to matter to you - {theme} - keeps appearing, even when the topic changes. |
| conflict_theme | A recurring tension around {theme} - it surfaced in more than one place. |
| ownership_return | These threads are yours. You surfaced them. Of these, which one feels most unfinished? |
| recommendation | Synthesis ready. {count} recurring theme(s) identified. {longitudinal_notice}Activate Conversation Pattern Synthesizer from skills/frameworks/conversation-synthesis/content/conversation-synthesis.md. Use non-fixed framing. Name 2-3 themes max. Each theme: 1-2 sentences + specific anchor to something user said. End with ownership return + one reflective question from the deep-inquiry bank: the 'Synthesis Questions' section. Themes detected: {themes}. |

### Recurring emotional theme signals

#### loneliness

- "alone"
- "lonely"
- "isolated"
- "no one understands"
- "no one sees"
- "invisible"
- "disconnected"
- "left out"
- "on my own"
- "by myself"

#### fear

- "afraid"
- "scared"
- "terrified"
- "anxious"
- "worried"
- "panic"
- "what if"
- "might fail"
- "might lose"
- "might leave"

#### grief

- "grief"
- "grieve"
- "grieving"
- "lost"
- "loss"
- "gone"
- "miss"
- "no longer"
- "used to have"
- "used to be"
- "mourning"

#### not_enough

- "not enough"
- "not good enough"
- "never enough"
- "inadequate"
- "fall short"
- "don't measure up"
- "disappointing"
- "failure"
- "failing"

#### freedom_vs_safety

- "trapped"
- "stuck"
- "constrained"
- "can't leave"
- "have to stay"
- "freedom"
- "escape"
- "break free"
- "on my own terms"

#### anger

- "angry"
- "furious"
- "resentment"
- "bitter"
- "frustrated"
- "fed up"
- "sick of"
- "not fair"
- "unfair"

#### shame

- "ashamed"
- "shame"
- "embarrassed"
- "humiliated"
- "exposed"
- "judged"
- "what will they think"
- "don't want them to know"

### Recurring value signals

#### autonomy

- "my choice"
- "my own terms"
- "freedom to"
- "decide for myself"
- "don't want to be told"
- "independent"
- "my own path"

#### honesty

- "honest"
- "truth"
- "real"
- "authentic"
- "genuine"
- "pretend"
- "mask"
- "hiding"
- "showing my true"
- "being real"

#### connection

- "belong"
- "belonging"
- "close to"
- "connected"
- "relationship"
- "intimacy"
- "understood"
- "seen"
- "known"

#### meaning

- "meaning"
- "meaningful"
- "purpose"
- "matters"
- "point"
- "worth it"
- "for something"
- "makes sense"

#### safety

- "safe"
- "secure"
- "protected"
- "stable"
- "certain"
- "don't want to lose"
- "afraid to lose"

#### creativity_depth

- "creative"
- "depth"
- "interesting"
- "curious"
- "explore"
- "discover"
- "wonder"
- "bored when"
- "alive when"

### Recurring inner-conflict signals

#### seen_vs_hidden

- "want to be seen"
- "afraid to be seen"
- "want to be known"
- "don't want to be exposed"
- "hide"
- "show"

#### closeness_vs_distance

- "want connection"
- "push away"
- "pull back"
- "when they get close"
- "afraid of closeness"
- "want to be close but"

#### knowing_vs_avoiding

- "i know but"
- "i see it but"
- "i understand but still"
- "part of me knows"
- "choose not to look"

#### change_vs_familiar

- "want to change"
- "keep going back"
- "same patterns"
- "comfortable"
- "familiar even though"
- "known even if"

#### giving_vs_receiving

- "give so much"
- "never receive"
- "hard to receive"
- "easier to give"
- "take care of everyone"
- "no one takes care"
