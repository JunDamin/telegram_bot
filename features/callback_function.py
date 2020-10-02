import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.data_management import (
    create_connection,
    write_csv,
    select_all_logs,
    select_logs_by_chat_id,
    select_log,
    update_remarks,
    delete_log,
)
from features.log import log_info
from features.function import (
    check_status,
    update_location,
    update_sub_category,
    set_log_basic,
    get_logs_of_today,
    make_text_from_logbook,
    get_logs_of_the_day,
)

# Status variables for conversation

# Delete log
HANDLE_DELETE_LOG_ID, HANDLE_LOG_DELETE = map(chr, range(5, 7))
# Add remarks
HANDLE_REMARKS_LOG_ID, HANDLE_REMARKS = map(chr, range(7, 9))
# regex pattern
SUB_CATEGORY = "Office|Home"


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
    conn = create_connection()
    record = select_all_logs(conn)
    conn.close()
    write_csv(record)
    update.message.reply_document(document=open("signing.csv", "rb"))




@log_info()
def cancel(update, context):
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@log_info()
def check_log(update, context):
    user = update.message.from_user

    conn = create_connection()
    rows = select_logs_by_chat_id(conn, user.id)
    rows = rows[-1::-1]
    conn.close()

    header_message = "Here is your recent log info.\n"
    text_message = make_text_from_logbook(rows, header_message)

    update.message.reply_text(text_message)


@log_info()
def get_a_log(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        conn = create_connection()
        rows = select_log(conn, log_id)
        conn.close()
        print(rows)
        header_message = "You have been logged as below.\n"
        text_message = make_text_from_logbook(rows, header_message)
        update.message.reply_text(text_message)

    else:
        update.message.reply_text("please send me a log id first.")
        context.user_data["status"] = "GET_LOG_ID"


@log_info()
def ask_log_id_for_remarks(update, context):
    update.message.reply_text(
        "Which log do you want to add remarks?\nPlease send me the log number."
    )
    context.user_data["status"] = "ASK_REMARKS_CONTENT"


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
            return True
        else:
            update.message.reply_text("log id is not exist. Please try again")
            raise ValueError
    except ValueError:
        update.message.reply_text("Please. Send us numbers only.")
        return False


@log_info()
def set_remarks(update, context):
    log_id = context.user_data.get("remarks_log_id")
    content = update.message.text

    conn = create_connection()
    update_remarks(conn, log_id, content)
    conn.close()

    update.message.reply_text("remarks has been updated.")
    context.user_data["log_id"] = log_id
    get_a_log(update, context)


def get_logs_today(update, context):
    """ """
    text_message = get_logs_of_today()
    update.message.reply_text(text_message)


@log_info()
def ask_log_id_to_remove(update, context):
    """ """
    update.message.reply_text(
        "Which log do you want to remove?\nPlease send me the log number."
    )
    context.user_data["status"] = "REMOVE_LOG_ID"


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
        return True
    except ValueError:
        update.message.reply_text("Please. Send me numbers only.")
        return False


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
    return True


@log_info()
def ask_date_for_log(update, context):

    text_message = "Please send the date as YYYY-MM-DD format"
    update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    context.user_data["status"] = "DATE_FOR_LOG"


def reply_logs_of_the_date(update, context):
    the_date = update.message.text
    import datetime.date as date

    try:
        text_message = get_logs_of_the_day(date.fromisoformat(the_date))
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
        return True
    except ValueError:
        return False
