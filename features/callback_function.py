from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler
from features.db_management import (
    create_connection,
    write_csv,
    select_record
)
from features.log import log_info
from features.data_IO import (
    get_logs_of_today,
    make_text_from_logs,
    get_logs_of_the_day,
    get_text_of_log_by_id,)
from features.authority import private_only
from features.message import reply_markdown
from features.constant import LOG_COLUMN

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@log_info()
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_markdown_v2(
        """*bold \*text*
_italic \*text_
__underline__
~strikethrough~
*bold _italic bold ~italic bold strikethrough~ __underline italic bold___ bold*
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
`inline fixed-width code`
```
pre-formatted fixed-width code block
```
```python
pre-formatted fixed-width code block written in the Python programming language
```"""
    )
    context.user_data["status"] = "START"


@log_info()
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


@log_info()
def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    conn = create_connection()
    record = select_record(conn, "logbook", ["*"], {})
    conn.close()
    header = [
        "id",
        "chat_id",
        "first_name",
        "last_name",
        "datetime",
        "category",
        "sub_category",
        "longitude",
        "latitude",
        "remarks",
        "confirmation",
    ]
    write_csv(record, header, "signing.csv")
    update.message.reply_document(document=open("signing.csv", "rb"))


@log_info()
def cancel(update, context):
    update.message.reply_message(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@log_info()
def check_log(update, context):
    user = update.message.from_user

    conn = create_connection()
    rows = select_record(conn, "logbook", LOG_COLUMN, {"chat_id": user.id}, "ORDER BY timestamp DESC LIMIT 6")
    rows = rows[-1::-1]
    conn.close()

    header_message = "Here is your recent log info.\n"
    text_message = make_text_from_logs(rows, header_message)

    reply_markdown(update, context, text_message)


@log_info()
def get_a_log(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        text_message = "You have been logged as below.\n"
        text_message += get_text_of_log_by_id(log_id)
        reply_markdown(update, context, text_message)

    else:
        update.message.reply_text("please send me a log id first.")
        context.user_data["status"] = "GET_LOG_ID"


def get_logs_today(update, context):
    """ """
    text_message = get_logs_of_today()
    reply_markdown(update, context, text_message)


@log_info()
def ask_date_for_log(update, context):

    text_message = "Please send the date as YYYY-MM-DD format"
    reply_markdown(update, context, text_message)
    context.user_data["status"] = "DATE_FOR_LOG"


def reply_logs_of_the_date(update, context):
    the_date = update.message.text
    import datetime.date as date

    try:
        text_message = get_logs_of_the_day(date.fromisoformat(the_date))
        reply_markdown(update, context, text_message)
        return True
    except ValueError:
        return False


@log_info()
def get_work_content_file(update, context):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contents")
    rows = cursor.fetchall()
    conn.close()
    record = [list(map(lambda x: str(x).replace("\\n", "\n"), row)) for row in rows]
    write_csv(
        record,
        [
            "id",
        ],
        "work_content.csv",
    )
    update.message.reply_document(document=open("work_content.csv", "rb"))


command_handlers = (
    CommandHandler("check", private_only(check_log)),
    CommandHandler("today", get_logs_today),
    CommandHandler("logbook", private_only(send_file)),
    CommandHandler("work_content", private_only(get_work_content_file)),
    CommandHandler("start", start),
    CommandHandler("help", help_command),
)
