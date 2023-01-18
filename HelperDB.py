import sqlite3
from sqlite3 import Error


class Users:
    PHONE_NUMBER = "Phone_number"
    NAME = "Name"
    PROFILE_PICTURE = "Profile_picture"
    PASSWORD_HASH = "Password_hash"


def __dict_factory__(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = __dict_factory__
    except Error as e:
        print(e)
    finally:
        return conn


def create_users_table(conn):
    try:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            Phone_number text PRIMARY KEY,
            Name text NOT NULL,
            Profile_picture text,
            Password_hash text); 
        """)
    except Error as e:
        print(e)


def add_user(conn, user):
    sql = ''' INSERT INTO users(Phone_number,Name,Profile_picture,Password_hash)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def get_users(conn, phone_number, args='*'):
    cur = conn.cursor()
    cur.execute(f"SELECT {args} FROM users WHERE Phone_number=?", (phone_number,))
    return cur.fetchall()
