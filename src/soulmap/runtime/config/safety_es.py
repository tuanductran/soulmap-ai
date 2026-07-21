"""Spanish crisis-detection language pack.

Isolated from other language packs so it can be reviewed and extended
independently. See ``safety_languages.py`` for how packs are combined for
detection, and ``safety_en.py`` for the canonical English pack this mirrors.
"""

from __future__ import annotations

LANGUAGE_CODE = "es"
LANGUAGE_NAME = "Spanish"

CRISIS_TIER1: tuple[str, ...] = (
    "quiero morir",
    "quiero morirme",
    "quiero terminar con mi vida",
    "quiero acabar con mi vida",
    "acabar con todo",
    "quiero suicidarme",
    "suicidarme",
    "matarme",
    "quiero matarme",
    "no quiero seguir viviendo",
    "no quiero vivir mas",
    "no quiero vivir más",
    "no quiero existir",
    "estarian mejor sin mi",
    "estarían mejor sin mí",
    "pensando en el suicidio",
    "pensando en suicidarme",
    "pensando en hacerme daño",
    "sin razon para vivir",
    "sin razón para vivir",
    "la vida no vale la pena",
    "hacerme daño",
    "lastimarme",
    "cortarme",
    "autolesion",
    "autolesión",
)

CRISIS_TIER2: tuple[str, ...] = (
    "no puedo mas",
    "no puedo más",
    "estoy completamente roto",
    "estoy completamente rota",
    "no me queda nada",
    "todo es inutil",
    "todo es inútil",
    "nada importa",
    "no siento nada",
    "me siento vacio",
    "me siento vacío",
    "no hay esperanza",
    "estoy atrapado",
    "estoy atrapada",
    "no veo salida",
    "abuso",
    "me lastimo",
    "me lastimó",
    "violencia en casa",
    "no estoy a salvo",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "soy el elegido",
    "soy la elegida",
    "solo yo puedo salvar",
    "tengo una mision cosmica",
    "tengo una misión cósmica",
    "he ascendido",
    "estoy mas evolucionado que",
    "estoy más evolucionado que",
)
