import pytz
from telegram import KeyboardButton
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    check_status,
    update_sub_category,
    set_basic_user_data,
    make_text_from_logbook,
    select_log_to_text,
    confirm_record,
)
from features.message import (
    reply_markdown,
    set_context,
    set_location,
    get_log_id_and_record,
    send_initiating_message_by_branch,
)

from features.data_management import (
    create_connection,
    select_log,
    delete_log,
)
from features.text_function import (
    make_text_signing_in_greeting,
    make_text_signing_in_and_ask_info,
)


# Sign in status
(ANSWER_WORKPLACE, ANSWER_LOG_DELETE, ANSWER_SIGN_IN_LOCATION, ANSWER_CONFIRMATION) = [
    "sign_in" + str(i) for i in range(4)
]


# Sign in Conv
@log_info()
def start_signing_in(update, context):

    # set variables and context
    user = update.message.from_user
    dt = update.message.date.astimezone(pytz.timezone("Africa/Douala"))
    log_id, record, is_exist = get_log_id_and_record(update, context, "signing in")
    context_dict = {"log_id": log_id, "status": "SIGN_IN"}
    set_context(update, context, context_dict)

    # set dictionary data
    rewrite_header_message = "You have already signed in as below. "
    rewrite_footer_message = "\nDo you want to *_delete it_* and sign in again? or SKIP it?"

    data_dict = {
        "new": {
            "group_message": make_text_signing_in_greeting(log_id, user.first_name, dt),
            "private_message": make_text_signing_in_and_ask_info(
                log_id, user.first_name, dt
            ),
            "keyboard": [
                ["Office", "Home"],
            ],
            "return": ANSWER_WORKPLACE,
        },
        "rewrite": {
            "group_message": make_text_from_logbook(
                [
                    record,
                ],
                rewrite_header_message,
            ),
            "private_message": make_text_from_logbook(
                (record,),
                rewrite_header_message,
                rewrite_footer_message,
            ),
            "keyboard": [
                ["Delete and Sign In Again", "SKIP"],
            ],
            "return": None,
        },
    }
    return send_initiating_message_by_branch(update, context, is_exist, data_dict)


@log_info()
def ask_confirmation_of_removal(update, context):
    log_id = context.user_data.get("log_id")
    if log_id:
        conn = create_connection()
        row = select_log(conn, log_id)
        conn.close()

        header_message = f"Do you really want to do remove log No.{log_id}?\n"
        text_message = make_text_from_logbook(row, header_message)
        keyboard = [["REMOVE SIGN IN LOG", "NO"]]

        reply_markdown(update, context, text_message, keyboard)

        return ANSWER_LOG_DELETE
    else:
        text_message = "An Error has been made. Please try again."
        reply_markdown(update, context, text_message)
        return ConversationHandler.END


def override_log_and_ask_work_type(update, context):

    choices = {"REMOVE SIGN IN LOG": True, "NO": False}
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

    log_id = set_basic_user_data(update, context, "signing in")
    context.user_data["log_id"] = log_id
    return ask_sub_category(update, context)


def ask_sub_category(update, context):

    text_message = "Would you like to share where you work?"
    keyboard = [
        ["Office", "Home"],
    ]
    reply_markdown(update, context, text_message, keyboard)

    return ANSWER_WORKPLACE


@log_info()
def set_sub_category_and_ask_location(update, context):
    """Get sub category"""

    # save log work type data
    if check_status(context, "SIGN_IN"):
        update_sub_category(context.user_data["log_id"], update.message.text)

        text_message = """I see! Please send me your location by click the button on your phone.
    1. Please check your location service is on.(if not please turn on your location service)
    2. Desktop app can not send location"""
        keyboard = [
            [
                KeyboardButton("Share Location", request_location=True),
            ],
        ]
        reply_markdown(update, context, text_message, keyboard)

    return ANSWER_SIGN_IN_LOCATION


@log_info()
def set_sign_in_location_and_ask_confirmation(update, context):
    if update.message.text == "DEROUTE":
        update.message.location = lambda x: None
        setattr(update.message.location, "longitude", 1)
        setattr(update.message.location, "latitude", 1)
        print("DEROUTED")
    user_data = context.user_data

    HEADER_MESSAGE = "You have signed in as below. Do you want to confirm?"
    if set_location(update, context):
        text_message = HEADER_MESSAGE
        keyboard = [["Confirm", "Edit"]]
        text_message += select_log_to_text(user_data.get("log_id"))

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
        return ask_sub_category(update, context)
