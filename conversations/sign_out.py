import pytz
from telegram import KeyboardButton
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
    set_basic_user_data,
    make_text_from_logbook,
    select_log_to_text,
    confirm_record,
    set_work_content,
    delete_log_and_content,
    delete_content,
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
)

# Sign out
(
    ANSWER_WORK_TYPE,
    ANSWER_WORK_CONTENT,
    ANSWER_CONTENT_CONFIRMATION,
    ANSWER_LOG_DELETE,
    ANSWER_SIGN_OUT_LOCATION,
    ANSWER_CONFIRMATION,
) = ["sign_out" + str(i) for i in range(6)]


# Sign out conv
@log_info()
def start_signing_out(update, context):

    # set variables and context
    user = update.message.from_user
    dt = update.message.date.astimezone(pytz.timezone("Africa/Douala"))
    log_id, record, is_exist = get_log_id_and_record(update, context, "signing out")
    context_dict = {"log_id": log_id, "status": "SIGN_OUT"}
    set_context(update, context, context_dict)

    SIGN_OUT_GREETING = (
        f"""Good evening, {user.first_name}.\nYou have signed out today."""
    )
    dt = update.message.date.astimezone(pytz.timezone("Africa/Douala"))
    SIGN_TIME = f"""signing time: {dt.strftime("%m-%d *__%H:%M__*")}"""
    ASK_INFO = "Would you like to share your today's content of work?"
    CHECK_DM = """"Please check my DM(Direct Message) to you"""

    # set dictionary data
    rewrite_header_message = "You have already signed out as below. "
    rewrite_footer_message = (
        "\nDo you want to delete it and sign out again? or SKIP it?"
    )

    data_dict = {
        "new": {
            "group_message": f"{SIGN_OUT_GREETING}\n{CHECK_DM}\n{SIGN_TIME}",
            "private_message": f"{SIGN_OUT_GREETING}\n{ASK_INFO}\n{SIGN_TIME}",
            "keyboard": [
                [
                    "I worked at Office",
                    "I would like to report because I worked at home",
                ]
            ],
            "return": ANSWER_WORK_TYPE,
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
                ["Delete and Sign Out Again", "SKIP"],
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
        keyboard = [["REMOVE SIGN OUT LOG", "NO"]]

        reply_markdown(update, context, text_message, keyboard)

        return ANSWER_LOG_DELETE
    else:
        text_message = "An Error has been made. Please try again."
        reply_markdown(update, context, text_message)
        return ConversationHandler.END


def override_log(update, context):

    choices = {"REMOVE SIGN OUT LOG": True, "NO": False}
    answer = choices.get(update.message.text)
    if answer:
        log_id = delete_log_and_content(update, context)
        text_message = f"Log No. {log_id} has been Deleted\n"
        reply_markdown(update, context, text_message)
    else:
        text_message = "process has been stoped. The log has not been deleted."
        reply_markdown(update, context, text_message)
        return ConversationHandler.END
    log_id = set_basic_user_data(update, context, "signing out")
    context.user_data["log_id"] = log_id
    return ask_work_type(update, context)


def ask_sign_out_location(update, context):
    text_message = """I see! Please send me your location by click the button on your phone.
    1. Please check your location service is on.\n(if not please turn on your location service)
    2. Desktop app can not send location"""
    keyboard = [
        [
            KeyboardButton(
                """Share location infomation for signing out""",
                request_location=True,
            ),
        ]
    ]

    reply_markdown(update, context, text_message, keyboard)

    return ANSWER_SIGN_OUT_LOCATION


@log_info()
def set_sign_out_location(update, context):
    if update.message.text == "DEROUTE":
        update.message.location = lambda x: None
        setattr(update.message.location, "longitude", 1)
        setattr(update.message.location, "latitude", 1)
        print("DEROUTED")
    user_data = context.user_data
    HEADER_MESSAGE = "You have signed out as below. Do you want to confirm?"
    if set_location(update, context):
        text_message = HEADER_MESSAGE
        keyboard = [["Confirm", "Edit"]]
        text_message += select_log_to_text(user_data.get("log_id"))

        reply_markdown(update, context, text_message, keyboard)

        return ANSWER_CONFIRMATION
    else:
        return ConversationHandler.END


def confirm_the_data(update, context):
    print("test")
    choices = {"Confirm": True, "Edit": False}
    answer = choices.get(update.message.text)
    if answer:
        confirm_record(update, context)
        context.user_data.clear()
        text_message = "Confirmed"
        reply_markdown(update, context, text_message)
        return ConversationHandler.END
    else:
        return ask_work_type(update, context)


def ask_work_type(update, context):
    delete_content(update, context)
    text_message = "Would you like to share your today's content of work?"
    keyboard = [
        ["I worked at Office", "I would like to report because I worked at home"]
    ]

    reply_markdown(update, context, text_message, keyboard)

    return ANSWER_WORK_TYPE


@log_info()
def ask_work_content(update, context):

    text_message = "OK. Please text me what you have done today for work briefly."
    reply_markdown(update, context, text_message)

    return ANSWER_WORK_CONTENT


@log_info()
def check_work_content(update, context):

    answer = update.message.text

    context.user_data["work_content"] = answer
    text_message = f"Content of Work\n{answer}\n\nIs it ok?"
    keyboard = [["YES", "NO"]]
    reply_markdown(update, context, text_message, keyboard)

    return ANSWER_CONTENT_CONFIRMATION


@log_info()
def save_content_and_ask_location(update, context):
    print(context.user_data.get("work_content"))
    set_work_content(update, context, context.user_data.get("work_content"))

    return ask_sign_out_location(update, context)
