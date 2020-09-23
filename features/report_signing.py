import csv
import pytz
import os
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

cameroon_tz = pytz.timezone('Africa/Douala')

WORK_TYPE, LOCATION = range(2)


def start(update, context):
    reply_keyboard = [['Office', 'Home']]
    update.message.reply_text(
        text=f'{update.message.from_user.first_name}, are you working at the office or home?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return WORK_TYPE


def work_type(update, context):
    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('I see! Please send me your location by click the button', reply_markup=reply_markup)

    return LOCATION


def location(update, context):
    user_location = update.message.location
    update.message.reply_text(f'longitude: {user_location.longitude}\
     latitude: {user_location.latitude} has been registered.')

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def conv_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Start register today"), start)],

        states={
            WORK_TYPE: [MessageHandler(Filters.regex('^(Office|Home)$'), work_type)],

            LOCATION: [MessageHandler(Filters.photo, location), location],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


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
