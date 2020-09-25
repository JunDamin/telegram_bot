import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """Create a database connection to a SQLite
    :param db_file: database address
    :return conn: Connection to the database"""

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """
    Create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: A CREATE TABLE statement
    :return:
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        return True
    except Error as e:
        print(e)

    return None


def create_attendee_basic(conn, attendee):
    """
    Create a new attendance into attendance table
    :param conn:
    :param attendee: Attendance info
    :return attendee id:
    """

    sql = """INSERT INTO attendance(chat_id, first_name, last_name, datetime, type)
    VALUES(?, ?, ?, ?, ?)"""

    cursor = conn.cursor()
    cursor.execute(sql, attendee)
    conn.commit()
    return cursor.lastrowid


def update_attendee_type(conn, work_type):
    """
    :param conn:
    :param work_type:
    :return attendee id:
    """

    sql = """UPDATE attendance
        SET work_type = ?
        WHERE id = ?"""

    cursor = conn.cursor()
    cursor.execute(sql, work_type)
    conn.commit()
    return cursor.lastrowid


def update_attendee_location(conn, location_data):
    """
    :param conn:
    :param work_type:
    :return attendee id:
    """

    sql = """UPDATE attendance
        SET longitude = ?,
            latitude = ?
        WHERE id = ?"""

    cursor = conn.cursor()
    cursor.execute(sql, location_data)
    conn.commit()
    return cursor.lastrowid


def select_all_atendee(conn):
    """
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance")

    rows = cursor.fetchall()

    return rows
