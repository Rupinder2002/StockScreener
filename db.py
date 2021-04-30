import sqlite3


def getConnectionCursor():
    return sqlite3.connect('C:/Users/ssonkar/Documents/Algo/stockscreener/persistence/db/app.db')