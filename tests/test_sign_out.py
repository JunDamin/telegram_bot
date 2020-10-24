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
async def test_sign_out_check(client: TelegramClient):
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
    reply = await get_reply_of_message_of_id(bot_id, "SKIP", client)
    reply = await get_reply_of_message_of_id(chat_room_id, "sign out", client)
    reply = await get_reply_of_message_of_id(bot_id, "", client)

    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)
        await erase_log(bot_id, str(log_id), client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_sign_out_first(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Get back Test
    reply = await get_reply_of_message_of_id(chat_room_id, "sign out", client)
    m = re.search(r"Log No.(\d+)", reply)
    reply = await get_reply_of_message_of_id(bot_id, "", client)

    if m:
        log_id = m.group(1)
        print(log_id)

    # conversation
    async with client.conversation(bot_id) as conv:

        sleep(sleep_time)

        qna = [
            ("I worked at Office", "I see"),
            ("DEROUTE", "You have signed out as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_sign_out_rewrite(client: TelegramClient):

    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Get back Test
    reply = await get_reply_of_message_of_id(chat_room_id, "sign out", client)
    m = re.search(r"Log No.(\d+)", reply)
    log_id = m.group(1)

    reply = await get_reply_of_message_of_id(bot_id, "", client)

    sleep(sleep_time)
    # Signing Out conversation
    async with client.conversation(bot_id) as conv:

        qna = [
            ("Delete and Sign Out Again", "Do you really want to do remove log No."),
            ("REMOVE SIGN OUT LOG", "has been Deleted"),
        ]

        await check_assert_with_qna(qna, conv)

        response = await conv.get_response()
        print(response.text)
        assert "Would you like to share your today's content of work" in response.text

        qna = [
            (
                "I would like to report",
                "OK. Please text me what you have done",
            ),
            ("It is a test", "Content of Work"),
            ("YES", "I see"),
            ("DEROUTE", "You have signed out as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)

    # earase log after use
    await erase_log(bot_id, str(log_id), client)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_sign_out_edit(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Get back Test
    reply = await get_reply_of_message_of_id(chat_room_id, "sign out", client)
    m = re.search(r"Log No.(\d+)", reply)
    if m:
        log_id = m.group(1)

    reply = await get_reply_of_message_of_id(bot_id, "", client)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        qna = [
            (
                "I would like to report",
                "OK. Please text me what you have done",
            ),
            ("It is a test", "Content of Work"),
            ("YES", "I see"),
            ("DEROUTE", "You have signed out as below"),
            ("Edit", "Would you like to share your today's content of work"),
            ("I worked at Office", "I see"),
            ("DEROUTE", "You have signed out as below"),
            ("Confirm", "Confirmed"),
        ]

        await check_assert_with_qna(qna, conv)

        # earase log after use
        if m:
            await erase_log(bot_id, str(log_id), client)

    await client.disconnect()
    await client.disconnected


if __name__ == "__main__":
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.loop.run_until_complete(test_sign_out_check(client))
    client.loop.run_until_complete(test_sign_out_first(client))
    client.loop.run_until_complete(test_sign_out_rewrite(client))
