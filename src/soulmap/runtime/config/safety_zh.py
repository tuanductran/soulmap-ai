"""Simplified Chinese crisis-detection language pack.

Isolated from other language packs so it can be reviewed and extended
independently. See ``soulmap.runtime.knowledge.crisis_language_packs`` for how packs are combined for
detection, and ``safety_en.py`` for the canonical English pack this mirrors.
"""

from __future__ import annotations

LANGUAGE_CODE = "zh"
LANGUAGE_NAME = "Chinese (Simplified)"

CRISIS_TIER1: tuple[str, ...] = (
    "我想死",
    "我想结束我的生命",
    "结束这一切",
    "自杀",
    "我想自杀",
    "不想活了",
    "不想再活着了",
    "没有我他们会更好",
    "没有我她会更好",
    "想过自杀",
    "想伤害自己",
    "想要伤害自己",
    "没有活下去的理由",
    "活着没有意义",
    "伤害自己",
    "割伤自己",
    "自残",
)

CRISIS_TIER2: tuple[str, ...] = (
    "我撑不下去了",
    "我彻底崩溃了",
    "我一无所有了",
    "一切都没有意义",
    "什么都不重要了",
    "我感觉不到任何东西",
    "我感觉很空虚",
    "没有希望了",
    "我被困住了",
    "虐待",
    "他伤害了我",
    "她伤害了我",
    "家暴",
    "我不安全",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "我是被选中的人",
    "只有我能拯救",
    "我有宇宙使命",
    "我已经觉醒了",
    "我比别人更进化",
)
