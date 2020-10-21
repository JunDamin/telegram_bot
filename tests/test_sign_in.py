import os
import pytest
import re
from time import sleep
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

# Remember to use your own values from my.telegram.org!
load_dotenv()
env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path)

# Your API ID, hash and session string here
api_id = int(os.environ["APP_ID"])
api_hash = os.environ["APP_HASH"]
session_str = os.environ["SESSION"]
chat_room_id = -444903176
bot_id = "@KOICA_test_bot"
sleep_time = 0.5


@pytest.mark.asyncio
async def test_sign_in_check(client: TelegramClient):
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

    # ...Sign In Test
    await client.send_message(bot_id, "SKIP")
    messages = await client.get_messages(bot_id)
    for message in messages:
        print(message.text)

    await client.send_message(chat_room_id, "sign in")
    messages = await client.get_messages(chat_room_id)
    for message in messages:
        print(message.text)
    sleep(sleep_time)

    messages = await client.get_messages(bot_id)
    for message in messages:
        print(message.text)
        m = re.search(r"Log No.(\d+)", message.text)
        if m:
            log_id = m.group(1)
    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        if m:
            # Erase log
            await conv.send_message("/로그삭제")
            response = await conv.get_response()
            print(response.text)

            sleep(sleep_time)

            await conv.send_message(str(log_id))
            response = await conv.get_response()
            print(response.text)

            sleep(sleep_time)

            await conv.send_message("YES")
            response = await conv.get_response()
            print(response.text)

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_sign_in_first(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Sign In Test
    await client.send_message(chat_room_id, "sign in")
    messages = await client.get_messages(chat_room_id)
    for message in messages:
        print(message.text)

    sleep(sleep_time)

    messages = await client.get_messages(bot_id)
    for message in messages:
        print(message.text)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        sleep(sleep_time)

        # reply sub-category
        await conv.send_message("Office")
        response = await conv.get_response()
        print(response.text)
        assert "I see" in response.text

        sleep(sleep_time)

        # reply location
        await conv.send_message("DEROUTE")
        response = await conv.get_response()
        print(response.text)
        assert "You have signed in as below. Do you want to confirm" in response.text

        sleep(sleep_time)

        await conv.send_message("Confirm")
        response = await conv.get_response()
        print(response.text)
        assert "Confirmed" in response.text

    await client.disconnect()
    await client.disconnected


@pytest.mark.asyncio
async def test_sign_in_rewrite(client: TelegramClient):

    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Sign In Test
    await client.send_message(chat_room_id, "sign in")
    messages = await client.get_messages(chat_room_id)
    for message in messages:
        print(message.text)

    sleep(sleep_time)

    messages = await client.get_messages(bot_id)
    for message in messages:
        print(message.text)

    sleep(sleep_time)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        # response
        await conv.send_message("Delete and Sign In Again")
        response = await conv.get_response()
        print(response.text)
        assert "Do you really want to do remove log No." in response.text

        sleep(sleep_time)

        # check confirmation
        await conv.send_message("REMOVE SIGN IN LOG")
        response = await conv.get_response()
        print(response.text)
        assert "Log No." in response.text
        assert "has been Deleted" in response.text

        sleep(sleep_time)

        response = await conv.get_response()
        print(response.text)
        assert "Would you like to share where you work" in response.text

        sleep(sleep_time)

        # check confirmation
        await conv.send_message("Office")
        response = await conv.get_response()
        print(response.text)
        assert "I see! Please send me your location by click" in response.text

        sleep(sleep_time)

        # get location
        await conv.send_message("DEROUTE")
        response = await conv.get_response()
        print(response.text)
        assert "You have signed in as below" in response.text

        sleep(sleep_time)

        log_id = re.search(r"Log No.(\d+)", response.text).group(1)
        print(log_id)
        await conv.send_message("Confirm")
        response = await conv.get_response()
        print(response.text)

        sleep(sleep_time)

        # Erase log
        await conv.send_message("/로그삭제")
        response = await conv.get_response()
        print(response.text)
        await conv.send_message(str(log_id))
        response = await conv.get_response()
        print(response.text)
        await conv.send_message("YES")
        response = await conv.get_response()
        print(response.text)

    await client.disconnect()
    await client.disconnected



@pytest.mark.asyncio
async def test_sign_in_edit(client: TelegramClient):
    sleep(sleep_time)
    # Getting information about yourself
    _ = await client.connect()

    # ...Sign In Test
    await client.send_message(chat_room_id, "sign in")
    messages = await client.get_messages(chat_room_id)
    for message in messages:
        print(message.text)

    sleep(sleep_time)

    messages = await client.get_messages(bot_id)
    for message in messages:
        print(message.text)

    # Signing in conversation
    async with client.conversation(bot_id) as conv:

        sleep(sleep_time)

        # reply sub-category
        await conv.send_message("Office")
        response = await conv.get_response()
        print(response.text)
        assert "I see" in response.text

        sleep(sleep_time)

        # reply location
        await conv.send_message("DEROUTE")
        response = await conv.get_response()
        print(response.text)
        assert "You have signed in as below. Do you want to confirm" in response.text

        sleep(sleep_time)

        # Edit
        await conv.send_message("Edit")
        response = await conv.get_response()
        print(response.text)


        # reply sub-category
        await conv.send_message("Office")
        response = await conv.get_response()
        print(response.text)
        assert "I see" in response.text

        sleep(sleep_time)

        # reply location
        await conv.send_message("DEROUTE")
        response = await conv.get_response()
        print(response.text)
        assert "You have signed in as below. Do you want to confirm" in response.text

        sleep(sleep_time)

        # Confirmed
        await conv.send_message("Confirm")
        response = await conv.get_response()
        print(response.text)
        assert "Confirmed" in response.text


    await client.disconnect()
    await client.disconnected


if __name__ == "__main__":
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.loop.run_until_complete(test_sign_in_check(client))
    client.loop.run_until_complete(test_sign_in_first(client))
    client.loop.run_until_complete(test_sign_in_rewrite(client))
