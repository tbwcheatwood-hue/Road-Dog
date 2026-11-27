"""Society hands on the front-page chat.

Off until that chat needs the team again. Flip ``ENABLED`` to put the
society tools and the team card back on the next chat turn. Society agent
chats and spoken turns are unchanged.
"""

from __future__ import annotations

ENABLED: bool = False

_EXACT = frozenset(
    {
        "delegate-to-agent",
        "message-agent",
    }
)


def chat_offers_society() -> bool:
    """Whether the front-page chat may see society tools and the team card."""
    return ENABLED


def chat_turn_hides_society(tool_origin: str | None) -> bool:
    """True on a front-page chat turn while the switch above is off."""
    return not ENABLED and (tool_origin or "") == "agent-chat"


def is_society_hand(name: str) -> bool:
    """A society command or one of the lead's three society tools."""
    folded = (name or "").strip().lower().replace("_", "-")
    return folded.startswith("society-") or folded in _EXACT


def drop_society_hands(tools: dict) -> dict:
    """The same map without society hands. Other tools stay."""
    return {name: tool for name, tool in tools.items() if not is_society_hand(name)}
