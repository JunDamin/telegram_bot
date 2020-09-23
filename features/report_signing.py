import csv
import pytz
import os
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup


cameroon_tz = pytz.timezone('Africa/Douala')


def get_signing_data(update, context, report_type):
    """ collect recording data from messages """
    record = {
            "id": update.message.from_user.id,
            "first_name": update.message.from_user.first_name,
            "last_name": update.message.from_user.last_name,
            "datetime": update.message.date.astimezone(cameroon_tz),
            "type": report_type,
            }
    return record


def reply_sign_in(update, context, record):
    """ reply when signing in """
    update.message.reply_text(
        f"good morning, {record['first_name']}\nyou have signed in at {record['datetime']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True, selective=False)
        )


def reply_sign_out(update, context, record):
    """ reply when signing in """
    update.message.reply_text(
        f"good evening, {record['first_name']}\nyou have signed out at {record['datetime']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True, selective=False)
        )


def report_signing(update, context, report_type, reply_callback):
    """ get update message data and report """
    record = get_signing_data(update, context, report_type)
    reply_callback(update, context, record)
    if not os.path.exists("signing.csv"):
        with open("signing.csv", mode='a', encoding="utf-8-sig") as signing_file:
            fieldnames = ["id", "first_name", "last_name", "datetime", "type"]
            writer = csv.DictWriter(signing_file, fieldnames=fieldnames)
            writer.writeheader()
    with open("signing.csv", mode='a', encoding="utf-8-sig") as signing_file:
        fieldnames = ["id", "first_name", "last_name", "datetime", "type"]
        writer = csv.DictWriter(signing_file, fieldnames=fieldnames)
        writer.writerow(record)
    # Send a message for location
    ask_location(update, context)
    print(record)


def ask_location(update, context):
    bot = context.bot
    user_id = update.message.from_user.id
    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    bot.send_message(chat_id=user_id, text='Please Share your location:', reply_markup=reply_markup)
