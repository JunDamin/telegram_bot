from telegram.ext import ConversationHandler
from features.data_management import create_connection, select_record, update_record
from features.function import make_text_from_logbook
from features.log import log_info
from features.message import reply_markdown, set_context
from features.constant import LOG_COLUMN

# Delete log
ANSWER_LOG_ID, ANSWER_CONFIRMATION = map(chr, range(7, 9))


@log_info()
def ask_log_id_to_edit(update, context):
    """ """

    user = update.message.from_user

    conn = create_connection()
    rows = select_record(
        conn,
        "logbook",
        LOG_COLUMN,
        {"chat_id": user.id},
        "ORDER BY datetime DESC LIMIT 3",
    )
    rows = rows[-1::-1]
    conn.close()

    text_message = "Which log do you want to edit?\nPlease send me the log number."
    text_message = make_text_from_logbook(rows, text_message)

    reply_markdown(update, context, text_message)

    context.user_data["status"] = "EDIT_LOG_ID"

    return ANSWER_LOG_ID


@log_info()
def ask_confirmation_of_edit(update, context):
    log_id = update.message.text
    try:
        int(log_id)
        keyboard = [["YES", "NO"]]

        conn = create_connection()
        rows = select_record(conn, "logbook", LOG_COLUMN, {"id": log_id})
        conn.close()

        header_message = f"Do you really want to do edit log No.{log_id}?\n"
        text_message = make_text_from_logbook(rows, header_message)
        reply_markdown(update, context, text_message, keyboard)

        chat_id = rows[0][1]

        set_context(update, context, {"log_id": log_id, "chat_id": chat_id})

        return ANSWER_CONFIRMATION
    except ValueError:
        text_message = "Please. Send me numbers only."
        reply_markdown(update, context, text_message)
        return ANSWER_LOG_ID


@log_info()
def start_edit(update, context):
    choices = {"YES": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = context.user_data.get("log_id")

        conn = create_connection()
        rows = select_record(conn, "logbook", ("category", "history"), {"id": log_id})
        category = rows[0][0]
        history = rows[0][1] if rows[0][1] else ""
        history += f"Edited at {update.message.date} for {category}\n"
        update_record(conn, "logbook", {"history": history}, log_id)
        conn.close()
        keyboard_dict = {
            "signing in": [
                ["Office", "Home"],
            ],
            "signing out": [
                [
                    "I worked at Office",
                    "I would like to report because I worked at home",
                ]
            ],
            "getting back": [
                ["Without any member of KOICA", "With KOICA Colleagues"],
            ],
        }
        status_dict = {
            "signing in": "SIGN_IN",
            "signing out": "SIGN_OUT",
            "getting back": "GET_BACK",
        }
        context.user_data["status"] = status_dict.get(category)

        text_message = f"start to edit Log No.{log_id} by press button\n"
        reply_markdown(update, context, text_message, keyboard_dict.get(category))
    else:
        text_message = "process has been stoped. The log has not been deleted."
        reply_markdown(update, context, text_message)
        context.user_data.clear()
    return ConversationHandler.END
