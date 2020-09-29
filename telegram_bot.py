import os
import re
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from features.callback_function import (
    start,
    help_command,
    send_file,
    start_signing_in,
    start_signing_out,
    check_log,
    ask_log_id_for_remarks,
    connect_message_status,
    get_back_to_work,
    get_logs_today,
    ask_log_id_to_remove,
)
from features.data_management import create_connection, create_table


load_dotenv()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# DB Setting
database = "db.sqlite3"
sql_create_attendance_table = """CREATE TABLE IF NOT EXISTS logbook (
    id integer PRIMARY KEY,
    chat_id text NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    datetime text NOT NULL,
    category text NOT NULL,
    sub_category text,
    longitude text,
    latitude text,
    remarks text
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
    dp.add_handler(CommandHandler("check", check_log))
    dp.add_handler(CommandHandler("today", get_logs_today))
    dp.add_handler(CommandHandler("logbook", send_file))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("remarks", ask_log_id_for_remarks))
    dp.add_handler(CommandHandler("remove", ask_log_id_to_remove))

    # on messages handling i.e message - set callback function for each message keywords

    dp.add_handler(
        MessageHandler(
            Filters.regex(re.compile("sign.{0,3} in", re.IGNORECASE)), start_signing_in
        )
    )
    dp.add_handler(
        MessageHandler(
            Filters.regex(re.compile("sign.{0,3} out", re.IGNORECASE)),
            start_signing_out,
        )
    )
    dp.add_handler(
        MessageHandler(
            Filters.regex(
                re.compile("back from break|back to work|lunch over", re.IGNORECASE)
            ),
            get_back_to_work,
        )
    )
    # dp.add_handler(MessageHandler(Filters.location, location))
    dp.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command | Filters.location, connect_message_status
        )
    )

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
