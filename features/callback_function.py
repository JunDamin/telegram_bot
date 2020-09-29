import pytz
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.data_management import (
    create_connection,
    write_csv,
    select_all_logs,
    select_logs_by_chat_id,
    select_log,
    update_remarks,
    delete_log,
)
from features.log import log_info
from features.function import (
    update_location,
    update_sub_category,
    set_log_basic,
    get_logs_of_today,
    make_text_from_logbook,
)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@log_info()
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")
    context.user_data["status"] = "START"


@log_info()
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


@log_info()
def send_file(update, context):
    """ Send a file when comamnd /signbook is issued"""
    conn = create_connection()
    record = select_all_logs(conn)
    conn.close()
    write_csv(record)
    update.message.reply_document(document=open("signing.csv", "rb"))


@log_info()
def start_signing_in(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user
    log_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing in",
    )
    log_id = set_log_basic(log_basic)
    SIGN_IN_GREETING = f"""Good morning, {user.first_name}.\n
You have been signed in with Log No. {log_id}"""
    SIGN_TIME = f"""signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"""
    ASK_INFO = """Would you like to share where you work?"""
    CHECK_DM = """"Please check my DM(Direct Message) to you"""

    # check if the chat is group or not
    if update.message.chat.type == "group":
        text_message = f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
        update.message.reply_text(text=text_message)

    # set status
    context.user_data["log_id"] = log_id
    context.user_data["category"] = "signing in"
    context.user_data["status"] = "SIGN_IN_WITH_SUB_CATEGORY"

    # send Private message to update
    try:
        text_message = f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [
            ["Office", "Home"],
        ]
        bot.send_message(
            chat_id=user.id,
            text=text_message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

    except Unauthorized:
        update.effective_message.reply_text(
            "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
        )

    return True


@log_info()
def start_signing_out(update, context):

    # set variables

    bot = context.bot
    user = update.message.from_user
    log_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "signing out",
    )
    log_id = set_log_basic(log_basic)

    SIGN_OUT_GREETING = (
        f"""Good evening, {user.first_name}.\nYou have been signed out today."""
    )
    SIGN_TIME = f"signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"
    ASK_INFO = "Please share your location infomation."
    CHECK_DM = """"Please check my DM(Direct Message) to you"""
    text_message = f"{SIGN_OUT_GREETING}/n{SIGN_TIME}"

    if update.message.chat.type == "group":
        text_message = f"{SIGN_OUT_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
        update.message.reply_text(text=text_message)

    # set status
    context.user_data["log_id"] = log_id
    context.user_data["category"] = "signing out"
    context.user_data["status"] = "SIGN_OUT_WITH_LOCATION"

    try:
        text_message = f"{SIGN_OUT_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [
            [
                KeyboardButton(
                    """Share location infomation for signing out""",
                    request_location=True,
                ),
            ]
        ]
        bot.send_message(
            chat_id=user.id,
            text=text_message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

    except Unauthorized:
        update.effective_message.reply_text(
            "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
        )

    return True


@log_info()
def set_location(update, context):
    user_data = context.user_data
    user_location = update.message.location

    update_location(
        user_data["log_id"],
        user_location.longitude,
        user_location.latitude,
    )

    update.message.reply_text(
        f"longitude: {user_location.longitude}, latitude: {user_location.latitude} has been logged.\
    Good bye!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return True


@log_info()
def set_sub_category(update, context):
    """Get sub category"""
    # save log work type data
    update_sub_category(context.user_data["log_id"], update.message.text)

    keyboard = [
        [
            KeyboardButton("Share Location", request_location=True),
        ],
    ]

    update.message.reply_text(
        """I see! Please send me your location by click the button on your phone.
(Desktop app can not send location)""",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )
    return True


@log_info()
def cancel(update, context):
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def connect_message_status(update, context):
    status = context.user_data.get("status")
    call_back = None

    callback_dict = {
        "SIGN_IN_WITH_SUB_CATEGORY": (set_sub_category, "SIGN_IN_WITH_LOCATION"),
        "SIGN_IN_WITH_LOCATION": (set_location, None),
        "ASK_REMARKS_CONTENT": (ask_content_for_remarks, "SET_REMARKS"),
        "SET_REMARKS": (set_remarks, None),
        "REMOVE_LOG_ID": (ask_confirmation_of_removal, "CONFIRM_DELETE_LOG"),
        "CONFIRM_DELETE_LOG": (remove_log, None),
    }

    if callback_dict.get(status):
        call_back, next_status = callback_dict.get(status)

    if call_back:
        if call_back(update, context):
            context.user_data["status"] = next_status


@log_info()
def check_log(update, context):
    user = update.message.from_user

    conn = create_connection()
    rows = select_logs_by_chat_id(conn, user.id)
    rows = rows[-1::-1]
    conn.close()

    header_message = "You have been logged as below.\n"
    text_message = make_text_from_logbook(rows, header_message)

    update.message.reply_text(text_message)


@log_info()
def get_a_log(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        conn = create_connection()
        rows = select_log(conn, log_id)
        conn.close()
        print(rows)
        text_message = "You have been logged as below.\n"
        for (
            log_id,
            _,
            first_name,
            last_name,
            datetime,
            category,
            sub_category,
            longitude,
            latitude,
            remarks,
        ) in rows:

            record = f"""
            log id : {log_id}
            datetime : {datetime}
            category : {category} - {sub_category}
            longitude, latitude : {longitude}, {latitude}
            remarks :{remarks}\n"""

            text_message += record

        update.message.reply_text(text_message)

    else:
        update.message.reply_text("please send me a log id first.")
        context.user_data["status"] = "GET_LOG_ID"


@log_info()
def ask_log_id_for_remarks(update, context):
    update.message.reply_text(
        "Which log do you want to add remarks?\nPlease send me the log number."
    )
    context.user_data["status"] = "ASK_REMARKS_CONTENT"


@log_info()
def ask_content_for_remarks(update, context):
    text = update.message.text
    try:
        int(text)
        context.user_data["remarks_log_id"] = update.message.text
        update.message.reply_text("What remarks? do you want to add?")
        return True
    except ValueError:
        update.message.reply_text("Please. Send us numbers only.")
        return False


@log_info()
def set_remarks(update, context):
    log_id = context.user_data.get("remarks_log_id")
    content = update.message.text

    conn = create_connection()
    update_remarks(conn, log_id, content)
    conn.close()

    update.message.reply_text("remarks has been updated.")
    context.user_data["log_id"] = log_id
    get_a_log(update, context)


@log_info()
def get_back_to_work(update, context):

    # set variables
    bot = context.bot
    user = update.message.from_user
    log_basic = (
        user.id,
        user.first_name,
        user.last_name,
        update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "lunch over",
    )
    log_id = set_log_basic(log_basic)

    # set message texts
    SIGN_IN_GREETING = f"""Good afternoon, {user.first_name}.\n
Welcome back. You have been logged with Log No. {log_id}"""
    SIGN_TIME = f"""signing time: {update.message.date.astimezone(pytz.timezone('Africa/Douala'))}"""
    ASK_INFO = """Did you have lunch with KOICA collagues?"""
    CHECK_DM = """"Please check my DM(Direct Message) to you"""

    # check if the chat is group or not
    if update.message.chat.type == "group":
        text_message = f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
        update.message.reply_text(text=text_message)

    # set status
    context.user_data["log_id"] = log_id
    context.user_data["category"] = "lunch over"
    context.user_data["status"] = "BACK_TO_WORK"

    # send Private message to update
    try:
        text_message = f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
        reply_keyboard = [
            ["Alone", "With Someone"],
        ]
        bot.send_message(
            chat_id=user.id,
            text=text_message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

    except Unauthorized:
        update.effective_message.reply_text(
            "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
        )

    return True


@log_info()
def set_lunch_location(update, context):
    """  """
    # save log work type data
    update_sub_category(context.user_data["log_id"], update.message.text)

    keyboard = [
        [
            KeyboardButton("Share Location", request_location=True),
        ],
    ]

    update.message.reply_text(
        """I see! Please send me your location by click the button on your phone.
(Desktop app can not send location)""",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )
    return True


def get_logs_today(update, context):
    """ """
    text_message = get_logs_of_today()
    update.message.reply_text(text_message)


@log_info()
def ask_log_id_to_remove(update, context):
    """ """
    update.message.reply_text(
        "Which log do you want to remove?\nPlease send me the log number."
    )
    context.user_data["status"] = "REMOVE_LOG_ID"


@log_info()
def ask_confirmation_of_removal(update, context):
    text = update.message.text
    try:
        int(text)
        context.user_data["remove_log_id"] = text
        keyboard = [["YES", "NO"]]
        update.message.reply_text(
            f"Do you really want to do remove log No.{text}?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
        return True
    except ValueError:
        update.message.reply_text("Please. Send me numbers only.")
        return False


@log_info()
def remove_log(update, context):
    choices = {"YES": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = context.user_data.get("remove_log_id")

        conn = create_connection()
        row = select_log(conn, log_id)
        delete_log(conn, log_id)
        
        header_message = f"Log No. {log_id} has been Deleted\n"
        text_message = make_text_from_logbook(row, header_message)
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    else:
        text_message = "process has been stoped. The log has not been deleted."
        update.message.reply_text(text_message, reply_markup=ReplyKeyboardRemove())
    return True
