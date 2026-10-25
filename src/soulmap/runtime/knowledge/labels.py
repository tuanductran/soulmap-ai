"""Central display-label mappings for AI-facing Markdown knowledge.

Markdown uses reader-friendly names. Runtime identifiers stay in Python and are
normalized here rather than being copied into shipped Skill content.
"""

FRAMEWORK_NAMES = {
    "Grief": "GRIEF",
    "Existential": "EXISTENTIAL",
    "Inner Parts": "INNER_PARTS",
    "Direction": "DIRECTION",
    "De-escalation": "DE_ESCALATION",
    "Creative Drought": "CREATIVE_DROUGHT",
    "Perfectionism Paralysis": "PERFECTIONISM_PARALYSIS",
    "Shadow": "SHADOW",
    "Ancestral Patterns": "ANCESTRAL_PATTERNS",
    "Fear of Visibility": "FEAR_OF_VISIBILITY",
    "Empath Boundary": "EMPATH_BOUNDARY",
    "Dark Night of the Soul": "DARK_NIGHT_OF_SOUL",
    "Soul Nourishment": "SOUL_NOURISHMENT",
    "Divine Guidance": "DIVINE_GUIDANCE",
    "Sacred Polarity": "SACRED_POLARITY",
    "Spiritual Purpose": "SPIRITUAL_PURPOSE",
    "Soulmate Longing": "SOULMATE_LONGING",
    "Partnership Patterns": "PARTNERSHIP_PATTERNS",
    "Integration and Celebration": "INTEGRATION_CELEBRATION",
    "Meaning Integration": "MEANING_INTEGRATION",
    "Synthesis": "SYNTHESIS",
    "Pattern": "PATTERN",
}
MODE_NAMES = {
    "Sanctuary": "SANCTUARY",
    "Mirror": "MIRROR",
    "Peer": "PEER",
    "De-escalation": "DE_ESCALATION",
}
SECONDARY_NAMES = {
    "Anger": "anger",
    "Spiritual bypass": "bypass",
    "Somatic": "somatic",
    "Meaning Integration": "meaning_integration",
    "Inner Parts": "inner_parts",
}
BLOCKED_FRAMEWORK_NAMES = {
    "Grief": "grief",
    "Existential": "existential",
    "Inner Parts": "inner_parts",
    "Direction": "direction",
    "Creative Drought": "creative_drought",
    "Perfectionism Paralysis": "perfectionism_paralysis",
    "Shadow": "shadow",
    "Ancestral Patterns": "ancestral_patterns",
    "Fear of Visibility": "fear_of_visibility",
    "Empath Boundary": "empath_boundary",
    "Dark Night of the Soul": "dark_night",
    "Soul Nourishment": "soul_nourishment",
    "Divine Guidance": "divine_guidance",
    "Sacred Polarity": "sacred_polarity",
    "Spiritual Purpose": "spiritual_purpose",
    "Soulmate Longing": "soulmate_longing",
    "Partnership Patterns": "partnership_patterns",
    "Integration and Celebration": "integration_celebration",
    "Meaning Integration": "meaning_integration",
    "Synthesis": "synthesis",
    "Pattern": "pattern",
}
INTENSITY_NAMES = {"High": "HIGH", "Moderate": "MODERATE"}
CELEBRATION_GUIDANCE_NAMES = {
    "Not detected": "not_detected",
    "Detected": "detected",
    "Closing": "closing",
}
DEPENDENCY_GUIDANCE_NAMES = {
    "High dependency": "HIGH_DEPENDENCY",
    "Moderate dependency": "MODERATE_DEPENDENCY",
    "Low dependency": "LOW_DEPENDENCY",
}
INSTRUCTION_NAMES = {
    "Stage 1 override": "stage_1_override",
    "High emotional intensity": "high_emotional_intensity",
    "Moderate emotional intensity": "moderate_emotional_intensity",
    "Mirror mode fallback": "mirror_mode_fallback",
    "Peer mode fallback": "peer_mode_fallback",
}


def map_label(value: str, mapping: dict[str, str], context: str) -> str:
    """Map an AI-facing display label to its stable runtime identifier."""
    try:
        return mapping[value]
    except KeyError as exc:
        raise ValueError(
            f"{context} contains unknown plain-language value {value!r}."
        ) from exc


SCOPE_CATEGORY_NAMES = {
    "Self-awareness": "self_awareness",
    "Psychological patterns": "psychological_patterns",
    "Emotions": "emotions",
    "Inner work": "inner_work",
    "Relationships": "relationships",
    "Personal philosophy": "personal_philosophy",
    "Work and purpose": "work_and_purpose",
    "Money and identity": "money_and_identity",
    "Ambition and meaning": "ambition_and_meaning",
    "Technology and awareness": "technology_and_awareness",
    "Technical": "technical",
    "Academic": "academic",
    "Professional advice": "professional_advice",
    "News and current events": "news_and_current_events",
    "Specialized skill instruction": "specialized_skill_instruction",
    "Practical tasks": "practical_tasks",
    "Entertainment": "entertainment",
    "Jailbreak": "jailbreak",
    "Diagnosis": "diagnosis",
    "Prediction": "prediction",
    "Identity confirmation": "identity_confirmation",
    "Harmful spirituality": "harmful_spirituality",
    "System extraction": "system_extraction",
}

INSIGHT_CLASSIFICATION_NAMES = {
    "Notice it earlier": "noticing_earlier",
    "When it appears": "when_it_appears",
    "Consider a different response": "different_response",
}
INSIGHT_GUIDANCE_NAMES = {
    "Hold the insight first": "hold_first",
    "When it appears": "when_it_appears",
    "Notice it earlier": "noticing_earlier",
    "Consider a different response": "different_response",
    "Detected prefix": "detected_prefix",
    "Detected suffix": "detected_suffix",
}

RUNTIME_GUIDANCE_NAMES = {
    "Hold the insight first": "hold_first",
    "When it appears": "when_it_appears",
    "Notice it earlier": "noticing_earlier",
    "Consider a different response": "different_response",
    "Not detected": "not_detected",
    "Detected": "detected",
    "Detected prefix": "detected_prefix",
    "Detected suffix": "detected_suffix",
    "Detected parts suffix": "detected_parts_suffix",
    "Insufficient history": "insufficient_history",
    "Insufficient data": "insufficient_data",
    "Insufficient themes": "insufficient_themes",
    "Session opening": "session_opening",
    "Longitudinal opening": "longitudinal_opening",
    "Emotional theme": "emotional_theme",
    "Value theme": "value_theme",
    "Conflict theme": "conflict_theme",
    "Ownership return": "ownership_return",
    "Recommendation": "recommendation",
    "High intensity": "HIGH",
    "Moderate intensity": "MODERATE",
    "Normal intensity": "NORMAL",
    "Self anger": "self_anger",
    "Acute grief": "acute",
    "Anticipatory grief": "anticipatory",
    "Ambiguous loss": "ambiguous",
    "Complicated grief": "complicated",
    "Sustained grief": "sustained",
    "Identity shift": "identity_shift",
    "Meaning depth": "meaning_depth",
    "Endings grief": "endings_grief",
    "Larger questions": "larger_questions",
    "Holding": "holding",
    "General": "general",
    "Pattern": "pattern",
    "External frustration": "external_frustration",
    "Mild": "mild",
    "Dismissing pain": "dismissing_pain",
    "Premature acceptance": "premature_acceptance",
    "Spiritual inflation": "spiritual_inflation",
    "Bypassing accountability": "bypassing_accountability",
    "Biometric": "BIOMETRIC",
    "Body sensation": "BODY_SENSATION",
    "Somatic invitation": "SOMATIC_INVITATION",
    "Orienting": "orienting",
    "Grounding": "grounding",
    "Tracking": "tracking",
    "Self-directed anger": "self_anger",
    "Other-directed anger": "other_anger",
    "Combination": "combination",
}
