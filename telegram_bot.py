import os
import logging
from pprint import pprint
import pytz
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
cameroon_tz = pytz.timezone('Africa/Douala')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging

# Bot setting
token = os.getenv("TOKEN")
print(token)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def get_signing_data(update, context, report_type):
    """ collect recording data from messages """
    record = {
            "type": report_type,
            "first_name": update.message.from_user.first_name,
            "last_name": update.message.from_user.last_name,
            "datetime": update.message.date.astimezone(cameroon_tz),
            }
    return record


def ask_location(update, context):
    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Please Share your location:',
                              reply_markup=reply_markup)


def reply_sign_in(update, context, record):
    """ reply when signing in """
    update.message.reply_text(
        f"good morning, {record['first_name']}\nyou have signed in at {record['datetime']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True, selective=False)
        )
    if update.message.chat.type == "private":
        ask_location(update, context)


def reply_sign_out(update, context, record):
    """ reply when signing in """
    update.message.reply_text(
        f"good evening, {record['first_name']}\nyou have signed out at {record['datetime']}",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True, selective=False)
        )
    if update.message.chat.type == "private":
        ask_location(update, context)


def report_signing(update, context, report_type, reply_callback):
    """ get update message data and report """
    record = get_signing_data(update, context, report_type)
    reply_callback(update, context, record)


def get_current_location(update, context):
    """ listen location"""
    record = {
        "first_name": update.message.from_user.first_name,
        "last_name": update.message.from_user.last_name,
        "time": update.message.date.astimezone(cameroon_tz),
        "location": update.message.location
    }
    update.message.reply_text(f"{record['first_name']}'s location is {record['location']}",
                              reply_markup=ReplyKeyboardRemove(
                                remove_keyboard=True, selective=False))


def echo(update, context):
    """Echo the user message."""

    pprint(str(update.message))

    text = update.message.text
    text = text.lower()
    text = text.strip()

    if text in ["signing in"]:
        report_signing(update, context, "signing in", reply_sign_in)
    elif text in ["signing out"]:
        report_signing(update, context, "signing out", reply_sign_out)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # on location information
    dp.add_handler(MessageHandler(Filters.location, get_current_location))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
