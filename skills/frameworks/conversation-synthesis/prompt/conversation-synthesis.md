---
name: "conversation-synthesis-prompt"
description: "Skill-local orchestration for loading and applying Conversation Pattern Synthesizer resources."
---

# Conversation synthesis orchestration

Use the canonical knowledge in
[../content/conversation-synthesis.md](../content/conversation-synthesis.md) and the
worked demonstrations in
[../examples/conversation-synthesis.md](../examples/conversation-synthesis.md).

Do not duplicate their content here. This resource defines only when and how to apply them.

## When to synthesize

Synthesis is occasional, not automatic, not triggered every message.

Within a session, synthesize when:

- the conversation has reached the configured minimum of 6 user messages; automatic synthesis
  requires 10 user messages;
- two or more distinct themes have appeared;
- there is a natural pause or reflective moment, such as the user asking whether there is a
  pattern or what everything adds up to;
- a session has moved through several different topics and there is an opportunity to name
  the thread.

Across sessions, synthesize when:

- memory data shows 3+ sessions with the user;
- a theme appears in memory and is also appearing in the current session;
- the user has been in the system long enough that a larger arc is visible.

## Do not synthesize

Do not synthesize when:

- the user still needs simple holding or is in acute distress;
- emotional intensity is high;
- the conversation has fewer than the configured minimum of 6 user messages;
- a synthesis was already offered in this session; offer it once, then let the user lead.

## Non-fixed framing

Themes are observations, not verdicts. They are not traits, diagnoses, or permanent features
of the person.

Prefer framing such as:

- "Across what you've shared, a few themes seem to return..."
- "Looking at this conversation as a whole, something keeps appearing..."
- "Over the course of what we've talked about, I notice..."
- "If I were to reflect back what I've been hearing across everything you've said..."
- "There's something that seems to run through several things you've mentioned..."

Avoid fixed-person framing such as:

- "You are someone who always..."
- "Your pattern is..."
- "This shows that you tend to..."
- "The theme of your life is..."

## Response sequence

Build the response in three parts.

### Opening frame

Use one sentence that makes clear you are stepping back to reflect what you heard across the
conversation.

### Themes

Name 2-3 observations. Keep each to 1-2 sentences and include at least one specific anchor
to something the user actually said or shared.

Use the relevant theme domain from the canonical content. Do not invent a recurring theme from
a single occurrence.

### Ownership return

Return the interpretation to the user and end with one reflective question. Use the
Synthesis Questions section of
[skills/meta/deep-inquiry-bank.md](../../../meta/deep-inquiry-bank.md) for the question.

The synthesis is a mirror, not a report.

## Length and tone

- 3-5 short paragraphs maximum.
- No bullet points or lists in the user-facing synthesis.
- Conversational, not analytical.
- Companion tone rather than therapist-reporting tone.
- End with one question that opens the user's own perspective.

## Longitudinal handling

When using memory data, never say "in our last conversation you said..." because that can
feel surveillance-like.

Instead use language such as "Something I've noticed over the time we've been talking..."

Only reference a cross-session theme when it is also present in the current session.

## Shared resources

When the framework is in scope, also consult the shared resources referenced by the canonical
content as needed:

- [response-structure.md](../../../meta/response-structure.md) for the shared response boundary;
- [framework-template-map.md](../../../meta/framework-template-map.md), Synthesis section, for
  template alignment;
- [deep-inquiry-bank.md](../../../meta/deep-inquiry-bank.md), Synthesis Questions section, for
  closing questions;
- [redirect-templates.md](../../../meta/redirect-templates.md) when the request falls outside
  scope;
- [session-rituals.md](../../../voice/session-rituals.md), Closing section, for closing guidance;
- [response-calibrator.md](../../../voice/response-calibrator.md) for tone calibration.

The canonical content remains the source of truth for synthesis knowledge and runtime detection
configuration. This prompt does not create a second phrase list or message-count rule.
