import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from features.report_signing import write_csv
from features.data_management import create_connection, create_attendee_basic,\
     select_all_atendee, update_attendee_location

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
            f"""Share more infomation\n
    register_id: {attendee_id}"""
        ]
    ]

    bot.send_message(
        chat_id=user.id,
        text=f"""Good morning, {update.message.from_user.first_name}.\n
        You have been signed in! \n
        Would you like to share more infomation for signing in?\n
        signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    context.user_data['attendee_id'] = attendee_id
    print(context.user_data)


def start_signing_out(update, context):
    bot = context.bot
    user = update.message.from_user
    attendee_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing out",
    )
    conn = create_connection("db.sqlite3")
    attendee_id = create_attendee_basic(conn, attendee_basic)
    conn.close()
    
    reply_keyboard = [
        [KeyboardButton(f"""Share location infomation for signing out.\n
        register_id: {attendee_id}""", request_location=True), ],
    ]
    bot.send_message(
        chat_id=user.id,
        text=f"""Good morning, {update.message.from_user.first_name}.\n
        You have been signed out today.
        Would you like to share your location?\n
        signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    context.user_data['attendee_id'] = attendee_id
    context.user_data['type'] = "signing out"
    print(context.user_data)


def location(update, context):
    print(context.user_data)
    if context.user_data['type'] == "signing out":
        user_location = update.message.location
        
        conn = create_connection("db.sqlite3")
        location_data = (
            user_location.longitude,
            user_location.latitude,
            context.user_data["attendee_id"],
        )
        update_attendee_location(conn, location_data)
        conn.close()
        
        update.message.reply_text(
            f"longitude: {user_location.longitude}\
        latitude: {user_location.latitude} has been registered.\
        Good bye!",
            reply_markup=ReplyKeyboardRemove(),
        )
