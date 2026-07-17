# Runtime Knowledge Migration Roadmap

Detector runtime code originally carried its own copies of clinical and
reflective phrase lists as Python constants (detection keywords, cycle
phrases, reflection language, and similar knowledge content). These
constants were hand-written alongside - and independent of - the Markdown
skill files that describe the same frameworks for response generation.

That duplication is a maintainability risk: a phrase edited in one place
does not automatically update the other, so the runtime's detection
behavior and the documented framework knowledge can silently drift apart
over time.

Markdown is becoming the single source of truth for this knowledge.
Runtime code loads phrase lists directly from the shipped Markdown skill
files at import time instead of hardcoding them. This removes the
duplication at its root: there is only one place to edit a detection
phrase, and the runtime is guaranteed to reflect it.

---

# Current Status

The following runtime knowledge domains have completed migration to
Markdown-backed loading:

- Meaning-related detection knowledge (direction, existential, insight,
  inner-conflict framework signals)
- Anger detection signals
- Grief detection signals
- Celebration detection signals
- Pattern-mapper, shadow-pattern, and spiritual-bypass detection knowledge
  formerly held in `src/soulmap/runtime/config/patterns.py`

As part of this work, `src/soulmap/runtime/config/affect.py` has been
fully retired as a runtime knowledge source, and
`src/soulmap/runtime/config/patterns.py` has been removed from the
repository entirely. Detectors that previously imported from either
module now load their phrase lists directly from their owning Markdown
skill files.

---

# Current Runtime Ownership

Detectors that have completed migration load their knowledge directly
from their owning Markdown skill file at import time, using the shared
loader utilities in `src/soulmap/runtime/knowledge/`. Each such detector
declares its Markdown source path and section inline, so the mapping
between a detector and its knowledge source is discoverable by reading
the detector itself rather than by consulting a separate registry.

Repository tooling (`soulmap audit-knowledge`) independently verifies
this ownership by tracing runtime imports and cross-referencing them
against Markdown content. That tool - not this document - is the
authoritative, up-to-date record of which constants are active, which
are orphaned, and which Markdown file owns which detection phrases.
Contributors should re-run it rather than trust a prior summary, since
ownership can change with any migration batch.

---

# Remaining Repository Work

## Safe to migrate later

None identified. `src/soulmap/runtime/config/patterns.py` has been
removed, and no other non-protected module currently holds orphaned
knowledge constants according to repository audit tooling.

## Requires additional audit

None currently open. Re-run `soulmap audit-knowledge` before assuming
this stays true, since the inventory changes with every migration batch.

## Protected

`src/soulmap/runtime/config/safety.py` and `src/soulmap/runtime/detectors/
crisis_detector.py` are out of scope for this migration. See "Protected
Modules" below.

---

# Protected Modules

`safety.py` and `crisis_detector.py` remain out of scope for this
migration effort. Safety-critical detection (crisis signals, dependency
signals) carries a much higher cost of failure than framework-detection
knowledge: a parsing error or an incomplete Markdown migration in this
path risks missing a genuine safety signal, not just misclassifying a
reflective framework.

Migrating this module is not ruled out permanently, but it requires
stronger evidence than the standard migration bar used elsewhere in this
roadmap - at minimum, dedicated review of the safety and crisis
evaluation suites before and after any change, not just the standard
validation checklist.

---

# Patterns Module

`src/soulmap/runtime/config/patterns.py` has been removed from the
repository. The constants it held were retired only after each one was
independently confirmed, per constant, to have zero remaining runtime
importers, an explicit Markdown owner, and a detector that already
loaded the equivalent content directly from that Markdown file. This
section is kept as a record of that migration rather than as an open
item.

---

# Meaning Module

`MISALIGNMENT_SIGNALS` in `src/soulmap/runtime/config/meaning.py`
remains in place. It was intentionally preserved rather than migrated
alongside the rest of the meaning-related knowledge, because the
direction detector that uses equivalent signals loads its own copy
directly from Markdown independently of this constant. Removing it
without first re-confirming, via the audit tooling, that nothing else
depends on it would be a guess rather than an evidence-based migration
decision, so it is left in place until a dedicated audit says otherwise.

---

# Migration Principles

These rules were established over the course of this migration and
should govern any future batch:

- Audit first. Never remove a constant on the basis of its name or
  apparent redundancy alone.
- The repository is the source of truth. Prior summaries, roadmap
  documents, or conversation history are not a substitute for re-running
  the audit tooling and reading the current code.
- Runtime evidence is required before deletion: a constant must have
  zero remaining importers, confirmed independently of any single tool.
- Markdown ownership must be verified by reading the consuming
  detector's loading code, not inferred from a constant's name.
- Cross-check every audit finding with an independent repository search
  before acting on it.
- Full validation is required before any migration batch is considered
  complete.
- Keep each migration batch as small as possible. A batch should touch
  only the constants being removed and their now-unnecessary re-exports.

---

# Validation Checklist

Run the full validation suite before merging any future migration
batch:

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

A batch is not complete if any of these fail. Investigate before
continuing rather than proceeding past an unexplained failure.

---

# Success Criteria

The runtime knowledge migration is complete when `soulmap audit-knowledge`
reports zero orphaned constants outside of modules that
have been explicitly and permanently designated as protected (see
"Protected Modules"), and every remaining runtime detection phrase list
is loaded directly from its owning Markdown skill file rather than
hardcoded in Python.

---

# Future Work

The repository's own audit tooling is the authoritative record of what
work remains at any given time. As of the most recent audit, the only
orphaned constants are `MISALIGNMENT_SIGNALS` (intentionally preserved;
see "Meaning Module") and the contents of `safety.py` (protected; see
above) - there is no non-protected module with outstanding migration
work. Future contributors should re-run `soulmap audit-knowledge` rather
than rely on this section, since the inventory changes with every
migration batch.
