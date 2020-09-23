import pytz
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


cameroon_tz = pytz.timezone('Africa/Douala')


def get_current_location(update, context):
    """ listen location"""
    record = {
        "id": update.message.from_user.id,
        "first_name": update.message.from_user.first_name,
        "last_name": update.message.from_user.last_name,
        "time": update.message.date.astimezone(cameroon_tz),
        "location": update.message.location
    }
    update.message.reply_text(
        f"{record['first_name']}'s location is {record['location']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
