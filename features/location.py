import pytz
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


cameroon_tz = pytz.timezone('Africa/Douala')


def ask_location(update, context):
    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Please Share your location:',
                              reply_markup=reply_markup)


def get_current_location(update, context):
    """ listen location"""
    record = {
        "first_name": update.message.from_user.first_name,
        "last_name": update.message.from_user.last_name,
        "time": update.message.date.astimezone(cameroon_tz),
        "location": update.message.location
    }
    update.message.reply_text(
        f"{record['first_name']}'s location is {record['location']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
