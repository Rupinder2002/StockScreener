import db
import sqlite3
import patterns


connection = db.getConnectionCursor()
cursor = connection.cursor()
for key, value in patterns.patterns.items():
    cursor.execute('''INSERT into patterns (key,name) values (?,?)''',(key,value))
    connection.commit()
    