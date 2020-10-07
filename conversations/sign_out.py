import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    set_log_basic,
    set_location,
    get_today_log_of_chat_id_category,
    make_text_from_logbook,
    select_log_to_text,
)
from features.data_management import (
    create_connection,
    select_log,
    delete_log,
    update_log_confirmation,
)

# Sign out
(
    ANSWER_WORK_TYPE,
    ANSWER_WORK_CONTENT,
    ANSWER_CONTENT_CONFIRMATION,
    ANSWER_LOG_DELETE,
    ANSWER_SIGN_OUT_LOCATION,
    ANSWER_CONFIRMATION,
) = ["sign_out" + str(i) for i in range(6)]


# Sign out conv
@log_info()
def start_signing_out(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user

    basic_user_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "datetime": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "category": "signing out",
    }
    for key in basic_user_data:
        context.user_data[key] = basic_user_data[key]

    rows = get_today_log_of_chat_id_category(
        basic_user_data["user_id"], basic_user_data["category"]
    )

    if not rows:
        log_id = set_log_basic(
            tuple(
                basic_user_data[i]
                for i in ("user_id", "first_name", "last_name", "datetime", "category")
            )
        )

        SIGN_OUT_GREETING = (
            f"""Good evening, {user.first_name}.\nYou have been signed out today."""
        )
        SIGN_TIME = f"signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"
        ASK_INFO = "Would you like to share your today's content of work?"
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
            reply_keyboard = [["I worked at Office", "I would like to report"]]
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

        return ANSWER_WORK_TYPE

    else:
        record = rows[0]
        log_id = record[0]
        context.user_data["log_id"] = log_id
        context.user_data["status"] = "SIGN_OUT"
        try:
            message = "You have already signed out as below. "
            text_message = make_text_from_logbook(rows, message)

            update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())

            text_message += "\nDo you want to delete it and sign out again? or SKIP it?"
            reply_keyboard = [
                ["Delete and Sign Out Again", "SKIP"],
            ]
            bot.send_message(
                chat_id=user.id,
                text=text_message,
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                ),
            )
            return ANSWER_SIGN_OUT_LOCATION

        except Unauthorized:
            update.effective_message.reply_text(
                "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
            )


@log_info()
def ask_confirmation_of_removal(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        context.user_data["remove_log_id"] = log_id
        keyboard = [["REMOVE SIGN OUT LOG", "NO"]]

        conn = create_connection()
        row = select_log(conn, log_id)
        conn.close()

        header_message = f"Do you really want to do remove log No.{log_id}?\n"
        text_message = make_text_from_logbook(row, header_message)

        update.message.reply_text(
            text_message,
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
        return ANSWER_LOG_DELETE
    else:
        text_message = "An Error has been made. Please try again."
        update.message.reply_text(text=text_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def override_log(update, context):

    choices = {"REMOVE SIGN OUT LOG": True, "NO": False}
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
    return ask_work_type(update, context)


def ask_sign_out_location(update, text):
    text_message = """I see! Please send me your location by click the button on your phone.
    1. Please check your location service is on./n(if not please turn on your location service)
    2. Desktop app can not send location"""
    reply_keyboard = [
        [
            KeyboardButton(
                """Share location infomation for signing out""",
                request_location=True,
            ),
        ]
    ]
    update.message.reply_text(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ANSWER_SIGN_OUT_LOCATION


@log_info()
def set_sign_out_location(update, context):
    user_data = context.user_data
    HEADER_MESSAGE = "You have signed out as below. Do you want to confirm?"
    if set_location(update, context):
        text_message = HEADER_MESSAGE
        keyboard = ReplyKeyboardMarkup([["Confirm", "Edit"]], one_time_keyboard=True)
        text_message += select_log_to_text(user_data.get("log_id"))
        update.message.reply_text(
            text_message,
            reply_markup=keyboard,
        )
        return ANSWER_CONFIRMATION
    else:
        return ConversationHandler.END


def confirm_the_data(update, context):
    print("test")
    choices = {"Confirm": True, "Edit": False}
    answer = choices.get(update.message.text)
    if answer:
        conn = create_connection()
        data = ("user confirmed", context.user_data.get("log_id"))
        update_log_confirmation(conn, data)
        [
            context.user_data.pop(key)
            for key in (
                "user_id",
                "first_name",
                "last_name",
                "datetime",
                "category",
                "status",
            )
        ]
        update.message.reply_text("Confirmed", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        return ask_work_type(update, context)


def ask_work_type(update, context):
    text_message = "Would you like to share your today's content of work?"
    reply_keyboard = [["I worked at Office", "I would like to report"]]
    update.message.reply_text(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return ANSWER_WORK_TYPE


def ask_work_content(update, context):
    update.message.reply_text(
        "OK. Please share us your content work as a text message."
    )
    return ANSWER_WORK_CONTENT


def check_work_content(update, context):

    answer = update.message.text
    update.message.reply_text(
        f"Content of Work\n{answer}\n\nIs it ok?",
        reply_markup=ReplyKeyboardMarkup([["YES", "NO"]]),
    )

    return ANSWER_CONTENT_CONFIRMATION


def save_content_and_ask_location(update, context):
    # save content
    return ask_sign_out_location(update, context)
