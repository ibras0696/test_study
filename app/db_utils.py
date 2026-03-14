import sqlite3

def create_table(conn):
    conn.execute('CREATE TABLE city (name TEXT)')

def add_city(conn,name):
    conn.execute('INSERT INTO city (name) VALUES (?)', (name,))
    conn.commit()

def get_city(conn):
    cursor = conn.execute('SELECT name FROM city')
    return [res[0] for res in cursor.fetchall()]




def creat_table(conn):
    conn.execute('CREATE TABLE number(num TEXT)')

def add_number(conn, num):
    conn.execute('INSERT INTO number (num) VALUES (?)', (num,))
    conn.commit()

def get_number(conn):
    cursor = conn.execute('SELECT num FROM number')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        number = row[0]
        if int(number) > 10:
            result.append(number)

    return result
