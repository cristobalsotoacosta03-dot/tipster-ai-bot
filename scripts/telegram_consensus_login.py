"""
One-time interactive login for the Telegram "consensus" reader.

This is NOT the bot (TELEGRAM_BOT_TOKEN) - it logs in as a real user account
(via Telethon) so it can read public channels the bot could never join on
its own. Run this yourself, locally, once:

    pip install telethon
    python scripts/telegram_consensus_login.py

You'll be asked for:
1. Your phone number (the one you registered the secondary/work Telegram
   account with) - international format, e.g. +34600000000
2. The login code Telegram sends you (via the Telegram app itself, or SMS)
3. Your 2FA password, only if you have two-step verification enabled

At the end it prints a session string. Copy it into your .env as:

    TELEGRAM_CONSENSUS_SESSION=<the printed string>

That session string is a credential - treat it like a password. Never
commit it, never paste it anywhere public. With it, the deployed bot can
read the configured public channels without asking you to log in again.
"""
import asyncio
import os

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = os.environ.get("TELEGRAM_CONSENSUS_API_ID") or input("api_id: ").strip()
API_HASH = os.environ.get("TELEGRAM_CONSENSUS_API_HASH") or input("api_hash: ").strip()


async def main():
    async with TelegramClient(StringSession(), int(API_ID), API_HASH) as client:
        session_string = client.session.save()
        me = await client.get_me()
        print(f"\nLogged in as: {me.first_name} (@{me.username or 'sin username'})")
        print("\n=== Guarda esto en tu .env como TELEGRAM_CONSENSUS_SESSION ===")
        print(session_string)
        print("=== No lo compartas ni lo subas a git ===\n")


if __name__ == "__main__":
    asyncio.run(main())
