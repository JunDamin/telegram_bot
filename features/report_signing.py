import csv
import pytz
import os
import re
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from features.data_management import create_connection, update_attendee_location, update_attendee_type

cameroon_tz = pytz.timezone('Africa/Douala')

WORK_TYPE, LOCATION = range(2)


def start(update, context):
    print(context.user_data)
    reply_keyboard = [['Office', 'Home']]
    update.message.reply_text(
        text=f'{update.message.from_user.first_name}, are you working at the office or home?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    raw_text = update.message.text
    m = re.search("register_id: ([0-9]+)", raw_text)
    context.user_data['attendee_id'] = m.group(1)
    print(m.group(1))
    return WORK_TYPE


def work_type(update, context):
    print(context.user_data)
    conn = create_connection("db.sqlite3")
    work_type = (update.message.text, context.user_data["attendee_id"])
    update_attendee_type(conn, work_type)
    conn.close()

    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('I see! Please send me your location by click the button', reply_markup=reply_markup)
    print('test work_type')
    return LOCATION


def location(update, context):
    print(context.user_data)
    user_location = update.message.location
    conn = create_connection("db.sqlite3")
    location_data = (user_location.longitude, user_location.latitude, context.user_data["attendee_id"])
    update_attendee_location(conn, location_data)
    conn.close()
    
    update.message.reply_text(f'longitude: {user_location.longitude}\
     latitude: {user_location.latitude} has been registered.', reply_markup=ReplyKeyboardRemove())
    print('test location')

    print(context.user_data)

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

            LOCATION: [MessageHandler(Filters.location, location)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


def write_csv(record):
    if not os.path.exists("signing.csv"):
        with open("signing.csv", mode='a', encoding="utf-8-sig") as signing_file:
            fieldnames = ["id", "first_name", "last_name", "datetime", "type", "work_type", "longitude", "latitude"]
            writer = csv.DictWriter(signing_file, fieldnames=fieldnames)
            writer.writeheader()
    with open("signing.csv", mode='a', encoding="utf-8-sig") as signing_file:
        fieldnames = ["id", "first_name", "last_name", "datetime", "type", "work_type", "longitude", "latitude"]
        writer = csv.DictWriter(signing_file, fieldnames=fieldnames)
        writer.writerow(record)
