"""Run SoulMap detectors and return one primary framework choice."""

import asyncio
import json
import logging
import os
import sys
import time
from collections.abc import Callable
from typing import cast

from soulmap.runtime.detectors.ancestral_detector import detect_ancestral
from soulmap.runtime.detectors.anger_detector import detect_anger
from soulmap.runtime.detectors.celebration_detector import detect_celebration
from soulmap.runtime.detectors.creative_drought_detector import detect_creative_drought
from soulmap.runtime.detectors.crisis_detector import detect_crisis
from soulmap.runtime.detectors.dark_night_detector import detect_dark_night
from soulmap.runtime.detectors.dependency_detector import analyze_dependency
from soulmap.runtime.detectors.direction_detector import detect_direction_need
from soulmap.runtime.detectors.divine_guidance_detector import detect_divine_guidance
from soulmap.runtime.detectors.emotional_intensity_detector import detect_intensity
from soulmap.runtime.detectors.empath_detector import detect_empath_overwhelm
from soulmap.runtime.detectors.existential_detector import detect_existential
from soulmap.runtime.detectors.grief_detector import detect_grief
from soulmap.runtime.detectors.inner_conflict_detector import detect_inner_conflict
from soulmap.runtime.detectors.insight_detector import detect_insight
from soulmap.runtime.detectors.partnership_patterns_detector import (
    detect_partnership_patterns,
)
from soulmap.runtime.detectors.pattern_detector import detect_patterns
from soulmap.runtime.detectors.perfectionism_paralysis_detector import (
    detect_perfectionism_paralysis,
)
from soulmap.runtime.detectors.sacred_polarity_detector import detect_sacred_polarity
from soulmap.runtime.detectors.shadow_pattern_detector import detect_shadow_patterns
from soulmap.runtime.detectors.somatic_detector import detect_somatic
from soulmap.runtime.detectors.soul_nourishment_detector import detect_soul_nourishment
from soulmap.runtime.detectors.soulmate_longing_detector import (
    detect_soulmate_longing,
)
from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass
from soulmap.runtime.detectors.spiritual_purpose_detector import (
    detect_spiritual_purpose,
)
from soulmap.runtime.detectors.visibility_fear_detector import detect_visibility_fear
from soulmap.runtime.guards.response_safety_gate import apply_safety_gate
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_memory_fields,
)
from soulmap.runtime.knowledge.framework_template_source import resolve_template
from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules
from soulmap.runtime.routing.scope_classifier import classify_message
from soulmap.runtime.routing.stage_detector import detect_stage
from soulmap.runtime.synthesis.conversation_synthesizer import (
    should_synthesize,
    synthesize,
)

_LOGGER = logging.getLogger(__name__)


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
    detector_fn: Callable[..., dict[str, object]],
    *args: object,
    debug_events: list[dict[str, object]] | None = None,
    **kwargs: object,
) -> dict[str, object]:
    """Run one detector off the event loop and capture debug metadata.

    Args:
        detector_name: Detector name, used in debug events and error messages.
        detector_fn: The detector callable. Detectors are synchronous, so this
            runs in a worker thread.
        *args: Positional arguments forwarded to the detector.
        debug_events: List to append this run's timing and outcome to, or None
            to skip recording.
        **kwargs: Keyword arguments forwarded to the detector.

    Returns:
        The detector's result dict.

    Raises:
        TypeError: If the detector returns anything other than a dict, which
            would otherwise fail later as a confusing routing error.
    """
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
        # A broken detector must not fail the whole request (one bad
        # framework should not cost the user a response), so this returns an
        # empty result rather than re-raising. That degrades silently unless
        # logged here: debug_events only exists when SOULMAP_DEBUG is set, so
        # without this call a production detector failure leaves no trace.
        _LOGGER.warning("%s raised during routing: %s", detector_name, error)
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


def _finish(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object],
    selection: dict[str, object],
    debug_events: list[dict] | None,
    *,
    template_required: bool | None = None,
) -> dict[str, object]:
    """Apply safety, then attach the knowledge-authored template contract."""
    result = _apply_safety_gate(message, history, memory, selection, debug_events)
    if template_required is None:
        template_required = load_orchestration_rules().template_routing_required
    if template_required and result.get("safety_status") != "BLOCK":
        framework = result.get("primary_framework")
        mode = result.get("mode")
        if isinstance(framework, str) and isinstance(mode, str):
            template_context = result.get("context")
            if not isinstance(template_context, dict):
                template_context = {}
            result["template"] = resolve_template(
                framework,
                mode,
                template_context,
            )
    return _maybe_attach_debug(result, debug_events)


def _simple_selection(
    framework: str, detector_result: dict[str, object]
) -> dict[str, object]:
    """Build the selection dict shared by single-signal Mirror frameworks.

    Several frameworks (creative drought, perfectionism paralysis, shadow,
    ancestral patterns, and others below) need nothing beyond Mirror mode, no
    secondary layer, and the detector's own recommendation as the
    instruction. This is that shared shape, so a new framework of this kind
    only needs its detector, not another copy of the same five-key dict.
    """
    return {
        "primary_framework": framework,
        "secondary_layer": None,
        "mode": "MIRROR",
        "context": detector_result,
        "instruction": detector_result.get("recommendation", ""),
        "blocked": [],
    }


async def select_framework_async(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None = None,
) -> dict:
    """Run detector phases and return exactly one framework selection."""
    memory = memory or {}
    orchestration_rules = load_orchestration_rules()
    debug_enabled = str(os.getenv("SOULMAP_DEBUG", "0")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    debug_events: list[dict] | None = [] if debug_enabled else None

    # This is the routing short-circuit checkpoint. response_safety_gate.py
    # deliberately re-derives crisis from the raw message before delivery;
    # see ADR 0001 for the defense-in-depth rationale.
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
        return _finish(message, history, memory, selection, debug_events)

    dep = await _run_detector_async(
        "dependency_detector",
        analyze_dependency,
        history,
        debug_events=debug_events,
    )

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
        return _finish(message, history, memory, selection, debug_events)

    if orchestration_rules.phase_1_safety_before_framework_selection:
        scope = classify_message(message)
        if str(scope.get("tier", "")).startswith("BLACKLIST"):
            selection = {
                "primary_framework": "MIRROR",
                "secondary_layer": None,
                "mode": "MIRROR",
                "routing_action": "SAFETY_REDIRECT",
                "context": {"scope": scope},
                "instruction": scope.get("explanation", ""),
                "blocked": ["ALL_FRAMEWORKS"],
            }
            result = _apply_safety_gate(
                message, history, memory, selection, debug_events
            )
            result["scope"] = scope
            return _maybe_attach_debug(result, debug_events)

    breakthrough = await _run_detector_async(
        "insight_detector",
        detect_insight,
        message,
        history,
        debug_events=debug_events,
    )
    if (
        breakthrough.get("insight_detected")
        and breakthrough.get("strength")
        == orchestration_rules.breakthrough_min_strength
    ):
        selection = {
            "primary_framework": "MEANING_INTEGRATION",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": breakthrough,
            "instruction": breakthrough.get("recommendation", ""),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

    intensity_task = _run_detector_async(
        "emotional_intensity_detector",
        detect_intensity,
        message,
        history,
        debug_events=debug_events,
    )
    stage_task = _run_detector_async(
        "stage_detector",
        detect_stage,
        [*history, {"role": "user", "content": message}],
        memory,
        debug_events=debug_events,
    )
    intensity, early_stage = await asyncio.gather(intensity_task, stage_task)
    intensity_level = intensity.get("level", "NORMAL")

    user_count = sum(
        1 for item in history if isinstance(item, dict) and item.get("role") == "user"
    )
    early_stage_value = early_stage.get("stage", 1)
    if (
        early_stage_value == 1
        and user_count + 1 <= orchestration_rules.stage_1_max_user_messages
    ):
        selection = {
            "primary_framework": "MIRROR",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": {"stage": 1, "stage_override": True},
            "instruction": (
                "Stage 1 first-contact override. Use minimal-depth presence and "
                "reflection; do not activate a framework."
            ),
            "blocked": ["ALL_FRAMEWORKS"],
        }
        return _finish(message, history, memory, selection, debug_events)

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
                "SANCTUARY MODE. Activate emotional-deescalation.md 3-step "
                "protocol: acknowledge → ground → normalize. NO 5-step framework. "
                "NO inquiry question. 2-4 sentences maximum. Wait for user."
            ),
            "blocked": ["ALL_REFLECTIVE_FRAMEWORKS"],
        }
        return _finish(message, history, memory, selection, debug_events)

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

        if (
            insight.get("insight_detected")
            and insight.get("strength") == orchestration_rules.breakthrough_min_strength
        ):
            selection = {
                "primary_framework": "MEANING_INTEGRATION",
                "secondary_layer": None,
                "mode": "MIRROR",
                "context": insight,
                "instruction": insight.get("recommendation", ""),
                "blocked": [],
            }
            return _finish(message, history, memory, selection, debug_events)

        # Primary-priority rules are authoritative even at MODERATE intensity.
        # If none matches, use the knowledge-authored intensity fallback.
        secondary = (
            "meaning_integration"
            if insight.get("insight_detected")
            else ("inner_parts" if conflict.get("conflict_detected") else None)
        )

        fallback = next(
            (
                rule
                for rule in orchestration_rules.intensity_fallback
                if rule.level == "MODERATE"
            ),
            None,
        )
        if fallback is None:
            raise ValueError(
                "MODERATE intensity fallback is missing from orchestration contract."
            )

        if secondary not in fallback.allowed_secondary:
            secondary = None

        selection = {
            "primary_framework": fallback.framework,
            "secondary_layer": secondary,
            "mode": fallback.mode,
            "context": intensity,
            "instruction": (
                "Hold the framework lightly and slow the conversation before "
                "deeper reflection."
            ),
            "blocked": ["direction", "existential", "synthesis"],
        }
        return _finish(message, history, memory, selection, debug_events)

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
        "dark_night": _run_detector_async(
            "dark_night_detector",
            detect_dark_night,
            message,
            history,
            debug_events=debug_events,
        ),
        "soul_nourishment": _run_detector_async(
            "soul_nourishment_detector",
            detect_soul_nourishment,
            message,
            history,
            debug_events=debug_events,
        ),
        "divine_guidance": _run_detector_async(
            "divine_guidance_detector",
            detect_divine_guidance,
            message,
            history,
            debug_events=debug_events,
        ),
        "sacred_polarity": _run_detector_async(
            "sacred_polarity_detector",
            detect_sacred_polarity,
            message,
            history,
            debug_events=debug_events,
        ),
        "spiritual_purpose": _run_detector_async(
            "spiritual_purpose_detector",
            detect_spiritual_purpose,
            message,
            history,
            debug_events=debug_events,
        ),
        "soulmate_longing": _run_detector_async(
            "soulmate_longing_detector",
            detect_soulmate_longing,
            message,
            history,
            debug_events=debug_events,
        ),
        "partnership_patterns": _run_detector_async(
            "partnership_patterns_detector",
            detect_partnership_patterns,
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
    _raw_stage = early_stage.get("stage", 1)
    # Detector results are dicts of object, so narrow the stage here rather
    # than at each comparison. A non-integer stage falls back to 1, the most
    # conservative journey stage, instead of raising mid-routing.
    current_stage = _raw_stage if isinstance(_raw_stage, int) else 1
    pattern = {}
    if user_count >= 1:
        # Include current message so single-turn pattern signals are captured
        pattern_history = [*history, {"role": "user", "content": message}]
        pattern = await _run_detector_async(
            "pattern_detector",
            detect_patterns,
            pattern_history,
            debug_events=debug_events,
        )

    res["pattern"] = pattern
    if (
        res["insight"].get("insight_detected")
        and res["insight"].get("strength")
        == orchestration_rules.breakthrough_min_strength
    ):
        selection = {
            "primary_framework": "MEANING_INTEGRATION",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["insight"],
            "instruction": res["insight"].get("recommendation", ""),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

    for rule in orchestration_rules.primary_priority:
        result = res.get(rule.result, {})
        if not isinstance(result, dict):
            continue

        detected = result.get(rule.detected)
        if not detected:
            continue
        if rule.requires_no_insight and res["insight"].get("insight_detected"):
            continue
        if rule.requires and not result.get(rule.requires):
            continue
        if rule.requires_not and result.get(rule.requires_not):
            continue

        secondary = (
            "meaning_integration"
            if rule.insight_secondary and res["insight"].get("insight_detected")
            else None
        )
        selection = {
            "primary_framework": rule.framework,
            "secondary_layer": secondary,
            "mode": rule.mode,
            "context": result,
            "instruction": result.get("recommendation", ""),
            "blocked": list(rule.blocked),
        }
        return _finish(message, history, memory, selection, debug_events)

    mode = "PEER" if current_stage >= orchestration_rules.peer_min_stage else "MIRROR"
    secondary_layer = None
    for secondary_rule in orchestration_rules.secondary_priority:
        secondary_result = res.get(secondary_rule.result, {})
        if isinstance(secondary_result, dict) and secondary_result.get(
            secondary_rule.detected
        ):
            secondary_layer = secondary_rule.name
            break

    selection = {
        "primary_framework": "MIRROR",
        "secondary_layer": secondary_layer,
        "mode": mode,
        "context": {"stage": current_stage},
        "instruction": (
            "MIRROR mode: 5-step arc. End with one question from deep-inquiry-bank.md."
            if mode == "MIRROR"
            else "PEER mode: dialogue, light structure. End with one question."
        ),
        "blocked": [],
    }
    return _finish(message, history, memory, selection, debug_events)


def select_framework(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None = None,
) -> dict[str, object]:
    """Select the framework for a message from synchronous code.

    A blocking wrapper over :func:`select_framework_async`. Call the async
    form directly from an existing event loop, since ``asyncio.run`` cannot
    nest.

    Args:
        message: The user's current message.
        history: Prior turns, each a dict with ``role`` and ``content``.
        memory: Prior-session context, or None when there is none.

    Returns:
        The selector result, including exactly one ``primary_framework``, the
        ``mode``, and the safety gate's verdict.
    """
    return asyncio.run(select_framework_async(message, history, memory))


if __name__ == "__main__":

    async def main() -> None:
        """Route a JSON payload from standard input and print the result."""
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
