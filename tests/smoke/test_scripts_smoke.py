"""Smoke tests for detector and orchestrator command-line entrypoints."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULES_PKG = "soulmap.runtime.detectors"
TEST_ENV = {
    **os.environ,
    "PYTHONPATH": f"{ROOT / 'src'}{os.pathsep}{os.environ['PYTHONPATH']}"
    if os.environ.get("PYTHONPATH")
    else str(ROOT / "src"),
}
SPECIAL_MODULES = {
    "framework_selector": "soulmap.runtime.routing.framework_selector",
    "scope_classifier": "soulmap.runtime.routing.scope_classifier",
}


def _bash_runtime_available() -> bool:
    # The repo's shell hooks and wrapper scripts are macOS/Linux tooling. GitHub's
    # Windows runners may expose a bash executable via Git Bash, but that is not the
    # supported contract for these smoke tests and can fail for path/runtime reasons
    # unrelated to the repo's shipped Windows workflow.
    if os.name == "nt":
        return False

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
            "soulmap.runtime.guards.response_safety_gate",
            {
                "message": "I feel lost and alone.",
                "history": [{"role": "user", "content": "I feel lost and alone."}],
                "memory": {},
                "selection": {"primary_framework": "MIRROR", "mode": "MIRROR"},
            },
        ),
        (
            "soulmap.runtime.guards.response_contract",
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
            "soulmap.runtime.routing.scope_classifier",
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
            "soulmap.runtime.routing.stage_detector",
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
        "soulmap.runtime.routing.framework_selector", payload, timeout_s=10
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
        [sys.executable, "-m", "soulmap.runtime.routing.framework_selector"], "[]"
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert json.loads(result.stdout) == {"error": "Input must be a JSON object."}


def test_soulmap_demo_rejects_invalid_json_stdin() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap.runtime.experimental.soulmap_demo", "--stdin"],
        "not-json",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert "JSON parse error:" in json.loads(result.stdout)["error"]


def test_soulmap_demo_rejects_empty_stdin() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap.runtime.experimental.soulmap_demo", "--stdin"]
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout) == {"error": "No input provided."}


def test_soulmap_demo_survives_malformed_history_items() -> None:
    """A malformed history entry must not crash the safety gate.

    The demo checked that history was a list but not that its items were well
    formed, then called the selector in process. The detectors and
    `apply_safety_gate` index each entry as `m["content"]`, so an entry
    missing that key raised a KeyError from inside the gate. Every other entry
    point normalizes through the shared payload helper, which is what kept
    them safe.
    """
    payload = json.dumps(
        {
            "message": "i feel lost and do not know which direction to go",
            "history": [
                {"role": "user"},
                {"role": "user", "content": 123},
                "not a dict",
            ],
            "memory": {},
        }
    )
    result = run_process(
        [sys.executable, "-m", "soulmap.runtime.experimental.soulmap_demo", "--stdin"],
        payload,
    )

    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout)["primary_framework"] == "DIRECTION"


def test_soulmap_demo_surfaces_framework_selector_payload_errors() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap.runtime.experimental.soulmap_demo", "--stdin"],
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
        ".claude/hooks/block-push-to-main.sh",
        ".claude/hooks/post-edit-markdown.sh",
        ".claude/hooks/post-edit-evals.sh",
        ".claude/hooks/post-edit-python.sh",
        ".claude/hooks/post-edit-tests.sh",
        ".claude/hooks/session-start.sh",
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
    result = run_process(["bash", ".claude/hooks/post-edit-evals.sh"], payload, 15)

    assert result.returncode == 0, result.stderr
    assert "Markdown contract issues detected" not in result.stdout
    assert "[hook:post-edit-evals] Markdown contract eval passed." in result.stderr


def test_post_edit_markdown_hook_bootstraps_repo_python_for_relative_paths() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    payload = json.dumps({"tool_input": {"file_path": "AGENTS.md"}})
    result = run_process(["bash", ".claude/hooks/post-edit-markdown.sh"], payload, 15)

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
        result = run_process(["bash", ".claude/hooks/post-edit-tests.sh"], payload, 15)
    finally:
        failing_test.unlink(missing_ok=True)

    assert result.returncode == 0, result.stderr
    assert "Test failures in" in result.stdout
    assert "[hook:post-edit-tests] Tests failed" in result.stderr


def test_soulmap_demo_surfaces_missing_required_fields() -> None:
    result = run_process(
        [sys.executable, "-m", "soulmap.runtime.experimental.soulmap_demo", "--stdin"],
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
            "soulmap.runtime.experimental.soulmap_demo",
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
            "soulmap.runtime.experimental.soulmap_demo",
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
            "soulmap.runtime.experimental.soulmap_demo",
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


def test_scope_classifier_blocks_specialized_skill_instruction_request() -> None:
    data = run_module(
        "scope_classifier",
        {"message": "Write a marketing plan for my new product launch."},
    )
    assert data["tier"] == "BLACKLIST_LAYER1"
    assert data["category"] == "specialized_skill_instruction"
    assert data["matched_keyword"] == "marketing"


def test_scope_classifier_blocks_seo_optimization_request() -> None:
    data = run_module(
        "scope_classifier",
        {"message": "Can you optimize my website for search engines?"},
    )
    assert data["tier"] == "BLACKLIST_LAYER1"
    assert data["category"] == "specialized_skill_instruction"
    assert data["matched_keyword"] == "optimize my website"


@pytest.mark.parametrize(
    ("message", "category", "matched_keyword"),
    [
        ("Can you explain these algorithms to me?", "technical", "algorithms"),
        ("I keep getting stuck debugging this program.", "technical", "debugging"),
        ("Solve these equations for my homework.", "technical", "equations"),
        ("Help me with these essays for class.", "academic", "essays"),
        ("Should I buy some stocks this year?", "professional_advice", "stocks"),
        (
            "Can you write these cover letters for me?",
            "practical_tasks",
            "cover letters",
        ),
        ("I need to book some travel plans.", "practical_tasks", "travel plans"),
        ("I need a translation of this document.", "practical_tasks", "translation"),
        ("Can you help with crosswords tonight?", "entertainment", "crosswords"),
        ("Help me with a puzzle I am stuck on.", "entertainment", "puzzle"),
    ],
    ids=[
        "technical-algorithms",
        "technical-debugging",
        "technical-equations",
        "academic-essays",
        "professional-stocks",
        "practical-cover-letters",
        "practical-travel-plans",
        "practical-translation",
        "entertainment-crosswords",
        "entertainment-puzzle",
    ],
)
def test_scope_classifier_blocks_documented_keyword_variants(
    message: str, category: str, matched_keyword: str
) -> None:
    """Every documented blacklist phrase must actually be blocked.

    Each keyword in this table is a literal example phrase from
    skills/safety/whitelist-blacklist-system.md. Word-boundary matching means a
    documented keyword's plural or inflected form needs its own explicit entry
    in the layer-1 blacklist, or the documented topic silently falls through
    to ambiguous instead of being blocked.
    """
    data = run_module("scope_classifier", {"message": message})
    assert data["tier"] == "BLACKLIST_LAYER1"
    assert data["category"] == category
    assert data["matched_keyword"] == matched_keyword


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
        "soulmap.runtime.detectors.anger_detector",
        "soulmap.runtime.experimental.biometric_ingest",
        "soulmap.runtime.synthesis.conversation_synthesizer",
        "soulmap.runtime.detectors.crisis_detector",
        "soulmap.runtime.detectors.direction_detector",
        "soulmap.runtime.detectors.emotional_intensity_detector",
        "soulmap.runtime.detectors.existential_detector",
        "soulmap.runtime.routing.framework_selector",
        "soulmap.runtime.detectors.grief_detector",
        "soulmap.runtime.detectors.inner_conflict_detector",
        "soulmap.runtime.detectors.insight_detector",
        "soulmap.runtime.memory.memory_ledger",
        "soulmap.runtime.guards.response_contract",
        "soulmap.runtime.guards.response_safety_gate",
        "soulmap.runtime.routing.scope_classifier",
        "soulmap.runtime.detectors.shadow_pattern_detector",
        "soulmap.runtime.detectors.somatic_detector",
        "soulmap.runtime.detectors.spiritual_bypass_detector",
    ]

    for module in modules:
        result = run_process([sys.executable, "-m", module], "[]")
        assert result.returncode == 1, module
        assert "Traceback" not in result.stdout, module
        assert "Traceback" not in result.stderr, module
        assert json.loads(result.stdout) == {"error": "Input must be a JSON object."}, (
            module
        )


# --- The sourced activation helper ---
#
# scripts/activate_venv.sh is the one script here that must NOT set
# `-euo pipefail`. It runs in the caller's shell, so those options would stay
# set after it returns and the developer's next failing command would kill
# their interactive shell. These cover that contract, because the repo's own
# shell rule otherwise says to set them everywhere.
#
# Both gate on _bash_runtime_available() like every other shell test here. A
# bare `shutil.which("bash")` is not enough: on a Windows runner that resolves
# to the WSL stub, which only prints "no installed distributions" and exits 1,
# so the tests ran against something that is not bash at all.

ACTIVATE_SCRIPT = ROOT / "scripts" / "activate_venv.sh"


def test_activate_helper_refuses_to_be_executed_directly() -> None:
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    result = subprocess.run(
        ["bash", str(ACTIVATE_SCRIPT)], capture_output=True, text=True, check=False
    )

    assert result.returncode == 1
    assert "must be sourced" in result.stderr


def test_sourcing_the_activate_helper_does_not_leak_shell_options() -> None:
    """Sourcing must not leave errexit set in the caller's shell.

    With `set -euo pipefail` in the script, the `false` below ended the shell
    and the final marker never printed. That would end an interactive session
    on the developer's next failing command.
    """
    if not _bash_runtime_available():
        pytest.skip("bash runtime is not available on this platform")

    script = (
        f"source {ACTIVATE_SCRIPT}\n"
        "false\n"
        "echo SURVIVED\n"
        'echo "leftover=${_soulmap_root:-none}"\n'
    )
    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )

    assert "SURVIVED" in result.stdout, result.stderr
    assert "leftover=none" in result.stdout
