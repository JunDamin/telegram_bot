import re
from telegram.ext import ConversationHandler, MessageHandler, Filters
from features.callback_function import (
    HANDLE_SIGN_IN_LOCATION,
    HANDLE_WORKPLACE,
    SUB_CATEGORY,
    HANDLE_SIGN_OUT_LOCATION,
    start_signing_in,
    set_sub_category,
    set_location,
    start_signing_out,
)
from features.function import public_only


sign_in_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex(re.compile("sign.{0,3} in", re.IGNORECASE)),
            public_only(start_signing_in),
        )
    ],
    states={
        HANDLE_WORKPLACE: [
            MessageHandler(Filters.regex(SUB_CATEGORY), set_sub_category),
            MessageHandler(
                Filters.text & ~Filters.regex(SUB_CATEGORY), start_signing_in
            ),
        ],
        HANDLE_SIGN_IN_LOCATION: [MessageHandler(Filters.location, set_location)],
    },
    fallbacks=[],
    map_to_parent={},
)


sign_out_conv = ConversationHandler(
    entry_points=[
        MessageHandler(
            Filters.regex(re.compile("sign.{0,3} out", re.IGNORECASE)),
            public_only(start_signing_out),
        )
    ],
    states={
        HANDLE_SIGN_OUT_LOCATION: [MessageHandler(Filters.location, set_location)],
    },
    fallbacks=[],
    map_to_parent={},
)