# Runtime Knowledge Architecture

Detectors in `src/soulmap/runtime/` load their phrase lists directly from the
shipped Markdown skill files at import time. The loader utilities in
`src/soulmap/runtime/knowledge/` provide the parsing layer between Markdown
structure and Python data structures.

This means there is one place to edit a detection phrase. The runtime reflects
the skill files automatically, so detection behavior and documented framework
knowledge cannot silently drift apart.

## How detectors load knowledge

Each detector declares its Markdown source path and section heading inline. The
detector resolves the skill file at import time using `default_skill_path()` or
`default_pattern_mapper_path()` from the knowledge module, which walks the
directory tree or uses the `SOULMAP_REPO_ROOT` environment variable when set.

Two loader utilities cover all current detector patterns:

- `keyword_lists.py` parses flat quoted-phrase lists and labeled phrase groups
  from a named section under a Markdown heading. Used by detectors that need a
  plain tuple of matching phrases per category.
- `pattern_source.py` parses the structured `## Pattern N:` sections in
  `skills/frameworks/pattern-mapper.md` into typed `PatternSignal` objects with
  names, descriptions, detection signals, cycle phrases, and reflection language.

The mapping between a detector and its Markdown source is visible by reading the
detector itself. There is no separate registry.

The `soulmap audit-knowledge` command independently verifies this ownership by
tracing runtime imports and cross-referencing them against Markdown content. It is
the authoritative, up-to-date record of which constants are active, which are
orphaned, and which Markdown file owns which detection phrases. Trust the tool
over any static document.

## Protected modules

`src/soulmap/runtime/config/safety.py` and
`src/soulmap/runtime/detectors/crisis_detector.py` use hardcoded Python constants
rather than Markdown-loaded phrase lists. This is intentional.

Safety-critical detection carries a much higher cost of failure than
framework-detection knowledge. A parsing error or an incomplete Markdown loading
path risks missing a genuine crisis or dependency signal, not just misclassifying
a reflective framework. That asymmetry justifies keeping the safety layer
hardcoded.

Any future proposal to migrate these modules requires at minimum:

- a full pass of the safety and crisis evaluation suites before and after the change
- independent verification that every signal variant is preserved
- explicit sign-off that the Markdown parsing path is reliable enough for safety use

The default answer to migrating these modules is no.

## Knowledge layer guidelines

These rules apply to any future change to detection phrase lists, loader utilities,
or the Markdown sections that back them:

- Audit before changing. Run `soulmap audit-knowledge` to establish the current
  state before touching any phrase list or loader.
- The repository is the source of truth. This document and prior summaries are not
  a substitute for running the audit tooling and reading the current code.
- Runtime evidence is required. A phrase or constant must have a confirmed Markdown
  owner and a detector that already loads from that file before any cleanup is
  considered safe.
- Verify Markdown ownership by reading the consuming detector's loading code, not
  by inferring it from a constant's name.
- Cross-check every audit finding with an independent repository search before
  acting on it.
- Keep each change as small as possible. A change should touch only the phrases
  being modified and their immediate loading context.
- Run the full validation suite before merging. A change is not complete if any
  step below fails.

## Validation

Run the full suite before merging any change to the knowledge layer:

- `soulmap format`
- `soulmap audit-knowledge`
- `soulmap lint`
- `pyright`
- `pytest`
- `soulmap eval-groups`
- `soulmap eval-markdown-contracts`
- `soulmap eval-responses`
- the safety evaluation suite
- `git diff --check`
