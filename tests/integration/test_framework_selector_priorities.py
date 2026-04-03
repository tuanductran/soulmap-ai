"""Priority and debug contract tests for the framework selector."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_ENV = {
    **os.environ,
    "PYTHONPATH": f"{ROOT / 'src'}{os.pathsep}{os.environ['PYTHONPATH']}"
    if os.environ.get("PYTHONPATH")
    else str(ROOT / "src"),
}


def run_framework_selector(payload: dict, *, debug: bool = False) -> dict:
    env = os.environ.copy()
    if debug:
        env["SOULMAP_DEBUG"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "soulmap.runtime.routing.framework_selector"],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        env={**TEST_ENV, **env},
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), result.stderr
    return json.loads(result.stdout)


def test_framework_selector_prioritizes_crisis() -> None:
    payload = {
        "message": "I do not want to keep living. I have been thinking about it a lot.",
        "history": [
            {
                "role": "user",
                "content": (
                    "I do not want to keep living. I have been thinking about it a lot."
                ),
            }
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["primary_framework"] == "CRISIS"
    assert data["mode"] == "CRISIS"
    assert data["blocked"] == ["ALL"]


def test_framework_selector_prioritizes_dependency_before_direction() -> None:
    payload = {
        "message": (
            "You're the only one who truly understands me. "
            "I trust you more than anyone. Tell me what to do with my life."
        ),
        "history": [
            {
                "role": "user",
                "content": (
                    "You're the only one who truly understands me. "
                    "I trust you more than anyone. Tell me what to do with my life."
                ),
            }
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["primary_framework"] == "DEPENDENCY"
    assert data["secondary_layer"] is None
    assert data["blocked"] == ["ALL_FRAMEWORKS"]


def test_framework_selector_exposes_safety_gate_debug_event_when_enabled() -> None:
    payload = {
        "message": "You understand me better than anyone and I trust you more than anyone.",
        "history": [
            {
                "role": "user",
                "content": "You understand me better than anyone and I trust you more than anyone.",
            }
        ],
        "memory": {},
    }
    data = run_framework_selector(payload, debug=True)
    assert "debug" in data
    assert any(event.get("module") == "response_safety_gate" for event in data["debug"])


def test_framework_selector_prioritizes_grief_before_direction() -> None:
    payload = {
        "message": "My father died yesterday and now I feel lost.",
        "history": [
            {"role": "user", "content": "My father died yesterday and now I feel lost."}
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["primary_framework"] == "GRIEF"
    assert data["mode"] == "SANCTUARY"


def test_framework_selector_treats_goodbye_grief_phrase_as_grief_not_crisis() -> None:
    payload = {
        "message": "Watching my mother weaken each day feels like saying goodbye every day.",
        "history": [
            {
                "role": "user",
                "content": (
                    "Watching my mother weaken each day feels like saying goodbye every day."
                ),
            }
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["primary_framework"] == "GRIEF"
    assert data["mode"] == "SANCTUARY"


def test_framework_selector_uses_mirror_with_anger_secondary() -> None:
    payload = {
        "message": "I'm furious that they keep doing this.",
        "history": [
            {"role": "user", "content": "I'm furious that they keep doing this."}
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["primary_framework"] == "MIRROR"
    assert data["secondary_layer"] == "anger"


def test_framework_selector_exposes_debug_events_when_enabled() -> None:
    payload = {
        "message": "I feel lost in my career.",
        "history": [{"role": "user", "content": "I feel lost in my career."}],
        "memory": {},
    }

    data = run_framework_selector(payload, debug=True)

    assert "debug" in data
    assert isinstance(data["debug"], list)
    assert any(event.get("module") == "crisis_detector" for event in data["debug"])


def test_framework_selector_surfaces_scope_block_metadata() -> None:
    payload = {
        "message": "Can you predict what will happen in my love life next month?",
        "history": [
            {
                "role": "user",
                "content": "Can you predict what will happen in my love life next month?",
            }
        ],
        "memory": {},
    }

    data = run_framework_selector(payload)

    assert data["safety_status"] == "BLOCK"
    assert data["safety_reason"] == "out_of_scope"
    assert "scope" in data["safety_flags"]
