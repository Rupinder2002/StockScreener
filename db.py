import sqlite3


def getConnectionCursor():
    return sqlite3.connect('./app2.db')