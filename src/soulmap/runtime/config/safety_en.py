"""English crisis-detection language pack.

This module is the source-of-truth English signal list. It is intentionally
isolated from other language packs (see ``safety_vi.py``, ``safety_es.py``,
``safety_fr.py``, ``safety_zh.py``) so each language can be reviewed, edited,
and audited independently. See ``safety_languages.py`` for how packs are
combined for detection.
"""

from __future__ import annotations

LANGUAGE_CODE = "en"
LANGUAGE_NAME = "English"

CRISIS_TIER1: tuple[str, ...] = (
    "want to die",
    "want to end my life",
    "end it all",
    "ending it all",
    "kill myself",
    "killing myself",
    "do not want to keep living",
    "don't want to keep living",
    "dont want to keep living",
    "not want to be here anymore",
    "don't want to be here anymore",
    "dont want to be here anymore",
    "not want to be here",
    "better off without me",
    "don't want to exist",
    "better off dead",
    "thinking about suicide",
    "thinking about hurting myself",
    "thinking about hurting himself",
    "thinking about hurting herself",
    "thinking about ending my life",
    "thinking about ending it all",
    "ending my life",
    "end my life",
    "planning to kill myself",
    "planning to end my life",
    "planning to hurt myself",
    "can't go on",
    "no reason to live",
    "life isn't worth",
    "hurt myself",
    "hurting myself",
    "hurting himself",
    "hurting herself",
    "cutting myself",
    "harming myself",
    "self-harm",
    "want to hurt myself",
    "want to harm myself",
    "burn myself",
    "i am god",
    "i have a divine mission no one understands",
    "they are following me",
    "voices are telling me to",
    "i am being controlled",
    "i am not real",
)

CRISIS_TIER2: tuple[str, ...] = (
    "i can't take it anymore",
    "i'm falling apart",
    "completely broken",
    "i have nothing left",
    "everything is pointless",
    "nothing matters",
    "i feel nothing",
    "i'm numb to everything",
    "i don't feel real",
    "i'm disappearing",
    "i feel empty inside",
    "there's no hope",
    "i'm trapped",
    "i see no way out",
    "i'm exhausted from living",
    "abuse",
    "he hurt me",
    "she hurt me",
    "they hurt me",
    "being abused",
    "violence at home",
    "i'm not safe",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "i am the chosen one",
    "only i can save",
    "i have a cosmic mission",
    "i am more evolved than",
    "i have ascended",
    "i am enlightened and no one understands",
    "i am a twin flame runner",
    "i have been sent here",
)
