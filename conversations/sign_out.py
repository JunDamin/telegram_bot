import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    set_basic_user_data,
    set_location,
    get_today_log_of_chat_id_category,
    make_text_from_logbook,
    select_log_to_text,
    confirm_record,
    set_work_content,
    delete_log_and_content,
    delete_content
)
from features.data_management import (
    create_connection,
    select_log,
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

    # check
    user = update.message.from_user
    rows = get_today_log_of_chat_id_category(user.id, "signing out")

    if not rows:
        log_id = set_basic_user_data(update, context, "signing out")

        SIGN_OUT_GREETING = (
            f"""Good evening, {user.first_name}.\nYou have signed out today."""
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
            reply_keyboard = [["I worked at Office", "I would like to report because I worked at home"]]
            context.bot.send_message(
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
            context.bot.send_message(
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
        log_id = delete_log_and_content(update, context)
        text_message = f"Log No. {log_id} has been Deleted\n"
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    else:
        text_message = "process has been stoped. The log has not been deleted."
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    log_id = set_basic_user_data(update, context, "signing out")
    context.user_data["log_id"] = log_id
    return ask_work_type(update, context)


def ask_sign_out_location(update, text):
    text_message = """I see! Please send me your location by click the button on your phone.
    1. Please check your location service is on.\n(if not please turn on your location service)
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
        confirm_record(update, context)
        context.user_data.clear()
        update.message.reply_text("Confirmed", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        return ask_work_type(update, context)


def ask_work_type(update, context):
    delete_content(update, context)
    text_message = "Would you like to share your today's content of work?"
    reply_keyboard = [["I worked at Office", "I would like to report because I worked at home"]]
    update.message.reply_text(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ANSWER_WORK_TYPE


@log_info()
def ask_work_content(update, context):
    update.message.reply_text(
        "OK. Please text me what you have done todya for work briefly.", reply_markup=ReplyKeyboardRemove()
    )
    return ANSWER_WORK_CONTENT


@log_info()
def check_work_content(update, context):

    answer = update.message.text

    context.user_data["work_content"] = answer

    update.message.reply_text(
        f"Content of Work\n{answer}\n\nIs it ok?",
        reply_markup=ReplyKeyboardMarkup([["YES", "NO"]]),
    )

    return ANSWER_CONTENT_CONFIRMATION


@log_info()
def save_content_and_ask_location(update, context):
    print(context.user_data.get("work_content"))
    set_work_content(update, context, context.user_data.get("work_content"))

    return ask_sign_out_location(update, context)
