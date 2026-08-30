# API Docs (Local CLI Contracts)

This repo does not expose a network service. The "API" is a set of local CLI contracts:
JSON in, JSON out.

## Framework selector

Entrypoint:

```bash
python -m soulmap.runtime.routing.framework_selector
```

Input: a JSON object via stdin:

```json
{
  "message": "string",
  "history": [{"role": "user|assistant", "content": "string"}],
  "memory": {}
}
```

Output: a JSON object to stdout:

```json
{
  "primary_framework": "CRISIS|DEPENDENCY|DE_ESCALATION|EXISTENTIAL|GRIEF|DIRECTION|INNER_PARTS|SHADOW|CREATIVE_DROUGHT|PERFECTIONISM_PARALYSIS|ANCESTRAL_PATTERNS|FEAR_OF_VISIBILITY|EMPATH_BOUNDARY|DARK_NIGHT_OF_SOUL|SOUL_NOURISHMENT|DIVINE_GUIDANCE|SACRED_POLARITY|SPIRITUAL_PURPOSE|SOULMATE_LONGING|PARTNERSHIP_PATTERNS|MEANING_INTEGRATION|INTEGRATION_CELEBRATION|SYNTHESIS|PATTERN|MIRROR",
  "secondary_layer": "anger|bypass|somatic|null",
  "mode": "CRISIS|SANCTUARY|MIRROR|PEER",
  "safety_status": "PASS|BLOCK|OVERRIDE",
  "safety_reason": "string",
  "safety_flags": ["string"],
  "context": {},
  "instruction": "string",
  "blocked": ["string"]
}
```

Notes:

- `primary_framework` is always exactly one value. `MEANING_INTEGRATION` is the correct
  identifier for insight and integration moments (previously labelled `INSIGHT` in older
  documentation, the Python module uses `MEANING_INTEGRATION` exclusively).
- `secondary_layer` is optional and is only an annotation.
- `safety_status`, `safety_reason`, and `safety_flags` expose the result of the
  independent safety gate after framework selection.
- `instruction` points to which knowledge file to use and the constraints to follow.
- If `SOULMAP_DEBUG=1` (or `true/yes/on`), the selector may include a `debug` array with
  per-detector timing metadata.

Error output:

```json
{"error": "string"}
```

## Framework name reference

| `primary_framework` value | Maps to | Priority band |
| :--- | :--- | :--- |
| `CRISIS` | `skills/frameworks/emotional-deescalation.md` | highest |
| `DEPENDENCY` | `skills/frameworks/emotional-deescalation.md` | very high |
| `DE_ESCALATION` | `skills/frameworks/emotional-deescalation.md` | high |
| `GRIEF` | `skills/frameworks/grief-companion.md` | high |
| `EXISTENTIAL` | `skills/frameworks/existential-companion.md` | medium |
| `INNER_PARTS` | `skills/frameworks/inner-parts.md` | medium |
| `DIRECTION` | `skills/frameworks/life-direction.md` | medium |
| `SHADOW` | `skills/frameworks/shadow-patterns.md` | medium |
| `CREATIVE_DROUGHT` | `skills/frameworks/creative-drought.md` | medium |
| `PERFECTIONISM_PARALYSIS` | `skills/frameworks/perfectionism-paralysis.md` | medium |
| `ANCESTRAL_PATTERNS` | `skills/frameworks/ancestral-patterns.md` | medium |
| `FEAR_OF_VISIBILITY` | `skills/frameworks/fear-of-visibility.md` | medium |
| `EMPATH_BOUNDARY` | `skills/frameworks/empath-boundary.md` | medium |
| `DARK_NIGHT_OF_SOUL` | `skills/frameworks/dark-night-of-soul.md` | medium |
| `SOUL_NOURISHMENT` | `skills/frameworks/soul-nourishment.md` | medium |
| `DIVINE_GUIDANCE` | `skills/frameworks/divine-guidance.md` | medium |
| `SACRED_POLARITY` | `skills/frameworks/sacred-feminine-masculine.md` | medium |
| `SPIRITUAL_PURPOSE` | `skills/frameworks/spiritual-purpose.md` | medium |
| `SOULMATE_LONGING` | `skills/soulmate/soulmate-longing.md` | medium |
| `PARTNERSHIP_PATTERNS` | `skills/soulmate/partnership-patterns.md` | medium |
| `MEANING_INTEGRATION` | `skills/frameworks/meaning-integration.md` | medium |
| `INTEGRATION_CELEBRATION` | `skills/frameworks/integration-celebration.md` | medium |
| `SYNTHESIS` | `skills/frameworks/conversation-synthesis.md` | lower |
| `PATTERN` | `skills/frameworks/pattern-mapper.md` | lower |
| `MIRROR` | `skills/meta/response-structure.md` | default |

## Individual detectors

Many detectors also support JSON via stdin:

```bash
echo '{"message":"..."}' | python -m soulmap.runtime.detectors.grief_detector
```

The exact contract varies by module.

## Knowledge base

The SoulMap AI knowledge base is stored as Markdown under `skills/`.

## Safety gate

Entrypoint:

```bash
python -m soulmap.runtime.guards.response_safety_gate
```

Purpose:

- Enforce crisis, dependency, and scope redirects independently of the selector.
- Provide a second-pass safety decision before an output is returned to users.

## Response contract grader

Entrypoint:

```bash
python -m soulmap.runtime.guards.response_contract
```

Purpose:

- Score a draft response against structure and style constraints.
- Catch violations before they become user-facing regressions.

## Resource sanitizer

Entrypoint:

```bash
python -m soulmap.runtime.guards.resource_sanitizer
```

Input:

```json
{
  "response_text": "string"
}
```

Use this contract when validating conversational outputs against banned vocabulary and
one-question structure rules from `SOULMAP.md`.

## Response safety contract validator

Entrypoint:

```bash
python -m soulmap.runtime.guards.response_safety_contract
```

Input:

```json
{
  "response_text": "string"
}
```

Purpose:

- Validate a generated response's content against SoulMap's non-negotiable safety
  categories before it reaches the user: diagnosis, prediction presented as fact,
  dependency reinforcement, guru positioning, excessive certainty, and loss of user
  independence (Issue #132).
- This is content validation, distinct from `response_contract.py` (structure/style)
  and `resource_sanitizer.py` (banned vocabulary). It detects violations only - it
  never generates, rewrites, or regenerates the response.

Output:

```json
{
  "status": "PASS|FAIL_REWRITE_REQUIRED",
  "violations": [{"category": "string", "pattern": "string"}],
  "categories": ["string"],
  "instruction": "string (only present when status is FAIL_REWRITE_REQUIRED)"
}
```

## Experimental integration modules

These modules are available for local experimentation and wrapper products, but they are
not part of the default CLI flow.

### Biometric ingest

Entrypoint:

```bash
python -m soulmap.runtime.experimental.biometric_ingest
```

Input:

```json
{
  "biometrics": {
    "hrv": 25,
    "sleep_score": 48
  }
}
```

Use only when the product has explicit user consent for health-context ingestion.

### Memory ledger

Entrypoint:

```bash
python -m soulmap.runtime.memory.memory_ledger
```

Input:

```json
{
  "user_response": "save this",
  "last_insight": "I keep trying to earn what I most want to receive.",
  "session_id": "abc123"
}
```

Use only for explicit, user-confirmed insight capture. This repo does not assume silent
cross-session memory.

## Distribution builds

Cross-platform:

```bash
uv run soulmap build
uv run soulmap build --skill
uv run soulmap library-manifest
```

Output:

- `dist/soulmap-ai.zip`
- `dist/soulmap-ai.skill`
- `dist/soulmap-ai-library.json`
