"""Detect life-direction lostness and values-level misalignment."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

LOSTNESS_SIGNALS = [
    "i feel lost",
    "i'm lost",
    "feel so lost",
    "feeling lost",
    "don't know what i want",
    "don't know what to do with my life",
    "don't know where i'm going",
    "no idea what i want",
    "have no direction",
    "no sense of direction",
    "lost my direction",
    "don't know who i am anymore",
    "lost myself",
    "don't recognize myself",
    "don't know what matters to me",
    "not sure what i'm doing with my life",
    "what am i doing with my life",
    "what's the point",
    "is this all there is",
]

MEANING_SIGNALS = [
    "no purpose",
    "feel purposeless",
    "lost my purpose",
    "no sense of purpose",
    "nothing feels meaningful",
    "nothing matters",
    "what's the meaning",
    "feel empty",
    "feel hollow",
    "going through the motions",
    "just existing",
    "not really living",
    "feel like a robot",
    "life feels flat",
    "life feels pointless",
    "no passion",
    "lost my passion",
    "nothing excites me",
    "nothing interests me",
    "bored with everything",
    "bored with my life",
]

SHOULD_SIGNALS = [
    "should want this but i don't",
    "supposed to want",
    "supposed to be happy",
    "have everything i wanted but",
    "achieved my goals but",
    "reached my goal but",
    "got what i worked for but",
    "should feel satisfied but",
    "should feel happy but",
    "feels like it's not mine",
    "living someone else's life",
    "living someone else's dream",
    "don't know if this is really what i want",
    "is this even what i want",
    "following someone else's script",
    "doing what was expected",
    "never questioned it before",
    "just followed the path",
]

COMPARISON_SIGNALS = [
    "everyone else seems to know",
    "everyone else has it figured out",
    "everyone else knows what they're doing",
    "everyone else has direction",
    "why can't i figure it out",
    "why don't i have it together",
    "behind everyone else",
    "falling behind",
    "not where i should be",
    "compare myself to",
    "compared to others",
]

TRANSITION_SIGNALS = [
    "at a crossroads",
    "don't know which way to go",
    "big decision",
    "life transition",
    "major change",
    "starting over",
    "reinventing myself",
    "chapter ending",
    "new chapter",
    "midlife",
    "quarter life",
    "don't know what's next",
    "what comes next",
    "what now",
    "reassessing everything",
    "questioning everything",
    "reevaluating",
]

MISALIGNMENT_SIGNALS = [
    "feels off",
    "something feels wrong",
    "something feels missing",
    "not aligned",
    "out of alignment",
    "feels inauthentic",
    "not being true to myself",
    "compromising myself",
    "selling out",
    "not living my values",
    "acting against my values",
    "not who i want to be",
    "not the person i wanted to become",
    "drifted from what matters",
    "lost track of what matters",
]


def _suggest_lens(msg: str) -> str:
    """Suggest which of the four inquiry lenses is most relevant."""
    if any(s in msg for s in MEANING_SIGNALS[:6]):
        return (
            "Lens 1 (meaning) — ask about what has felt meaningful, even in small ways"
        )
    if any(
        s in msg
        for s in ["drain", "exhaust", "energiz", "alive", "resist", "putting off"]
    ):
        return "Lens 2 (energy) — ask about what energizes vs. drains"
    if any(s in msg for s in SHOULD_SIGNALS[:4] + COMPARISON_SIGNALS[:4]):
        return "Lens 3 (respect) — ask what kind of life they would genuinely admire"
    if any(s in msg for s in MISALIGNMENT_SIGNALS[:6]):
        return "Lens 4 (misalignment) — help locate the gap between values and current life"
    return "Lens 1 (meaning) — start with what feels meaningful as the opening lens"


def detect_direction_need(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect whether the user needs the Life Direction Clarifier framework.

    Returns:
        Dict with: direction_detected (bool), type (str), score (int),
                   signals (list), suggested_lens (str), presentation (str),
                   recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    direction_types = []

    signal_groups = [
        ("lostness", LOSTNESS_SIGNALS, 3),
        ("meaning_void", MEANING_SIGNALS, 3),
        ("should_vs_want", SHOULD_SIGNALS, 2),
        ("comparison", COMPARISON_SIGNALS, 2),
        ("transition", TRANSITION_SIGNALS, 2),
        ("misalignment", MISALIGNMENT_SIGNALS, 2),
    ]

    for type_name, signals, weight in signal_groups:
        for phrase in signals:
            if phrase in msg:
                score += weight
                signals_found.append(f"{type_name}: '{phrase}'")
                if type_name not in direction_types:
                    direction_types.append(type_name)
                break  # one match per group per pass is enough

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-4:]
        history_signals = (
            LOSTNESS_SIGNALS[:8] + MEANING_SIGNALS[:6] + TRANSITION_SIGNALS[:6]
        )
        for past_msg in recent_user:
            if any(phrase in past_msg for phrase in history_signals):
                score += 1
                if "sustained" not in direction_types:
                    direction_types.append("sustained")
                break

    if score < 2:
        return {
            "direction_detected": False,
            "type": None,
            "score": score,
            "signals": signals_found,
            "suggested_lens": None,
            "presentation": None,
            "recommendation": "No direction signals detected. Continue standard pipeline.",
        }

    presentation_map = {
        "lostness": "lost",
        "meaning_void": "meaning_void",
        "should_vs_want": "should_vs_want",
        "comparison": "comparison",
        "transition": "transition",
        "misalignment": "misalignment",
    }
    primary_type = direction_types[0] if direction_types else "lostness"
    presentation = presentation_map.get(primary_type, "lost")

    suggested_lens = _suggest_lens(msg)

    recommendation = (
        f"Life direction uncertainty detected (type: {primary_type}). "
        "Activate Life Direction Clarifier from skills/frameworks/life-direction.md. "
        "Explore VALUES, not options. Do NOT suggest a direction or validate a leaning. "
        f"Start with: {suggested_lens}. "
        "Use one lens at a time. Follow the user's energy. "
        "End with one reflective question about what kind of life feels honest to them. "
        "Retrieve question from skills/meta/deep-inquiry-bank.md — 'Direction-Specific Questions' section."
    )

    return {
        "direction_detected": True,
        "type": primary_type,
        "score": score,
        "signals": signals_found,
        "suggested_lens": suggested_lens,
        "presentation": presentation,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")

        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_direction_need(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
