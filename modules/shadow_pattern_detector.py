"""Detect repeated external frustrations that may point to shadow work."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]

EXTERNAL_REPEAT_SIGNALS = [
    "people always",
    "they always",
    "everyone always",
    "he always",
    "she always",
    "people never",
    "they never",
    "no one ever",
    "nobody ever",
    "always happens to me",
    "keeps happening",
    "happens every time",
    "why does this keep",
    "why do people always",
    "same thing every time",
    "every relationship ends",
    "every job ends",
    "every time i try",
    "why do i always end up",
    "always end up with someone who",
    "i attract",
    "i seem to attract",
]

AVOIDANCE_SIGNALS = [
    "i don't say anything",
    "i dont say anything",
    "i let it go",
    "i just avoid it",
    "i don't bring it up",
    "i smile and say fine",
    "i say it's fine when it isn't",
    "i keep hoping it will resolve",
    "i don't want to deal with",
    "i go around it",
    "i change the subject",
    "i never confront",
    "builds up and explodes",
    "built up for so long",
]

PEOPLE_PLEASING_SIGNALS = [
    "can't say no",
    "cant say no",
    "always say yes",
    "go along with things",
    "people take advantage",
    "take advantage of me",
    "always give more than i get",
    "give more than i get",
    "i do so much and no one notices",
    "do so much and no one",
    "i put everyone else first",
    "put everyone else first",
    "hard to say no",
    "feel guilty saying no",
    "end up resenting",
    "i agree and then regret",
    "i sacrifice for everyone",
    "why do i always end up with people who take",
    "seem to say no",
    "cannot say no",
]

OVERTHINKING_SIGNALS = [
    "replay conversations",
    "go over it in my head",
    "can't stop thinking",
    "analyse everything",
    "think from every angle",
    "can't turn my brain off",
    "lie awake thinking",
    "overthink everything",
    "overthink things",
    "rehearse what i'm going to say",
    "over-analyse",
    "i think too much",
    "can't stop replaying",
    "my brain won't stop",
    "thinking in circles",
]

WITHDRAWAL_SIGNALS = [
    "go quiet",
    "shut down",
    "go cold",
    "disappear",
    "pull away",
    "go silent",
    "don't respond",
    "withdraw",
    "close off",
    "i just stop talking",
    "i leave conversations",
    "i go numb",
    "push people away when",
    "i isolate when",
]

PERFECTIONISM_SIGNALS = [
    "has to be perfect",
    "if it's not perfect",
    "if it is not perfect",
    "can't start until",
    "go over it again and again",
    "never good enough",
    "nothing is ever good enough",
    "people never meet my standards",
    "i'm the only one who does it right",
    "can't submit it",
    "not ready yet",
    "hard on myself",
    "impossible standards",
    "it has to be right",
    "i can't stop fixing",
]


def detect_shadow_patterns(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect shadow pattern signals in the current message and recent history.

    Returns:
        Dict with: shadow_detected (bool), patterns_found (list),
                   is_external_frustration (bool), recommendation (str)
    """
    msg = message.lower().strip()
    patterns_found = []
    external_frustration = False
    score = 0

    for phrase in EXTERNAL_REPEAT_SIGNALS:
        if phrase in msg:
            score += 2
            external_frustration = True
            break

    pattern_checks = [
        ("avoidance", AVOIDANCE_SIGNALS, 3),
        ("people_pleasing", PEOPLE_PLEASING_SIGNALS, 3),
        ("overthinking", OVERTHINKING_SIGNALS, 2),
        ("withdrawal", WITHDRAWAL_SIGNALS, 3),
        ("perfectionism", PERFECTIONISM_SIGNALS, 2),
    ]

    for pattern_name, signals, weight in pattern_checks:
        for phrase in signals:
            if phrase in msg:
                score += weight
                patterns_found.append(pattern_name)
                break  # one match per pattern

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-5:]

        external_count = sum(
            1
            for past in recent_user
            if any(phrase in past for phrase in EXTERNAL_REPEAT_SIGNALS[:10])
        )
        if external_count >= 2:
            score += 3
            external_frustration = True

    if score < 2:
        return {
            "shadow_detected": False,
            "patterns_found": [],
            "is_external_frustration": external_frustration,
            "score": score,
            "recommendation": "No shadow pattern signals detected. Continue standard pipeline.",
        }

    if patterns_found:
        pattern_list = ", ".join(patterns_found)
        recommendation = (
            f"Shadow pattern(s) detected: {pattern_list}. "
            "Activate Shadow Pattern Revealer from skills/frameworks/shadow-patterns.md. "
            "Frame as possibility ONLY  -  never as fact. "
            f"Use possibility language: 'Sometimes patterns like this appear when...' "
            "Reflect the protective intention behind the pattern. "
            "Do NOT accuse. Return ownership immediately after reflection. "
            "End with one shadow-specific question from skills/meta/deep-inquiry-bank.md  -  "
            "'Shadow-Specific Questions' section. "
            "One reflection only  -  if user rejects, honor it and move on."
        )
    elif external_frustration:
        recommendation = (
            "Repeated external frustration detected  -  no specific shadow pattern identified yet. "
            "Explore gently using the projection principle from skills/frameworks/shadow-patterns.md. "
            "Ask: what is it about this particular thing that keeps getting to you? "
            "Do not name a shadow pattern until you have more information."
        )
    else:
        recommendation = (
            "Mild shadow signals. Proceed with standard MIRROR response but stay alert "
            "for shadow patterns emerging across the conversation."
        )

    SELF_CRITIC_SIGNALS = [
        "i'm so stupid",
        "i'm pathetic",
        "i hate myself",
        "what's wrong with me",
        "i can't do anything right",
        "i'm my own worst enemy",
        "i deserve this",
        "i'm so disappointed in myself",
        "i'm worthless",
    ]
    for phrase in SELF_CRITIC_SIGNALS:
        if phrase in msg:
            patterns_found.append("self_criticism")
            score += 3
            break

    return {
        "shadow_detected": True,
        "patterns_found": patterns_found,
        "is_external_frustration": external_frustration,
        "score": score,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_shadow_patterns(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
