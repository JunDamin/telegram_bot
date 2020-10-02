import re
from telegram.ext import ConversationHandler, MessageHandler, Filters
from features.function import public_only, private_only
from conversations import sign_in, sign_out, get_back, set_remarks


# sign in sequences from group chat to private
start_sign_in_conv = MessageHandler(
    Filters.regex(re.compile("sign.{0,3} in", re.IGNORECASE)),
    public_only(sign_in.start_signing_in),
)

sign_in_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex(re.compile("^Office$|^Home$")) & Filters.private,
            sign_in.set_sub_category,
        )
    ],
    states={
        sign_in.HANDLE_SIGN_IN_LOCATION: [
            MessageHandler(Filters.location, sign_in.set_location)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# sign out sequences from group chat to private
start_sign_out_conv = MessageHandler(
    Filters.regex(re.compile("sign.{0,3} out", re.IGNORECASE)),
    public_only(sign_out.start_signing_out),
)
sign_out_conv = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.location | Filters.private, sign_out.set_location)
    ],
    states={
        sign_out.HANDLE_SIGN_OUT_LOCATION: [
            MessageHandler(Filters.location | Filters.private, sign_out.set_location)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)


# get back sequences from group chat to private

start_get_back_conv = MessageHandler(
    Filters.regex(re.compile("back from break|back to work|lunch over", re.IGNORECASE)),
    public_only(get_back.get_back_to_work),
)

get_back_conv = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex("^Alone$|^With Someone$") | Filters.private, get_back.set_lunch_location)
    ],
    states={
        get_back.HANDLE_LUNCH_LOCATION: [
            MessageHandler(Filters.location | Filters.private, get_back.set_location)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)

# set remarks

set_remarks_conv = ConversationHandler(
    entry_points=[
       MessageHandler(Filters.regex("/비고작성"), private_only(set_remarks.ask_log_id_for_remarks))
    ],
    states={
        set_remarks.HANDLE_REMARKS_LOG_ID: [
            MessageHandler(Filters.regex("[0-9]*") | Filters.private, set_remarks.ask_content_for_remarks),
        ],
        set_remarks.HANDLE_REMARKS_CONTENT: [
            MessageHandler(Filters.text | Filters.private, set_remarks.set_remarks),
        ]
    },
    fallbacks=[],
    map_to_parent={},
)

# add handlers from conversation
handlers = (
    sign_in_conv,
    start_sign_in_conv,
    start_sign_out_conv,
    sign_out_conv,
    start_get_back_conv,
    get_back_conv,
    set_remarks_conv,
)
