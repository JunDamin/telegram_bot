from features.data_management import (
    create_connection,
    update_log_type,
    update_log_location,
)


def set_location(id, longitude, latitude):
    
    conn = create_connection("db.sqlite3")
    location_data = (
        longitude,
        latitude,
        id
    )
    update_log_location(conn, location_data)
    conn.close()


def set_work_type(id, category):

    conn = create_connection("db.sqlite3")
    work_type = (category, id)
    update_log_type(conn, work_type)
    conn.close()
