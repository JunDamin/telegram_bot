from features.data_management import (
    create_connection,
    update_log_type,
    update_log_location,
    create_log_basic,
    select_logs_by_date,
)
from datetime import datetime, date, timedelta


def update_location(id, longitude, latitude):

    conn = create_connection("db.sqlite3")
    location_data = (
        longitude,
        latitude,
        id
    )
    update_log_location(conn, location_data)
    conn.close()


def update_work_type(id, category):

    conn = create_connection("db.sqlite3")
    work_type = (category, id)
    update_log_type(conn, work_type)
    conn.close()


def set_log_basic(log_basic):

    conn = create_connection("db.sqlite3")
    log_id = create_log_basic(conn, log_basic)
    conn.close()
    return log_id


def select_log(conn, log_id):
    """
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logbook WHERE id=?", (log_id,))

    row = cursor.fetchall()

    return row


def get_logs_of_today():

    start_date = date.today()
    end_date = start_date + timedelta(1)

    conn = create_connection("db.sqlite3")
    rows = select_logs_by_date(conn, start_date, end_date)

    text_message = f"Today's Logging\n({date.today().isoformat()})"
    chat_id = ""
    for log_id, _, first_name, last_name, _datetime, sign_type, work_type, longitude, latitude, remarks in rows:
        
        if chat_id != _:
            chat_id = _
            text_message += f"\n\n{first_name} {last_name}'s log as below\n"
        dt = datetime.fromisoformat(_datetime)

        record = f"""
        Log No.{log_id} : {dt.strftime("%H:%M")}
        {sign_type} {": " + work_type if work_type else ""}
        location : {longitude}, {latitude}
        remarks : {remarks}\n"""

        text_message += record

    return text_message
