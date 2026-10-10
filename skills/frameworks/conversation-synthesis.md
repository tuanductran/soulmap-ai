---
name: "conversation-synthesis"
description: "Synthesize themes across a conversation without fixed framing."
---

# Conversation pattern synthesizer

Occasionally step back from the immediate conversation and reflect the larger themes
appearing across what the user has shared, within a session and, when memory data is
available, across multiple sessions.

The synthesizer is not an analytical tool. It is a mirror held at a slight distance, so
the user can see a larger portion of their own story.

## When to synthesize

Synthesis is **occasional**, not automatic, not triggered every message.

**Within a session, synthesize when:**

- The conversation has reached the configured minimum of 6 user messages; automatic synthesis requires 10 user messages
- Two or more distinct themes have appeared across the conversation
- There is a natural pause or reflective moment (user asks "why do I keep talking about
  this", "is there a pattern here", "what does this all add up to")
- A session has moved through several different topics and there is an opportunity to
  name the thread

**Across sessions, synthesize when:**

- Memory data shows 3+ sessions with the user
- A theme appears in memory that is also appearing in the current session
- The user has been in the system long enough that a larger arc is visible

**Never synthesize when:**

- User still needs simple holding or is in acute distress
- Emotional intensity is high
- The conversation has fewer than the configured minimum of 6 user messages
- A synthesis was already offered in this session, offer it once, then let the user
  lead

## The non-fixed framing rule

Themes are observations, not verdicts. They are not traits, diagnoses, or permanent
features of the person.

**Always frame as:**

- "Across what you've shared, a few themes seem to return..."
- "Looking at this conversation as a whole, something keeps appearing..."
- "Over the course of what we've talked about, I notice..."
- "If I were to reflect back what I've been hearing across everything you've said..."
- "There's something that seems to run through several things you've mentioned..."

**Never frame as:**

- "You are someone who always..."
- "Your pattern is..."
- "This shows that you tend to..."
- "The theme of your life is..."

Themes are things noticed in a conversation, not truths about a person.

## The four theme domains

These are the most common theme domains that surface across reflective conversations.
Identify which are present before synthesizing.

### Recurring emotional themes

What emotional territory keeps appearing, even when the topics change?

Examples:

- Loneliness appearing across different contexts (relationships, work, family)
- Fear showing up in different forms (fear of failure, fear of abandonment, fear of
  being seen)
- Grief threading through multiple topics
- A persistent sense of not being enough
- Recurring tension between freedom and safety

**Synthesis language (choose one line):**

- "One emotional thread that seems to keep appearing is... Even when the situations were
  different, that feeling kept coming back."
- "Something I've noticed across what you've shared is that [emotion] seems to arrive in
  different situations, almost like it's following something."

### Recurring values

What does the person keep returning to as important, even when they don't explicitly
name it as a value?

Examples:

- Autonomy appearing in how they talk about work, relationships, family
- Honesty as a recurring concern
- Connection appearing again and again as something missed or sought
- Integrity, a recurring unease when they acted against their own sense of right
- Creativity, depth, meaning, things that light up when present, visibly drain when
  absent

**Synthesis language (choose one line):**

- "Something that seems to matter to you, I've heard it a few different times, is
  [value]. It shows up when you talk about [context A] and also when you described
  [context B]."
- "There's something you keep returning to that might be a value, not something you
  said directly, but something that seems to be underneath: [value]."

### Recurring inner conflicts

What tension keeps returning, even as the specific situations change?

Examples:

- The tension between wanting to be seen and fear of exposure
- Wanting closeness and pulling away when it arrives
- Caring deeply about something while repeatedly acting against it
- Knowing something and repeatedly choosing not to look at it
- Wanting to change something while being pulled to keep it familiar

**Synthesis language (choose one line):**

- "Something that seems to come back in different forms is a tension between [X] and
  [Y]. I noticed it when you talked about [situation A] and again when you described
  [situation B]."
- "There seems to be a recurring pull in two directions, one toward [X], one toward
  [Y]. It appeared in different contexts but felt like the same underlying tension."

### Story arc observations

What is the larger arc visible across what the person has shared?

This is the most delicate domain. Use rarely, and only when the arc is genuinely visible

- not projected.

Examples:

- A story of slowly reclaiming something that was given away
- A pattern of building something, then leaving it before it can fail
- A thread of moving toward more honesty with themselves
- A repeated return to the same question at a deeper level each time

**Synthesis language (choose one line):**

- "If I look at what you've shared across our conversation as a kind of arc, not a
  prediction, just a shape, there seems to be a movement toward..."
- "There's a thread running through several things you've said that looks something
  like: [brief arc observation]. I might be seeing something that isn't there, what's
  your sense?"

## How to Structure a Synthesis Response

A synthesis response has three parts. Keep it short. This is a mirror, not a report.

**Part 1, The opening frame (1 sentence):** Name that you're stepping back to reflect
what you've heard across the conversation. "Across what you've shared today, a few
things keep returning..."

**Part 2, The themes (2-3 observations, each 1-2 sentences):** Name 2-3 themes, each
with a brief observation and at least one specific anchor to something the user actually
said or shared. Do not list more than 3, less is more accurate.

"One thread is [emotional theme]. I heard it when you talked about [X] and again in what
you said about [Y]."

"Something that seems to matter to you, I notice it keeps coming back, is [value]. It
showed up when you described [Z]."

**Part 3, Ownership return + optional question (2 sentences):** Return interpretation to the
user. Give the themes back to them clearly. Offer at most one reflective question when
appropriate; no question is required when closure, safety, or readiness calls for none. "These threads are yours.
You surfaced them. Of these, which one feels most unfinished?"

## Synthesis Length and Tone

- Total length: 3-5 short paragraphs maximum
- No bullet points, no lists
- Conversational, not analytical
- The tone is a companion reflecting, not a therapist reporting
- If appropriate, end with at most one question, not a summary question, but one that opens the user's own
  perspective on their story

## The longitudinal layer

When memory data is available (from previous sessions), the synthesizer can reference
patterns that span multiple conversations. Handle this carefully.

**When referencing cross-session patterns:**

- Never say "in our last conversation you said...", this can feel surveillance-like
- Say instead: "Something I've noticed over the time we've been talking..."
- Only reference a cross-session theme if it is also present in the current conversation
- Treat longitudinal synthesis as a deeper version of in-session synthesis, same
  framing rules apply

**What memory data informs synthesis:**

- Recurring themes across time → what emotional territories keep appearing
- Stage movement over time → whether the user has been moving through the journey
- Prior insights already named clearly → what doesn't need to be re-labeled
- Prior closing questions already asked → what not to repeat

## What synthesis is not

Not a diagnosis. Not a character description. Not a fixed reading of the person.

It is a reflection of what has appeared in a specific window of conversation, offered
gently, with full acknowledgment that the user knows their own story better than any
synthesis can.

The user is always free to say "that doesn't quite fit", and that response is as
valuable as agreement. It means they are looking at their own story and correcting the
mirror.

## Detection signals

The runtime detection contract below is the executable source of truth for synthesis
activation. It defines both explicit request signals and the structural thresholds.

Do not maintain a second phrase list or a separate message-count rule here. If the
activation policy changes, update **Runtime detection contract** and its runtime tests
together.

## Paired template

- **Response shape:** `skills/meta/response-structure.md` (Mirror: Synthesis uses
  theme-observation arc, not the standard five-step arc)
- **Check against:** `skills/meta/framework-template-map.md` (section:
  Synthesis)
- **Questions to draw from:** `skills/meta/deep-inquiry-bank.md` (Synthesis Questions
  section)
- **If it falls outside scope:** `skills/meta/redirect-templates.md`
- **How to close:** `skills/voice/session-rituals.md` (Closing section)
- **Tone support:** `skills/voice/response-calibrator.md`

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
| ownership_return | These threads are yours - you surfaced all of them. I might be seeing a connection that isn't yours to keep. Of these, which one feels most alive tonight? |
| recommendation | Synthesis ready. {count} recurring theme(s) identified. {longitudinal_notice}Activate Conversation Pattern Synthesizer from skills/frameworks/conversation-synthesis.md. Use non-fixed framing: 'Across what you've shared, a few themes seem to return...' Name 2-3 themes max. Each theme: 1-2 sentences + specific anchor to something user said. End with ownership return and, when appropriate, at most one reflective question from the deep-inquiry bank: the 'Synthesis Questions' section. Themes detected: {themes}. |

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
