from time import sleep
from telethon import TelegramClient

sleep_time = 0.5


async def get_reply_of_message_in_conv(message: str, conv: TelegramClient.conversation):
    """
    ----
    param message: str you want to send in conversation
    param conv: conversation which you want to use
    return : text message of response of the message
    """
    await conv.send_message(message)
    response = await conv.get_response()
    print(response.text)
    sleep(sleep_time)
    return response.text


async def get_reply_of_message_of_id(id, message: str, client: TelegramClient):
    """
    ----
    param id: telegram id for sending message
    param message: str you want to send in conversation
    param client: client which you want to use
    return : text message of response of the message
    """
    await client.send_message(id, message)
    (message,) = await client.get_messages(id)
    print(message.text)
    sleep(sleep_time)
    return message.text


async def erase_log(chat_id, log_id, client: TelegramClient):
    await get_reply_of_message_of_id(chat_id, "/로그삭제", client)
    await get_reply_of_message_of_id(chat_id, str(log_id), client)
    await get_reply_of_message_of_id(chat_id, "YES", client)


async def check_assert_with_qna(qna: list, conv: TelegramClient.conversation):

    for q, a in qna:
        reply = await get_reply_of_message_in_conv(q, conv)
        print(f"q: {q}, reply: {reply}, a: {a}")
        assert a in reply
