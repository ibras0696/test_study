import sqlite3

DATA_BASE_URL = 'data.db'


def get_con():
    with sqlite3.connect(DATA_BASE_URL) as conn:
        yield conn


def create_table(conn: sqlite3.connect):
    conn.execute('CREATE TABLE number(num TEXT)')


