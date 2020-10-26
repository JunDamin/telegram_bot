from telegram.ext import ConversationHandler
from features.data_management import (
    create_connection,
    delete_log,
    select_record
)
from features.function import make_text_from_logbook
from features.log import log_info
from features.message import (
    reply_markdown,
)
from features.constant import LOG_COLUMN

# Delete log
HANDLE_DELETE_LOG_ID, HANDLE_LOG_DELETE = map(chr, range(5, 7))


@log_info()
def ask_log_id_to_remove(update, context):
    """ """
    text_message = "Which log do you want to remove?\nPlease send me the log number."
    reply_markdown(update, context, text_message)

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
        row = select_record(conn, "logbook", LOG_COLUMN, {"id": log_id})
        conn.close()

        header_message = f"Do you really want to do remove log No.{log_id}?\n"
        text_message = make_text_from_logbook(row, header_message)
        reply_markdown(update, context, text_message, keyboard)

        return HANDLE_LOG_DELETE
    except ValueError:
        text_message = "Please. Send me numbers only."
        reply_markdown(update, context, text_message)
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

        text_message = f"Log No.{log_id} has been Deleted\n"
        reply_markdown(update, context, text_message)
        context.user_data.clear()
    else:
        text_message = "process has been stoped. The log has not been deleted."
        reply_markdown(update, context, text_message)
    return ConversationHandler.END
