import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    check_status,
    update_sub_category,
    set_log_basic,
    get_today_log_of_chat_id_category,
    make_text_from_logbook,
    set_location,
)
from features.data_management import create_connection, select_log, delete_log


# Sign in status
(
    HANDLE_WORKPLACE,
    HANDLE_LOG_DELETE,
    HANDLE_SIGN_IN_LOCATION,
) = ["sign_in" + str(i) for i in range(3)]


# Sign in Conv
@log_info()
def start_signing_in(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user

    basic_user_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "datetime": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "category": "signing in",
    }
    for key in basic_user_data:
        context.user_data[key] = basic_user_data[key]

    rows = get_today_log_of_chat_id_category(
        basic_user_data["user_id"], basic_user_data["category"]
    )

    if not rows:
        log_id = set_log_basic(
            tuple(
                basic_user_data[key]
                for key in (
                    "user_id",
                    "first_name",
                    "last_name",
                    "datetime",
                    "category",
                )
            )
        )

        SIGN_IN_GREETING = f"""Good morning, {user.first_name}.\nYou have been signed in with Log No. {log_id}"""
        SIGN_TIME = f"""signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"""
        ASK_INFO = """Would you like to share where you work?"""
        CHECK_DM = """"Please check my DM(Direct Message) to you"""

        # check if the chat is group or not
        if update.message.chat.type == "group":
            text_message = f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
            update.message.reply_text(text=text_message)

        # set status
        context.user_data["log_id"] = log_id
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
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                ),
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
            )

        return HANDLE_WORKPLACE
    else:
        record = rows[0]
        log_id = record[0]
        context.user_data["log_id"] = log_id
        context.user_data["status"] = "SIGN_IN"
        try:
            message = "You have already signed in as below. "
            text_message = make_text_from_logbook(rows, message)

            update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())

            text_message += "\nDo you want to edit it? or SKIP it?"
            reply_keyboard = [
                ["Delete and Sign In Again", "SKIP"],
            ]
            bot.send_message(
                chat_id=user.id,
                text=text_message,
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                ),
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
            )


@log_info()
def ask_confirmation_of_removal(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        context.user_data["remove_log_id"] = log_id
        keyboard = [["REMOVE SIGN IN LOG", "NO"]]

        conn = create_connection()
        row = select_log(conn, log_id)
        conn.close()

        header_message = f"Do you really want to do remove log No.{log_id}?\n"
        text_message = make_text_from_logbook(row, header_message)

        update.message.reply_text(
            text_message,
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
        return HANDLE_LOG_DELETE
    else:
        text_message = "An Error has been made. Please try again."
        update.message.reply_text(text=text_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def override_log(update, context):

    choices = {"REMOVE SIGN IN LOG": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = context.user_data.get("log_id")

        conn = create_connection()
        delete_log(conn, log_id)
        conn.close()

        text_message = f"Log No. {log_id} has been Deleted\n"
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    else:
        text_message = "process has been stoped. The log has not been deleted."
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    log_id = set_log_basic(
        tuple(
            context.user_data.get(key)
            for key in (
                "user_id",
                "first_name",
                "last_name",
                "datetime",
                "category",
            )
        )
    )
    result = ask_sub_category(update, context)

    return result


def ask_sub_category(update, context):

    text_message = (
        "Would you like to share where you work?"
    )
    reply_keyboard = [
        ["Office", "Home"],
    ]
    update.message.reply_text(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
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
    (1. Please turn on your location service of your phone.
    2. Desktop app can not send location)""",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
    return HANDLE_SIGN_IN_LOCATION


@log_info()
def set_sign_in_location(update, context):
    HEADER_MESSAGE = "You have signed in as below."
    set_location(update, context, HEADER_MESSAGE, ConversationHandler.END)
    context.user_data.pop("status")
    return ConversationHandler.END
