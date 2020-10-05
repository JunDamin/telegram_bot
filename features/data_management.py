import csv
import sqlite3
from sqlite3 import Error


def create_connection(db_file="db.sqlite3"):
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


def insert_record(conn, record):
    """
    Create a new log into logbook table
    :param conn:
    :param record: (chat_id, frist_name, last_name, datetime, category, sub_category, longitude, latitude)
    :return log id:
    """

    sql = """INSERT INTO logbook(chat_id, first_name, last_name, datetime, category, sub_category, logitude, latitude)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""

    cursor = conn.cursor()
    cursor.execute(sql, record)
    conn.commit()
    return cursor.lastrowid


def create_log_basic(conn, log):
    """
    Create a new log into logbook table
    :param conn:
    :param log: log info
    :return log id:
    """

    sql = """INSERT INTO logbook(chat_id, first_name, last_name, datetime, category)
    VALUES(?, ?, ?, ?, ?)"""

    cursor = conn.cursor()
    cursor.execute(sql, log)
    conn.commit()
    return cursor.lastrowid


def update_log_category(conn, category, log_id):
    """
    :param conn:
    :param categroy:
    :return log id:
    """

    sql = """UPDATE logbook
        SET category = ?
        WHERE id = ?"""

    data = (category, log_id)

    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    return cursor.lastrowid


def update_log_sub_category(conn, sub_category):
    """
    :param conn:
    :param sub_categroy:
    :return log id:
    """

    sql = """UPDATE logbook
        SET sub_category = ?
        WHERE id = ?"""

    cursor = conn.cursor()
    cursor.execute(sql, sub_category)
    conn.commit()
    return cursor.lastrowid


def update_log_location(conn, location_data):
    """
    :param conn:
    :param sub_categroy:
    :return log id:
    """

    sql = """UPDATE logbook
        SET longitude = ?,
            latitude = ?
        WHERE id = ?"""

    cursor = conn.cursor()
    cursor.execute(sql, location_data)
    conn.commit()
    return cursor.lastrowid


def update_log_confirmation(conn, data):
    """
    :param conn:
    :param data: (confirmation, id)
    :return log id:
    """

    sql = """UPDATE logbook
        SET confirmation = ?
        WHERE id = ?"""

    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    return cursor.lastrowid


def select_all_logs(conn):
    """"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logbook")

    rows = cursor.fetchall()

    return rows


def write_csv(record):
    with open("signing.csv", mode="w", encoding="utf-8-sig") as signing_file:
        fieldnames = [
            "id",
            "chat_id",
            "first_name",
            "last_name",
            "datetime",
            "category",
            "sub_category",
            "longitude",
            "latitude",
            "remarks",
        ]
        writer = csv.writer(signing_file)
        writer.writerow(fieldnames)
        writer.writerows(record)


def select_logs_by_chat_id(conn, chat_id):
    """"""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM logbook WHERE chat_id = {chat_id} ORDER BY id DESC LIMIT 6"
    )

    rows = cursor.fetchall()

    return rows


def select_log_by_chat_id_category_date(conn, chat_id, category, start_date, end_date):
    """"""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM logbook \
        WHERE (chat_id = '{chat_id}' AND category = '{category}' AND datetime > '{start_date}' AND '{end_date}') ORDER BY datetime;"
    )

    rows = cursor.fetchall()

    return rows


def update_remarks(conn, log_id, content):

    data = (content, log_id)
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE logbook
        SET remarks = ?
        WHERE id = ?""",
        data,
    )
    conn.commit()


def select_logs_by_date(conn, start_date, end_date):

    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM logbook \
        WHERE strftime('%s', datetime) \
        BETWEEN strftime('%s', '{start_date}') AND strftime('%s', '{end_date}') ORDER BY first_name;"
    )
    rows = cursor.fetchall()

    return rows


def select_log(conn, log_id):
    """"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logbook WHERE id = ?", (log_id,))

    row = cursor.fetchall()

    return row


def delete_log(conn, log_id):
    """"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logbook WHERE id = ?;", (log_id,))
    conn.commit()
