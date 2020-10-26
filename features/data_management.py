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
        timestamp text NOT NULL,
        category text NOT NULL,
        sub_category text,
        longitude text,
        latitude text,
        remarks text,
        confirmation text,
        work_content_id,
        history text,
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
        timestamp text NOT NULL,
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


def make_sql_select_record(
    table_name, columns, equal_condition: dict, extra_condition: str
):
    if equal_condition:
        condition_list = [
            " {} = '{}' ".format(key, equal_condition.get(key))
            for key in equal_condition.keys()
        ]
        condition = "AND ".join(condition_list)
    else:
        condition = ""
    sql = f"""SELECT {", ".join(columns)} FROM {table_name}
     {'WHERE' if condition or extra_condition else ""} {condition} {extra_condition};"""

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
    :param record: dict
    :return log id:
    """

    sql = make_sql_insert_record(table_name, record)
    print(sql)

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return cursor.lastrowid


def select_record(
    conn, table_name: str, columns: list, equal_condition: dict, extra_condition=""
):

    sql = make_sql_select_record(table_name, columns, equal_condition, extra_condition)
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


def write_csv(record, header: list, file_name: str):
    with open(file_name, mode="w", encoding="utf-8-sig") as signing_file:
        writer = csv.writer(signing_file)
        writer.writerow(header)
        writer.writerows(record)
