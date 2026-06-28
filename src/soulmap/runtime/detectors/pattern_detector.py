"""Detect recurring self-described patterns across conversation history."""

from __future__ import annotations

import json
import sys
from typing import cast

from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json_value

PATTERN_SIGNALS = {
    "abandonment_loop": {
        "name": "Abandonment Loop",
        "description": "Anticipates being left. Creates distance before closeness can deepen. Ends relationships preemptively.",
        "keywords": [
            "i always leave",
            "leave before",
            "they always leave",
            "knew they would go",
            "people always leave",
            "push people away",
            "end it before",
            "before they can",
            "i knew it would end",
            "saw it coming",
            "they'll leave eventually",
            "doesn't matter they'll go",
            "waiting for them to leave",
        ],
        "cycle_phrases": [
            "always ends the same",
            "same thing happens",
            "every relationship",
        ],
        "soulmap_role": "Reflect with care. This pattern often carries grief beneath it.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear when closeness starts to feel dangerous  -  where getting close also means preparing to lose.",
        },
    },
    "approval_seeking": {
        "name": "Approval Seeking",
        "description": "Decisions and self-worth driven by others' reactions. Constant monitoring of how one is perceived.",
        "keywords": [
            "what do they think",
            "what will they think",
            "i don't know what they think",
            "if they're upset with me",
            "hate when i can't tell",
            "did i do something wrong",
            "they seemed off",
            "are they mad at me",
            "want everyone to be okay",
            "changed my mind because",
            "worried they'd think",
            "didn't want to seem",
            "need them to understand",
            "hope they don't think",
        ],
        "cycle_phrases": [
            "always worry about",
            "constantly thinking about what",
            "always checking",
        ],
        "soulmap_role": "Name gently. Many people have never had their own reactions treated as primary.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear when other people's reactions become the main measure of whether something was okay.",
        },
    },
    "emotional_avoidance": {
        "name": "Emotional Avoidance",
        "description": "Feelings are analyzed rather than experienced. Emotional content is intellectualized, deflected, or 'processed' quickly.",
        "keywords": [
            "i'm fine",
            "i'm okay",
            "not a big deal",
            "i've dealt with it",
            "i've processed it",
            "i know logically",
            "rationally speaking",
            "don't really feel",
            "don't feel sad just",
            "think about it a lot",
            "it is what it is",
            "moved on",
            "over it now",
            "not emotional about it",
            "shouldn't feel this way",
            "no point feeling",
        ],
        "cycle_phrases": [
            "always analyze",
            "tend to overthink",
            "live in my head",
        ],
        "soulmap_role": "Move slowly. Do not name this pattern early. Let the feeling become visible before reflecting.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear when feelings become safer to think about than to feel  -  where the mind becomes a kind of refuge from what the body already knows.",
        },
    },
    "self_sabotage": {
        "name": "Self-Sabotage",
        "description": "Undoes progress right before a threshold. Pulls back when things are going well. Disrupts closeness, success, or positive momentum.",
        "keywords": [
            "right when it was going well",
            "don't know why i did that",
            "ruined it again",
            "messed it up",
            "always do this",
            "keep getting in my own way",
            "self-destructive",
            "shot myself in the foot",
            "when things are good i",
            "right before something good",
            "pulled away when",
            "pushed them away when",
            "why do i always do this",
        ],
        "cycle_phrases": [
            "every time things get good",
            "right before",
            "always happens when",
        ],
        "soulmap_role": "Name with curiosity, not judgment. The pattern usually protects something real.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear right at the edge of something good  -  where part of you moves toward it and another part finds a way to pull back.",
        },
    },
    "over_responsibility": {
        "name": "Over-Responsibility",
        "description": "Takes on others' emotions as their problem to solve. Feels guilty when others are unhappy. Self-worth tied to being needed.",
        "keywords": [
            "feel responsible for",
            "my fault they felt",
            "i should have done more",
            "can't let them down",
            "feel guilty when they're upset",
            "my job to fix",
            "feel bad when they're sad",
            "need to make it okay",
            "can't say no",
            "exhausted from helping",
            "everyone comes to me",
            "i just want them to be okay",
            "if only i had",
            "could have prevented",
        ],
        "cycle_phrases": [
            "always end up taking care of",
            "somehow become responsible",
        ],
        "soulmap_role": "Reflect the exhaustion first, then gently name the pattern.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear when other people's pain becomes something that belongs to you to fix  -  where not fixing it means you've somehow failed.",
        },
    },
    "fear_of_rejection": {
        "name": "Fear of Rejection",
        "description": "Avoids initiating, asking, or expressing needs. Prefers ambiguity over asking and risking a no.",
        "keywords": [
            "didn't want to bother",
            "didn't want to seem needy",
            "didn't ask because",
            "what if they say no",
            "rather not know",
            "too scared to ask",
            "never initiated",
            "wait for them to",
            "don't want to impose",
            "feel like a burden",
            "can't handle rejection",
            "what if they don't want to",
            "keep things to myself",
            "never said anything because",
        ],
        "cycle_phrases": [
            "never ask for what i need",
            "always wait",
            "keep it to myself",
        ],
        "soulmap_role": "Name with gentleness. This pattern often carries a deep fear that needs are a burden.",
        "reflection_language": {
            "en": "It sounds like a pattern that may appear when asking for something  -  connection, help, a yes  -  feels like it carries a risk that isn't worth taking.",
        },
    },
}


def detect_patterns(conversation_messages: list) -> dict:
    """
    Analyze conversation history to detect psychological/behavioral patterns.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.

    Returns:
        Dict with: patterns_detected (list), primary_pattern (str|None),
                   combination (bool), recommendation (str), wait_for_more (bool)
    """
    user_messages = [
        m["content"].lower()
        for m in conversation_messages
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    if len(user_messages) < 2:
        return {
            "patterns_detected": [],
            "primary_pattern": None,
            "combination": False,
            "wait_for_more": True,
            "recommendation": "Only one user message  -  listen and be present. Do not name patterns yet.",
        }

    scores = dict.fromkeys(PATTERN_SIGNALS, 0)
    signals_found = {pattern: [] for pattern in PATTERN_SIGNALS}

    full_text = " ".join(user_messages)

    for pattern_id, data in PATTERN_SIGNALS.items():
        for kw in data["keywords"]:
            if kw in full_text:
                scores[pattern_id] += 2
                if kw not in signals_found[pattern_id]:
                    signals_found[pattern_id].append(kw)

        for phrase in data["cycle_phrases"]:
            if phrase in full_text:
                scores[pattern_id] += 3
                if phrase not in signals_found[pattern_id]:
                    signals_found[pattern_id].append(f"[cycle] {phrase}")

    detected = [
        {
            "pattern": pid,
            "name": PATTERN_SIGNALS[pid]["name"],
            "score": scores[pid],
            "signals": signals_found[pid],
            "reflection_en": PATTERN_SIGNALS[pid]["reflection_language"]["en"],
            "soulmap_role": PATTERN_SIGNALS[pid]["soulmap_role"],
        }
        for pid in scores
        if scores[pid] >= 2
    ]

    detected.sort(key=lambda x: -x["score"])

    primary = detected[0]["pattern"] if detected else None
    combination = len(detected) >= 2

    if not detected:
        recommendation = (
            "No strong pattern signals detected yet. Continue listening. "
            "Do not name a pattern  -  wait for more data."
        )
    elif combination:
        combo_names = " + ".join(d["name"] for d in detected[:2])
        recommendation = (
            f"Pattern combination detected: {combo_names}. "
            f"Name the primary pattern first ({detected[0]['name']}), then gently note the connection. "
            "Use: 'What you're describing in both situations sounds connected  -  like two expressions of the same underlying thread.'"
        )
    else:
        recommendation = (
            f"Primary pattern: {detected[0]['name']}. "
            f"Use the reflection language from skills/frameworks/pattern-mapper.md. "
            f"SoulMap role: {detected[0]['soulmap_role']} "
            f"Follow with a pattern-specific inquiry question from skills/meta/deep-inquiry-bank.md."
        )

    return {
        "patterns_detected": detected,
        "primary_pattern": primary,
        "combination": combination,
        "wait_for_more": False,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json_value(strip=True)
        if isinstance(data, list):
            messages = cast(list, data)
        else:
            messages = cast(list, data.get("messages", []))
        result = detect_patterns(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
