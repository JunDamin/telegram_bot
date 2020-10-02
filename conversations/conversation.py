import re
from telegram.ext import ConversationHandler, MessageHandler, Filters
from features.function import public_only
from conversations import sign_in, sign_out


start_sign_in_cov = sign_in.start_signing_in
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

start_sign_out_cov = sign_out.start_signing_out
sign_out_conv = ConversationHandler(
    entry_points=[MessageHandler(Filters.location | Filters.private, sign_out.set_location)],
    states={
        sign_out.HANDLE_SIGN_OUT_LOCATION: [
            MessageHandler(Filters.location | Filters.private, sign_out.set_location)
        ],
    },
    fallbacks=[],
    map_to_parent={},
)