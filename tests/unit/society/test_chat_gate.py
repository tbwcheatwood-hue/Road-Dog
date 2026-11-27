"""Front-page chat keeps society hands off until the switch is flipped."""

from __future__ import annotations

import jarvis.society.chat_gate as chat_gate


def test_chat_is_off_and_a_spoken_turn_is_not() -> None:
    assert chat_gate.chat_offers_society() is False
    assert chat_gate.chat_turn_hides_society("agent-chat") is True
    assert chat_gate.chat_turn_hides_society("society") is False
    assert chat_gate.chat_turn_hides_society(None) is False


def test_only_society_hands_match() -> None:
    assert chat_gate.is_society_hand("society-create-agent")
    assert chat_gate.is_society_hand("society_status")
    assert chat_gate.is_society_hand("delegate_to_agent")
    assert chat_gate.is_society_hand("message-agent")
    assert chat_gate.is_society_hand("search_web") is False
    assert chat_gate.is_society_hand("spawn_worker") is False


def test_drop_keeps_everything_else() -> None:
    tools = {
        "search_web": object(),
        "society-create-agent": object(),
        "delegate-to-agent": object(),
        "Read": object(),
    }
    kept = chat_gate.drop_society_hands(tools)
    assert sorted(kept) == ["Read", "search_web"]
