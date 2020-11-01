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
async def test_get_back_check(client: TelegramClient):
    # Getting information about yourself

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
    await get_reply_of_message_of_id(chat_room_id, "back to work", client)
    reply = await get_reply_of_message_of_id(bot_id, "", client)
    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)
        await erase_log(bot_id, str(log_id), client)


@pytest.mark.asyncio
async def test_get_back_first(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself

    # ...Get back Test
    await get_reply_of_message_of_id(chat_room_id, "back to work", client)

    reply = await get_reply_of_message_of_id(bot_id, "", client)
    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)
        print(log_id)
    # conversation
    async with client.conversation(bot_id) as conv:

        sleep(sleep_time)

        qna = [
            ("Without any member of KOICA", "I see"),
            ("Not Available", "You have gotten back as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)


@pytest.mark.asyncio
async def test_get_back_rewrite(client: TelegramClient):

    sleep(sleep_time)
    # ...Get back Test
    reply = await get_reply_of_message_of_id(chat_room_id, "back to work", client)

    reply = await get_reply_of_message_of_id(bot_id, "", client)
    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)
    sleep(sleep_time)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        qna = [
            (
                "Delete and Get Back to Work Again",
                "Do you really want to do remove log No.",
            ),
            ("REMOVE GET BACK LOG", "has been Deleted"),
        ]

        await check_assert_with_qna(qna, conv)

        response = await conv.get_response()
        print(response.text)
        assert "Did you have lunch with KOICA Colleauge" in response.text

        qna = [
            ("With KOICA Colleagues", "I see"),
            ("Not Available", "You have gotten back as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)

    # earase log after use
    await erase_log(bot_id, str(log_id), client)


@pytest.mark.asyncio
async def test_get_back_edit(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself

    # ...Get back Test
    reply = await get_reply_of_message_of_id(chat_room_id, "back to work", client)
    reply = await get_reply_of_message_of_id(bot_id, "", client)
    m = re.search(r"Log No.(\d+)", reply)
    log_id = m.group(1)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        qna = [
            ("With KOICA Colleagues", "I see"),
            ("Not Available", "You have gotten back as below"),
            ("Edit", "Did you have lunch with KOICA Colleauge"),
            ("With KOICA Colleagues", "I see"),
            ("Not Available", "You have gotten back as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)

        # earase log after use
        await erase_log(bot_id, str(log_id), client)


if __name__ == "__main__":
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.connect()
    client.loop.run_until_complete(test_get_back_check(client))
    client.loop.run_until_complete(test_get_back_first(client))
    client.loop.run_until_complete(test_get_back_rewrite(client))
    client.disconnect()
    client.disconnecte
