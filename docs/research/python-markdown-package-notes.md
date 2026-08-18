# Python Markdown package research notes

Observed during package research on 2026-08-18.

## markdown-it-py

Upstream: [markdown-it-py][1].

The repository README describes CommonMark baseline parsing, configurable syntax rules, a plugin model, token parsing via `MarkdownIt.parse`, HTML rendering, optional front matter/footnote plugins from `mdit-py-plugins`, security guidance, and active maintenance. The observed repository page showed 1.4k stars, 353 commits, and a latest commit dated Jul 8, 2026. The project is MIT-licensed.

The most relevant fit for SoulMap is not immediate rendering, but replacing regex-only Markdown structure inspection with a token stream for links, images, headings, fenced code, tables, front matter, and plugin syntax while retaining SoulMap-specific policy checks.

## Mistune

Upstream: [Mistune][2].

The repository README describes a fast Python Markdown parser with renderers and plugins. The observed repository page showed 3.1k stars, 843 commits, release v3.3.4 dated Jul 22, 2026, and BSD-3-Clause licensing. Mistune is a credible alternative for rendering or custom AST/plugin work, but markdown-it-py is the closer fit for CommonMark/GFM-compatible token-level linting and link/anchor analysis.

## Initial gap assessment

SoulMap currently has no runtime dependency and uses a deliberately small regex/subset parser in `src/soulmap/devtools/support/markdown.py`. The likely high-value gap is parser-backed structural analysis for Markdown contracts, not adding a renderer to the runtime package. Any adoption should remain a dev dependency, preserve the existing CLI contract, and keep SoulMap-specific checks outside the third-party parser.

## mdformat

Upstream: [mdformat][3].

The documentation describes mdformat 1.0.0 as an opinionated CommonMark-compliant formatter with a Python API, CLI, plugin API, and stable style choices. It intentionally does not support non-CommonMark engine syntax by default and may escape custom syntax to preserve rendering. It is therefore a possible future formatter, but not a drop-in replacement for SoulMap's current `pymarkdownlnt` contract without a migration comparison over the full knowledge base.

## mdit-py-plugins

Docs: [mdit-py-plugins][4].

The plugin collection provides front matter, GFM, autolinks, footnotes, definition lists, task lists, heading anchors, word count, containers, admonitions, math, subscript/superscript and MyST-related extensions. The front matter plugin parses an initial YAML block, while the GFM plugin can enable front matter and task lists. This is a strong companion to markdown-it-py if SoulMap adopts more parser-backed structural checks.

## python-frontmatter

Upstream: [python-frontmatter][5].

The package loads and parses YAML, JSON, TOML or other front matter with handlers. The observed repository page showed v1.3.0 released May 20, 2026, 185 commits, MIT license and migration to uv. It is a candidate only if SoulMap expands frontmatter beyond the current simple `name`/`description` key-value subset; otherwise adding it would be unnecessary dependency weight.

## Pydantic and jsonschema

Docs: [Pydantic validation][6].

Pydantic provides typed models, strict/lax validation modes, serialization and JSON Schema generation. It is a strong candidate for larger structured payloads or public Python APIs, but SoulMap's current CLI payload helpers are small, explicit, and security-conscious. Replacing them wholesale would add migration surface without an immediate Markdown-specific benefit.

Docs: [jsonschema][7].

`jsonschema` implements JSON Schema validation for Python, supports multiple drafts including Draft 2020-12, schema referencing, format validation and detailed validation errors. It is a better targeted candidate than Pydantic for validating generated Library catalogs/manifests or future eval datasets, provided a schema file and a real contract are added first. It should remain a dev/CI dependency unless runtime consumers need schema validation.

## References

[1]: https://github.com/executablebooks/markdown-it-py "markdown-it-py"
[2]: https://github.com/lepture/mistune "Mistune"
[3]: https://mdformat.readthedocs.io/en/stable/ "mdformat documentation"
[4]: https://mdit-py-plugins.readthedocs.io/en/latest/ "mdit-py-plugins documentation"
[5]: https://github.com/eyeseast/python-frontmatter "python-frontmatter"
[6]: https://pydantic.dev/docs/validation/latest/get-started/ "Pydantic validation documentation"
[7]: https://python-jsonschema.readthedocs.io/en/stable/ "jsonschema documentation"
