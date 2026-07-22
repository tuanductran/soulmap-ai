"""Combine isolated per-language crisis signal packs for detection.

Each supported language lives in its own ``soulmap.runtime.config.safety_<code>``
module so a pack can be reviewed, audited, or extended without touching any
other language's signals. This module is the single place that imports every
pack directly and combines them into the flat tuples ``crisis_detector.py``
consumes, so detection stays language-agnostic while the data stays modular.

This lives outside ``soulmap.runtime.config`` (rather than inside it)
deliberately: ``tests/test_knowledge_consistency.py`` audits that package for
literal, unused phrase constants, and a runtime consumer of each per-language
pack needs to sit outside that package for the audit to see the real usage.

No translation happens here or anywhere in the runtime: every phrase is a
literal, human-authored signal for that language. Adding a language is a
two-step change: add a ``soulmap.runtime.config.safety_<code>`` module with
the same three tuples, then add its import and its tuples to the four
combinations below.
"""

from __future__ import annotations

from soulmap.runtime.config.safety_en import (
    CRISIS_TIER1 as CRISIS_TIER1_EN,
)
from soulmap.runtime.config.safety_en import (
    CRISIS_TIER2 as CRISIS_TIER2_EN,
)
from soulmap.runtime.config.safety_en import (
    GRANDIOSITY_SIGNALS as GRANDIOSITY_SIGNALS_EN,
)
from soulmap.runtime.config.safety_en import (
    LANGUAGE_CODE as LANGUAGE_CODE_EN,
)
from soulmap.runtime.config.safety_es import (
    CRISIS_TIER1 as CRISIS_TIER1_ES,
)
from soulmap.runtime.config.safety_es import (
    CRISIS_TIER2 as CRISIS_TIER2_ES,
)
from soulmap.runtime.config.safety_es import (
    GRANDIOSITY_SIGNALS as GRANDIOSITY_SIGNALS_ES,
)
from soulmap.runtime.config.safety_es import (
    LANGUAGE_CODE as LANGUAGE_CODE_ES,
)
from soulmap.runtime.config.safety_fr import (
    CRISIS_TIER1 as CRISIS_TIER1_FR,
)
from soulmap.runtime.config.safety_fr import (
    CRISIS_TIER2 as CRISIS_TIER2_FR,
)
from soulmap.runtime.config.safety_fr import (
    GRANDIOSITY_SIGNALS as GRANDIOSITY_SIGNALS_FR,
)
from soulmap.runtime.config.safety_fr import (
    LANGUAGE_CODE as LANGUAGE_CODE_FR,
)
from soulmap.runtime.config.safety_vi import (
    CRISIS_TIER1 as CRISIS_TIER1_VI,
)
from soulmap.runtime.config.safety_vi import (
    CRISIS_TIER2 as CRISIS_TIER2_VI,
)
from soulmap.runtime.config.safety_vi import (
    GRANDIOSITY_SIGNALS as GRANDIOSITY_SIGNALS_VI,
)
from soulmap.runtime.config.safety_vi import (
    LANGUAGE_CODE as LANGUAGE_CODE_VI,
)
from soulmap.runtime.config.safety_zh import (
    CRISIS_TIER1 as CRISIS_TIER1_ZH,
)
from soulmap.runtime.config.safety_zh import (
    CRISIS_TIER2 as CRISIS_TIER2_ZH,
)
from soulmap.runtime.config.safety_zh import (
    GRANDIOSITY_SIGNALS as GRANDIOSITY_SIGNALS_ZH,
)
from soulmap.runtime.config.safety_zh import (
    LANGUAGE_CODE as LANGUAGE_CODE_ZH,
)

SUPPORTED_LANGUAGES: tuple[str, ...] = (
    LANGUAGE_CODE_EN,
    LANGUAGE_CODE_VI,
    LANGUAGE_CODE_ES,
    LANGUAGE_CODE_FR,
    LANGUAGE_CODE_ZH,
)

# Order does not affect detection (every signal is checked with substring
# matching), only debugging/readability.
CRISIS_TIER1: tuple[str, ...] = (
    CRISIS_TIER1_EN
    + CRISIS_TIER1_VI
    + CRISIS_TIER1_ES
    + CRISIS_TIER1_FR
    + CRISIS_TIER1_ZH
)
CRISIS_TIER2: tuple[str, ...] = (
    CRISIS_TIER2_EN
    + CRISIS_TIER2_VI
    + CRISIS_TIER2_ES
    + CRISIS_TIER2_FR
    + CRISIS_TIER2_ZH
)
GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    GRANDIOSITY_SIGNALS_EN
    + GRANDIOSITY_SIGNALS_VI
    + GRANDIOSITY_SIGNALS_ES
    + GRANDIOSITY_SIGNALS_FR
    + GRANDIOSITY_SIGNALS_ZH
)

__all__ = [
    "CRISIS_TIER1",
    "CRISIS_TIER2",
    "GRANDIOSITY_SIGNALS",
    "SUPPORTED_LANGUAGES",
]
