import pytz
from datetime import date, timedelta
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from features.data_management import (
    create_connection,
    update_log_category,
    update_log_sub_category,
    update_log_location,
    create_log_basic,
    select_logs_by_date,
    select_log,
    select_log_by_chat_id_category_date,
    update_log_confirmation,
    insert_record,
    update_record,
    select_record,
    delete_record,
)
from features.text_function import make_record_text


def check_status(context, status):
    user_data = context.user_data
    user_status = user_data.get("status")
    return status == user_status


def private_only(func):
    def wrapper(*args, **kwargs):
        chat_type = args[0].message.chat.type
        if chat_type == "private":
            return func(*args, **kwargs)
        else:
            args[0].message.reply_text("please send me as DM(Direct Message)")

    return wrapper


def public_only(func):
    def wrapper(*args, **kwargs):
        chat_type = args[0].message.chat.type
        print(chat_type)
        if chat_type == "group":
            return func(*args, **kwargs)
        else:
            args[0].message.reply_text("please send in the group chat")

    return wrapper


def update_sub_category(log_id, sub_category):

    conn = create_connection("db.sqlite3")
    record = {"sub_category": sub_category}
    update_log_sub_category(conn, record, log_id)
    conn.close()


def set_basic_user_data(update, context, category):
    """

    return: log_id
    """
    user = update.message.from_user

    basic_user_data = {
        "chat_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "datetime": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "category": category,
    }

    conn = create_connection("db.sqlite3")
    log_id = create_log_basic(conn, basic_user_data)
    conn.close()

    for key in basic_user_data:
        context.user_data[key] = basic_user_data[key]

    return log_id


def get_logs_of_today():

    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_logs_by_date(conn, start_date, end_date)

    header_message = f"Today's Logging\n({date.today().isoformat()})"
    text_message = make_text_from_logbook(rows, header_message)

    return text_message


def get_logs_of_the_day(the_date):

    start_date = the_date
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_logs_by_date(conn, start_date, end_date)

    header_message = f"{start_date.isoformat()}'s Logging\n"
    text_message = make_text_from_logbook(rows, header_message)

    return text_message


def get_today_log_of_chat_id_category(chat_id, category):
    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_log_by_chat_id_category_date(
        conn, chat_id, category, start_date, end_date
    )
    conn.close()
    return rows


def make_text_from_logbook(rows, header=""):

    text_message = header

    chat_id = ""
    for row in rows:
        
        user_id = row[1]
        first_name = row[2]
        last_name = row[3]
        work_content_id = row[-1]

        if chat_id != user_id:
            chat_id = user_id
            text_message += f"\n\n*_{first_name} {last_name}_'s log as below*\n"

        record = make_record_text(row)

        if work_content_id:
            conn = create_connection()
            rows = select_record(
                conn, "contents", ["work_content"], {"id": work_content_id}
            )
            work_content = rows[0][0].replace("\\n", "\n")
            record += f"    work content : {work_content} \n"
        text_message += record

    return text_message


def update_category(log_id, category):

    conn = create_connection("db.sqlite3")
    record = {"category": category}
    update_log_category(conn, record, log_id)
    conn.close()


def check_log_id(log_id):

    ans = False

    conn = create_connection("db.sqlite3")
    row = select_log(conn, log_id)
    conn.close()
    if row:
        ans = True

    return ans


def select_log_to_text(log_id):

    conn = create_connection()
    rows = select_log(conn, log_id)
    conn.close()
    text_message = make_text_from_logbook(rows)

    return text_message


def put_location(location, user_data):
    """
    docstring
    """

    if location:
        conn = create_connection("db.sqlite3")
        record = {"longitude": location.longitude, "latitude": location.latitude}
        update_log_location(conn, record, str(user_data.get("log_id")))
        conn.close()
        return True

    return False


def set_location(update, context):
    user_location = update.message.location
    user_data = context.user_data
    if put_location(user_location, user_data):
        return 1
    else:
        update.message.reply_text(
            """Something went wrong. Please try again""",
            reply_markup=ReplyKeyboardRemove(),
        )
        return 0


def confirm_record(update, context):
    conn = create_connection()
    record = {"confirmation": "user confirmed"}
    update_log_confirmation(conn, record, context.user_data.get("log_id"))


def set_work_content(update, context, work_content):

    user = update.message.from_user

    record = {
        "chat_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "datetime": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "work_content": work_content,
    }

    conn = create_connection()
    content_id = insert_record(conn, "contents", record)
    logbook_record = {"work_content_id": content_id}
    update_record(conn, "logbook", logbook_record, context.user_data.get("log_id"))
    conn.close()


def delete_log_and_content(update, context):
    """"""

    log_id = context.user_data.get("log_id")
    conn = create_connection()
    work_content_id = select_record(
        conn, "logbook", ["work_content_id"], {"id": log_id}
    )[0][0]
    delete_record(conn, "contents", {"id": work_content_id})
    delete_record(conn, "logbook", {"id": log_id})

    return log_id


def delete_content(update, context):

    log_id = context.user_data.get("log_id")
    conn = create_connection()
    work_content_id = select_record(
        conn, "logbook", ["work_content_id"], {"id": log_id}
    )[0][0]
    update_record(conn, "logbook", {"work_content_id": ""}, log_id)
    delete_record(conn, "contents", {"id": work_content_id})
    return log_id


def send_markdown(update, context, user_id, text_message, reply_keyboard=False):

    text_message = text_message.replace(".", "\\.")
    text_message = text_message.replace("-", "\\-")

    context.bot.send_message(
        chat_id=user_id,
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        if reply_keyboard
        else ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def reply_markdown(update, context, text_message, reply_keyboard=False):

    text_message = convert_text_to_md(text_message)

    update.message.reply_markdown_v2(
        text=text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        if reply_keyboard
        else ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def convert_text_to_md(text):
    convert_dict = {
        ".": "\\.",
        "-": "\\-",
        "!": "\\!",
        "(": "\\(",
        ")": "\\)",
        "+": "\\+",
    }
    for key in convert_dict:
        text = text.replace(key, convert_dict[key])

    return text
