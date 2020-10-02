import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    check_status,
    update_location,
    update_sub_category,
    set_log_basic,
)


# Sign in
HANDLE_WORKPLACE, HANDLE_SIGN_IN_LOCATION = range(2)


# Sign in Conv
@log_info()
def start_signing_in(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user
    log_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing in",
    )
    log_id = set_log_basic(log_basic)
    SIGN_IN_GREETING = f"""Good morning, {user.first_name}.\n
You have been signed in with Log No. {log_id}"""
    SIGN_TIME = f"""signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"""
    ASK_INFO = """Would you like to share where you work?"""
    CHECK_DM = """"Please check my DM(Direct Message) to you"""

    # check if the chat is group or not
    if update.message.chat.type == "group":
        text_message = f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
        update.message.reply_text(text=text_message)

    # set status
    context.user_data["log_id"] = log_id
    context.user_data["category"] = "signing in"
    context.user_data["status"] = "SIGN_IN"

    # send Private message to update
    try:
        text_message = f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [
            ["Office", "Home"],
        ]
        bot.send_message(
            chat_id=user.id,
            text=text_message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

    except Unauthorized:
        update.effective_message.reply_text(
            "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
        )

    return HANDLE_WORKPLACE


@log_info()
def set_sub_category(update, context):
    """Get sub category"""
    # save log work type data
    if check_status(context, "SIGN_IN"):
        update_sub_category(context.user_data["log_id"], update.message.text)

        keyboard = [
            [
                KeyboardButton("Share Location", request_location=True),
            ],
        ]

        update.message.reply_text(
            """I see! Please send me your location by click the button on your phone.
    (Desktop app can not send location)""",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
    return HANDLE_SIGN_IN_LOCATION


@log_info()
def set_sign_in_location(update, context):
    user_data = context.user_data
    user_location = update.message.location

    if user_location:
        update_location(
            user_data.get("log_id"),
            user_location.longitude,
            user_location.latitude,
        )

        update.message.reply_text(
            f"longitude: {user_location.longitude}, latitude: {user_location.latitude} has been logged.\
        Good bye!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    else:
        keyboard = [
            [
                KeyboardButton("Share Location", request_location=True),
            ],
        ]

        update.message.reply_text(
            """Something went wrong. Please send again me your location by click the button on your phone.
    (Desktop app can not send location)""",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )

        return ConversationHandler.END
