# Runtime key ownership

Python-facing identifiers belong in `config/runtime-keys.json`, not in the prose or table labels of `skills/**/*.md`.

- Markdown uses human-readable labels and owns the meaning and guidance.
- The config maps stable runtime identifiers to those labels; it is the only place where those identifiers are declared for the mappings it owns.
- Markdown guidance must not use Python format placeholders such as `{name}`. Compose variable details in Python, or declare machine-facing templates in a dedicated structured config.
- A shared identifier should have a stable, documented meaning. If it is a domain concept rather than an implementation identifier, explain it in a dedicated terminology document such as `skills/meta/runtime-terminology.md`.
- Do not mass-replace tokens based on spelling alone. Confirm a runtime consumer, update the config mapping and tests together, and preserve the original safety behavior.

This boundary is being migrated incrementally. A key-like token not listed in the config is not automatically safe: audit its consumer before deciding whether it is a domain term, a prose label, or a runtime identifier.
