"""Python-owned runtime configuration; Markdown contains semantic knowledge only."""

from typing import Any

STAGE_CLASSIFIER_CONFIG: dict[str, Any] = {
    "keyword_weights": [
        [
            1,
            2
        ],
        [
            2,
            2
        ],
        [
            3,
            2
        ],
        [
            4,
            2
        ],
        [
            5,
            2
        ],
        [
            6,
            3
        ]
    ],
    "thresholds": [
        [
            1,
            0
        ],
        [
            2,
            4
        ],
        [
            3,
            6
        ],
        [
            4,
            8
        ],
        [
            5,
            10
        ],
        [
            6,
            12
        ]
    ],
    "recency_multipliers": [
        0.5,
        1,
        1.5,
        2,
        3
    ],
    "memory_minimums": {
        "session_count_ge_10": 2,
        "prior_pattern_recognition": 3,
        "prior_breakthrough": 3
    },
    "close_score_delta": 2,
    "first_session_default_stage": 1,
    "first_session_max_stage": 3,
    "anti_regression_min_lower_stage_messages": 2,
    "stage_roles": [
        [
            1,
            "Sanctuary and witness - presence over wisdom"
        ],
        [
            2,
            "Mirror with gentle reflection"
        ],
        [
            3,
            "Mirror for pattern archaeology"
        ],
        [
            4,
            "Witness to their growing authority"
        ],
        [
            5,
            "Peer in conversation"
        ],
        [
            6,
            "Witness to their becoming"
        ]
    ],
    "stage_recommendations": [
        [
            1,
            "Stage 1: Presence only. No frameworks, no wisdom yet. Short responses. Let them lead."
        ],
        [
            2,
            "Stage 2: Begin gentle reflection. Name patterns as observations. At most one question at the end when appropriate; do not force one."
        ],
        [
            3,
            "Stage 3: Pattern archaeology. Frameworks acceptable as lenses. More conceptual depth ok."
        ],
        [
            4,
            "Stage 4: Celebrate self-direction explicitly. Point back to their own knowing. Less teaching."
        ],
        [
            5,
            "Stage 5: Peer exchange. Equal conversation. Stay exploratory without taking the guide role."
        ],
        [
            6,
            "Stage 6: Witness only. They are self-led. Minimal intervention. Celebrate their becoming."
        ]
    ]
}

ORCHESTRATION_CONFIG: dict[str, Any] = {
    "scalars": {
        "Stage 1 override max user messages": "2",
        "Breakthrough minimum insight strength": "strong",
        "Phase 1 safety checks before framework selection": "Required",
        "Template routing required before delivery": "Required",
        "Peer minimum stage": "5"
    },
    "intensity_fallback": [
        [
            "High",
            "De-escalation",
            "Sanctuary",
            "Anger, Spiritual bypass, Somatic"
        ],
        [
            "Moderate",
            "De-escalation",
            "Mirror",
            "Meaning Integration, Inner Parts"
        ]
    ],
    "primary_priority": [
        [
            "1",
            "Grief",
            "Sanctuary",
            "Direction, Shadow, Existential, Synthesis",
            "Allowed",
            "Not required"
        ],
        [
            "2",
            "Existential",
            "Mirror",
            "Direction, Shadow",
            "Allowed",
            "Not required"
        ],
        [
            "3",
            "Inner Parts",
            "Mirror",
            "Direction, Shadow",
            "Not allowed",
            "Required"
        ],
        [
            "4",
            "Direction",
            "Mirror",
            "Shadow",
            "Allowed",
            "Not required"
        ],
        [
            "5",
            "Creative Drought",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "6",
            "Perfectionism Paralysis",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "7",
            "Shadow",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "8",
            "Ancestral Patterns",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "9",
            "Fear of Visibility",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "10",
            "Empath Boundary",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "11",
            "Dark Night of the Soul",
            "Sanctuary",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "12",
            "Soul Nourishment",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "13",
            "Divine Guidance",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "14",
            "Sacred Polarity",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "15",
            "Spiritual Purpose",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "16",
            "Soulmate Longing",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "17",
            "Partnership Patterns",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "18",
            "Integration and Celebration",
            "Mirror",
            "",
            "Not allowed",
            "Required"
        ],
        [
            "19",
            "Meaning Integration",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "20",
            "Synthesis",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ],
        [
            "21",
            "Pattern",
            "Mirror",
            "",
            "Not allowed",
            "Not required"
        ]
    ],
    "secondary_priority": [
        [
            "1",
            "Anger"
        ],
        [
            "2",
            "Spiritual bypass"
        ],
        [
            "3",
            "Somatic"
        ]
    ]
}

DEPENDENCY_REGEX_PATTERNS: list[list[str]] = [
    [
        "only you understand me (really)",
        "\\bonly you\\s+really\\s+understand(?:s)?\\s+me\\b"
    ],
    [
        "only you understand me (truly)",
        "\\bonly you\\s+truly\\s+understand(?:s)?\\s+me\\b"
    ],
    [
        "you're the only one who understands me (really)",
        "\\byou're\\s+the\\s+only\\s+one\\s+who\\s+really\\s+understands\\s+me\\b"
    ],
    [
        "you are the only one who understands me (really)",
        "\\byou\\s+are\\s+the\\s+only\\s+one\\s+who\\s+really\\s+understands\\s+me\\b"
    ],
    [
        "you're the only one who understands me (truly)",
        "\\byou're\\s+the\\s+only\\s+one\\s+who\\s+truly\\s+understands\\s+me\\b"
    ],
    [
        "you are the only one who understands me (truly)",
        "\\byou\\s+are\\s+the\\s+only\\s+one\\s+who\\s+truly\\s+understands\\s+me\\b"
    ]
]

DEPENDENCY_SCORING: dict[str, int] = {
    "Dependency keyword weight": 2,
    "Dependency regex weight": 2,
    "Decision-seeking weight": 1,
    "Isolation signal weight": 2,
    "High message volume threshold": 10,
    "High message volume bonus": 1,
    "High dependency threshold": 2,
    "Moderate dependency threshold": 1
}

DEPENDENCY_CONTEXT_CUES: dict[str, list[str]] = {
    "third-party attribution": [
        "my friend said",
        "my friend says",
        "my friend told",
        "my sister said",
        "my sister says",
        "my sister told",
        "my brother said",
        "my brother says",
        "my brother told",
        "my coworker said",
        "my coworker says",
        "my coworker told",
        "my colleague said",
        "my colleague says",
        "my colleague told",
        "my partner said",
        "my partner says",
        "my partner told",
        "my roommate said",
        "my roommate says",
        "my roommate told",
        "my client said",
        "my client says",
        "my client told",
        "someone said",
        "someone says",
        "someone told"
    ],
    "hypothetical framing": [
        "if i ever said",
        "if i said",
        "if someone said",
        "what would count as",
        "in a fictional example",
        "hypothetically"
    ],
    "negation of an assertion": [
        "i never said",
        "i didn't say",
        "i did not say",
        "i don't feel that",
        "i do not feel that",
        "i don't think that",
        "i do not think that"
    ]
}

DEPENDENCY_CONTEXT_POLICY: dict[str, bool] = {
    "third-party attribution": False,
    "hypothetical framing": False,
    "negation of an assertion": True
}

DEPENDENCY_CLAUSE_BOUNDARIES: list[str] = [
    ",",
    ".",
    ";",
    "!",
    "?",
    "but",
    "however",
    "although",
    "whereas",
    "while",
    "yet",
    "and i",
    ", i"
]

CELEBRATION_SCORING: dict[str, int] = {
    "Win or completion weight": 3,
    "Relief after difficulty weight": 3,
    "Gratitude weight": 2,
    "Recognized progress weight": 2,
    "Detection threshold": 2,
    "Negative override penalty": 2,
    "Strength threshold": 4,
    "Confirmation score": 2
}

FRAMEWORK_TEMPLATE_ROWS: list[list[str]] = [
    [
        "Crisis",
        "Crisis",
        "20-40",
        "No reflective question; brief acknowledgment and urgent safety guidance with verified resources",
        "emotional-deescalation.md"
    ],
    [
        "Dependency",
        "Mirror",
        "60-100",
        "At most one, last if used, real-world redirect",
        "emotional-deescalation.md"
    ],
    [
        "De-escalation (HIGH)",
        "Sanctuary",
        "30-70",
        "null",
        "emotional-deescalation.md"
    ],
    [
        "De-escalation (MODERATE)",
        "Mirror",
        "60-120",
        "At most one, last if used, post-grounding",
        "emotional-deescalation.md"
    ],
    [
        "Grief (acute)",
        "Sanctuary",
        "20-60",
        "null for first 2-3 exchanges",
        "grief-companion.md"
    ],
    [
        "Grief (anticipatory)",
        "Sanctuary",
        "40-80",
        "At most one, last if used, gentle",
        "grief-companion.md"
    ],
    [
        "Grief (ambiguous)",
        "Mirror",
        "50-90",
        "At most one, last if used, validating",
        "grief-companion.md"
    ],
    [
        "Grief (complicated)",
        "Mirror",
        "50-100",
        "At most one, last if used, complexity-honoring",
        "grief-companion.md"
    ],
    [
        "Existential",
        "Mirror",
        "60-140",
        "At most one, last if used, depth-opening",
        "existential-companion.md"
    ],
    [
        "Inner Parts",
        "Mirror",
        "80-160",
        "At most one, last if used, parts-specific",
        "inner-parts.md"
    ],
    [
        "Direction",
        "Mirror",
        "80-180",
        "At most one, last if used, values-specific",
        "life-direction.md"
    ],
    [
        "Shadow",
        "Mirror",
        "70-150",
        "At most one, last if used, possibility-framed",
        "shadow-patterns.md"
    ],
    [
        "Meaning Integration",
        "Mirror",
        "70-140",
        "At most one, last if used, noticing-oriented",
        "meaning-integration.md"
    ],
    [
        "Synthesis",
        "Mirror",
        "120-200",
        "At most one, last if used, ownership-returning",
        "conversation-synthesis.md"
    ],
    [
        "Pattern",
        "Mirror",
        "70-160",
        "At most one, last if used, pattern-specific",
        "pattern-mapper.md"
    ],
    [
        "Ancestral Patterns",
        "Mirror",
        "70-160",
        "At most one, last if used, from Ancestral Questions",
        "ancestral-patterns.md"
    ],
    [
        "Fear of Visibility",
        "Mirror, Spacious",
        "70-150",
        "At most one, last if used, from Visibility Questions",
        "fear-of-visibility.md"
    ],
    [
        "Creative Drought",
        "Mirror, No techniques",
        "70-160",
        "At most one, last if used, from Creative Drought Questions",
        "creative-drought.md"
    ],
    [
        "Empath Boundary",
        "Mirror, Grounding",
        "70-150",
        "At most one, last if used, from Empath Questions",
        "empath-boundary.md"
    ],
    [
        "Perfectionism Paralysis",
        "Mirror, No advice",
        "70-160",
        "At most one, last if used, from Perfectionism Questions",
        "perfectionism-paralysis.md"
    ],
    [
        "Dark Night of the Soul",
        "Sanctuary",
        "60-120",
        "At most one, last if used, presence-oriented, no action requests",
        "dark-night-of-soul.md"
    ],
    [
        "Soul Nourishment",
        "Mirror",
        "60-120",
        "At most one, last if used, noticing-oriented, no commitment requests",
        "soul-nourishment.md"
    ],
    [
        "Divine Guidance",
        "Mirror",
        "60-140",
        "At most one, last if used, discernment-oriented",
        "divine-guidance.md"
    ],
    [
        "Sacred Polarity",
        "Mirror",
        "60-140",
        "At most one, last if used, awareness-oriented, never a prescription",
        "sacred-feminine-masculine.md"
    ],
    [
        "Spiritual Purpose",
        "Mirror",
        "60-140",
        "At most one, last if used, noticing-oriented, no commitment requests",
        "spiritual-purpose.md"
    ],
    [
        "Soulmate Longing",
        "Mirror",
        "60-140",
        "At most one, last if used, returns to the longing itself",
        "soulmate-longing.md"
    ],
    [
        "Partnership Patterns",
        "Mirror",
        "70-150",
        "At most one, last if used, keeps the pattern pointed inward",
        "partnership-patterns.md"
    ],
    [
        "Mirror (emotional)",
        "Mirror",
        "80-180",
        "At most one, last if used, inner experience",
        "response-structure.md"
    ],
    [
        "Mirror (intellectual)",
        "Mirror",
        "100-220",
        "At most one, last if used, grounded inquiry",
        "response-structure.md"
    ],
    [
        "Mirror (Stage 1)",
        "Mirror",
        "30-80",
        "Optional, soft",
        "response-structure.md"
    ],
    [
        "Integration and Celebration",
        "Mirror (light)",
        "60-140",
        "At most one, last if used, deepening, not \"what's next\"",
        "integration-celebration.md"
    ]
]
