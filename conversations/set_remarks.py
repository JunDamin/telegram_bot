from telegram.ext import ConversationHandler
from features.data_management import (
    create_connection,
    select_log,
    update_remarks,
)
from features.function import select_log_to_text
from features.log import log_info


# Add remarks
HANDLE_REMARKS_LOG_ID, HANDLE_REMARKS_CONTENT = map(chr, range(7, 9))


@log_info()
def ask_log_id_for_remarks(update, context):
    update.message.reply_text(
        "Which log do you want to add remarks?\nPlease send me the log number."
    )
    context.user_data["status"] = "ASK_REMARKS_CONTENT"

    return HANDLE_REMARKS_LOG_ID


@log_info()
def ask_content_for_remarks(update, context):
    text = update.message.text
    try:
        int(text)
        conn = create_connection()
        row = select_log(conn, text)
        conn.close()

        if row:
            context.user_data["remarks_log_id"] = text
            update.message.reply_text("What remarks? do you want to add?")
            return HANDLE_REMARKS_CONTENT
        else:
            update.message.reply_text("log id is not exist. Please try again")
            raise ValueError
    except ValueError:
        update.message.reply_text("Please. Send us numbers only.")
        return HANDLE_REMARKS_LOG_ID


@log_info()
def set_remarks(update, context):
    log_id = context.user_data.get("remarks_log_id")
    content = update.message.text

    conn = create_connection()
    update_remarks(conn, log_id, content)
    conn.close()

    context.user_data["log_id"] = log_id

    text_message = "remarks has been updated.\n"
    text_message += select_log_to_text(log_id)
    update.message.reply_text(text_message)

    return ConversationHandler.END
