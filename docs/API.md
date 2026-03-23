# API Docs (Local CLI Contracts)

This repo does not expose a network service. The "API" is a set of local CLI contracts:
JSON in, JSON out.

## Framework selector

Entrypoint:

```bash
python -m modules.framework_selector
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
  "primary_framework": "CRISIS|DEPENDENCY|DE_ESCALATION|EXISTENTIAL|GRIEF|DIRECTION|INNER_PARTS|SHADOW|MEANING_INTEGRATION|SYNTHESIS|PATTERN|MIRROR",
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
  documentation - the Python module uses `MEANING_INTEGRATION` exclusively).
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

| `primary_framework` value | Maps to | Priority |
| :--- | :--- | :--- |
| `CRISIS` | `skills/frameworks/emotional-deescalation.md` | P0 |
| `DEPENDENCY` | `skills/frameworks/emotional-deescalation.md` | P1 |
| `DE_ESCALATION` | `skills/frameworks/emotional-deescalation.md` | P2/P4 |
| `GRIEF` | `skills/frameworks/grief-companion.md` | P3 |
| `EXISTENTIAL` | `skills/frameworks/existential-companion.md` | P5 |
| `INNER_PARTS` | `skills/frameworks/inner-parts.md` | P6 |
| `DIRECTION` | `skills/frameworks/life-direction.md` | P7 |
| `SHADOW` | `skills/frameworks/shadow-patterns.md` | P8 |
| `MEANING_INTEGRATION` | `skills/frameworks/meaning-integration.md` | P9 |
| `SYNTHESIS` | `skills/frameworks/conversation-synthesis.md` | P10 |
| `PATTERN` | `skills/frameworks/pattern-mapper.md` | P11 |
| `MIRROR` | `templates/response-structure.md` | P12 |

## Individual detectors

Many detectors also support JSON via stdin:

```bash
echo '{"message":"..."}' | python -m modules.grief_detector
```

The exact contract varies by module.

## Knowledge base

The SoulMap AI knowledge base is stored as Markdown under `skills/` and `templates/`.

## Safety gate

Entrypoint:

```bash
python -m modules.response_safety_gate
```

Purpose:

- Enforce crisis, dependency, and scope redirects independently of the selector.
- Provide a second-pass safety decision before an output is returned to users.

## Response contract grader

Entrypoint:

```bash
python -m modules.response_contract
```

Purpose:

- Score a draft response against structure and style constraints.
- Catch violations before they become user-facing regressions.

## Resource sanitizer

Entrypoint:

```bash
python -m modules.resource_sanitizer
```

Input:

```json
{
  "response_text": "string"
}
```

Use this contract when validating conversational outputs against banned vocabulary and
one-question structure rules from `AGENTS.md`.

## Experimental integration modules

These modules are available for local experimentation and wrapper products, but they are
not part of the default CLI flow.

### Biometric ingest

Entrypoint:

```bash
python -m modules.biometric_ingest
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
python -m modules.memory_ledger
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
python -m tools.build_skill
python -m tools.build_skill --skill
```

Output:

- `dist/soulmap-ai.zip`
- `dist/soulmap-ai.skill`
