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
from soulmap.runtime.routing.stage_detector import detect_stage
from soulmap.runtime.synthesis.conversation_synthesizer import (
    should_synthesize,
    synthesize,
)

# The grief types that claim the primary route, per the priority table in
# skills/meta/orchestration.md. Shared by the moderate-intensity branch and the
# normal-intensity branch so the two cannot drift apart.
_GRIEF_TYPES = ("acute", "anticipatory", "ambiguous", "complicated")

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
) -> dict[str, object]:
    """Close out a selection: apply the safety gate, then attach debug data.

    Every branch below ends by calling this with its own ``selection`` dict,
    so the safety gate and the debug-event contract stay identical across all
    of them by construction rather than by each branch repeating the call.
    """
    return _maybe_attach_debug(
        _apply_safety_gate(message, history, memory, selection, debug_events),
        debug_events,
    )


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

        # Grief outranks moderate-intensity de-escalation. orchestration.md
        # reserves "force De-escalation as primary regardless of topic" for HIGH
        # intensity; MODERATE says "apply slow-down mode, hold framework
        # lightly", and its priority table lists Grief above
        # De-escalation (MODERATE) under a first-match-wins rule.
        #
        # Demoting grief to a secondary layer here meant that adding an
        # expression of distress to a loss took grief-companion.md away: "my dog
        # died this morning" reached GRIEF in sanctuary mode, while "my dog died
        # this morning and I cannot stop crying" fell to a generic slow-down
        # that ends with a question. The person crying got the longer, more
        # question-ended response.
        if grief.get("grief_detected") and grief.get("grief_type") in _GRIEF_TYPES:
            selection = {
                "primary_framework": "GRIEF",
                "secondary_layer": (
                    "meaning_integration" if insight.get("insight_detected") else None
                ),
                "mode": "SANCTUARY",
                "context": {"grief": grief, "intensity": intensity},
                "instruction": (
                    "Activate grief-companion.md at moderate intensity. Ground "
                    "first, then witness the loss before any reflection. Keep it "
                    "short. End with one grief-specific question."
                ),
                "blocked": ["direction", "shadow", "existential", "synthesis"],
            }
            return _finish(message, history, memory, selection, debug_events)

        secondary = None
        if insight.get("insight_detected"):
            secondary = "meaning_integration"
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
    _raw_stage = res["stage"].get("stage", 1)
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

    if (
        res["grief"].get("grief_detected")
        and res["grief"].get("grief_type") in _GRIEF_TYPES
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
                "Activate grief-companion.md. Presence first, witness the loss "
                "before any reflection. End with one grief-specific question."
            ),
            "blocked": ["direction", "shadow", "existential", "synthesis"],
        }
        return _finish(message, history, memory, selection, debug_events)

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
                "Activate existential-companion.md. Territory: "
                f"{res['existential'].get('territory', 'general')}. Hold space. "
                "Do not resolve. End with one question that goes deeper."
            ),
            "blocked": ["direction", "shadow"],
        }
        return _finish(message, history, memory, selection, debug_events)

    if res["conflict"].get("conflict_detected") and not res["insight"].get(
        "insight_detected"
    ):
        selection = {
            "primary_framework": "INNER_PARTS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["conflict"],
            "instruction": (
                "Activate inner-parts.md. Name 1-2 parts with hidden intention. "
                "Do not take sides. End with one parts-specific question."
            ),
            "blocked": ["direction", "shadow"],
        }
        return _finish(message, history, memory, selection, debug_events)

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
                "Activate life-direction.md. Presentation: "
                f"{res['direction'].get('presentation', 'lost')}. Explore values "
                "NOT options. End with direction-specific question."
            ),
            "blocked": ["shadow"],
        }
        return _finish(message, history, memory, selection, debug_events)

    if res["creative_drought"].get("creative_drought_detected"):
        selection = _simple_selection("CREATIVE_DROUGHT", res["creative_drought"])
        return _finish(message, history, memory, selection, debug_events)

    if res["perfectionism"].get("perfectionism_paralysis_detected"):
        selection = _simple_selection("PERFECTIONISM_PARALYSIS", res["perfectionism"])
        return _finish(message, history, memory, selection, debug_events)

    if res["shadow"].get("shadow_detected"):
        selection = {
            "primary_framework": "SHADOW",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["shadow"],
            "instruction": (
                "Activate shadow-patterns.md. Frame as possibility ONLY. Return "
                "ownership. End with shadow-specific question."
            ),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

    if res["ancestral"].get("ancestral_detected"):
        selection = _simple_selection("ANCESTRAL_PATTERNS", res["ancestral"])
        return _finish(message, history, memory, selection, debug_events)

    if res["visibility_fear"].get("visibility_fear_detected"):
        selection = _simple_selection("FEAR_OF_VISIBILITY", res["visibility_fear"])
        return _finish(message, history, memory, selection, debug_events)

    if res["empath"].get("empath_detected"):
        selection = _simple_selection("EMPATH_BOUNDARY", res["empath"])
        return _finish(message, history, memory, selection, debug_events)

    if res["dark_night"].get("dark_night_detected"):
        selection = _simple_selection("DARK_NIGHT_OF_SOUL", res["dark_night"])
        return _finish(message, history, memory, selection, debug_events)

    if res["soul_nourishment"].get("soul_nourishment_detected"):
        selection = _simple_selection("SOUL_NOURISHMENT", res["soul_nourishment"])
        return _finish(message, history, memory, selection, debug_events)

    if res["divine_guidance"].get("divine_guidance_detected"):
        selection = _simple_selection("DIVINE_GUIDANCE", res["divine_guidance"])
        return _finish(message, history, memory, selection, debug_events)

    if res["sacred_polarity"].get("sacred_polarity_detected"):
        selection = _simple_selection("SACRED_POLARITY", res["sacred_polarity"])
        return _finish(message, history, memory, selection, debug_events)

    if res["spiritual_purpose"].get("spiritual_purpose_detected"):
        selection = _simple_selection("SPIRITUAL_PURPOSE", res["spiritual_purpose"])
        return _finish(message, history, memory, selection, debug_events)

    if res["soulmate_longing"].get("soulmate_longing_detected"):
        selection = _simple_selection("SOULMATE_LONGING", res["soulmate_longing"])
        return _finish(message, history, memory, selection, debug_events)

    if res["partnership_patterns"].get("partnership_pattern_detected"):
        selection = _simple_selection(
            "PARTNERSHIP_PATTERNS", res["partnership_patterns"]
        )
        return _finish(message, history, memory, selection, debug_events)

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
        return _finish(message, history, memory, selection, debug_events)

    if res["insight"].get("insight_detected"):
        selection = {
            "primary_framework": "MEANING_INTEGRATION",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["insight"],
            "instruction": (
                "Activate meaning-integration.md. Hold the insight first. Do NOT "
                "prescribe change. End with conscious-noticing question."
            ),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

    if res["synthesis"].get("synthesis_triggered") and res["synthesis"].get(
        "synthesis_ready"
    ):
        selection = {
            "primary_framework": "SYNTHESIS",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": res["synthesis"],
            "instruction": (
                "Activate conversation-synthesis.md. Name 2-3 themes max. Return "
                "ownership. End with synthesis question."
            ),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

    if pattern and pattern.get("primary_pattern") and not pattern.get("wait_for_more"):
        selection = {
            "primary_framework": "PATTERN",
            "secondary_layer": None,
            "mode": "MIRROR",
            "context": pattern,
            "instruction": (
                "Activate pattern-mapper.md. Pattern: "
                f"{pattern.get('primary_pattern')}. Reflect hidden intention. End "
                "with pattern-specific question."
            ),
            "blocked": [],
        }
        return _finish(message, history, memory, selection, debug_events)

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
