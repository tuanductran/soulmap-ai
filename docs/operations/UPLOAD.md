# Claude distribution and portable knowledge ZIP

SoulMap is maintained and documented as a **Claude-first Skill/plugin**. The standard ZIP is also a portable Markdown knowledge archive that other AI assistants may read and understand when they support ZIP inspection or Markdown file uploads. It does not make those assistants Claude-compatible plugin hosts, and it does not guarantee automatic Skill execution on another platform.

## Build and verify

~~~bash
uv run soulmap build
uv run soulmap dev --once
uv run soulmap library-manifest
~~~

The commands create the release archives and the separate Library manifest. The manifest records the shipped inventory, compatibility metadata, artifact sizes, and SHA-256 digests. It is verification metadata, not an installer.

## Distribution artifacts

### dist/soulmap-ai.skill

The Claude Code plugin-aware archive contains the canonical knowledge files plus the complete **.claude-plugin/** metadata directory, including **plugin.json** and **marketplace.json**.

Use it when you need the Claude Code plugin manifest and marketplace metadata. Extract it before using a local plugin directory or running Claude Code validation. It is not the direct-upload ZIP format for Claude.ai Custom Skills.

### dist/soulmap-ai.zip

The portable knowledge archive contains:

- **SKILL.md** — the single canonical Skill entrypoint.
- **SOULMAP.md** — the behavioral contract, product doctrine, and safety boundaries.
- **skills/** — supporting reflective frameworks, safety, voice, and other canonical knowledge.
- **LICENSE** — the project license.

It intentionally excludes **.claude-plugin/**, developer tooling, tests, and internal templates. Use it for Claude.ai Custom Skills staging or for other AI assistants that can inspect ZIP files or read the extracted Markdown files.

### Python distribution

The Python wheel and source distribution are local developer, test, and repository CLI tooling. They are not standalone knowledge runtimes and are not intended for import into an AI assistant.

## Claude Code plugin workflow

The plugin manifest lives at **.claude-plugin/plugin.json**. It gives Claude Code the stable plugin identifier, display name, version, publisher metadata, and the explicit root Skill declaration.

From the repository root, validate the manifest:

~~~bash
claude plugin validate . --strict
~~~

For a local smoke test, start Claude Code with the repository as a plugin directory:

~~~bash
claude --plugin-dir .
~~~

The Git marketplace catalog is retained for repository-based Claude Code compatibility. Anthropic is moving third-party plugin discovery toward its unified directory; check the [Claude plugins documentation](https://code.claude.com/docs/en/plugins) and [directory management page](https://claude.ai/directory/manage) for current publishing and discovery steps.

## Claude.ai Custom Skills workflow

Claude.ai expects a ZIP containing a named Skill directory at the top level, with a lowercase **skill.md** file inside it. The repository keeps its canonical entrypoint as uppercase **SKILL.md**; rename it only in a temporary Claude.ai staging copy.

1. Build the standard archive with **uv run soulmap build**.
2. Extract **dist/soulmap-ai.zip** into a directory named **soulmap-ai/**.
3. Rename **soulmap-ai/SKILL.md** to **soulmap-ai/skill.md** in that staging copy.
4. Create a ZIP of the **soulmap-ai/** folder itself. Do not ZIP only its contents.
5. In Claude, open **Customize → Skills → + → Create skill → Upload a skill**.
6. Upload the ZIP, enable the Skill, and test representative prompts.

The **.skill** artifact is not a substitute for this named-folder ZIP. See Anthropic's [custom Skill packaging instructions](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## Other AI assistants

The standard ZIP contains ordinary Markdown knowledge. The following services are provided as links only; this repository does not maintain platform-specific setup guides or claim direct Skill execution for them.

- [ChatGPT](https://chatgpt.com/)
- [Manus](https://manus.im/)
- [Gemini](https://gemini.google.com/)
- [Microsoft Copilot](https://copilot.microsoft.com/)
- [Perplexity](https://www.perplexity.ai/)

When a platform cannot inspect the ZIP itself, extract it and provide the relevant Markdown files. Platform upload support, file limits, and runtime behavior are controlled by each service; check that service's current documentation.

## Release verification

Before publishing, verify:

- The root **SKILL.md** is the only shipped Skill entrypoint.
- **plugin.json**, **marketplace.json**, **SKILL.md**, **pyproject.toml**, and the Claude integration guide share the same version.
- The standard ZIP excludes **.claude-plugin/** and the Claude plugin archive includes it.
- Both artifacts pass member-boundary, extracted-content, and SHA-256 verification.
- The repository's lint, test, Markdown-contract, and safety-evaluation gates pass.

See [LIBRARY.md](LIBRARY.md) for the Library manifest contract and [DEV.md](../engineering/DEV.md) for the development and packaging workflow.
