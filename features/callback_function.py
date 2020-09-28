import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.data_management import (
    create_connection,
    select_all_log,
    write_csv,
)
from features.log import log_info
from features.function import update_location, update_work_type, set_log_basic

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@log_info()
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")
    context.user_data["status"] = "START"


@log_info()
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


@log_info()
def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    conn = create_connection("db.sqlite3")
    record = select_all_log(conn)
    conn.close()
    write_csv(record)
    update.message.reply_document(document=open("signing.csv", "rb"))


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
    context.user_data["type"] = "signing in"
    context.user_data["status"] = "SIGN_IN_WITH_WORKTYPE"

    # send Private message to update
    try:
        text_message = f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [["Office", "Home"], ]
        bot.send_message(
            chat_id=user.id,
            text=text_message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

    except Unauthorized:
        update.effective_message.reply_text(
            "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
        )


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
    context.user_data["type"] = "signing out"
    context.user_data["status"] = "SIGN_OUT_WITH_LOCATION"

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


@log_info()
def set_location(update, context):
    user_data = context.user_data
    user_location = update.message.location

    update_location(
        user_data["log_id"],
        user_location.longitude,
        user_location.latitude,
    )

    update.message.reply_text(
        f"longitude: {user_location.longitude}, latitude: {user_location.latitude} has been logged.\
    Good bye!",
        reply_markup=ReplyKeyboardRemove(),
    )


@log_info()
def set_work_type(update, context):
    """Get Work type"""
    # save log work type data
    update_work_type(context.user_data["log_id"], update.message.text)

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


@log_info()
def cancel(update, context):
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def connect_message_status(update, context):
    status = context.user_data.get("status")
    call_back = None

    callback_dict = {
        "SIGN_IN_WITH_WORKTYPE": (set_work_type, "SIGN_IN_WITH_LOCATION"),
        "SIGN_IN_WITH_LOCATION": (set_location, None)
    }

    if callback_dict.get(status):
        call_back, next_status = callback_dict.get(status)

    if call_back:
        call_back(update, context)
        context.user_data["status"] = next_status
