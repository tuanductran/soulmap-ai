"""Run SoulMap detectors and return one primary framework choice."""

import asyncio
import json
import os
import sys
import time
from typing import cast

from modules.ancestral_detector import detect_ancestral
from modules.anger_detector import detect_anger
from modules.celebration_detector import detect_celebration
from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_memory_fields,
)
from modules.conversation_synthesizer import should_synthesize, synthesize
from modules.creative_drought_detector import detect_creative_drought
from modules.crisis_detector import detect_crisis
from modules.dependency_detector import analyze_dependency
from modules.direction_detector import detect_direction_need
from modules.emotional_intensity_detector import detect_intensity
from modules.empath_detector import detect_empath_overwhelm
from modules.existential_detector import detect_existential
from modules.grief_detector import detect_grief
from modules.inner_conflict_detector import detect_inner_conflict
from modules.insight_detector import detect_insight
from modules.pattern_detector import detect_patterns
from modules.perfectionism_paralysis_detector import detect_perfectionism_paralysis
from modules.response_safety_gate import apply_safety_gate
from modules.shadow_pattern_detector import detect_shadow_patterns
from modules.somatic_detector import detect_somatic
from modules.spiritual_bypass_detector import detect_bypass
from modules.stage_detector import detect_stage
from modules.visibility_fear_detector import detect_visibility_fear


def _analyze_synthesis(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None = None,
) -> dict:
    """Mirror the CLI contract for the conversation synthesizer."""
    trigger = should_synthesize(message, history)
    if not trigger["should"]:
        return {
            "synthesis_triggered": False,
            "reason": trigger["reason"],
            "recommendation": "Synthesis not triggered. Continue standard pipeline.",
        }

    result = synthesize(message, history, memory or {})
    result["synthesis_triggered"] = True
    result["trigger_reason"] = trigger["reason"]
    return result


async def _run_detector_async(
    detector_name: str,
    detector_fn,
    *args,
    debug_events: list[dict] | None = None,
    **kwargs,
) -> dict:
    """Run one detector in-process and capture optional debug metadata."""
    start = time.perf_counter()
    try:
        result = await asyncio.to_thread(detector_fn, *args, **kwargs)
        if not isinstance(result, dict):
            raise TypeError(
                f"{detector_name} returned {type(result).__name__}, expected dict"
            )
        if debug_events is not None:
            debug_events.append(
                {
                    "module": detector_name,
                    "execution": "in_process",
                    "duration_ms": int((time.perf_counter() - start) * 1000),
                }
            )
        return result
    except Exception as error:
        if debug_events is not None:
            debug_events.append(
                {
                    "module": detector_name,
                    "execution": "in_process",
                    "duration_ms": int((time.perf_counter() - start) * 1000),
                    "error": str(error),
                }
            )
        return {}


def _maybe_attach_debug(out: dict, debug_events: list[dict] | None) -> dict:
    if debug_events is None:
        return out
    out["debug"] = debug_events
    return out


def _apply_safety_gate(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object],
    selection: dict[str, object],
    debug_events: list[dict] | None = None,
) -> dict[str, object]:
    result = apply_safety_gate(message, history, memory, selection)
    if debug_events is not None:
        debug_events.append(
            {
                "module": "response_safety_gate",
                "execution": "in_process",
                "status": result.get("status"),
                "reason": result.get("reason"),
            }
        )
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict[str, object], gated_selection))
    out["safety_status"] = result.get("status")
    out["safety_reason"] = result.get("reason")
    out["safety_flags"] = result.get("flags", [])
    return out


async def select_framework_async(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None = None,
) -> dict:
    """Run detector phases and return exactly one framework selection."""
    memory = memory or {}
    debug_enabled = str(os.getenv("SOULMAP_DEBUG", "0")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    debug_events: list[dict] | None = [] if debug_enabled else None

    crisis = await _run_detector_async(
        "crisis_detector",
        detect_crisis,
        message,
        debug_events=debug_events,
    )
    crisis_tier = crisis.get("tier", 0)
    if crisis_tier == 1:
        selection = {
            "primary_framework": "CRISIS",
            "secondary_layer": None,
            "mode": "CRISIS",
            "context": crisis,
            "instruction": (
                "IMMEDIATE CRISIS RESPONSE. Use CRISIS_RESPONSE[lang] from "
                "skills/frameworks/emotional-deescalation.md. No other "
                "framework. No question."
            ),
            "blocked": ["ALL"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    dep_task = _run_detector_async(
        "dependency_detector",
        analyze_dependency,
        history,
        debug_events=debug_events,
    )
    intensity_task = _run_detector_async(
        "emotional_intensity_detector",
        detect_intensity,
        message,
        history,
        debug_events=debug_events,
    )

    dep, intensity = await asyncio.gather(dep_task, intensity_task)
    intensity_level = intensity.get("level", "NORMAL")

    if dep.get("level") == "HIGH_DEPENDENCY":
        selection = {
            "primary_framework": "DEPENDENCY",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": dep,
            "instruction": (
                "Dependency redirect. Use DEP_REDIRECT from "
                "skills/frameworks/emotional-deescalation.md. Warm, direct, "
                "one question pointing toward real-world support."
            ),
            "blocked": ["ALL_FRAMEWORKS"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if intensity_level == "HIGH" or crisis_tier == 2:
        tasks = {
            "somatic": _run_detector_async(
                "somatic_detector",
                detect_somatic,
                message,
                debug_events=debug_events,
            ),
            "anger": _run_detector_async(
                "anger_detector",
                detect_anger,
                message,
                history,
                debug_events=debug_events,
            ),
            "bypass": _run_detector_async(
                "spiritual_bypass_detector",
                detect_bypass,
                message,
                history,
                debug_events=debug_events,
            ),
        }
        results = await asyncio.gather(*tasks.values())
        res = dict(zip(tasks.keys(), results, strict=True))

        somatic_active = res["somatic"].get("somatic_detected", False)
        anger_active = res["anger"].get("anger_detected", False)
        bypass_active = res["bypass"].get("bypass_detected", False)

        selection = {
            "primary_framework": "DE_ESCALATION",
            "secondary_layer": (
                "anger"
                if anger_active
                else (
                    "bypass"
                    if bypass_active
                    else ("somatic" if somatic_active else None)
                )
            ),
            "mode": "SANCTUARY",
            "context": {"intensity": intensity, "crisis": crisis},
            "instruction": (
                "SANCTUARY MODE. Activate emotional_deescalation.md 3-step "
                "protocol: acknowledge → ground → normalize. NO 5-step framework. "
                "NO inquiry question. 2-4 sentences maximum. Wait for user."
            ),
            "blocked": ["ALL_REFLECTIVE_FRAMEWORKS"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if intensity_level == "MODERATE":
        tasks = {
            "insight": _run_detector_async(
                "insight_detector",
                detect_insight,
                message,
                history,
                debug_events=debug_events,
            ),
            "grief": _run_detector_async(
                "grief_detector",
                detect_grief,
                message,
                history,
                debug_events=debug_events,
            ),
            "conflict": _run_detector_async(
                "inner_conflict_detector",
                detect_inner_conflict,
                message,
                history,
                debug_events=debug_events,
            ),
        }
        insight, grief, conflict = await asyncio.gather(*tasks.values())

        secondary = None
        if insight.get("insight_detected"):
            secondary = "meaning_integration"
        elif grief.get("grief_detected"):
            secondary = "grief"
        elif conflict.get("conflict_detected"):
            secondary = "inner_parts"

        selection = {
            "primary_framework": "DE_ESCALATION",
            "secondary_layer": secondary,
            "mode": "MIRROR",
            "context": intensity,
            "instruction": (
                "MODERATE intensity. Slow the conversation. Acknowledge first. "
                "Hold framework lightly. If secondary_layer is set, move into it "
                "gently after grounding. End with a softer question."
            ),
            "blocked": ["direction", "existential", "synthesis"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    tasks = {
        "grief": _run_detector_async(
            "grief_detector",
            detect_grief,
            message,
            history,
            debug_events=debug_events,
        ),
        "conflict": _run_detector_async(
            "inner_conflict_detector",
            detect_inner_conflict,
            message,
            history,
            debug_events=debug_events,
        ),
        "direction": _run_detector_async(
            "direction_detector",
            detect_direction_need,
            message,
            history,
            debug_events=debug_events,
        ),
        "shadow": _run_detector_async(
            "shadow_pattern_detector",
            detect_shadow_patterns,
            message,
            history,
            debug_events=debug_events,
        ),
        "insight": _run_detector_async(
            "insight_detector",
            detect_insight,
            message,
            history,
            debug_events=debug_events,
        ),
        "existential": _run_detector_async(
            "existential_detector",
            detect_existential,
            message,
            history,
            debug_events=debug_events,
        ),
        "stage": _run_detector_async(
            "stage_detector",
            detect_stage,
            history,
            debug_events=debug_events,
        ),
        "somatic": _run_detector_async(
            "somatic_detector",
            detect_somatic,
            message,
            debug_events=debug_events,
        ),
        "anger": _run_detector_async(
            "anger_detector",
            detect_anger,
            message,
            history,
            debug_events=debug_events,
        ),
        "bypass": _run_detector_async(
            "spiritual_bypass_detector",
            detect_bypass,
            message,
            history,
            debug_events=debug_events,
        ),
        "synthesis": _run_detector_async(
            "conversation_synthesizer",
            _analyze_synthesis,
            message,
            history,
            memory,
            debug_events=debug_events,
        ),
        "celebration": _run_detector_async(
            "celebration_detector",
            detect_celebration,
            message,
            history,
            debug_events=debug_events,
        ),
        "ancestral": _run_detector_async(
            "ancestral_detector",
            detect_ancestral,
            message,
            history,
            debug_events=debug_events,
        ),
        "visibility_fear": _run_detector_async(
            "visibility_fear_detector",
            detect_visibility_fear,
            message,
            history,
            debug_events=debug_events,
        ),
        "creative_drought": _run_detector_async(
            "creative_drought_detector",
            detect_creative_drought,
            message,
            history,
            debug_events=debug_events,
        ),
        "empath": _run_detector_async(
            "empath_detector",
            detect_empath_overwhelm,
            message,
            history,
            debug_events=debug_events,
        ),
        "perfectionism": _run_detector_async(
            "perfectionism_paralysis_detector",
            detect_perfectionism_paralysis,
            message,
            history,
            debug_events=debug_events,
        ),
    }

    results = await asyncio.gather(*tasks.values())
    res = dict(zip(tasks.keys(), results, strict=True))

    user_count = sum(
        1 for item in history if isinstance(item, dict) and item.get("role") == "user"
    )
    current_stage = res["stage"].get("stage", 1)
    pattern = {}
    if user_count >= 1:
        # Include current message so single-turn pattern signals are captured
        pattern_history = list(history) + [{"role": "user", "content": message}]
        pattern = await _run_detector_async(
            "pattern_detector",
            detect_patterns,
            pattern_history,
            debug_events=debug_events,
        )

    if res["grief"].get("grief_detected") and res["grief"].get("grief_type") in (
        "acute",
        "anticipatory",
        "ambiguous",
        "complicated",
    ):
        secondary = (
            "meaning_integration" if res["insight"].get("insight_detected") else None
        )
        selection = {
            "primary_framework": "GRIEF",
            "secondary_layer": secondary,
            "mode": "SANCTUARY",
            "context": res["grief"],
            "instruction": (
                "Activate grief_companion.md. Presence first  -  witness the loss "
                "before any reflection. End with one grief-specific question."
            ),
            "blocked": ["direction", "shadow", "existential", "synthesis"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["existential"].get("existential_detected"):
        secondary = (
            "meaning_integration" if res["insight"].get("insight_detected") else None
        )
        selection = {
            "primary_framework": "EXISTENTIAL",
            "secondary_layer": secondary,
            "mode": "MIRROR",
            "context": res["existential"],
            "instruction": (
                "Activate existential_companion.md. Territory: "
                f"{res['existential'].get('territory', 'general')}. Hold space. "
                "Do not resolve. End with one question that goes deeper."
            ),
            "blocked": ["direction", "shadow"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["conflict"].get("conflict_detected") and not res["insight"].get(
        "insight_detected"
    ):
        selection = {
            "primary_framework": "INNER_PARTS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["conflict"],
            "instruction": (
                "Activate inner_parts.md. Name 1-2 parts with hidden intention. "
                "Do not take sides. End with one parts-specific question."
            ),
            "blocked": ["direction", "shadow"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["direction"].get("direction_detected"):
        selection = {
            "primary_framework": "DIRECTION",
            "secondary_layer": (
                "meaning_integration"
                if res["insight"].get("insight_detected")
                else None
            ),
            "mode": "MIRROR",
            "context": res["direction"],
            "instruction": (
                "Activate life_direction.md. Presentation: "
                f"{res['direction'].get('presentation', 'lost')}. Explore values "
                "NOT options. End with direction-specific question."
            ),
            "blocked": ["shadow"],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["creative_drought"].get("creative_drought_detected"):
        selection = {
            "primary_framework": "CREATIVE_DROUGHT",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["creative_drought"],
            "instruction": res["creative_drought"].get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["perfectionism"].get("perfectionism_paralysis_detected"):
        selection = {
            "primary_framework": "PERFECTIONISM_PARALYSIS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["perfectionism"],
            "instruction": res["perfectionism"].get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["shadow"].get("shadow_detected"):
        selection = {
            "primary_framework": "SHADOW",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["shadow"],
            "instruction": (
                "Activate shadow_patterns.md. Frame as possibility ONLY. Return "
                "ownership. End with shadow-specific question."
            ),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["ancestral"].get("ancestral_detected"):
        selection = {
            "primary_framework": "ANCESTRAL_PATTERNS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["ancestral"],
            "instruction": res["ancestral"].get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["visibility_fear"].get("visibility_fear_detected"):
        selection = {
            "primary_framework": "FEAR_OF_VISIBILITY",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["visibility_fear"],
            "instruction": res["visibility_fear"].get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["empath"].get("empath_detected"):
        selection = {
            "primary_framework": "EMPATH_BOUNDARY",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["empath"],
            "instruction": res["empath"].get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["celebration"].get("celebration_detected") and not res["insight"].get(
        "insight_detected"
    ):
        celebration_ctx = res["celebration"]
        selection = {
            "primary_framework": "INTEGRATION_CELEBRATION",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": celebration_ctx,
            "instruction": celebration_ctx.get("recommendation", ""),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["insight"].get("insight_detected"):
        selection = {
            "primary_framework": "MEANING_INTEGRATION",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["insight"],
            "instruction": (
                "Activate meaning_integration.md. Hold the insight first. Do NOT "
                "prescribe change. End with conscious-noticing question."
            ),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if res["synthesis"].get("synthesis_triggered") and res["synthesis"].get(
        "synthesis_ready"
    ):
        selection = {
            "primary_framework": "SYNTHESIS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["synthesis"],
            "instruction": (
                "Activate conversation_synthesis.md. Name 2-3 themes max. Return "
                "ownership. End with synthesis question."
            ),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    if pattern and pattern.get("primary_pattern") and not pattern.get("wait_for_more"):
        selection = {
            "primary_framework": "PATTERN",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": pattern,
            "instruction": (
                "Activate pattern_mapper.md. Pattern: "
                f"{pattern.get('primary_pattern')}. Reflect hidden intention. End "
                "with pattern-specific question."
            ),
            "blocked": [],
        }
        return _maybe_attach_debug(
            _apply_safety_gate(message, history, memory, selection, debug_events),
            debug_events,
        )

    mode = "PEER" if current_stage >= 5 else "MIRROR"
    somatic_active = res["somatic"].get("somatic_detected", False)
    anger_active = res["anger"].get("anger_detected", False)
    bypass_active = res["bypass"].get("bypass_detected", False)

    selection = {
        "primary_framework": "MIRROR",
        "secondary_layer": (
            "anger"
            if anger_active
            else (
                "bypass" if bypass_active else ("somatic" if somatic_active else None)
            )
        ),
        "mode": mode,
        "context": {"stage": current_stage},
        "instruction": (
            "MIRROR mode: 5-step arc. End with one question from deep-inquiry-bank.md."
            if mode == "MIRROR"
            else "PEER mode: dialogue, light structure. End with one question."
        ),
        "blocked": [],
    }
    return _maybe_attach_debug(
        _apply_safety_gate(message, history, memory, selection, debug_events),
        debug_events,
    )


def select_framework(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None = None,
) -> dict:
    return asyncio.run(select_framework_async(message, history, memory))


if __name__ == "__main__":

    async def main() -> None:
        try:
            data = read_stdin_json(strip=True)
            message, history, memory = require_message_history_memory_fields(data)

            result = await select_framework_async(message, history, memory)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        except ValueError as error:
            print_json_error(error)
            sys.exit(1)
        except Exception as error:
            print_json_error(error)
            sys.exit(1)

    asyncio.run(main())
