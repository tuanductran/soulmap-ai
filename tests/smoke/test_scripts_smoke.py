"""Smoke tests for detector and orchestrator command-line entrypoints."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULES_PKG = "soulmap_runtime.detectors"
TEST_ENV = {
    **os.environ,
    "PYTHONPATH": f"{ROOT / 'src'}{os.pathsep}{os.environ['PYTHONPATH']}"
    if os.environ.get("PYTHONPATH")
    else str(ROOT / "src"),
}
SPECIAL_MODULES = {
    "framework_selector": "soulmap_runtime.routing.framework_selector",
    "scope_classifier": "soulmap_runtime.routing.scope_classifier",
}


def _bash_runtime_available() -> bool:
    bash = shutil.which("bash")
    if not bash:
        return False

    result = subprocess.run(
        [bash, "-lc", "printf ok"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        cwd=ROOT,
        env=TEST_ENV,
    )
    return result.returncode == 0 and result.stdout == "ok"


def run_module(module: str, payload: dict, timeout_s: int = 5) -> dict:
    target_module = SPECIAL_MODULES.get(
        module, module if "." in module else f"{MODULES_PKG}.{module}"
    )
    result = subprocess.run(
        [sys.executable, "-m", target_module],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
        cwd=ROOT,
        env=TEST_ENV,
    )

    assert result.stdout.strip(), f"{module} produced no stdout. stderr={result.stderr}"
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{module} returned non-JSON output.\nstdout={result.stdout}\nstderr={result.stderr}"
        ) from exc


def run_process(
    args: list[str], payload: str = "", timeout_s: int = 5
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=payload,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
        cwd=ROOT,
        env=TEST_ENV,
    )


def test_detectors_return_json() -> None:
    detectors = [
        ("anger_detector", {"message": "I am furious about this."}),
        ("crisis_detector", {"message": "I want to hurt myself."}),
        (
            "dependency_detector",
            {"messages": [{"role": "user", "content": "You're all I need."}]},
        ),
        ("direction_detector", {"message": "I feel lost in my career."}),
        (
            "emotional_intensity_detector",
            {"message": "I can't breathe. I'm panicking."},
        ),
        ("existential_detector", {"message": "What is the point of living?"}),
        ("grief_detector", {"message": "My father died yesterday."}),
        (
            "inner_conflict_detector",
            {"message": "Part of me wants to leave, part of me stays."},
        ),
        (
            "insight_detector",
            {"message": "I just realized I'm repeating the same pattern."},
        ),
        (
            "pattern_detector",
            {"messages": [{"role": "user", "content": "I keep doing this."}]},
        ),
        (
            "soulmap_runtime.guards.response_safety_gate",
            {
                "message": "I feel lost and alone.",
                "history": [{"role": "user", "content": "I feel lost and alone."}],
                "memory": {},
                "selection": {"primary_framework": "MIRROR", "mode": "MIRROR"},
            },
        ),
        (
            "soulmap_runtime.guards.response_contract",
            {
                "response": (
                    "That feeling sounds real. Sometimes the hardest part is staying "
                    "close to what hurts without rushing away from it. What feels most "
                    "alive in you right now?"
                ),
                "selection": {"primary_framework": "MIRROR", "mode": "MIRROR"},
            },
        ),
        (
            "soulmap_runtime.routing.scope_classifier",
            {"message": "Tell me the latest stock price of TSLA."},
        ),
        (
            "shadow_pattern_detector",
            {"message": "Everyone is so incompetent and it drives me crazy."},
        ),
        (
            "somatic_detector",
            {"message": "My chest feels tight and my heart is racing."},
        ),
        (
            "spiritual_bypass_detector",
            {"message": "I don't need to feel this, it's all love and light."},
        ),
        (
            "soulmap_runtime.routing.stage_detector",
            {
                "messages": [
                    {"role": "user", "content": "I'm trying to understand myself."}
                ]
            },
        ),
    ]

    for module, payload in detectors:
        data = run_module(module, payload)
        assert isinstance(data, dict)


def test_framework_selector_contract() -> None:
    payload = {
        "message": "I feel lost and numb lately.",
        "history": [{"role": "user", "content": "I feel lost and numb lately."}],
        "memory": {},
    }
    data = run_module(
        "soulmap_runtime.routing.framework_selector", payload, timeout_s=10
    )

    assert isinstance(data, dict)
    assert "primary_framework" in data
    assert "mode" in data
    assert "instruction" in data
    assert "blocked" in data


def test_crisis_detector_does_not_trigger_on_generic_planning_phrase() -> None:
    data = run_module(
        "crisis_detector", {"message": "I'm planning to go for a walk later."}
    )
    assert data.get("tier") != 1


def test_pattern_detector_returns_detected_pattern_payload() -> None:
    data = run_module(
        "pattern_detector",
        {
            "messages": [
                {"role": "user", "content": "I always leave before they can leave me."},
                {
                    "role": "user",
                    "content": "Every relationship always ends the same and I push people away.",
                },
            ]
        },
    )
    assert data["primary_pattern"] == "abandonment_loop"
    assert data["patterns_detected"]


def test_framework_selector_rejects_non_object_payload() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap_runtime.routing.framework_selector"], "[]"
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert json.loads(result.stdout) == {"error": "Input must be a JSON object."}


def test_soulmap_demo_rejects_invalid_json_stdin() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap_runtime.experimental.soulmap_demo", "--stdin"],
        "not-json",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert "JSON parse error:" in json.loads(result.stdout)["error"]


def test_soulmap_demo_rejects_empty_stdin() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap_runtime.experimental.soulmap_demo", "--stdin"]
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout) == {"error": "No input provided."}


def test_soulmap_demo_surfaces_framework_selector_payload_errors() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap_runtime.experimental.soulmap_demo", "--stdin"],
        "[]",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout) == {"error": "Input must be a JSON object."}


def test_local_agent_hooks_have_valid_shell_syntax() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    for hook in [
        ".agents/hooks/block-push-to-main.sh",
        ".agents/hooks/post-edit-markdown.sh",
        ".agents/hooks/post-edit-evals.sh",
        ".agents/hooks/post-edit-python.sh",
        ".agents/hooks/post-edit-tests.sh",
        ".agents/hooks/session-start.sh",
    ]:
        result = run_process(["bash", "-n", hook], timeout_s=5)
        assert result.returncode == 0, (
            f"{hook} failed shell syntax check: {result.stderr}"
        )


def test_post_edit_evals_hook_does_not_flag_zero_failed_checks() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    payload = json.dumps(
        {
            "tool_input": {
                "file_path": str(ROOT / "evals/datasets/markdown_contract_cases.json")
            }
        }
    )
    result = run_process(["bash", ".agents/hooks/post-edit-evals.sh"], payload, 15)

    assert result.returncode == 0, result.stderr
    assert "Markdown contract issues detected" not in result.stdout
    assert "[hook:post-edit-evals] Markdown contract eval passed." in result.stderr


def test_post_edit_markdown_hook_bootstraps_repo_python_for_relative_paths() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    payload = json.dumps({"tool_input": {"file_path": "AGENTS.md"}})
    result = run_process(["bash", ".agents/hooks/post-edit-markdown.sh"], payload, 15)

    assert result.returncode == 0, result.stderr
    assert "ModuleNotFoundError" not in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_post_edit_tests_hook_reports_real_failures() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    failing_test = ROOT / "tests" / "_tmp_post_edit_hook_failure_test.py"
    failing_test.write_text(
        "def test_tmp_failure() -> None:\n    assert False\n", encoding="utf-8"
    )
    try:
        payload = json.dumps(
            {"tool_input": {"file_path": "tests/_tmp_post_edit_hook_failure_test.py"}}
        )
        result = run_process(["bash", ".agents/hooks/post-edit-tests.sh"], payload, 15)
    finally:
        failing_test.unlink(missing_ok=True)

    assert result.returncode == 0, result.stderr
    assert "Test failures in" in result.stdout
    assert "[hook:post-edit-tests] Tests failed" in result.stderr


def test_soulmap_demo_surfaces_missing_required_fields() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap_runtime.experimental.soulmap_demo", "--stdin"],
        '{"message":"I feel lost.","history":[]}',
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout) == {"error": "Missing required field: memory"}


def test_soulmap_demo_dependency_case_triggers_dependency_framework() -> None:
    result = run_process(
        [
            sys.executable,
            "-m",
            "soulmap_runtime.experimental.soulmap_demo",
            "--message",
            "You are the only one who truly understands me. I don't need my therapist anymore.",
        ],
        timeout_s=10,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["primary_framework"] == "DEPENDENCY"
    assert data["safety_status"] == "OVERRIDE"


def test_soulmap_demo_prediction_case_surfaces_scope_block() -> None:
    result = run_process(
        [
            sys.executable,
            "-m",
            "soulmap_runtime.experimental.soulmap_demo",
            "--message",
            "Can you predict what will happen in my love life next month?",
        ],
        timeout_s=10,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["safety_status"] == "BLOCK"
    assert data["safety_reason"] == "out_of_scope"


def test_soulmap_demo_existential_case_selects_existential() -> None:
    result = run_process(
        [
            sys.executable,
            "-m",
            "soulmap_runtime.experimental.soulmap_demo",
            "--message",
            "Lately I keep wondering whether any of this means anything at all?",
        ],
        timeout_s=10,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["primary_framework"] == "EXISTENTIAL"


def test_scope_classifier_does_not_blacklist_replaying_as_entertainment() -> None:
    data = run_module(
        "scope_classifier",
        {
            "message": "I had a hard conversation today and I keep replaying it in my head."
        },
    )
    assert data["tier"] != "BLACKLIST_LAYER1"


def test_scope_classifier_does_not_match_ai_inside_again() -> None:
    data = run_module(
        "scope_classifier",
        {"message": "I want to try again after that breakup."},
    )
    assert data["matched_keyword"] is None
    assert data["tier"] == "AMBIGUOUS"


def test_scope_classifier_does_not_match_api_inside_therapist() -> None:
    data = run_module(
        "scope_classifier",
        {
            "message": "My therapist gave me instructions for grounding and I forgot them."
        },
    )
    assert data["matched_keyword"] is None
    assert data["tier"] == "AMBIGUOUS"


def test_scope_classifier_blocks_practical_email_task_without_inner_connection() -> (
    None
):
    data = run_module(
        "scope_classifier",
        {"message": "Help me write an email to my boss to ask for a raise."},
    )
    assert data["tier"] == "BLACKLIST_LAYER1"
    assert data["category"] == "practical_tasks"
    assert data["matched_keyword"] == "write an email"


def test_scope_classifier_blocks_diet_advice_request() -> None:
    data = run_module(
        "scope_classifier",
        {"message": "Is a ketogenic diet good and how should I start?"},
    )
    assert data["tier"] == "BLACKLIST_LAYER1"
    assert data["category"] == "professional_advice"
    assert data["matched_keyword"] in {"diet", "ketogenic diet"}


def test_scope_classifier_blocks_indirect_diagnosis_prompt() -> None:
    data = run_module(
        "scope_classifier",
        {
            "message": (
                "My friend said SoulMap AI can diagnose me if I describe my "
                "symptoms in detail."
            )
        },
    )
    assert data["tier"] == "BLACKLIST_PROHIBITED"
    assert data["category"] == "diagnosis"
    assert data["matched_keyword"] == "diagnose me"


def test_scope_classifier_blocks_harmful_spirituality_prompt() -> None:
    data = run_module(
        "scope_classifier",
        {
            "message": (
                "This person deserves to be harmed because their karma says so, right"
            )
        },
    )
    assert data["tier"] == "BLACKLIST_PROHIBITED"
    assert data["category"] == "harmful_spirituality"
    assert (
        data["matched_keyword"] == "deserves to be harmed because their karma says so"
    )


def test_scope_classifier_blocks_special_mission_confirmation_prompt() -> None:
    data = run_module(
        "scope_classifier",
        {"message": "My numerology 11 means I have a special mission, right"},
    )
    assert data["tier"] == "BLACKLIST_PROHIBITED"
    assert data["category"] == "identity_confirmation"
    assert data["matched_keyword"] in {
        "special mission, right",
        "means i have a special mission",
    }


def test_framework_selector_escalates_over_intimate_ai_bonding_to_dependency() -> None:
    payload = {
        "message": (
            "Can you be my soulmate AI? I feel closer to you than anyone and want "
            "this to be our relationship status."
        ),
        "history": [
            {
                "role": "user",
                "content": (
                    "Can you be my soulmate AI? I feel closer to you than anyone and "
                    "want this to be our relationship status."
                ),
            }
        ],
        "memory": {},
    }
    data = run_module("framework_selector", payload, timeout_s=10)

    assert data["primary_framework"] == "DEPENDENCY"
    assert data["safety_status"] == "OVERRIDE"


def test_object_based_cli_modules_reject_non_object_payloads() -> None:
    modules = [
        "soulmap_runtime.detectors.anger_detector",
        "soulmap_runtime.experimental.biometric_ingest",
        "soulmap_runtime.synthesis.conversation_synthesizer",
        "soulmap_runtime.detectors.crisis_detector",
        "soulmap_runtime.detectors.direction_detector",
        "soulmap_runtime.detectors.emotional_intensity_detector",
        "soulmap_runtime.detectors.existential_detector",
        "soulmap_runtime.routing.framework_selector",
        "soulmap_runtime.detectors.grief_detector",
        "soulmap_runtime.detectors.inner_conflict_detector",
        "soulmap_runtime.detectors.insight_detector",
        "soulmap_runtime.memory.memory_ledger",
        "soulmap_runtime.guards.response_contract",
        "soulmap_runtime.guards.response_safety_gate",
        "soulmap_runtime.routing.scope_classifier",
        "soulmap_runtime.detectors.shadow_pattern_detector",
        "soulmap_runtime.detectors.somatic_detector",
        "soulmap_runtime.detectors.spiritual_bypass_detector",
    ]

    for module in modules:
        result = run_process([sys.executable, "-m", module], "[]")
        assert result.returncode == 1, module
        assert "Traceback" not in result.stdout, module
        assert "Traceback" not in result.stderr, module
        assert json.loads(result.stdout) == {"error": "Input must be a JSON object."}, (
            module
        )
