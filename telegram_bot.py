import os
import logging
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from features.command import start, help_command, send_file, start_signing_in, start_signing_out, location
from features.report_signing import conv_handler
from features.data_management import create_connection, create_table
load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging

# DB Setting

database = "db.sqlite3"
sql_create_attendance_table = """CREATE TABLE IF NOT EXISTS attendance (
    id integer PRIMARY KEY,
    chat_id text NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    datetime text NOT NULL,
    type text NOT NULL,
    work_type text,
    longitude text,
    latitude text
);"""

conn = create_connection(database)
if conn is not None:
    # Create Project table
    create_table(conn, sql_create_attendance_table)
conn.close()

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
    dp.add_handler(MessageHandler(Filters.regex("(S|s)ign.{0,4} in"), start_signing_in))
    dp.add_handler(MessageHandler(Filters.regex("(S|s)ign.{0,4} out"), start_signing_out))
    dp.add_handler(MessageHandler(Filters.location, location))
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
