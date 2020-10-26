from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode


def send_markdown(update, context, user_id, text_message, reply_keyboard=False):

    text_message = text_message.replace(".", "\\.")
    text_message = text_message.replace("-", "\\-")

    context.bot.send_message(
        chat_id=user_id,
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        if reply_keyboard
        else ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def reply_markdown(update, context, text_message, reply_keyboard=False):

    text_message = convert_text_to_md(text_message)

    update.message.reply_markdown_v2(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        if reply_keyboard
        else ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def convert_text_to_md(text):
    convert_dict = {
        ".": "\\.",
        "-": "\\-",
        "!": "\\!",
        "(": "\\(",
        ")": "\\)",
        "+": "\\+",
    }
    for key in convert_dict:
        text = text.replace(key, convert_dict[key])

    return text
