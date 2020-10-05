import re
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, Filters
from features.function import public_only, private_only
from conversations import sign_in, sign_out, get_back, set_remarks, remove_log


def cancel(update, context):
    update.message.reply_text("Bye!", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


# sign in sequences from group chat to private
start_sign_in_conv = MessageHandler(
    Filters.regex(re.compile("sign.{0,3} in.?$", re.IGNORECASE)),
    public_only(sign_in.start_signing_in),
)

sign_in_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex(re.compile("^Office$|^Home$")) & Filters.private,
            sign_in.set_sub_category,
        ),
        MessageHandler(
            Filters.regex("^Delete and Sign In Again$") & Filters.private,
            sign_in.ask_confirmation_of_removal,
        ),
    ],
    states={
        sign_in.HANDLE_LOG_DELETE: [
            MessageHandler(
                Filters.regex("^REMOVE SIGN IN LOG$|^NO$") & Filters.private,
                sign_in.override_log,
            )
        ],
        sign_in.HANDLE_WORKPLACE: [
            MessageHandler(
                Filters.regex(re.compile("^Office$|^Home$")) & Filters.private,
                sign_in.set_sub_category,
            ),
        ],
        sign_in.HANDLE_SIGN_IN_LOCATION: [
            MessageHandler(Filters.location, sign_in.set_sign_in_location)
        ],
        sign_in.ASK_CONFIRMATION: [
            MessageHandler(Filters.regex("^Confirm$|^Edit$"), sign_in.confirm_the_data)
        ],
    },
    fallbacks=[MessageHandler(Filters.regex("^SKIP$"), cancel)],
    map_to_parent={},
)


# get back sequences from group chat to private
start_get_back_conv = MessageHandler(
    Filters.regex(
        re.compile("back from break.?$|back to work.?$|lunch over.?$", re.IGNORECASE)
    ),
    public_only(get_back.get_back_to_work),
)

get_back_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex("^Without any member of KOICA$|^With KOICA Colleagues$")
            & Filters.private,
            get_back.set_lunch_location,
        ),
        MessageHandler(
            Filters.regex("^Delete and Get Back to Work Again$") & Filters.private,
            get_back.ask_confirmation_of_removal,
        ),
    ],
    states={
        get_back.HANDLE_LOG_DELETE: [
            MessageHandler(
                Filters.regex("^REMOVE GET BACK LOG$|^NO$") & Filters.private,
                get_back.override_log,
            )
        ],
        get_back.HANDLE_LUNCH_TYPE: [
            MessageHandler(
                Filters.regex("^Without any member of KOICA$|^With KOICA Colleagues$")
                & Filters.private,
                get_back.set_lunch_location,
            ),
        ],
        get_back.HANDLE_LUNCH_LOCATION: [
            MessageHandler(
                Filters.location & Filters.private, get_back.set_get_back_location
            )
        ],
        get_back.ASK_CONFIRMATION: [
            MessageHandler(Filters.regex("^Confirm$|^Edit$"), get_back.confirm_the_data)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# sign out sequences from group chat to private
start_sign_out_conv = MessageHandler(
    Filters.regex(re.compile("sign.{0,3} out.?$", re.IGNORECASE)),
    public_only(sign_out.start_signing_out),
)
sign_out_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.location & Filters.private, sign_out.set_sign_out_location
        ),
        MessageHandler(
            Filters.regex("^Delete and Sign Out Again$") & Filters.private,
            sign_out.ask_confirmation_of_removal,
        ),
    ],
    states={
        sign_out.HANDLE_LOG_DELETE: [
            MessageHandler(
                Filters.regex("^REMOVE SIGN OUT LOG$|^NO$") & Filters.private,
                sign_out.override_log,
            )
        ],
        sign_out.HANDLE_SIGN_OUT_LOCATION: [
            MessageHandler(
                Filters.location & Filters.private, sign_out.set_sign_out_location
            )
        ],
        sign_out.ASK_CONFIRMATION: [
            MessageHandler(Filters.regex("^Confirm$|^Edit$"), sign_out.confirm_the_data)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# set remarks

set_remarks_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex("/비고작성"), private_only(set_remarks.ask_log_id_for_remarks)
        )
    ],
    states={
        set_remarks.HANDLE_REMARKS_LOG_ID: [
            MessageHandler(
                Filters.regex("[0-9]*") & Filters.private,
                set_remarks.ask_content_for_remarks,
            ),
        ],
        set_remarks.HANDLE_REMARKS_CONTENT: [
            MessageHandler(Filters.text & Filters.private, set_remarks.set_remarks),
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# delete log conversation

remove_log_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex("/로그삭제"), private_only(remove_log.ask_log_id_to_remove)
        )
    ],
    states={
        remove_log.HANDLE_DELETE_LOG_ID: [
            MessageHandler(
                Filters.regex("[0-9]*") & Filters.private,
                remove_log.ask_confirmation_of_removal,
            ),
        ],
        remove_log.HANDLE_LOG_DELETE: [
            MessageHandler(
                Filters.regex("^YES$|^NO$") & Filters.private, remove_log.remove_log
            ),
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# add handlers from conversation
handlers = (
    sign_in_conv,
    start_sign_in_conv,
    start_get_back_conv,
    get_back_conv,
    start_sign_out_conv,
    sign_out_conv,
    set_remarks_conv,
    remove_log_conv,
)
