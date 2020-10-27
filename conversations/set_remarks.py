from telegram.ext import ConversationHandler
from features.db_management import (
    create_connection,
    update_record,
)
from features.data_IO import get_text_of_log_by_id, get_record_by_log_id
from features.message import reply_markdown
from features.log import log_info


# Add remarks
HANDLE_REMARKS_LOG_ID, HANDLE_REMARKS_CONTENT = map(chr, range(7, 9))


@log_info()
def ask_log_id_for_remarks(update, context):

    text_message = (
        "Which log do you want to add remarks?\nPlease send me the log number."
    )

    reply_markdown(update, context, text_message)
    context.user_data["status"] = "ASK_REMARKS_CONTENT"

    return HANDLE_REMARKS_LOG_ID


@log_info()
def ask_content_for_remarks(update, context):
    text = update.message.text
    try:
        if get_record_by_log_id(text):
            context.user_data["remarks_log_id"] = text
            text_message = "What remarks? do you want to add?"
            reply_markdown(update, context, text_message)
            return HANDLE_REMARKS_CONTENT
        else:
            text_message = "log id is not exist. Please try again"
            reply_markdown(update, context, text_message)
            raise ValueError
    except ValueError:
        text_message = "Please. Send us numbers only."
        reply_markdown(update, context, text_message)
        return HANDLE_REMARKS_LOG_ID


@log_info()
def set_remarks(update, context):
    log_id = context.user_data.get("remarks_log_id")
    content = update.message.text
    record = {"remarks": content}

    conn = create_connection()
    update_record(conn, "logbook", record, log_id)
    conn.close()

    context.user_data["log_id"] = log_id

    text_message = "remarks has been updated.\n"
    text_message += get_text_of_log_by_id(log_id)
    reply_markdown(update, context, text_message)

    return ConversationHandler.END
