import os
from collections import deque
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
from features.callback_function import (
    start,
    help_command,
    send_file,
    check_log,
    get_logs_today,
)
from features.data_management import start_database
from features.function import private_only
from conversations.conversation import handlers

load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Bot setting
token = os.getenv("TOKEN")
print("telegram bot started")

start_database()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("check", private_only(check_log)))
    dp.add_handler(CommandHandler("today", get_logs_today))
    dp.add_handler(CommandHandler("logbook", private_only(send_file)))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on messages handling i.e message - set callback function for each message keywords

    # add hander from conversations
    deque(map(dp.add_handler, handlers))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
