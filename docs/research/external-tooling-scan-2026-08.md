# External tooling scan: QwenPaw, jscpd, codex-security

**Research date:** 2026-08-30. **Purpose:** a requested scan of three external
repositories for anything worth applying to SoulMap, specifically maturity gaps
in capabilities SoulMap already has rather than new features. Each repository
was cloned to a local scratch directory (not vendored, not added to the repo)
and read directly; one tool was also run diagnostically against SoulMap's own
tree to get real numbers instead of guessing from documentation alone.

## Scope

- [agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw): a full
  personal-AI-assistant product.
- [kucherenko/jscpd](https://github.com/kucherenko/jscpd): a copy/paste
  (duplicate code) detector, 224+ language formats, bundled by GitHub Super
  Linter, MegaLinter, and Codacy.
- [openai/codex-security](https://github.com/openai/codex-security): a CLI
  and SDK that runs an LLM-driven (Codex) security scan against a codebase.

## Findings and actions

| Repository | Classification | Reasoning | Action |
| --- | --- | --- | --- |
| QwenPaw | NOT APPLICABLE | Persistent 3-layer memory, agentic tool-use with a kernel-level sandbox, multi-channel deployment (DingTalk, Telegram, WeChat, ...), a plugin marketplace, and version-based telemetry are the product. Every one of those is a documented SoulMap non-goal: no cross-session memory bonding (Rule 1, `known-limitations.md`), no background jobs or platform adapters beyond Claude-first, no telemetry (`maintenance-boundary.md`). This is a different product category, not a maturity gap in something SoulMap has | None |
| jscpd | EVALUATED, NOT ADOPTED | See "jscpd diagnostic run" below | None (no dependency added); see "Rule additions" for what the exploration did produce |
| codex-security | NOT APPLICABLE AS A TOOL | Requires an OpenAI API key, runs a paid, cloud, LLM-agent-driven scan with its own findings database and Trusted Access approval program. CodeQL, `pip-audit`, and Socket Security already run in this repository's CI; `docs/operations/dependency-refresh.md` and the `ruff` config's own comment already record "not add a scanner merely because an alternative exists" | None as a tool; see "Rule additions" for the one thing worth keeping from it |

## jscpd diagnostic run

Rather than judge jscpd from its README alone, it was run against SoulMap's
actual `src/` and `skills/` trees (`npx jscpd@4 src skills --min-lines 5
--min-tokens 40`, one-off, nothing installed into the repo):

| Format | Files | Duplicated lines | Duplicated tokens |
| --- | --- | --- | --- |
| `markdown` | 77 | 50 (0.35%) | 612 (0.33%) |
| `python` | 93 | 541 (4.38%) | 3615 (4.86%) |

Both numbers are low, and reading the actual clone pairs shows why:

- Almost all of the Python "duplication" is two already-intentional, repo-wide
  templates: every detector module's docstring-plus-imports header
  (`.claude/rules/detector-development.md`'s documented "Module structure"),
  and the standard `argparse`-based `main()` wrapper every `devtools/checks/`
  module follows (build parser, resolve repo root, call `check_repo()`, print
  `path:line: message`, return 0 or 1). `python-tooling.md` already says not
  to force a shared helper onto a call site with a materially different
  contract just because the shape looks similar; these call sites already
  differ enough (different flags, different issue-formatting details) that
  forcing them through one helper would trade 10 duplicated lines for a
  parameterized helper that is harder to read at each site.
- One genuine, small candidate did surface:
  `src/soulmap/devtools/support/markdown.py`'s heading-anchor builder and
  `src/soulmap/runtime/guards/markdown_contract.py`'s numbered-heading check
  share an identical ~10-line preamble (walk lines, skip fenced blocks via
  `FenceTracker`, match `_ATX_HEADING_RE`, unpack `(_hashes, title)`) before
  diverging completely. This is real but tiny (11 lines, one pair of files)
  and was left alone rather than turned into a same-day refactor: extracting
  it trades a small, self-contained duplication for a new shared iterator
  both files would depend on, for a one-time saving under 15 lines. Recorded
  here rather than silently dropped, so a future pass that touches either
  file can fold the extraction in if it is doing related work anyway.
- Markdown duplication (0.35%) is consistent with the loaders already fixing
  the historical case this class of tool would normally justify itself on:
  `docs/ROADMAP.md`'s Phase 13 removed 140 duplicated detection phrases from
  shipped skill files, and `extract_keyword_section` and
  `extract_labeled_groups` in
  `src/soulmap/runtime/knowledge/keyword_lists.py` both end by returning
  `tuple(dict.fromkeys(...))`, deduplicating every phrase list at parse time.
  A duplicate phrase reintroduced into a skill file today cannot double-count
  a detector's score, because the same loader every detector uses already
  collapses it before scoring ever sees it. The remaining low duplication
  rate is mostly incidental short phrases, not the class of bug Phase 13
  fixed.

Conclusion: SoulMap does not have a live, unprotected duplication gap that
would justify a new dependency (jscpd ships as a Node.js package or a
downloaded Rust binary; this repository currently has zero Node.js
dependencies). Per `maintenance-boundary.md`'s valid-trigger test, none of "a
real blocker in the current workflow," "an active user or distribution need,"
or "protects an important safety or quality contract" holds here strongly
enough to add a new toolchain for a check whose findings are already this
close to noise.

## Rule additions

Two ideas were worth keeping without adopting either external tool, both
closing a real gap: something already implicit in this session's own working
discipline that was not yet written down anywhere in `.claude/`, so it would
not survive a session that lacked this specific context.

- `.claude/skills/code-quality-review/SKILL.md`: added "speculative
  validation, sanitization, or fallback logic for a scenario that cannot
  actually occur" to its "What to look for" list, from `codex-security`'s
  own `AGENTS.md` ("Avoid speculative defenses ... State the concrete
  failure it fixes"). SoulMap's outer system prompt already carries this
  principle, but nothing inside the repository itself stated it, so a
  contributor or a differently-configured agent reading only `.claude/`
  would not see it.
- `.claude/skills/cli-tooling-maintainer/SKILL.md`: added a bullet treating
  the `soulmap` command surface (`_command_table()` in `cli.py`) as a
  stability contract, adapted from the same `AGENTS.md`'s "Public CLI
  changes" section. This repository already behaves this way in practice
  (the CLI has grown by exactly 15 stable, well-documented commands over the
  life of the project, per `docs/engineering/API.md`), but the discipline
  was not written down anywhere a maintainer would find it before adding a
  16th.

Nothing from `codex-security`'s scanning behavior itself was kept: the two
bullets above come from its process documentation, not its product.

## Validation basis

Documentation-only change (two `.claude/skills/*.md` files and this research
note). Validated with `uv run soulmap markdown-contract --root .`,
`uv run soulmap check-links --root .`, `uv run soulmap check-case --root .`,
and `uv run soulmap lint`. No Python, Skill, test, or packaging surface was
touched. The jscpd diagnostic run was local and one-off; no dependency,
config file, or CI step was added for it.
