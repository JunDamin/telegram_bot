from features.report_signing import report_signing, reply_sign_in, reply_sign_out
from telegram import ReplyKeyboardMarkup

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    update.message.reply_document(document=open('signing.csv', 'rb'))


def start_signing(update, context):
    bot = context.bot
    user_id = update.message.from_user.id
    reply_keyboard = [['Start register today']]
    bot.send_message(
        chat_id=user_id,
        text=f'Good morning, {update.message.from_user.first_name}. Are you want to register today?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )


def echo(update, context):
    """Echo the user message."""

    text = update.message.text
    text = text.lower()
    text = text.strip()

    if text in ["signing in"]:
        report_signing(update, context, "signing in", reply_sign_in)
    elif text in ["signing out"]:
        report_signing(update, context, "signing out", reply_sign_out)
