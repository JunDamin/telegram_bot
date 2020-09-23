import os
import logging
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from features.command import start, help_command, send_file, start_signing
from features.report_signing import conv_handler

load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging

# Bot setting
token = os.getenv("TOKEN")
print("telegram bot started")


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
    dp.add_handler(CommandHandler("signbook", send_file))

    # on signing in command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.regex("(S|s)ign.{0,4} in"), start_signing))

    # on conversation handler
    signing_in_handler = conv_handler()
    dp.add_handler(signing_in_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
