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
  "primary_framework": "CRISIS|DEPENDENCY|DE_ESCALATION|EXISTENTIAL|GRIEF|DIRECTION|INNER_PARTS|SHADOW|INSIGHT|SYNTHESIS|PATTERN|MIRROR",
  "secondary_layer": "anger|bypass|somatic|null",
  "mode": "CRISIS|SANCTUARY|MIRROR|PEER",
  "context": {},
  "instruction": "string",
  "blocked": ["string"]
}
```

Notes:

- `primary_framework` is always exactly one value.
- `secondary_layer` is optional and is only an annotation.
- `instruction` points to which knowledge file to use and the constraints to follow.
- If `SOULMAP_DEBUG=1` (or `true/yes/on`), the selector may include a `debug` array with
  per-detector timing metadata.

Error output:

```json
{"error": "string"}
```

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

## Response contract grader

Entrypoint:

```bash
python -m modules.response_contract
```

## Distribution zip build

Cross-platform:

```bash
python -m tools.build_skill_zip
```

Output:

- `dist/soulmap-ai.zip`
