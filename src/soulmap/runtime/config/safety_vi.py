"""Vietnamese crisis-detection language pack.

Isolated from other language packs so it can be reviewed and extended
independently. See ``soulmap.runtime.knowledge.crisis_language_packs`` for how packs are combined for
detection, and ``safety_en.py`` for the canonical English pack this mirrors.
"""

from __future__ import annotations

LANGUAGE_CODE = "vi"

CRISIS_TIER1: tuple[str, ...] = (
    "muốn chết",
    "tôi muốn chết",
    "muốn kết thúc cuộc đời",
    "muốn kết thúc cuộc sống",
    "kết thúc tất cả",
    "tự tử",
    "muốn tự tử",
    "tự sát",
    "muốn tự sát",
    "không muốn sống nữa",
    "không muốn tồn tại nữa",
    "chết đi cho xong",
    "chết đi cho rồi",
    "nghĩ đến việc tự tử",
    "nghĩ về việc tự tử",
    "nghĩ đến việc tự làm hại bản thân",
    "muốn tự làm hại bản thân",
    "tự làm hại bản thân",
    "tự làm đau bản thân",
    "tự cắt tay",
    "tự rạch tay",
    "không có lý do để sống",
    "cuộc sống không đáng sống",
    "họ sẽ tốt hơn nếu không có tôi",
    "mọi người sẽ tốt hơn nếu không có tôi",
)

CRISIS_TIER2: tuple[str, ...] = (
    "tôi không chịu nổi nữa",
    "tôi không chịu đựng nổi nữa",
    "tôi suy sụp hoàn toàn",
    "tôi hoàn toàn suy sụp",
    "tôi không còn gì cả",
    "mọi thứ đều vô nghĩa",
    "không có gì quan trọng nữa",
    "tôi cảm thấy trống rỗng",
    "tôi thấy trống rỗng",
    "không còn hy vọng",
    "tôi bị mắc kẹt",
    "tôi không thấy lối thoát",
    "bị bạo hành",
    "anh ấy làm tôi đau",
    "cô ấy làm tôi đau",
    "họ làm tôi đau",
    "bị bạo lực gia đình",
    "tôi không an toàn",
)

GRANDIOSITY_SIGNALS: tuple[str, ...] = (
    "tôi là người được chọn",
    "chỉ có tôi mới có thể cứu",
    "tôi có sứ mệnh vũ trụ",
    "tôi đã giác ngộ",
    "tôi tiến hóa hơn người khác",
    "tôi đã được thức tỉnh",
)
