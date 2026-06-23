from __future__ import annotations

import json
from pathlib import Path

from soulmap.runtime.policy import load_policy_bundle

POLICY_DIR = Path("policies")
REQUIRED_FILES = {
    "allowlist.json",
    "denylist.json",
    "capability-registry.json",
    "policy-index.json",
    "schemas/policy-file.schema.json",
}


def test_policy_layer_files_are_valid_json() -> None:
    for filename in REQUIRED_FILES:
        with (POLICY_DIR / filename).open(encoding="utf-8") as file:
            document = json.load(file)
        if filename == "schemas/policy-file.schema.json":
            assert document["$schema"]
            assert document["title"] == "SoulMap policy metadata file"
        else:
            assert document["schema_version"]
            assert document["policy_id"].startswith("soulmap.")
            assert document["policy_version"]
            assert document["source_of_truth"] == "AGENTS.md"
            assert document["enforcement_mode"] == "metadata_only"


def test_policy_index_loads_referenced_files() -> None:
    bundle = load_policy_bundle()

    assert set(bundle.files) == {"allowlist", "denylist", "capability_registry"}
    assert bundle.index["runtime_contract"]["load_order"] == [
        "denylist",
        "allowlist",
        "capability_registry",
    ]


def test_policy_bundle_contains_critical_governance_ids() -> None:
    bundle = load_policy_bundle()

    bundle.require_policy_ids(
        {
            "prohibited.crisis",
            "prohibited.diagnosis",
            "prohibited.prediction",
            "core.self_awareness",
            "core.personal_spirituality",
            "capability.crisis_override",
        }
    )


def test_policy_files_do_not_duplicate_literal_detector_patterns() -> None:
    bundle = load_policy_bundle()

    denylist = bundle.files["denylist"]
    for section in ("request_types", "out_of_scope_categories"):
        for record in denylist[section]:
            assert "patterns" not in record
            assert "examples" not in record
            assert record["detectors"]
            assert record["capabilities"]


def test_policy_index_declares_metadata_only_runtime_contract() -> None:
    bundle = load_policy_bundle()

    assert bundle.index["enforcement_mode"] == "metadata_only"
    assert (
        "existing_runtime_denylists" in bundle.index["runtime_contract"]["precedence"]
    )
    assert (
        "runtime behavior must remain unchanged"
        in bundle.index["runtime_contract"]["fallback"]
    )
