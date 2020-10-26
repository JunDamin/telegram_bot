import pytz
from telegram import KeyboardButton
from telegram.ext import ConversationHandler
from features.log import log_info
from features.function import (
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
    delete_record,
    select_record
)
from features.constant import LOG_COLUMN

# Lunch break
ANSWER_LOG_DELETE, ANSWER_LUNCH_TYPE, ANSWER_LUNCH_LOCATION, ANSWER_CONFIRMATION = [
    "get_back" + str(i) for i in range(4, 8)
]


@log_info()
def get_back_to_work(update, context):

    # set variables and context
    user = update.message.from_user
    dt = update.message.date.astimezone(pytz.timezone("Africa/Douala"))
    log_id, record, is_exist = get_log_id_and_record(update, context, "getting back")
    context_dict = {"log_id": log_id, "status": "GET_BACK"}
    set_context(update, context, context_dict)

    GET_BACK_GREETING = f"""Good afternoon, {user.first_name}.\n
Welcome back. You have been logged with Log No.{log_id}"""
    dt = update.message.date.astimezone(pytz.timezone("Africa/Douala"))
    SIGN_TIME = f"""signing time: {dt.strftime("%m-%d *__%H:%M__*")}"""
    ASK_INFO = """Did you have lunch with KOICA collagues?"""
    CHECK_DM = """"Please check my DM(Direct Message) to you"""

    # set dictionary data
    rewrite_header_message = "You have already signed out as below. "
    rewrite_footer_message = "\nDo you want to delete it and sign out again? or SKIP it?"

    data_dict = {
        "new": {
            "group_message": f"{GET_BACK_GREETING}\n{CHECK_DM}\n{SIGN_TIME}",
            "private_message": f"{GET_BACK_GREETING}\n{ASK_INFO}\n{SIGN_TIME}",
            "keyboard": [
                ["Without any member of KOICA", "With KOICA Colleagues"],
            ],
            "return": ANSWER_LUNCH_TYPE
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
                ["Delete and Get Back to Work Again", "SKIP"],
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
        row = select_record(conn, "logbook", LOG_COLUMN, {"id": log_id})
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
        delete_record(conn, "logbook", {"id": log_id})
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
