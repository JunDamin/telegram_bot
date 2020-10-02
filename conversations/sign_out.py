import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    update_location,
    set_log_basic,
)

# Sign out
(HANDLE_SIGN_OUT_LOCATION,) = map(chr, range(2, 3))


# Sign out conv
@log_info()
def start_signing_out(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user
    log_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing out",
    )
    log_id = set_log_basic(log_basic)

    SIGN_OUT_GREETING = (
        f"""Good evening, {user.first_name}.\nYou have been signed out today."""
    )
    SIGN_TIME = f"signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"
    ASK_INFO = "Please share your location infomation."
    CHECK_DM = """"Please check my DM(Direct Message) to you"""
    text_message = f"{SIGN_OUT_GREETING}/n{SIGN_TIME}"

    if update.message.chat.type == "group":
        text_message = f"{SIGN_OUT_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
        update.message.reply_text(text=text_message)

    # set status
    context.user_data["log_id"] = log_id
    context.user_data["category"] = "signing out"
    context.user_data["status"] = "SIGN_OUT"

    try:
        text_message = f"{SIGN_OUT_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [
            [
                KeyboardButton(
                    """Share location infomation for signing out""",
                    request_location=True,
                ),
            ]
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

    return HANDLE_SIGN_OUT_LOCATION


@log_info()
def set_sign_out_location(update, context):
    user_data = context.user_data
    user_location = update.message.location
    if user_data.get('status') != "SIGN_OUT":
        return ConversationHandler.END

    if user_location:
        update_location(
            user_data["log_id"],
            user_location.longitude,
            user_location.latitude,
        )

        update.message.reply_text(
            f"longitude: {user_location.longitude}, latitude: {user_location.latitude} has been logged.\nGood bye!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return True
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
