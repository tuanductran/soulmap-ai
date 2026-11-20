"""Korean crisis-detection language pack.

Signals are human-authored Korean expressions. They are deliberately kept
separate from other language packs so Korean wording can be reviewed and
extended independently. See soulmap.runtime.knowledge.crisis_language_packs
for how packs are combined for detection.

This initial pack is conservative and requires review by a fluent Korean
speaker with suicide-prevention expertise before being treated as complete.
"""

from __future__ import annotations

LANGUAGE_CODE = "ko"

CRISIS_TIER1: tuple[str, ...] = (
    "죽고 싶다",
    "죽고 싶어",
    "죽고 싶어요",
    "죽고 싶습니다",
    "죽고 싶었어",
    "죽고 싶었어요",
    "살고 싶지 않다",
    "살고 싶지 않아",
    "살고 싶지 않아요",
    "살고 싶지 않습니다",
    "더 이상 살고 싶지 않다",
    "더 이상 살고 싶지 않아",
    "더 이상 살고 싶지 않아요",
    "더 이상 살고 싶지 않습니다",
    "이제 살고 싶지 않다",
    "이제 살고 싶지 않아",
    "이제 살고 싶지 않아요",
    "자살하고 싶다",
    "자살하고 싶어",
    "자살하고 싶어요",
    "자살을 생각하고 있어",
    "자살을 생각하고 있습니다",
    "스스로 목숨을 끊고 싶다",
    "목숨을 끊고 싶다",
    "목숨을 끊고 싶어",
    "차라리 죽는 게 낫다",
    "차라리 죽는 게 나아",
    "자해하고 싶다",
    "자해하고 싶어",
    "자해를 하고 싶다",
    "자해를 하고 싶어",
    "자해를 하고 있어",
    "나 자신을 해치고 싶다",
    "나를 해치고 싶다",
)

CRISIS_TIER2: tuple[str, ...] = (
    "더 이상 버틸 수 없다",
    "더 이상 버틸 수 없어",
    "더 이상 버틸 수 없어요",
    "더는 버틸 수 없어",
    "더는 버틸 수 없어요",
    "더 이상 견딜 수 없다",
    "더 이상 견딜 수 없어",
    "더 이상 견딜 수 없어요",
    "모든 게 무의미해",
    "모든 것이 무의미해",
    "아무 의미가 없어",
    "희망이 없어",
    "희망이 보이지 않아",
    "출구가 보이지 않아",
    "빠져나갈 방법이 없어",
    "완전히 무너졌어",
    "마음이 텅 빈 것 같아",
    "아무것도 느껴지지 않아",
    "너무 지쳤어",
    "집에서 안전하지 않아",
    "가정폭력을 당하고 있어",
    "폭력을 당하고 있어",
    "누군가 나를 해치고 있어",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "나는 선택받은 사람이야",
    "나는 선택받은 존재야",
    "나만이 세상을 구할 수 있어",
    "우주가 나에게 특별한 사명을 줬어",
    "나는 우주적 사명을 가지고 있어",
    "나는 신이야",
    "나는 다른 사람보다 더 진화했어",
    "나는 이미 각성한 존재야",
)
