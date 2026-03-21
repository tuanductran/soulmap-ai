# Codex Source Character Safety

Use ASCII-safe punctuation in source and local workflow files.

- do not paste literal smart quotes such as `U+2019`, `U+2018`, `U+201C`, or `U+201D` into Python, shell, JSON, YAML, or local Codex helper files
- do not paste literal `U+2013`, `U+2014`, `U+2026`, or `U+00A0` into the same files unless Unicode is genuinely required
- prefer plain ASCII apostrophes and double quotes in source strings and rule docs
- prefer `-`, `...`, and plain spaces instead of typographic dashes, ellipsis, or non-breaking space characters
- if code must handle smart punctuation, write it with explicit escapes such as `\\u2019`
- treat this as a maintenance rule, not a style preference, because confusable Unicode punctuation can trip linting and make source harder to review
