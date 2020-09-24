import csv
import pytz
import re
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from features.data_management import (
    create_connection,
    update_attendee_type,
)

cameroon_tz = pytz.timezone("Africa/Douala")

WORK_TYPE = range(1)


def start(update, context):
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
        "I see! Please send me your location by click the button",
        reply_markup=reply_markup,
    )
    print("test work_type")
    return ConversationHandler.END 


def cancel(update, context):
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def conv_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Share more infomation"), start)],
        states={
            WORK_TYPE: [MessageHandler(Filters.regex("^(Office|Home)$"), work_type)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


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
