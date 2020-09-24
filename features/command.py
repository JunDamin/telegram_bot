import pytz
from telegram import ReplyKeyboardMarkup
from features.report_signing import write_csv
from features.data_management import create_connection, create_attendee_basic, select_all_atendee

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    conn = create_connection("db.sqlite3")
    record = select_all_atendee(conn)
    conn.close()
    write_csv(record)
    update.message.reply_document(document=open("signing.csv", "rb"))


def start_signing_in(update, context):
    bot = context.bot
    user = update.message.from_user
    attendee_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing in",
    )
    conn = create_connection("db.sqlite3")
    attendee_id = create_attendee_basic(conn, attendee_basic)
    conn.close()
    
    reply_keyboard = [
        [
            f"""Start register today
    register_id: {attendee_id}"""
        ]
    ]

    bot.send_message(
        chat_id=user.id,
        text=f"""Good morning, {update.message.from_user.first_name}.\n
        Are you want to register today?\n
        signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    context.user_data['attendee_id'] = attendee_id
    print(context.user_data)