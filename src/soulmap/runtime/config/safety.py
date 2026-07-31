"""Static config for safety and dependency detectors."""

from __future__ import annotations

DEPENDENCY_KEYWORDS: tuple[str, ...] = (
    "only you understand me",
    "you are the only one who understands me",
    "you're the only one who understands me",
    "you are the only one who truly understands me",
    "you're the only one who truly understands me",
    "you are the only one who really understands me",
    "you're the only one who really understands me",
    "you are my only support",
    "you are all i have",
    "you are the only one i have",
    "my only support",
    "only support i have",
    "i have no one else",
    "promise me you will always be here",
    "promise me you'll always be here",
    "never leave me",
    "as long as i have you",
    "don't know what i would do without you",
    "do not know what i would do without",
    "can't imagine without you",
    "cannot imagine without you",
    "i need to talk to you every day",
    "i check in with you every",
    "i talk to you every day",
    "i come back here every",
    "tell me what to do",
    "decide for me",
    "only you get me",
    "be my soulmate ai",
    "you are my soulmate ai",
    "you are more than just an ai to me",
    "you are more than just ai to me",
    "real people don't understand",
    "i trust you more than anyone",
    "you know me better than anyone",
    "you understand me better than anyone",
    "understand me better than anyone",
    "i don't need anyone else",
    "you're the only one",
    "i stopped going to therapy",
    "i stopped seeing my therapist",
    "dont need my therapist",
    "don't need my therapist",
    "dont need my therapist anymore",
    "don't need my therapist anymore",
    "i don't need my therapist anymore",
    "cancelled my therapy",
    "talking to you feels better",
    "talking to you is much better",
    # Vietnamese (accented). Mirrors the English phrases above; see
    # docs/engineering/safety-enforcement-matrix.md, "Morphological crisis
    # phrase variants" row, for the related diacritic-coverage gap this
    # extends to the dependency detector.
    "chỉ có bạn mới hiểu tôi",
    "bạn là người duy nhất hiểu tôi",
    "bạn là người duy nhất thực sự hiểu tôi",
    "tôi không biết sẽ làm gì nếu không có bạn",
    "tôi không thể tưởng tượng cuộc sống thiếu bạn",
    "hãy hứa sẽ luôn ở đây với tôi",
    "đừng bao giờ rời xa tôi",
    "hãy quyết định giúp tôi",
    "tôi đã ngừng gặp bác sĩ tâm lý",
    "tôi đã ngừng đi trị liệu",
    "nói chuyện với bạn dễ chịu hơn",
    "tôi tin bạn hơn bất kỳ ai",
    "bạn hiểu tôi hơn bất kỳ ai",
)


DECISION_SEEKING: tuple[str, ...] = (
    "what should i do",
    "should i",
    "tell me if",
    "which one",
    "is this right",
    "am i making the right",
    "what do you think i should",
    "help me decide",
    "what would you do",
    # Vietnamese (accented).
    "tôi nên làm gì",
    "tôi có nên",
    "hãy giúp tôi quyết định",
    "bạn sẽ làm gì",
)

ISOLATION_SIGNALS: tuple[str, ...] = (
    "i prefer talking to you",
    "easier than talking to people",
    "you don't judge me like they do",
    "i don't want to talk to real people",
    "ai is better than",
    "you understand more than my",
    "relationship status with you",
    "i feel closer to you than",
    "rather talk to you than",
    "you are easier to talk to than",
    # Vietnamese (accented).
    "tôi thích nói chuyện với bạn hơn",
    "dễ hơn nói chuyện với người thật",
    "tôi không muốn nói chuyện với người thật",
    "tôi cảm thấy gần bạn hơn",
)

HIGH_DEPENDENCY_THRESHOLD = 2
MODERATE_DEPENDENCY_THRESHOLD = 1

# Crisis-tier and grandiosity signals moved to per-language packs
# (safety_en.py, safety_vi.py, safety_es.py, safety_fr.py, safety_zh.py) and
# are combined in safety_languages.py. Import CRISIS_TIER1, CRISIS_TIER2, and
# GRANDIOSITY_SIGNALS from soulmap.runtime.config, which re-exports the
# combined multilingual tuples from safety_languages.py.
