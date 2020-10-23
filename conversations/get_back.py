import pytz
from telegram import KeyboardButton
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    update_sub_category,
    set_basic_user_data,
    get_today_log_of_chat_id_category,
    make_text_from_logbook,
    select_log_to_text,
    set_location,
    select_log,
    confirm_record,
    reply_markdown,
    send_markdown,
)
from features.data_management import (
    create_connection,
    delete_log,
)


# Lunch break
ANSWER_LOG_DELETE, ANSWER_LUNCH_TYPE, ANSWER_LUNCH_LOCATION, ANSWER_CONFIRMATION = [
    "get_back" + str(i) for i in range(4, 8)
]


@log_info()
def get_back_to_work(update, context):

    # check
    user = update.message.from_user
    rows = get_today_log_of_chat_id_category(user.id, "getting back")

    if not rows:
        log_id = set_basic_user_data(update, context, "getting back")

        # set message texts
        SIGN_IN_GREETING = f"""Good afternoon, {user.first_name}.\n
Welcome back. You have been logged with Log No. {log_id}"""
        dt = update.message.date.astimezone(pytz.timezone('Africa/Douala'))
        SIGN_TIME = f"""signing time: {dt.strftime("%m-%d *__%H:%M__*")}"""
        ASK_INFO = """Did you have lunch with KOICA collagues?"""
        CHECK_DM = """"Please check my DM(Direct Message) to you"""

        # check if the chat is group or not
        if update.message.chat.type == "group":
            text_message = f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"
            reply_markdown(update, context, text_message)

        # set status
        context.user_data["log_id"] = log_id
        context.user_data["status"] = "GET_BACK"

        # send Private message to update
        try:
            text_message = f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
            reply_keyboard = [
                ["Without any member of KOICA", "With KOICA Colleagues"],
            ]
            send_markdown(update, context, user.id, text_message, reply_keyboard)

        except Unauthorized:
            text_message = (
                "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
            )
            reply_markdown(update, context, text_message)

        return ANSWER_LUNCH_TYPE
    else:
        record = rows[0]
        log_id = record[0]
        context.user_data["log_id"] = log_id
        context.user_data["status"] = "GET_BACK"
        try:
            message = "You have already reported in as below. "
            text_message = make_text_from_logbook(rows, message)
            reply_markdown(update, context, text_message)

            text_message += "\nDo you want to delete it and register again? or SKIP it?"
            reply_keyboard = [
                ["Delete and Get Back to Work Again", "SKIP"],
            ]
            send_markdown(update, context, user.id, text_message, reply_keyboard)

        except Unauthorized:
            reply_markdown(update, context, text_message)
            text_message = (
                "Please, send 'Hi!' to me as DM(Direct Message) to authorize!"
            )


@log_info()
def ask_confirmation_of_removal(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        context.user_data["remove_log_id"] = log_id

        conn = create_connection()
        row = select_log(conn, log_id)
        conn.close()

        header_message = f"Do you really want to do remove log No.{log_id}?\n"
        text_message = make_text_from_logbook(row, header_message)
        keyboard = [["REMOVE GET BACK LOG", "NO"]]

        reply_markdown(update, context, text_message, keyboard)
        return ANSWER_LOG_DELETE
    else:
        text_message = "An Error has been made. Please try again."
        reply_markdown(update, context, text_message)
        return ConversationHandler.END


def override_log_and_ask_lunch_type(update, context):

    choices = {"REMOVE GET BACK LOG": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = context.user_data.get("log_id")

        conn = create_connection()
        delete_log(conn, log_id)
        conn.close()

        text_message = f"Log No. {log_id} has been Deleted\n"
        reply_markdown(update, context, text_message)

    else:
        text_message = "process has been stoped. The log has not been deleted."
        reply_markdown(update, context, text_message)

        return ConversationHandler.END

    log_id = set_basic_user_data(update, context, "signing out")
    context.user_data["log_id"] = log_id
    return ask_lunch_type(update, context)


@log_info()
def ask_lunch_type(update, context):
    text_message = "Did you have lunch with KOICA Colleauges?"
    keyboard = [
        ["Without any member of KOICA", "With KOICA Colleagues"],
    ]
    reply_markdown(update, context, text_message, keyboard)
    return ANSWER_LUNCH_TYPE


@log_info()
def set_lunch_type_and_ask_lunch_location(update, context):
    """  """
    # save log work type data
    update_sub_category(context.user_data["log_id"], update.message.text)
    text_message = """I see! Please send me your location by click the button on your phone.
(Desktop app can not send location)"""
    keyboard = [
        [
            KeyboardButton("Share Location", request_location=True),
        ],
    ]
    reply_markdown(update, context, text_message, keyboard)
    return ANSWER_LUNCH_LOCATION


@log_info()
def set_lunch_location_and_ask_confirmation(update, context):
    if update.message.text == "DEROUTE":
        update.message.location = lambda x: None
        setattr(update.message.location, "longitude", 1)
        setattr(update.message.location, "latitude", 1)
        print("DEROUTED")
    user_data = context.user_data
    HEADER_MESSAGE = "You have gotten back as below. Do you want to confirm?"
    if set_location(update, context):
        text_message = HEADER_MESSAGE
        text_message += select_log_to_text(user_data.get("log_id"))
        keyboard = [["Confirm", "Edit"]]
        reply_markdown(update, context, text_message, keyboard)

        return ANSWER_CONFIRMATION
    else:
        return ConversationHandler.END


def confirm_the_data(update, context):
    choices = {"Confirm": True, "Edit": False}
    answer = choices.get(update.message.text)
    if answer:
        confirm_record(update, context)
        context.user_data.clear()
        text_message = "Confirmed"
        reply_markdown(update, context, text_message)

        return ConversationHandler.END
    else:
        return ask_lunch_type(update, context)
