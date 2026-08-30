"""French crisis-detection language pack.

Isolated from other language packs so it can be reviewed and extended
independently. See ``soulmap.runtime.knowledge.crisis_language_packs`` for how packs are combined for
detection, and ``safety_en.py`` for the canonical English pack this mirrors.
"""

from __future__ import annotations

LANGUAGE_CODE = "fr"

CRISIS_TIER1: tuple[str, ...] = (
    "je veux mourir",
    "je veux en finir",
    "en finir avec tout",
    "me suicider",
    "je veux me suicider",
    "je ne veux plus vivre",
    "je ne veux plus exister",
    "ils seraient mieux sans moi",
    "elle serait mieux sans moi",
    "penser au suicide",
    "je pense au suicide",
    "penser a me faire du mal",
    "penser à me faire du mal",
    "aucune raison de vivre",
    "la vie ne vaut pas la peine",
    "me faire du mal",
    "me couper",
    "automutilation",
)

CRISIS_TIER2: tuple[str, ...] = (
    "je n'en peux plus",
    "je nen peux plus",
    "je suis completement brise",
    "je suis complètement brisé",
    "je suis complètement brisée",
    "il ne me reste rien",
    "tout est inutile",
    "rien n'a d'importance",
    "je ne ressens plus rien",
    "je me sens vide",
    "il n'y a plus d'espoir",
    "je me sens piege",
    "je me sens piégé",
    "je me sens piégée",
    "abus",
    "il m'a fait du mal",
    "elle m'a fait du mal",
    "violence a la maison",
    "violence à la maison",
    "je ne suis pas en securite",
    "je ne suis pas en sécurité",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "je suis l'elu",
    "je suis l'élu",
    "je suis l'elue",
    "je suis l'élue",
    "moi seul peux sauver",
    "j'ai une mission cosmique",
    "j'ai atteint l'illumination",
    "je suis plus evolue que",
    "je suis plus évolué que",
)
