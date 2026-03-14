import sqlite3
from app.core.engine import create_table, add_city, get_city, creat_table, add_number, get_number



def test_add_and_get_user():
    conn = sqlite3.connect(":memory:")

    create_table(conn)
    add_city(conn, 'Grozny')
    city = get_city(conn)

    assert city == ["Grozny"]

def test_add_and_get_number():
    conn = sqlite3.connect(":memory:")

    creat_table(conn)
    add_number(conn, '11')
    number = get_number(conn)

    assert number == ['11']
    conn.close()