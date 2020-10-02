from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from features.data_management import (
    create_connection,
    select_log,
    delete_log,
)
from features.function import make_text_from_logbook
from features.log import log_info


# Delete log
HANDLE_DELETE_LOG_ID, HANDLE_LOG_DELETE = map(chr, range(5, 7))


@log_info()
def ask_log_id_to_remove(update, context):
    """ """
    update.message.reply_text(
        "Which log do you want to remove?\nPlease send me the log number."
    )
    context.user_data["status"] = "REMOVE_LOG_ID"

    return HANDLE_DELETE_LOG_ID


@log_info()
def ask_confirmation_of_removal(update, context):
    log_id = update.message.text
    try:
        int(log_id)
        context.user_data["remove_log_id"] = log_id
        keyboard = [["YES", "NO"]]

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
    except ValueError:
        update.message.reply_text("Please. Send me numbers only.")
        return HANDLE_DELETE_LOG_ID


@log_info()
def remove_log(update, context):
    choices = {"YES": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = context.user_data.get("remove_log_id")

        conn = create_connection()
        delete_log(conn, log_id)
        conn.close()

        text_message = f"Log No. {log_id} has been Deleted\n"
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    else:
        text_message = "process has been stoped. The log has not been deleted."
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
