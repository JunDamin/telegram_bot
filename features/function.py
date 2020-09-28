from features.data_management import (
    create_connection,
    update_log_type,
    update_log_location,
    create_log_basic,
)


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
