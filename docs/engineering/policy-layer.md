# SoulMap policy layer audit and safest evolution plan

## 1. Architecture Review

### What should be accepted immediately

| Item | Recommendation | Rationale | Benefit | Migration impact | Compatibility risk |
| --- | --- | --- | --- | --- | --- |
| `policies/` directory | Accept as additive governance metadata | It preserves `AGENTS.md` and gives reviewers stable policy ids | Better auditability without behavior change | New files only | Low |
| `policy-index.json` | Accept after clarifying `metadata_only` status | A single index prevents scattered governance metadata | CI and reports can discover policy files deterministically | New file only | Low |
| Contract tests | Accept | Tests protect file validity and critical ids | Prevents broken governance metadata from merging | Additive test coverage | Low |
| Source distribution inclusion | Accept | Policy metadata must ship with the knowledge package | Packaged audits see the same policy layer | One package manifest line | Low |

### What should be modified before merge

| Item | Required modification | Rationale | Benefit | Migration impact | Compatibility risk |
| --- | --- | --- | --- | --- | --- |
| Literal patterns in `denylist.json` | Remove from policy metadata | Patterns already live in runtime constants and eval datasets. Duplicating them creates drift | Maintains one behavioral implementation during metadata phase | JSON-only edit | Low |
| Runtime language in docs and loader | Reword to governance and diagnostics only | The layer must not imply policy-driven runtime enforcement yet | Avoids accidental behavior migration | Docs/docstring edit | Low |
| Version metadata | Add `policy_version`, `created_at`, `updated_at`, and `enforcement_mode` | Policy files need independent lifecycle and explicit non-enforcement status | Safer reviews and release notes | JSON-only edit | Low |
| Blocked social sources | Change from global hard block to source categorization and evidence weighting | Some social/user-generated sources may be relevant in narrow contexts but should not support authoritative claims | More nuanced web governance | JSON-only edit | Low |
| Capability ownership | Add owner metadata | Capabilities need accountable maintainers | Clearer review routing | JSON-only edit | Low |

### What should be delayed

| Item | Recommendation | Rationale | Benefit | Migration impact | Compatibility risk |
| --- | --- | --- | --- | --- | --- |
| Runtime migration to policy-driven detectors | Delay to Phase 3 or later | Existing detectors and evals are stable and safety-critical | Avoids destabilizing request handling | Medium to high | Medium to high |
| Skill frontmatter policy ids across all skills | Delay and apply only to safety-critical skills first | Bulk metadata edits add review noise | Gradual traceability | Medium | Low |
| Generated traceability report CLI | Delay until metadata shape stabilizes | Reports are useful but premature before registry coverage improves | Better audit output later | Medium | Low |
| Full policy drift detection | Delay until canonical ownership is settled | Drift checks can create false positives while JSON is metadata-only | Better governance later | Medium | Medium |

### What creates unnecessary complexity

Do not add a policy engine, rule expression language, or generated detector code now. These would increase architecture surface area without improving safety until there is evidence that current runtime constants are failing governance needs.

### What creates governance risk

The highest governance risk is treating JSON as a replacement constitution. `AGENTS.md` must remain primary. Policy JSON should cite `AGENTS.md`, not reinterpret it independently.

### What creates runtime risk

The highest runtime risk is loading policy records in detectors before parity tests prove equivalent behavior. The policy layer should remain `metadata_only` until coverage, drift reports, and eval comparisons demonstrate readiness.

## 2. Risk Analysis

| Risk | Source | Mitigation | Rationale | Benefit | Migration impact | Compatibility risk |
| --- | --- | --- | --- | --- | --- | --- |
| Doctrine drift | JSON, Markdown, and Python constants diverge | Keep JSON metadata-only and add validation first | Avoids competing sources of truth | Safer reviews | Low | Low |
| False enforcement claims | Capability registry says `enforced` without tests | Require test paths for enforced capabilities | Keeps audit claims evidence-backed | Better compliance posture | Low | Low |
| Web overblocking | Social domains globally blocked | Categorize and weight sources instead | Preserves nuance while avoiding weak evidence | Better research behavior later | Low | Low |
| Runtime regression | Detectors consume unproven policy data | Defer runtime migration | Production stability over architectural purity | None now | Low |
| Maintenance burden | Literal patterns duplicated in JSON | Store policy ids, detector refs, and capabilities only | One place remains responsible for matching behavior | Lower drift | Low | Low |

## 3. Policy Layer Review

### Allowlist and denylist design

`allowlist.json` and `denylist.json` should contain policy identifiers, detector references, capability references, skill references, severity, and guardrail intent. They should not contain literal detection patterns during the metadata-only phase.

| Design choice | Tradeoff | Decision |
| --- | --- | --- |
| Literal patterns | Easy to inspect but duplicates runtime constants and eval data | Do not include now |
| Policy identifiers | Stable anchors for docs, tests, and reports | Include now |
| Detector references | Shows current implementation ownership without changing behavior | Include now |
| Capability references | Connects policy rows to higher-level governance claims | Include now |
| Runtime actions | Can imply active enforcement | Use `guardrail_intent`, not executable action |

This minimizes maintenance burden because pattern matching remains in the existing detectors and classifiers while the policy layer becomes an audit map.

### Blocked web sources

Social and user-generated domains such as `reddit.com`, `youtube.com`, `x.com`, `facebook.com`, `instagram.com`, and `tiktok.com` should not be hard-blocked as a universal denylist in this metadata layer. They should be categorized as low-trust sources with evidence weighting.

Rationale: hard blocking is appropriate for commercial fortune-telling, harmful medical misinformation, and conspiracy/pseudoscience sources. Social sources are weak for authoritative claims, but they may be relevant for platform-policy context, public statements, abuse reporting patterns, or lived-experience research when clearly labeled and not treated as authority.

Decision: use source categorization and evidence weighting now. Defer retrieval enforcement until there is an actual web retrieval subsystem to govern.

### Policy versioning

Every policy file should include:

- `schema_version`, because file shape and validation rules evolve separately from policy content.
- `policy_version`, because policy content needs release tracking.
- `created_at`, because audits need origin dates.
- `updated_at`, because reviewers need to see when governance metadata last changed.
- `enforcement_mode`, because it prevents metadata from being mistaken for active runtime enforcement.

### Traceability

`capability-registry.json` is necessary but not sufficient long-term. It is sufficient for Phase 0 because it creates a stable metadata source. Generated reports should come later because reporting is only useful after policy ids, owners, statuses, and test paths stabilize.

## 4. Rollout Plan

### Phase 0

Objective: merge metadata-only governance scaffolding.

Files changed: `policies/*.json`, `policies/schemas/policy-file.schema.json`, `src/soulmap/runtime/policy/*`, `tests/contract/test_policy_layer.py`, `docs/engineering/policy-layer.md`, `pyproject.toml`.

Risks: reviewers may infer runtime enforcement from metadata.

Rollback strategy: remove `policies/`, loader package, tests, docs, and package manifest entry. Runtime behavior remains unchanged.

Success criteria: all tests pass, policy files validate, docs explicitly say metadata-only.

### Phase 1

Objective: improve governance validation without touching request-time behavior.

Files changed: add a CLI or devtool validator, expand contract tests, optionally add schema-aware checks.

Risks: overstrict validation can block harmless documentation edits.

Rollback strategy: disable validator from CI while preserving metadata files.

Success criteria: validator catches missing versions, owners, invalid paths, and missing test references.

### Phase 2

Objective: generate audit reports from metadata.

Files changed: add report generator under `src/soulmap/devtools/`, generated report under `docs/engineering/` if committed.

Risks: generated reports can become noisy.

Rollback strategy: keep generator but stop committing generated output.

Success criteria: report maps AGENTS rule to policy, skill, guard, and test with no manual table drift.

### Phase 3

Objective: add drift detection between Markdown doctrine, policy metadata, and runtime constants.

Files changed: devtool drift checks and tests only.

Risks: false positives because Markdown is nuanced and not all doctrine should become machine policy.

Rollback strategy: run drift detection as advisory only.

Success criteria: high-risk drift such as missing crisis or prediction ids is detected without blocking normal content edits.

### Phase 4

Objective: consider policy-informed runtime diagnostics, not enforcement migration.

Files changed: optional request trace metadata that records selected policy ids after existing detectors run.

Risks: request latency, logging privacy, mistaken reliance on metadata.

Rollback strategy: disable tracing behind a flag.

Success criteria: traces explain existing decisions without changing outputs or routing.

## 5. Missing Infrastructure

| Infrastructure | Decision | Why | Rationale | Benefit | Migration impact | Compatibility risk |
| --- | --- | --- | --- | --- | --- | --- |
| JSON Schemas | Add now, minimal | Basic shape validation is low-risk | Prevents malformed files | Safer metadata | Low | Low |
| Policy validation CLI | Add later | Tests are enough for Phase 0 | Avoids CLI surface before schema stabilizes | Better tooling later | Medium | Low |
| Policy report generator | Add later | Registry must stabilize first | Avoids generated-noise churn | Better audits later | Medium | Low |
| Policy drift detection | Add later | Needs canonical ownership rules | Prevents premature false positives | Stronger governance later | Medium | Medium |
| Policy ownership metadata | Add now | Owners are simple and useful | Clarifies review responsibility | Better maintainability | Low | Low |
| Policy coverage tests | Add now, minimal | Critical ids should never disappear | Protects safety metadata | CI guardrails | Low | Low |
| Policy audit reports | Add later | Static doc is enough for first merge | Avoids report churn | Better release governance later | Medium | Low |

## 6. Prioritized Roadmap

### P0

Goal: make the proposed policy layer safe to merge as metadata only.

Files: `policies/*.json`, `policies/schemas/policy-file.schema.json`, `tests/contract/test_policy_layer.py`, `docs/engineering/policy-layer.md`.

Implementation notes: remove literal patterns, add version fields, add `enforcement_mode`, change source handling to category/weight metadata, and add tests that assert no denylist pattern duplication.

Test requirements: `uv run pytest tests/contract/test_policy_layer.py`, `uv run ruff check src/soulmap/runtime/policy tests/contract/test_policy_layer.py`, `uv run pytest`.

Migration requirements: none. Runtime behavior remains unchanged.

### P1

Goal: add a policy validation CLI after metadata shape stabilizes.

Files: `src/soulmap/devtools/cli/validate_policy.py`, `src/soulmap/devtools/policy/validate.py`, tests under `tests/contract/`.

Implementation notes: validate required fields, path existence, capability test references, owner presence, and allowed status values.

Test requirements: unit tests for valid and invalid policy fixtures.

Migration requirements: optional CI command only.

### P2

Goal: generate a safety traceability report.

Files: `src/soulmap/devtools/policy/report.py`, `docs/engineering/generated-policy-traceability.md`.

Implementation notes: generate AGENTS rule → policy → skill → runtime guard → test mappings from registry metadata.

Test requirements: snapshot or structural tests for generated rows.

Migration requirements: decide whether generated files are committed or CI artifacts.

### P3

Goal: explore policy-informed diagnostics after evidence proves metadata quality.

Files: optional runtime trace context only.

Implementation notes: attach policy ids to decisions already made by existing detectors. Do not let policy ids decide outcomes.

Test requirements: golden tests proving response selection is unchanged.

Migration requirements: feature flag and rollback switch.

## 7. Exact Code Changes

Implemented changes for the safe metadata-only phase:

1. Updated all policy files to include `schema_version`, `policy_version`, `created_at`, `updated_at`, and `enforcement_mode`.
2. Removed literal request patterns and out-of-scope examples from `denylist.json`.
3. Added detector and capability references to allowlist and denylist records.
4. Replaced hard social-domain blocking with `web_source_policy` categorization and evidence weighting.
5. Added minimal JSON Schema at `policies/schemas/policy-file.schema.json`.
6. Updated loader docs to state behavior-neutral governance usage.
7. Expanded tests to enforce metadata-only posture and prevent literal pattern duplication.

The concrete file contents are the repository files in this patch. The relevant tests are in `tests/contract/test_policy_layer.py`.

## 8. Final Recommendation

Merge now:

- Metadata-only policy files with explicit versioning and `enforcement_mode`.
- Minimal policy schema.
- Runtime-neutral loader.
- Contract tests for policy validity, critical ids, metadata-only status, and no denylist pattern duplication.
- Architecture review and rollout documentation.

Change before merge:

- Remove literal patterns from policy JSON.
- Reword runtime integration language so it does not imply active enforcement.
- Replace social-source hard blocking with evidence weighting.
- Add ownership/version metadata.

Postpone:

- Runtime migration to policy-driven detection.
- Drift detection.
- Generated traceability reports.
- Broad skill frontmatter policy-id rollout.
- Policy validation CLI beyond contract tests.

Never implement:

- A replacement constitution in JSON.
- A policy engine that bypasses `AGENTS.md`, existing skills, or eval-backed runtime guards.
- Generated detector behavior from policy metadata without parity tests and evaluation evidence.
- A universal hard block on broad social platforms without context-sensitive source policy.
