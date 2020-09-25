from features.data_management import (
    create_connection,
    create_attendee_basic,
    select_all_atendee,
    update_attendee_type,
    update_attendee_location,
    write_csv,
)


def set_location(id, longitude, latitude):
    
    conn = create_connection("db.sqlite3")
    location_data = (
        longitude,
        latitude,
        id
    )
    update_attendee_location(conn, location_data)
    conn.close()


def set_work_type(id, category):
    
    conn = create_connection("db.sqlite3")
    work_type = (category, id)
    update_attendee_type(conn, work_type)
    conn.close()
