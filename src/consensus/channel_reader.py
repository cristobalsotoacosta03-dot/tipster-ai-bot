"""
Reads recent messages from configured public Telegram channels, using a
real user account (Telethon) instead of the bot's own token - the bot API
can't read channels it wasn't added to, but a public channel is readable
by any Telegram user, same as opening the app and scrolling.

Not connected to real Telegram in tests: `client` is injected so tests can
pass a fake with the same async interface, and this module never touches
the network on its own.
"""
from dataclasses import dataclass
from typing import List, Optional, Protocol

import logging

logger = logging.getLogger(__name__)


class ConsensusTelegramClient(Protocol):
    """The subset of telethon.TelegramClient's async interface this module
    needs - lets tests pass a lightweight fake instead of a real client."""

    async def get_messages(self, entity: str, limit: int) -> list:
        ...


@dataclass
class ChannelMessage:
    channel: str
    text: str


async def read_recent_messages(
    client: ConsensusTelegramClient,
    channels: List[str],
    limit_per_channel: int = 20,
) -> List[ChannelMessage]:
    """
    Fetch the last `limit_per_channel` messages from each configured
    channel. Errors on one channel (e.g. it went private, or was
    mistyped) are logged and skipped rather than aborting the whole read -
    a single bad channel in the list shouldn't take down consensus for
    every match.
    """
    results: List[ChannelMessage] = []

    for channel in channels:
        try:
            raw_messages = await client.get_messages(channel, limit=limit_per_channel)
        except Exception as e:
            logger.warning(f"Could not read channel '{channel}': {e}")
            continue

        for msg in raw_messages:
            text = getattr(msg, "text", None) or getattr(msg, "message", None)
            if text:
                results.append(ChannelMessage(channel=channel, text=text))

    return results


def build_telethon_client(api_id: str, api_hash: str, session_string: str):
    """
    Construct a real Telethon client from the credentials in .env. Not
    called anywhere yet - this is the one function that will need a real
    TELEGRAM_CONSENSUS_SESSION to exercise, so it's kept separate from
    read_recent_messages (which is fully unit-testable without Telethon
    installed even being relevant).
    """
    from telethon import TelegramClient
    from telethon.sessions import StringSession

    return TelegramClient(StringSession(session_string), int(api_id), api_hash)
