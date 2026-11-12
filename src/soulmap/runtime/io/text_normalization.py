"""Shared text normalization helpers for detector input handling."""

from __future__ import annotations

import re

RIGHT_SINGLE_QUOTE = "\u2019"

_APOSTROPHE_ELISIONS = re.compile(
    r"'(?:cause|em|til|round|bout|n|tis|twas|twere|twill|kay|course|cept)\b",
    re.IGNORECASE,
)
_QUOTE_PAIRS = {'"': '"', "\u201c": "\u201d", "\u2018": "'"}
_ATTRIBUTION_CUES = re.compile(
    r"\b(?:(?:my|our)\s+\w+(?:\s+\w+){0,2}|"
    r"someone|somebody|he|she|they|the\s+\w+(?:\s+\w+){0,2})\s+"
    r"(?:said|says|told me|tells me|mentioned|mentions|wrote|writes|"
    r"texted|messaged|asked|asks|reported|explained|shared|replied|responded|"
    r"think|thinks|thought|believe|believes|believed|"
    r"(?:may|might|could|would)\s+(?:say|tell me|mention|write|text|ask|"
    r"report|explain|share|reply|respond))"
    r"\b(?:\s+that)?\s*[:,]?\s*|"
    r"\b(?:bạn|mẹ|cha|bố|ba|anh|chị|em|cô|chú|ông|bà|họ|ai\s+đó|"
    r"người\s+\w+)(?:\s+(?:tôi|mình|ấy|đó))?\s+"
    r"(?:nói|bảo|kể|viết|nhắn|hỏi|chia sẻ|"
    r"nghĩ|tin|cảm thấy|cho rằng)\b(?:\s+(?:rằng|là))?\s*[:,]?\s*|"
    r"\b(?:my|our)\s+(?:friend|sister|brother|mother|father|mom|dad|parent|partner|spouse|"
    r"husband|wife|colleague|coworker|boss|manager|therapist|teacher|doctor|"
    r"neighbor|roommate|son|daughter|child|grandmother|grandfather)\s*:\s*|"
    r"\b(?:he|she|they)\s*:\s*",
    re.IGNORECASE,
)
_ATTRIBUTION_BOUNDARY = re.compile(
    r"[.!?;]|,\s*(?=(?:but|however|although|yet|and\s+i\b|i\s+(?:also|too|feel\s+(?:the\s+same|that\s+too))|"
    r"i\s+am\b|i\s+feel\b|nhưng|tuy\s+nhiên|mặc\s+dù)\b)|"
    r"\b(?:but|however|although|yet|nhưng|tuy\s+nhiên|mặc\s+dù)\b",
    re.IGNORECASE,
)


def normalize_message_text(message: str, *, strip: bool = True) -> str:
    """Normalize smart punctuation and collapse internal whitespace."""
    normalized = message.lower().replace(RIGHT_SINGLE_QUOTE, "'").replace("`", "'")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip() if strip else normalized


def mask_third_party_attribution(message: str) -> str:
    """Mask quoted and explicitly attributed third-party speech in detector input.

    Unattributed quotations remain intact because they may be the user's own
    words. The user's own text after a sentence or clear contrast boundary is
    preserved when another person's speech is reported in the same message.
    """
    text = normalize_message_text(message, strip=False)
    characters = list(text)
    quote_spans: list[tuple[int, int]] = []
    start: int | None = None
    closing: str | None = None

    for index, char in enumerate(text):
        if closing is None:
            if char in _QUOTE_PAIRS:
                start = index
                closing = _QUOTE_PAIRS[char]
            elif (
                char == "'"
                and (index == 0 or not text[index - 1].isalnum())
                and index + 1 < len(text)
                and not text[index + 1].isspace()
                and not text[index + 1].isdigit()
                and not _APOSTROPHE_ELISIONS.match(text[index:])
            ):
                start = index
                closing = "'"
            continue

        if char != closing:
            continue
        if (
            char == "'"
            and index > 0
            and index + 1 < len(text)
            and text[index - 1].isalnum()
            and text[index + 1].isalnum()
        ):
            continue
        if start is not None:
            quote_spans.append((start, index + 1))
        start = None
        closing = None

    if start is not None:
        quote_spans.append((start, len(text)))

    for span_start, span_end in quote_spans:
        prefix = text[:span_start]
        clause_start = max(
            prefix.rfind("."),
            prefix.rfind("!"),
            prefix.rfind("?"),
            prefix.rfind(";"),
        )
        suffix = text[span_end:].lstrip()
        if suffix.startswith((",", ":", ";")):
            suffix = suffix[1:].lstrip()
        is_attributed = _ATTRIBUTION_CUES.search(prefix[clause_start + 1 :]) is not None
        is_attributed = is_attributed or _ATTRIBUTION_CUES.match(suffix) is not None
        if is_attributed:
            characters[span_start:span_end] = [" "] * (span_end - span_start)
            if span_end > span_start:
                characters[span_end - 1] = "."

    unquoted = "".join(characters)
    for match in _ATTRIBUTION_CUES.finditer(unquoted):
        prefix = unquoted[: match.start()]
        clause_start = max(
            prefix.rfind("."),
            prefix.rfind("!"),
            prefix.rfind("?"),
            prefix.rfind(";"),
        )
        attributed_prefix = prefix[clause_start + 1 :]
        boundary = _ATTRIBUTION_BOUNDARY.search(unquoted, match.end())
        span_end = boundary.start() if boundary else len(unquoted)
        reported_content = unquoted[match.end() : span_end].strip()
        if attributed_prefix.rstrip().endswith((",", ":")) and not reported_content:
            characters[clause_start + 1 : match.start()] = [" "] * (
                match.start() - clause_start - 1
            )
        characters[match.end() : span_end] = [" "] * (span_end - match.end())

    return re.sub(r"\s+", " ", "".join(characters)).strip()
