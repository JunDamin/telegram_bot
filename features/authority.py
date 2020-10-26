def private_only(func):
    def wrapper(*args, **kwargs):
        chat_type = args[0].message.chat.type
        if chat_type == "private":
            return func(*args, **kwargs)
        else:
            args[0].message.reply_text("please send me as DM(Direct Message)")

    return wrapper


def public_only(func):
    def wrapper(*args, **kwargs):
        chat_type = args[0].message.chat.type
        print(chat_type)
        if chat_type == "group":
            return func(*args, **kwargs)
        else:
            args[0].message.reply_text("please send in the group chat")

    return wrapper


def self_only(func):
    def wrapper(*args, **kwargs):
        user = args[0].message.from_user
        chat_id = int(args[1].user_data.get("chat_id"))
        print(user.id, chat_id)
        if user.id == chat_id:
            return func(*args, **kwargs)
        else:
            args[0].message.reply_text("You can not access others data")

    return wrapper
