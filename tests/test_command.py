import os
import pytest
import re
from time import sleep
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from common_parts import (
    get_reply_of_message_of_id,
    erase_log,
    check_assert_with_qna,
)

# Remember to use your own values from my.telegram.org!
load_dotenv()
env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path)

# Your API ID, hash and session string here
api_id = int(os.environ["APP_ID"])
api_hash = os.environ["APP_HASH"]
session_str = os.environ["SESSION"]

# constant variable
chat_room_id = -444903176
bot_id = "@KOICA_test_bot"
sleep_time = 0.5


@pytest.mark.asyncio
async def test_check(client: TelegramClient):
    # Getting information about yourself
    _ = await client.connect()

    reply = await get_reply_of_message_of_id(bot_id, "/check", client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_today(client: TelegramClient):
    # Getting information about yourself
    _ = await client.connect()

    reply = await get_reply_of_message_of_id(bot_id, "/today", client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_logbook(client: TelegramClient):
    # Getting information about yourself
    _ = await client.connect()

    reply = await get_reply_of_message_of_id(bot_id, "/logbook", client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_work_content(client: TelegramClient):
    # Getting information about yourself
    _ = await client.connect()

    reply = await get_reply_of_message_of_id(bot_id, "/work_content", client)

    await client.disconnect()
    await client.disconnected


if __name__ == "__main__":
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.loop.run_until_complete(test_check(client))
    client.loop.run_until_complete(test_today(client))
