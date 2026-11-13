# Runtime Knowledge Architecture

For how this knowledge-loading layer fits into the full request pipeline
alongside routing and safety enforcement, see
[`docs/engineering/safety-architecture.md`](safety-architecture.md).

Detectors in `src/soulmap/runtime/` combine semantic knowledge from Markdown skill
files with executable policy owned by Python. Markdown remains the source for many
human-authored signal phrases, regex patterns, and response guidance. Numeric weights,
thresholds, scoring rules, routing priorities, and policy toggles that control execution
belong in `src/soulmap/runtime/knowledge/runtime_config.py`.

Most current detectors resolve stable source identifiers through the repository-internal
`src/soulmap/runtime/source_registry.py`; the registry maps those identifiers to shipped
knowledge files and their contract sections. The loader utilities in
`src/soulmap/runtime/knowledge/` provide the parsing layer between Markdown structure and
Python data structures. The registry itself is internal runtime metadata and is
intentionally excluded from the shipped knowledge archives.

For registry-backed, Markdown-driven detectors, each phrase has a canonical source
section that the runtime loads, reducing drift between detection inputs and documented
knowledge. This does not describe every detector: crisis signals remain in static
Python language packs and crisis-detector constants, as documented below.

## How detectors load knowledge

Registry-backed detectors resolve a stable source identifier at import time and then
load the registered Markdown path and section. The runtime registry validates that each
registered path stays under `skills/`, exists, and contains the registered signal,
contract, and guidance headings. A small set of loaders also supports direct path resolution for sources that are not
registry-backed. `default_skill_path()` resolves those runtime paths without importing
devtools; the pattern loader only parses a caller-supplied Markdown path and does not
perform repository path discovery.

Two loader utilities cover all current detector patterns:

- `keyword_lists.py` parses flat quoted-phrase lists and labeled phrase groups
  from a named section under a Markdown heading. Used by detectors that need a
  plain tuple of matching phrases per category.
- `pattern_source.py` parses the structured `## Pattern N:` sections in
  `skills/frameworks/pattern-mapper.md` into typed `PatternSignal` objects with
  names, descriptions, detection signals, cycle phrases, and reflection language.
  It accepts the Markdown path from its caller and does not resolve repository paths.

The stable mapping between runtime consumers and Markdown sources is centralized in
`src/soulmap/runtime/source_registry.py`. The registry is a machine-facing contract, not a
second knowledge base. Detector code should consume stable source identifiers rather
than duplicating repository paths.

The `soulmap audit-knowledge` command reports Python configuration usage and orphaned
constants, detects duplicate phrases between Python and Markdown, and flags exact phrase
overlaps between detector code and Markdown knowledge. It does not replace the
source-registry audit.

The separate `soulmap audit-knowledge-ownership` command checks the runtime source
boundary: calls to `runtime_skill_path()` must use literal identifiers registered in
`source_registry.py`; registered sources must have runtime consumers; and direct
`default_skill_path()` calls that bypass the registry are reported. This command does
not audit package membership or the complete build-artifact boundary.

## Ownership audit

The ownership audit is intentionally distinct from phrase-duplication checks. It
verifies that runtime Markdown consumers resolve sources through the central registry
and that the registry has neither unregistered references nor unused entries. Domain
classification is maintained as framework discovery metadata rather than as a separate
filesystem layer.

## Protected modules

The per-language crisis packs (`safety_en.py`, `safety_vi.py`, `safety_es.py`,
`safety_fr.py`, `safety_zh.py`), `src/soulmap/runtime/knowledge/crisis_language_packs.py`
(which combines the packs by direct import, not Markdown loading), and
`src/soulmap/runtime/detectors/crisis_detector.py` use hardcoded Python constants
rather than Markdown-loaded phrase lists. This is intentional.

`src/soulmap/runtime/config/safety.py` is currently a legacy stub with no safety constants:
it defines no safety constants and is not imported by the runtime. The phrase-tuple signals live in the per-language packs and are combined by
`crisis_language_packs.py`. The detector also evaluates its local
`CRISIS_TIER1_PATTERNS` and `FAREWELL_CRISIS_PATTERNS` regex lists directly.
The stub remains review-only; static reachability alone is not sufficient grounds to
delete it.

Crisis detection (Issue #130) is multilingual but still fully static: each
language pack is a literal, human-authored tuple of phrases with no translation
engine, no machine translation, and no external API call anywhere in the runtime.
Adding a language means adding a new `safety_<code>.py` module with the same three
tuples (`CRISIS_TIER1`, `CRISIS_TIER2`, `GRANDIOSITY_SIGNALS`) and importing it
from `crisis_language_packs.py` - nothing else in the detection pipeline changes,
and the crisis response policy itself does not vary by language.

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

- Audit before changing. Run `soulmap audit-knowledge` for config/phrase drift and
  `soulmap audit-knowledge-ownership` for source-registry boundaries before touching
  any phrase list or loader.
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
