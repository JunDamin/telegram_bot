import pytz
from datetime import date, timedelta
from features.db_management import (
    create_connection,
    insert_record,
    update_record,
    select_record,
    delete_record,
)
from features.text_function import make_record_text
from features.constant import LOG_COLUMN


def check_status(context, status):
    user_data = context.user_data
    user_status = user_data.get("status")
    return status == user_status


def put_sub_category(log_id, sub_category):

    conn = create_connection("db.sqlite3")
    record = {"sub_category": sub_category}
    update_record(conn, "logbook", record, log_id)
    conn.close()


def post_basic_user_data(update, context, category):
    """

    return: log_id
    """
    user = update.message.from_user

    basic_user_data = {
        "chat_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "timestamp": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
        "category": category,
    }

    conn = create_connection("db.sqlite3")
    log_id = insert_record(conn, "logbook", basic_user_data)
    conn.close()

    for key in basic_user_data:
        context.user_data[key] = basic_user_data[key]

    return log_id


def get_logs_of_today():

    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_record(
        conn,
        "logbook",
        LOG_COLUMN,
        {},
        f"strftime('%s', timestamp) \
        BETWEEN strftime('%s', '{start_date}') AND strftime('%s', '{end_date}')",
    )

    header_message = f"Today's Logging\n({date.today().isoformat()})"
    text_message = make_text_from_logs(rows, header_message)

    return text_message


def get_logs_of_the_day(the_date):

    start_date = the_date
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_record(
        conn,
        "logbook",
        LOG_COLUMN,
        {},
        f"strftime('%s', timestamp) \
        BETWEEN strftime('%s', '{start_date}') AND strftime('%s', '{end_date}')",
    )

    header_message = f"{start_date.isoformat()}'s Logging\n"
    text_message = make_text_from_logs(rows, header_message)

    return text_message


def get_today_log_of_chat_id_category(chat_id, category):
    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_record(
        conn,
        "logbook",
        LOG_COLUMN,
        {"chat_id": chat_id, "category": category},
        f" AND timestamp > '{start_date}' AND timestamp < '{end_date}' ORDER BY timestamp",
    )

    conn.close()
    return rows


def get_record_by_log_id(log_id):

    conn = create_connection("db.sqlite3")
    rows = select_record(conn, "logbook", LOG_COLUMN, {"id": log_id})
    conn.close()
    
    return rows


def get_text_of_log_by_id(log_id):

    conn = create_connection()
    rows = select_record(conn, "logbook", LOG_COLUMN, {"id": log_id})
    conn.close()
    text_message = make_text_from_logs(rows)

    return text_message


def put_location(location, user_data):
    """
    docstring
    """

    if location:
        conn = create_connection("db.sqlite3")
        record = {"longitude": location.longitude, "latitude": location.latitude}
        update_record(conn, "logbook", record, str(user_data.get("log_id")))
        conn.close()
        return True

    return False


def put_confirmation(update, context):
    conn = create_connection()
    record = {"confirmation": "user confirmed"}
    update_record(conn, "logbook", record, context.user_data.get("log_id"))


def post_work_content(update, context, work_content):

    user = update.message.from_user

    record = {
        "chat_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "timestamp": update.message.date.astimezone(pytz.timezone("Africa/Douala")),
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


def make_text_from_logs(logs, header="", footer=""):

    text_message = header

    chat_id = ""
    for row in logs:

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

    text_message += footer
    return text_message
