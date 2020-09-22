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
    print("test", update.message)


def sign_in(update, context):
    """read sign in and process"""
    pprint(eval(str(update.message)))
    update.message.reply_text(f"good morning, {update.message.chat.first_name}")


def signing_in(update, context):
    record = {
            "first_name": update.message.from_user.first_name,
            "last_name": update.message.from_user.last_name,
            "signing_time": update.message.date.astimezone(cameroon_tz),
        }
    update.message.reply_text(f"good morning, {record['first_name']} \n\
    you have signed in at {record['signing_time']}")
    keyboard = [[KeyboardButton("Share Location", request_location=True), ], ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('Please Share your location:', reply_markup=reply_markup)


def get_current_location(update, context):
    """ handle location"""
    user = update.message.from_user
    user_location = update.message.location
    print(user_location)
    update.message.reply_text(f"{user.first_name}'s location is {user_location}", 
    reply_markup=ReplyKeyboardRemove(remove_keyboard=True, selective=False))


def echo(update, context):
    """Echo the user message."""

    pprint(eval(str(update.message)))

    if update.message.text.lower() in ["signing in"]:
        signing_in(update, context)


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
    dp.add_handler(CommandHandler("sign_in", sign_in))

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
