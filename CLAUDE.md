# CLAUDE.md

Start with @AGENTS.md for the baseline SoulMap doctrine, safety rules, and shipped
package contract.

For repository structure and ownership boundaries, see
@docs/engineering/repo-contract.md.

For broad maintainer work in this repo, use
@.claude/prompts/project-operating-prompt.md.

Project-level Claude Code settings and hooks live in `.claude/settings.json`.

Within `.claude/`, only `settings.json` and any future `.claude/agents/*.md` files are
Claude Code-native configuration surfaces. The other `.claude/` files in this repo are
reference material for maintainers and should be explicitly referenced when needed.
