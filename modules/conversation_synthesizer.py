"""Detect synthesis moments and summarize recurring session themes."""

from __future__ import annotations

from collections import defaultdict
import json
import sys
from typing import TypedDict

from modules.cli_payload import (
    parse_json_object,
    require_dict_field,
    require_list_field,
    require_str_field,
)

Message = dict[str, str]


class ThemeScore(TypedDict):
    score: int
    anchors: list[int]


class RankedTheme(TypedDict):
    theme: str
    score: int
    anchors: list[int]


class ExtractedThemes(TypedDict, total=False):
    emotional: list[RankedTheme]
    values: list[RankedTheme]
    conflicts: list[RankedTheme]
    longitudinal: list[str]
    session_count: int


SYNTHESIS_REQUEST = [
    "is there a pattern here",
    "what's the pattern",
    "do you see a pattern",
    "what keeps coming up",
    "what do you notice",
    "what themes do you see",
    "what does this all add up to",
    "looking back at our conversation",
    "what have i been talking about",
    "why do i keep coming back to",
    "is there a thread",
    "what's the common thread",
    "what does this say about me",
    "what have you noticed about me",
    "can you reflect back",
    "can you summarize what",
    "across everything i've said",
    "throughout our conversation",
]

EMOTIONAL_THEMES = {
    "loneliness": [
        "alone",
        "lonely",
        "isolated",
        "no one understands",
        "no one sees",
        "invisible",
        "disconnected",
        "left out",
        "on my own",
        "by myself",
    ],
    "fear": [
        "afraid",
        "scared",
        "terrified",
        "anxious",
        "worried",
        "panic",
        "what if",
        "might fail",
        "might lose",
        "might leave",
    ],
    "grief": [
        "grief",
        "grieve",
        "grieving",
        "lost",
        "loss",
        "gone",
        "miss",
        "no longer",
        "used to have",
        "used to be",
        "mourning",
    ],
    "not_enough": [
        "not enough",
        "not good enough",
        "never enough",
        "inadequate",
        "fall short",
        "don't measure up",
        "disappointing",
        "failure",
        "failing",
    ],
    "freedom_vs_safety": [
        "trapped",
        "stuck",
        "constrained",
        "can't leave",
        "have to stay",
        "freedom",
        "escape",
        "break free",
        "on my own terms",
    ],
    "anger": [
        "angry",
        "furious",
        "resentment",
        "bitter",
        "frustrated",
        "fed up",
        "sick of",
        "not fair",
        "unfair",
    ],
    "shame": [
        "ashamed",
        "shame",
        "embarrassed",
        "humiliated",
        "exposed",
        "judged",
        "what will they think",
        "don't want them to know",
    ],
}

VALUES_THEMES = {
    "autonomy": [
        "my choice",
        "my own terms",
        "freedom to",
        "decide for myself",
        "don't want to be told",
        "independent",
        "my own path",
    ],
    "honesty": [
        "honest",
        "truth",
        "real",
        "authentic",
        "genuine",
        "pretend",
        "mask",
        "hiding",
        "showing my true",
        "being real",
    ],
    "connection": [
        "belong",
        "belonging",
        "close to",
        "connected",
        "relationship",
        "intimacy",
        "understood",
        "seen",
        "known",
    ],
    "meaning": [
        "meaning",
        "meaningful",
        "purpose",
        "matters",
        "point",
        "worth it",
        "for something",
        "makes sense",
    ],
    "safety": [
        "safe",
        "secure",
        "protected",
        "stable",
        "certain",
        "don't want to lose",
        "afraid to lose",
    ],
    "creativity_depth": [
        "creative",
        "depth",
        "interesting",
        "curious",
        "explore",
        "discover",
        "wonder",
        "bored when",
        "alive when",
    ],
}

CONFLICT_THEMES = {
    "seen_vs_hidden": [
        "want to be seen",
        "afraid to be seen",
        "want to be known",
        "don't want to be exposed",
        "hide",
        "show",
    ],
    "closeness_vs_distance": [
        "want connection",
        "push away",
        "pull back",
        "when they get close",
        "afraid of closeness",
        "want to be close but",
    ],
    "knowing_vs_avoiding": [
        "i know but",
        "i see it but",
        "i understand but still",
        "part of me knows",
        "choose not to look",
    ],
    "change_vs_familiar": [
        "want to change",
        "keep going back",
        "same patterns",
        "comfortable",
        "familiar even though",
        "known even if",
    ],
    "giving_vs_receiving": [
        "give so much",
        "never receive",
        "hard to receive",
        "easier to give",
        "take care of everyone",
        "no one takes care",
    ],
}


def _new_theme_score() -> ThemeScore:
    return {"score": 0, "anchors": []}


def extract_themes(messages: list[Message]) -> ExtractedThemes:
    """
    Scan all user messages and score emotional themes, values, and conflicts.
    Returns themes with scores and example anchors (message indices).
    """
    user_messages = [
        (i, m["content"].lower())
        for i, m in enumerate(messages)
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    emotional_scores: defaultdict[str, ThemeScore] = defaultdict(_new_theme_score)
    values_scores: defaultdict[str, ThemeScore] = defaultdict(_new_theme_score)
    conflict_scores: defaultdict[str, ThemeScore] = defaultdict(_new_theme_score)

    for msg_idx, msg in user_messages:
        for theme, keywords in EMOTIONAL_THEMES.items():
            for kw in keywords:
                if kw in msg:
                    emotional_scores[theme]["score"] += 1
                    if len(emotional_scores[theme]["anchors"]) < 2:
                        emotional_scores[theme]["anchors"].append(msg_idx)
                    break

        for value, keywords in VALUES_THEMES.items():
            for kw in keywords:
                if kw in msg:
                    values_scores[value]["score"] += 1
                    if len(values_scores[value]["anchors"]) < 2:
                        values_scores[value]["anchors"].append(msg_idx)
                    break

        for conflict, keywords in CONFLICT_THEMES.items():
            for kw in keywords:
                if kw in msg:
                    conflict_scores[conflict]["score"] += 1
                    if len(conflict_scores[conflict]["anchors"]) < 2:
                        conflict_scores[conflict]["anchors"].append(msg_idx)
                    break

    recurring_emotional = {k: v for k, v in emotional_scores.items() if v["score"] >= 2}
    recurring_values = {k: v for k, v in values_scores.items() if v["score"] >= 2}
    recurring_conflicts = {k: v for k, v in conflict_scores.items() if v["score"] >= 2}

    top_emotional = sorted(recurring_emotional.items(), key=lambda x: -x[1]["score"])[
        :2
    ]
    top_values = sorted(recurring_values.items(), key=lambda x: -x[1]["score"])[:2]
    top_conflicts = sorted(recurring_conflicts.items(), key=lambda x: -x[1]["score"])[
        :2
    ]

    return {
        "emotional": [
            {"theme": k, "score": v["score"], "anchors": v["anchors"]}
            for k, v in top_emotional
        ],
        "values": [
            {"theme": k, "score": v["score"], "anchors": v["anchors"]}
            for k, v in top_values
        ],
        "conflicts": [
            {"theme": k, "score": v["score"], "anchors": v["anchors"]}
            for k, v in top_conflicts
        ],
    }


def merge_memory_themes(
    extracted: ExtractedThemes, memory: dict[str, object]
) -> ExtractedThemes:
    """
    Enrich extracted themes with longitudinal memory data.
    Only add memory themes that also appear in current session.
    """
    memory_themes = memory.get("recurring_themes", [])
    if not isinstance(memory_themes, list):
        return extracted
    if not memory_themes:
        return extracted

    current_theme_names = set()
    for domain in ["emotional", "values", "conflicts"]:
        for theme_data in extracted.get(domain, []):
            current_theme_names.add(theme_data["theme"])

    longitudinal = []
    for mem_theme in memory_themes[:5]:
        if not isinstance(mem_theme, str):
            continue
        theme_lower = mem_theme.lower().replace("-", "_")
        if any(
            theme_lower in name or name in theme_lower for name in current_theme_names
        ):
            longitudinal.append(mem_theme)

    extracted["longitudinal"] = longitudinal[:3]
    session_count = memory.get("session_count", 1)
    extracted["session_count"] = session_count if isinstance(session_count, int) else 1
    return extracted


def should_synthesize(message: str, history: list[Message]) -> dict[str, str | bool]:
    """
    Determine whether synthesis is appropriate for this message.
    Returns: { should: bool, reason: str }
    """
    msg_lower = message.lower().strip()
    user_count = sum(
        1 for m in history if isinstance(m, dict) and m.get("role") == "user"
    )

    for phrase in SYNTHESIS_REQUEST:
        if phrase in msg_lower:
            return {"should": True, "reason": "explicit_request"}

    if user_count >= 10:
        reflective_indicators = [
            "i don't know",
            "i'm not sure",
            "i wonder",
            "what do you think",
            "i've been thinking",
            "i've been feeling",
            "it's strange",
        ]
        if any(r in msg_lower for r in reflective_indicators):
            return {"should": True, "reason": "natural_pause_long_session"}

    if user_count >= 12:
        return {"should": True, "reason": "long_session_threshold"}

    return {"should": False, "reason": "not_triggered"}


def synthesize(
    message: str, history: list[Message], memory: dict[str, object] | None = None
) -> dict[str, object]:
    """
    Full synthesis analysis. Call this when should_synthesize returns True.

    Returns:
        Dict with: themes, synthesis_ready (bool), synthesis_frame (str),
                   is_longitudinal (bool), recommendation (str)
    """
    user_count = sum(
        1 for m in history if isinstance(m, dict) and m.get("role") == "user"
    )

    if user_count < 6:
        return {
            "synthesis_ready": False,
            "reason": "insufficient_data",
            "themes": {},
            "recommendation": (
                "Not enough conversation history for synthesis. "
                "Continue standard response. Check again after 8+ user messages."
            ),
        }

    themes: ExtractedThemes = extract_themes(history)

    if memory:
        themes = merge_memory_themes(themes, memory)

    emotional_themes = themes.get("emotional", [])
    value_themes = themes.get("values", [])
    conflict_themes = themes.get("conflicts", [])

    total_themes = len(emotional_themes) + len(value_themes) + len(conflict_themes)

    if total_themes < 2:
        return {
            "synthesis_ready": False,
            "reason": "insufficient_recurring_themes",
            "themes": themes,
            "recommendation": (
                "Not enough recurring themes detected for synthesis. "
                "Continue standard response."
            ),
        }

    is_longitudinal = bool(themes.get("longitudinal"))
    session_count = themes.get("session_count", 1)

    if is_longitudinal and session_count >= 3:
        opening = "Over the time we've been talking — not just today — a few things keep returning."
    else:
        opening = "Across what you've shared today, a few themes seem to return."

    all_themes = []
    for t in emotional_themes:
        all_themes.append(("emotional", t["theme"], t["score"]))
    for t in value_themes:
        all_themes.append(("values", t["theme"], t["score"]))
    for t in conflict_themes:
        all_themes.append(("conflicts", t["theme"], t["score"]))

    all_themes.sort(key=lambda x: -x[2])
    top_3 = all_themes[:3]

    theme_descriptions = []
    for domain, theme_name, _score in top_3:
        readable = theme_name.replace("_", " ")
        if domain == "emotional":
            desc = f"An emotional thread of {readable} — it appeared in several different things you shared."
        elif domain == "values":
            desc = f"Something that seems to matter to you — {readable} — keeps appearing, even when the topic changes."
        else:  # conflicts
            desc = f"A recurring tension around {readable} — it surfaced in more than one place."
        theme_descriptions.append(desc)

    synthesis_frame = (
        opening
        + "\n\n"
        + "\n\n".join(theme_descriptions)
        + "\n\n"
        + "I might be missing something, or seeing a connection that isn't there. "
        "What do you notice when you look at all of this together?"
    )

    recommendation = (
        f"Synthesis ready. {len(top_3)} recurring theme(s) identified. "
        f"{'Longitudinal data available. ' if is_longitudinal else ''}"
        "Activate Conversation Pattern Synthesizer from skills/frameworks/conversation_synthesis.md. "
        "Use non-fixed framing: 'Across what you've shared, a few themes seem to return...' "
        "Name 2-3 themes max. Each theme: 1-2 sentences + specific anchor to something user said. "
        "End with ownership return + one reflective question from "
        "skills/meta/deep_inquiry_bank.md — 'Synthesis Questions' section. "
        f"Themes detected: {', '.join(f'{d}:{t}' for d, t, _ in top_3)}."
    )

    return {
        "synthesis_ready": True,
        "themes": {
            "emotional": themes.get("emotional", []),
            "values": themes.get("values", []),
            "conflicts": themes.get("conflicts", []),
            "longitudinal": themes.get("longitudinal", []),
        },
        "top_themes": top_3,
        "is_longitudinal": is_longitudinal,
        "synthesis_frame": synthesis_frame,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")
        memory = require_dict_field(data, "memory")

        if not message and not history:
            print(json.dumps({"error": "No message or history provided."}))
            sys.exit(1)

        trigger = should_synthesize(message, history)

        if not trigger["should"]:
            print(
                json.dumps(
                    {
                        "synthesis_triggered": False,
                        "reason": trigger["reason"],
                        "recommendation": "Synthesis not triggered. Continue standard pipeline.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            sys.exit(0)

        result = synthesize(message, history, memory)
        result["synthesis_triggered"] = True
        result["trigger_reason"] = trigger["reason"]

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
