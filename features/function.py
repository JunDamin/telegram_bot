from features.data_management import (
    create_connection,
    update_log_category,
    update_log_sub_category,
    update_log_location,
    create_log_basic,
    select_logs_by_date,
    select_log,
)
from datetime import datetime, date, timedelta


def update_location(id, longitude, latitude):

    conn = create_connection("db.sqlite3")
    location_data = (longitude, latitude, id)
    update_log_location(conn, location_data)
    conn.close()


def update_sub_category(log_id, sub_category):

    conn = create_connection("db.sqlite3")
    sub_category = (sub_category, log_id)
    update_log_sub_category(conn, sub_category)
    conn.close()


def set_log_basic(log_basic):

    conn = create_connection("db.sqlite3")
    log_id = create_log_basic(conn, log_basic)
    conn.close()
    return log_id


def get_logs_of_today():

    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_logs_by_date(conn, start_date, end_date)

    header_message = f"Today's Logging\n({date.today().isoformat()})"
    text_message = make_text_from_logbook(rows, header_message)

    return text_message


def make_text_from_logbook(rows, header):

    text_message = header

    chat_id = ""
    for (
        log_id,
        _,
        first_name,
        last_name,
        _datetime,
        category,
        sub_category,
        longitude,
        latitude,
        remarks,
    ) in rows:

        if chat_id != _:
            chat_id = _
            text_message += f"\n\n{first_name} {last_name}'s log as below\n"
        dt = datetime.fromisoformat(_datetime)

        record = f"""
        {category} {"- " + sub_category if sub_category else ""}
        Log No.{log_id} : {dt.strftime("%H:%M")}
        location : {longitude if not longitude else "-"}, {latitude if not latitude else "-"}
        remarks : {remarks if not remarks else "-"}\n"""

        text_message += record

    return text_message


def update_category(log_id, category):

    conn = create_connection("db.sqlite3")
    category = (category, log_id)
    update_log_category(conn, category)
    conn.close()


def check_log_id(log_id):

    ans = False

    conn = create_connection("db.sqlite3")
    row = select_log(conn, log_id)
    conn.close()

    if row:
        ans = True

    return ans
