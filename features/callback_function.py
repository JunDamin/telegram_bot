import pytz
import re
import csv
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.data_management import (create_connection, create_attendee_basic,
                                      select_all_atendee, update_attendee_type, update_attendee_location)
from features.log import log_info

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@log_info()
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


@log_info()
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


@log_info()
def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    conn = create_connection("db.sqlite3")
    record = select_all_atendee(conn)
    conn.close()
    write_csv(record)
    update.message.reply_document(document=open("signing.csv", "rb"))


@log_info()
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

    if update.message.chat.type == "group":
        update.message.reply_text(text=f"""Good morning, {update.message.from_user.first_name}.\n
        You have been signed in today.\n
        signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
        """)

    reply_keyboard = [
        [
            f"""Share more infomation\n
    register_id: {attendee_id}"""
        ]
    ]
    try:
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
        context.user_data['type'] = "signing in"
        print(update.message)
        if update.message.chat.type == "group":
            update.effective_message.reply_text("I've PM'ed you about asking more infomation!")
    except Unauthorized:
        update.effective_message.reply_text("Please, Contact me in PM(Personal Message) first for completion.")
    print(context.user_data)


@log_info()
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

    update.message.reply_text(text=f"""Good evening, {update.message.from_user.first_name}.\n
    You have been signed out today.\n
    signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
    """)

    reply_keyboard = [
        [KeyboardButton(f"""Share location infomation for signing out.\n
        register_id: {attendee_id}""", request_location=True), ],
    ]
    try:
        bot.send_message(
            chat_id=user.id,
            text=f"""Good evening, {update.message.from_user.first_name}.\n
            You have been signed out today.
            Would you like to share your location?\n
            signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}
            """,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        context.user_data['attendee_id'] = attendee_id
        context.user_data['type'] = "signing out"
        print(context.user_data)
        update.effective_message.reply_text("I've PM'ed you about asking more infomation!")
    except Unauthorized:
        update.effective_message.reply_text("Please, Contact me in PM(Personal Message) first for completion.")


@log_info()
def location(update, context):
    print(context.user_data)
    context_type = context.user_data.get("type")
    while context_type:
        if context_type == "signing out":
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
            context_type = None

        elif context_type == "signing in":
            print(context.user_data)
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
            latitude: {user_location.latitude} has been registered.",
                reply_markup=ReplyKeyboardRemove(),
            )
            context_type = None
            print(context.user_data)


cameroon_tz = pytz.timezone("Africa/Douala")
WORK_TYPE = range(1)


@log_info()
def start_conversation(update, context):
    print(context.user_data)
    reply_keyboard = [["Office", "Home"]]
    update.message.reply_text(
        text=f"{update.message.from_user.first_name}, are you working at the office or home?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    raw_text = update.message.text
    m = re.search("register_id: ([0-9]+)", raw_text)
    context.user_data["attendee_id"] = m.group(1)
    print(m.group(1))
    return WORK_TYPE


@log_info()
def work_type(update, context):
    print(context.user_data)
    conn = create_connection("db.sqlite3")
    work_type = (update.message.text, context.user_data["attendee_id"])
    update_attendee_type(conn, work_type)
    conn.close()

    keyboard = [
        [
            KeyboardButton("Share Location", request_location=True),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        """I see! Please send me your location by click the button on your phone.
        (Desktop app can not send location)
        """,
        reply_markup=reply_markup,
    )
    print("test work_type")
    return ConversationHandler.END


@log_info()
def cancel(update, context):
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def write_csv(record):
    with open("signing.csv", mode="w", encoding="utf-8-sig") as signing_file:
        fieldnames = [
            "id",
            "chat_id",
            "first_name",
            "last_name",
            "datetime",
            "type",
            "work_type",
            "longitude",
            "latitude",
        ]
        writer = csv.writer(signing_file)
        writer.writerow(fieldnames)
        writer.writerows(record)
