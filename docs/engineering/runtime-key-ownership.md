# Runtime key ownership

Python-facing identifiers belong in `config/runtime-keys.json`, not in the prose or table labels of `skills/**/*.md`.

- Markdown uses human-readable labels and owns the meaning and guidance.
- Each config entry maps a human-readable Markdown label to its stable runtime identifier; those identifiers are declared in config rather than embedded in the skill Markdown.
- Markdown guidance must not use Python format placeholders such as `{name}`. Compose variable details in Python, or declare machine-facing templates in a dedicated structured config.
- A shared identifier should have a stable, documented meaning. If it is a domain concept rather than an implementation identifier, explain it in a dedicated terminology document such as `skills/meta/runtime-terminology.md`.
- Do not mass-replace tokens based on spelling alone. Confirm a runtime consumer, update the config mapping and tests together, and preserve the original safety behavior.

The contract test scans every `skills/**/*.md` file for Python format placeholders and key-shaped identifiers in table-key positions. When a new runtime identifier is needed, add its mapping to config and test the consumer rather than embedding the identifier in Markdown. A token outside the current pattern checks still requires consumer-level review.
