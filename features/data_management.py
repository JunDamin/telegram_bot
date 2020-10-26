import csv
from collections import deque
import sqlite3
from sqlite3 import Error
from typing import Optional


def start_database():
    # DB Setting
    database = "db.sqlite3"
    sql_tuple = (
        """CREATE TABLE IF NOT EXISTS logbook (
        id integer PRIMARY KEY,
        chat_id text NOT NULL,
        first_name text NOT NULL,
        last_name text NOT NULL,
        datetime text NOT NULL,
        category text NOT NULL,
        sub_category text,
        longitude text,
        latitude text,
        remarks text,
        confirmation text,
        FOREIGN KEY (work_content_id) REFERENCES contents(id)
    );""",
        """CREATE TABLE IF NOT EXISTS users (
        chat_id text PRIMARY KEY,
        first_name text NOT NULL,
        last_name text NOT NULL,
        status text,
        remarks text
    );""",
        """CREATE TABLE IF NOT EXISTS contents (
        id integer PRIMARY KEY,
        chat_id text NOT NULL,
        first_name text NOT NULL,
        last_name text NOT NULL,
        datetime text NOT NULL,
        work_content text,
        remarks text
    );""",
    )

    conn = create_connection(database)
    if conn is not None:
        # Create Project table
        deque(map(lambda x: create_table(conn, x), sql_tuple))
    conn.close()


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


def make_sql_insert_record(table_name: str, record: dict):
    """
    docstring
    """
    keys = record.keys()
    values = tuple([str(record[key]) for key in keys])
    sql = f"""INSERT INTO {table_name}({", ".join(keys)})
    VALUES{values};"""

    return sql


def make_sql_select_record(table_name, columns, condition):
    condition_list = [
        " {} = '{}' ".format(key, condition.get(key)) for key in condition.keys()
    ]

    sql = f"""SELECT {", ".join(columns)} FROM {table_name}
     WHERE {", ".join(condition_list)};"""

    return sql


def make_sql_update_record(
    table_name: str, record: dict, pk: str, pk_name: Optional[str] = "id"
) -> str:
    """
    docstring
    """
    keys = record.keys()

    sql = f"""UPDATE {table_name} SET {', '.join(["{} = '{}'".format(key, record[key]) for key in keys])}
    WHERE {pk_name} = {pk};"""

    return sql


def make_sql_delete_record(table_name, condition):
    condition_list = [
        " {} = '{}' ".format(key, condition.get(key)) for key in condition.keys()
    ]

    sql = f"""DELETE FROM {table_name}
     WHERE {", ".join(condition_list)};"""

    return sql


def insert_record(conn, table_name: str, record: dict):
    """
    Create a new log into logbook table
    :param conn:
    :param record: (chat_id, frist_name, last_name, datetime, category, sub_category, longitude, latitude)
    :return log id:
    """

    sql = make_sql_insert_record(table_name, record)
    print(sql)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def select_record(conn, table_name: str, columns: list, condition: dict):

    sql = make_sql_select_record(table_name, columns, condition)
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)

    rows = cursor.fetchall()

    return rows


def update_record(conn, table_name: str, record: dict, pk):

    sql = make_sql_update_record(table_name, record, pk)
    print(sql)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def delete_record(conn, table_name: str, condition: dict):

    sql = make_sql_delete_record(table_name, condition)
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    return cursor.lastrowid


def create_log_basic(conn, record):
    """
    Create a new log into logbook table
    :param conn:
    :param log: log info
    :return log id:
    """

    sql = make_sql_insert_record("logbook", record)
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def update_log_category(conn, record, log_id):
    """
    :param conn:
    :param categroy:
    :return log id:
    """

    sql = make_sql_update_record("logbook", record, log_id)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def update_log_sub_category(conn, record, log_id):
    """
    :param conn:
    :param sub_categroy:
    :return log id:
    """

    sql = make_sql_update_record("logbook", record, log_id)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def update_log_location(conn, record, log_id):
    """
    :param conn:
    :param sub_categroy:
    :return log id:
    """

    sql = make_sql_update_record("logbook", record, log_id)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def update_log_confirmation(conn, record, log_id):
    """
    :param conn:
    :param data: (confirmation, id)
    :return log id:
    """

    sql = make_sql_update_record("logbook", record, log_id)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def select_all_logs(conn):
    """"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logbook")

    rows = cursor.fetchall()

    return rows


def write_csv(record, header: list, file_name: str):
    with open(file_name, mode="w", encoding="utf-8-sig") as signing_file:
        writer = csv.writer(signing_file)
        writer.writerow(header)
        writer.writerows(record)


def select_logs_by_chat_id(conn, chat_id):
    """"""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM logbook WHERE chat_id = {chat_id} ORDER BY datetime DESC LIMIT 6"
    )

    rows = cursor.fetchall()

    return rows


def select_log_by_chat_id_category_date(conn, chat_id, category, start_date, end_date):
    """"""
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT * FROM logbook \
         WHERE (chat_id = '{chat_id}'
         AND category = '{category}'
         AND datetime > '{start_date}'
         AND datetime <'{end_date}')
         ORDER BY datetime;"""
    )

    rows = cursor.fetchall()

    return rows


def update_remarks(conn, record, log_id):

    sql = make_sql_update_record("logbook", record, log_id)

    cursor = conn.cursor()
    cursor.execute(sql)
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
