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
async def test_edit_check(client: TelegramClient):
    # Getting information about yourself
    _ = await client.connect()

    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        print(dialog.name, "has ID", dialog.id)

    # ... get back Test
    await get_reply_of_message_of_id(bot_id, "SKIP", client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_edit(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Edit Test
    reply = await get_reply_of_message_of_id(bot_id, "/edit", client)
    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)
        print(log_id)
    # conversation
    async with client.conversation(bot_id) as conv:

        sleep(sleep_time)

        qna = [
            (log_id, "Do you really want to do edit log"),
            ("YES", "start to edit Log"),
            ("SKIP", "Bye"),
        ]

        await check_assert_with_qna(qna, conv)

    await client.disconnect()
    await client.disconnected


if __name__ == "__main__":
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.loop.run_until_complete(test_edit_check(client))
    client.loop.run_until_complete(test_edit(client))
