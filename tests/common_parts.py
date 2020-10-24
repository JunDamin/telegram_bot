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
    if message:
        await conv.send_message(message)
    response = await conv.get_response()
    print(response.text)
    sleep(sleep_time)
    return response.raw_text


async def get_reply_of_message_of_id(id, message: str, client: TelegramClient):
    """
    ----
    param id: telegram id for sending message
    param message: str you want to send in conversation
    param client: client which you want to use
    return : text message of response of the message
    """
    if message:
        message = await client.send_message(id, message)
        print("send message")
        message_id = message.id
    else:
        message_id = None

    while True:
        (message,) = await client.get_messages(id)
        if message_id != message.id:
            break
        else:
            print(message_id, message.id)
            sleep(sleep_time)
    print(message.text)
    sleep(sleep_time)
    return message.raw_text


async def erase_log(chat_id, log_id, client: TelegramClient):
    await get_reply_of_message_of_id(chat_id, "/로그삭제", client)
    await get_reply_of_message_of_id(chat_id, str(log_id), client)
    await get_reply_of_message_of_id(chat_id, "YES", client)
    sleep(sleep_time)


async def check_assert_with_qna(qna: list, conv: TelegramClient.conversation):

    for q, a in qna:
        reply = await get_reply_of_message_in_conv(q, conv)
        print(f"q: {q}, reply: {reply}, a: {a}")
        assert a in reply
