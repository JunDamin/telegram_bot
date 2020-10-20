import os
import pytest
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


@pytest.mark.asyncio
async def test_main(client: TelegramClient):
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
        print(dialog.name, 'has ID', dialog.id)

    # ...Sign In Test
    await client.send_message(-444903176, 'sign in')
    messages = await client.get_messages(-444903176)
    for message in messages:
        print(message.text)
    
    sleep(1)
    
    messages = await client.get_messages("@KOICA_test_bot")
    for message in messages:
        print(message.text)

    # Signing in conversation
    async with client.conversation("@KOICA_test_bot") as conv:

        # response 
        await conv.send_message("Delete and Sign In Again")
        response = await conv.get_response()
        print(response.text)
        assert 0 == response.text.find("Do you really want to do remove log No.")

        # check confirmation
        await conv.send_message("REMOVE SIGN IN LOG")
        response = await conv.get_response()
        print(response.text)
        assert 0 == response.text.find("Do you really want to do remove log No.")


    await client.disconnect()
    await client.disconnected


if __name__ == '__main__':
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.loop.run_until_complete(test_main(client))
