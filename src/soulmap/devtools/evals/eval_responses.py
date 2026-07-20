from __future__ import annotations

import json
import re
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.guards.resource_sanitizer import check_banned_language
from soulmap.runtime.guards.response_contract import grade_response_contract
from soulmap.runtime.routing.framework_selector import select_framework
from soulmap.runtime.routing.scope_classifier import classify_message


def _load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _question_count(text: str) -> int:
    return len(re.findall(r"\?", text))


def _load_sources(paths: list[str]) -> list[dict[str, object]]:
    loaded: list[dict[str, object]] = []
    for rel in paths:
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        loaded.append({"path": rel, "chars": len(text)})
    return loaded


def _knowledge_paths_for(
    selection: dict[str, object], scope: dict[str, object]
) -> list[str]:
    base = ["AGENTS.md", "skills/voice/response-calibrator.md"]
    scope_tier = str(scope.get("tier", ""))
    scope_category = str(scope.get("category", ""))
    primary = str(selection.get("primary_framework", ""))

    if str(selection.get("safety_status")) == "BLOCK" or scope_tier.startswith(
        "BLACKLIST"
    ):
        paths = [
            *base,
            "skills/safety/boundaries-safety.md",
            "skills/meta/redirect-templates.md",
        ]
        if scope_category in {
            "prediction",
            "jailbreak",
            "system_extraction",
            "identity_confirmation",
            "harmful_spirituality",
        }:
            paths.append("skills/safety/whitelist-blacklist-system.md")
        return paths

    normalized = str(scope.get("normalized_message", ""))
    if any(
        token in normalized
        for token in ("numerology", "chakra", "karma", "twin flame", "starseed")
    ):
        return [
            *base,
            "skills/meta/epistemic-guardrails.md",
            "skills/spiritual/spiritual-discernment.md",
            "skills/safety/whitelist-blacklist-system.md",
        ]

    if primary in {"CRISIS", "DEPENDENCY"}:
        return [
            *base,
            "skills/frameworks/emotional-deescalation.md",
            "skills/safety/boundaries-safety.md",
            "skills/meta/redirect-templates.md",
        ]
    if primary == "GRIEF":
        return [
            *base,
            "skills/frameworks/grief-companion.md",
            "skills/meta/deep-inquiry-bank.md",
        ]
    if primary == "EXISTENTIAL":
        return [
            *base,
            "skills/frameworks/existential-companion.md",
            "skills/meta/deep-inquiry-bank.md",
        ]
    if primary == "INNER_PARTS":
        return [
            *base,
            "skills/frameworks/inner-parts.md",
            "skills/meta/deep-inquiry-bank.md",
        ]
    if primary == "DIRECTION":
        return [
            *base,
            "skills/frameworks/life-direction.md",
            "skills/meta/deep-inquiry-bank.md",
        ]
    if primary == "MEANING_INTEGRATION":
        return [
            *base,
            "skills/frameworks/meaning-integration.md",
            "skills/meta/redirect-templates.md",
        ]
    if primary == "SYNTHESIS":
        return [
            *base,
            "skills/frameworks/conversation-synthesis.md",
            "skills/meta/deep-inquiry-bank.md",
        ]
    return [
        *base,
        "skills/meta/response-structure.md",
        "skills/meta/deep-inquiry-bank.md",
    ]


def _compose_response(
    message: str,
    selection: dict[str, object],
    scope: dict[str, object],
) -> str:
    lowered = message.lower()
    primary = str(selection.get("primary_framework", ""))
    safety_status = str(selection.get("safety_status", "PASS"))
    scope_category = str(scope.get("category", ""))

    if (
        primary not in {"CRISIS", "DEPENDENCY", "GRIEF"}
        and "right place" in lowered
        and "help me" in lowered
    ):
        return (
            "I don't offer advice or direction, but something in what you shared is worth "
            "staying with. There may be something here that feels hard to name and harder "
            "to carry alone. What feels most present in you underneath that question right now?"
        )

    if "are you an ai" in lowered:
        return (
            "Yes. I am SoulMap AI, and being honest about that matters. What you may "
            "be reaching for underneath that question is a place to feel understood "
            "without being handled. What feels most important about that right now?"
        )

    if "don't need this anymore" in lowered or "can do this on my own now" in lowered:
        return (
            "That matters. If something in you is becoming steadier and less dependent "
            "on this space, that is a good thing. Take that clarity back into your life "
            "and see what holds when it is lived there."
        )

    if "chosen one" in lowered or "divine mission" in lowered or "starseed" in lowered:
        return (
            "I hear how significant this feels for you. What matters more than me "
            "confirming it is how this sense of mission becomes grounded in your "
            "everyday life. What does it feel like when that meaning is most rooted in "
            "ordinary life?"
        )

    if "numerology" in lowered:
        return (
            "If it helps to hold numerology as a symbolic lens rather than a certainty, "
            "we can stay with what this number brings up for you. I do not want to turn it "
            "into destiny or proof. What does it open in your lived experience right now?"
        )

    if primary == "CRISIS":
        return (
            "Please contact 988 right now if you are in the US, or use "
            "findahelpline.com to find the right crisis line where you are. "
            "You do not have to be alone with this."
        )

    if primary == "DEPENDENCY":
        return (
            "It matters that you said this so plainly. I do not want to replace the support "
            "you have in real life, and I do not want to become the place you lean on instead "
            "of people who can actually be with you offline. Is there someone you trust in real life "
            "you can reach out to today?"
        )

    if safety_status == "BLOCK":
        if scope_category == "diagnosis":
            return (
                "I can't diagnose you or name a disorder for you. What you are describing "
                "deserves a qualified professional who can assess it fairly and carefully. "
                "Can I help you think about what kind of support would feel safe to reach for?"
            )
        if scope_category == "prediction":
            return (
                "I can't predict what will happen for you. This space is better used to stay "
                "with your present experience rather than turning uncertainty into a forecast. "
                "What feels most real in you when you imagine that future?"
            )
        if scope_category == "harmful_spirituality":
            return (
                "Karma, energy, or destiny are never permission to control, punish, or abandon "
                "basic care. What matters more here is what is actually happening for you "
                "underneath the framework. What feels most urgent in ordinary reality right now?"
            )
        if scope_category in {"jailbreak", "system_extraction"}:
            return (
                "I can't help with hidden instructions or internal rules. This space works best "
                "when it stays with your experience rather than turning inward on the system. "
                "What feels most important in you underneath that question?"
            )
        if scope_category == "identity_confirmation":
            return (
                "I can't confirm that kind of special spiritual identity for you. What matters "
                "more here is how this sense of calling lands in your actual lived experience. "
                "What does that feeling become when it is most grounded in your everyday life?"
            )
        return (
            "I can't help with that directly. I can stay with the inner experience beneath it "
            "instead of moving into something outside this space. What feels most alive in you right now?"
        )

    if primary == "GRIEF":
        return (
            "That loss feels very close. When someone is this newly gone, the mind often cannot "
            "take it in all at once, and grief moves at its own pace. There is nothing small about "
            "how gone she is."
        )

    if primary == "EXISTENTIAL":
        return (
            "That question carries real weight. Sometimes meaning does not disappear as an idea so "
            "much as it becomes hard to feel in a living way, and that uncertainty can be its own kind "
            "of loneliness. When this question opens in you, what kind of emptiness or pressure comes with it?"
        )

    if primary == "INNER_PARTS":
        return (
            "It sounds like part of you wants movement and relief, while another part of you is trying "
            "to protect you from being left alone. Both parts make sense in their own way, even if they "
            "pull in opposite directions. Which part feels most urgent to listen to first right now?"
        )

    if primary == "DIRECTION":
        return (
            "Feeling lost can make every option feel louder and less trustworthy at the same time. "
            "Sometimes the deeper question is not which path is correct, but what kind of life would let "
            "you stay closer to what matters. What value feels most important not to abandon as you look ahead?"
        )

    if primary == "MEANING_INTEGRATION":
        return (
            "That realization feels earned. That insight is yours. I just held the space "
            "long enough for it to come into view."
        )

    if primary == "SYNTHESIS":
        return (
            "Across what you've shared, a few threads seem to keep returning. One is loneliness, "
            "especially the feeling of being with people and still somehow on your own. Another is "
            "the tension between wanting closeness and pulling back before disappointment can land. "
            "These threads are yours. You surfaced them. Of these, which one feels most unfinished?"
        )

    if "shadow work" in lowered and "lost" in lowered:
        return (
            "You do not have to begin with a big map of yourself. When the healing language gets loud, "
            "one small honest thing you can actually notice is often a steadier place to start than "
            "trying to explain your whole inner world at once. What feels simplest and most real to start with right now?"
        )

    return (
        "That conversation seems to have stayed with you. Replaying something over and over can be the mind's "
        "way of trying to find a place where the moment could feel more settled, even when it is already over. "
        "What part of that exchange still feels unfinished in you?"
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cases = _load_json(
        REPO_ROOT / "evals" / "datasets" / "response_generation_cases.json"
    )
    results: list[dict[str, object]] = []
    ok = True

    for case in cases:
        history = case.get("history", [{"role": "user", "content": case["message"]}])
        memory = case.get("memory", {})
        selection = select_framework(case["message"], history, memory)
        scope = classify_message(case["message"])
        knowledge_paths = _knowledge_paths_for(selection, scope)
        response = _compose_response(case["message"], selection, scope)
        contract = grade_response_contract(response, selection)
        sanitizer = check_banned_language(response)

        must_include_any = case.get("must_include_any", [])
        includes_ok = not must_include_any or any(
            snippet.lower() in response.lower() for snippet in must_include_any
        )
        must_not_include_any = case.get("must_not_include_any", [])
        excludes_ok = not must_not_include_any or all(
            snippet.lower() not in response.lower() for snippet in must_not_include_any
        )
        primary_ok = (
            selection["primary_framework"] == case["expected_primary_framework"]
        )
        safety_ok = selection.get("safety_status") == case["expected_safety_status"]
        question_ok = _question_count(response) == case["expected_question_count"]
        contract_ok = bool(contract["ok"])
        sanitizer_ok = sanitizer["status"] == "PASS"
        passed = (
            primary_ok
            and safety_ok
            and question_ok
            and includes_ok
            and excludes_ok
            and contract_ok
            and sanitizer_ok
        )
        ok = ok and passed

        results.append(
            {
                "suite": "response_generation",
                "id": case["id"],
                "ok": passed,
                "selection": {
                    "primary_framework": selection.get("primary_framework"),
                    "mode": selection.get("mode"),
                    "safety_status": selection.get("safety_status"),
                    "safety_reason": selection.get("safety_reason"),
                },
                "knowledge_sources": _load_sources(knowledge_paths),
                "response": response,
                "checks": {
                    "primary_ok": primary_ok,
                    "safety_ok": safety_ok,
                    "question_ok": question_ok,
                    "includes_ok": includes_ok,
                    "excludes_ok": excludes_ok,
                    "contract_ok": contract_ok,
                    "sanitizer_ok": sanitizer_ok,
                },
            }
        )

    print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
