import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
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
