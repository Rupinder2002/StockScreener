import pandas as pd
import sqlite3
import db

def runStratey():
    connection = db.getConnectionCursor()
    cursor = connection.cursor()
    cursor.execute('''select symbol from stock''')
    stocks = cursor.fetchone()
    for stock in stocks:
        df = pd.read_sql('select * from stock_price', connection)
        if df.empty:
            continue
        df['20sma'] = df['Close'].rolling(window=20).mean()
        df['stddev'] = df['Close'].rolling(window=20).std()
         
        return df


    

