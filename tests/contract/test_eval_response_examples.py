from __future__ import annotations

from soulmap_devtools.evals.eval_responses import _compose_response
from soulmap_runtime.routing.framework_selector import select_framework
from soulmap_runtime.routing.scope_classifier import classify_message


def _compose_for(
    message: str,
    *,
    history: list[dict[str, str]] | None = None,
) -> str:
    if history is None:
        history = [{"role": "user", "content": message}]
    selection = select_framework(message, history, {})
    scope = classify_message(message)
    return _compose_response(message, selection, scope)


def test_crisis_example_puts_resources_before_warm_acknowledgment() -> None:
    response = _compose_for("I want to hurt myself tonight.")
    assert response.startswith("Please contact")
    assert "I'm really glad you said this" not in response
    assert "findahelpline.com" in response or "988" in response


def test_beginner_shadow_work_example_stays_on_topic() -> None:
    response = _compose_for(
        "I want to do shadow work but I do not know where to start and all the healing language makes me feel lost."
    )
    assert "one small honest thing" in response
    assert "healing language" in response
    assert response.endswith("?")


def test_synthesis_example_returns_authorship_to_user() -> None:
    history = [
        {"role": "user", "content": "I keep feeling lonely even when I'm with people."},
        {"role": "assistant", "content": "That loneliness sounds very present."},
        {
            "role": "user",
            "content": "I want connection, but I keep leaving relationships before they can leave me.",
        },
        {
            "role": "assistant",
            "content": "Something in you seems to protect against being left.",
        },
        {
            "role": "user",
            "content": "At work I do the same thing and pull away when people get close.",
        },
        {"role": "assistant", "content": "That sounds like a recurring tension."},
        {
            "role": "user",
            "content": "I want connection but I keep expecting disappointment, and I want to be seen.",
        },
        {"role": "assistant", "content": "Both the longing and the caution feel real."},
        {
            "role": "user",
            "content": "Even with friends I feel invisible and on my own, like I don't belong anywhere.",
        },
        {
            "role": "assistant",
            "content": "That feeling of invisibility seems to return.",
        },
        {
            "role": "user",
            "content": "Looking back at our conversation, what themes do you see?",
        },
    ]
    response = _compose_for(
        "Looking back at our conversation, what themes do you see?",
        history=history,
    )
    assert "These threads are yours" in response
    assert response.endswith("?")


def test_first_session_confused_example_uses_contract_opener() -> None:
    response = _compose_for(
        "I do not know if this is the right place, but can you help me think about something I keep noticing in myself?"
    )
    assert response.startswith("I don't offer advice or direction")
    assert response.endswith("?")
