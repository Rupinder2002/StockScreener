from nsetools import Nse
import insert
from datetime import date
from nsepy import get_history
import sqlite3
#import streamlit as st
from datetime import date,timedelta
#import db
from datetime import datetime

def updateTableList(connection):
    nse = Nse()
    all_stock_codes = nse.get_stock_codes(cached=False)
    all_stock_codes.pop('SYMBOL',None)
    insert.insertStock(all_stock_codes,connection)
    insert.insertPattern(connection)
    insert.insertsectors(connection)
    insert.insertstrategies(connection)

def updateStocksPrice(st,connection): 
    cursor = connection.cursor()
    cursor.execute('select Date from stock_price where symbol = "ZYDUSWELL" order by Date desc')
    start_date = cursor.fetchone()
    if start_date is None:
        start_date = date.today()
    else:    
        start_date = datetime.strptime(start_date[0], '%Y-%m-%d') + timedelta(1)
        start_date = start_date.date()
    end=date.today()
    first,last = st.beta_columns(2)
    first.subheader(f'Start Date : {start_date}')
    last.subheader(f'End Date : {end}')
    try:
        cursor.execute('''select symbol from stock''')
        stocks_symbols = cursor.fetchall()
        my_bar = st.progress(0)
        percent_complete = 1 
        i = 1  
        for symbol in stocks_symbols:
            percent_complete =  int( (i/len(stocks_symbols)) * 100)
            i=i+1    
            stock = get_history(symbol=symbol,
                   start=start_date,
                   end=end)
            if stock.empty:
                continue
            stock.reset_index()
            stock.columns = stock.columns.str.replace(" ", "_")
            stock['Date'] = stock.index
            stock['per_change'] = ((stock['Close'] / stock['Close'].shift(1) - 1)*100).fillna(0)
            stock = stock.assign(Symbol=symbol[0])
            stock['20sma'] = stock['Close'].rolling(window=20).mean()
            stock['21ema'] = stock['Close'].ewm(span=21,min_periods=0,adjust=False,ignore_na=False).mean()
            stock['50ema'] = stock['Close'].ewm(span=50,min_periods=0,adjust=False,ignore_na=False).mean()
            stock['200ema'] = stock['Close'].ewm(span=200,min_periods=0,adjust=False,ignore_na=False).mean()
            stock['stddev'] = stock['Close'].rolling(window=20).std()
            stock['lower_band'] = stock['20sma'] - (2* stock['stddev'])
            stock['upper_band'] = stock['20sma'] + (2* stock['stddev'])
            stock['TR'] = abs(stock['High']) - stock['Low']
            stock['ATR'] = stock['TR'].rolling(window=20).mean()

            stock['lower_keltner'] = stock['20sma'] - (stock['ATR'] * 1.5)
            stock['upper_keltner'] = stock['20sma'] + (stock['ATR'] * 1.5)
            obv = [] 
            obv.append(0)
            for index in range(1,len(stock.Close)):   
                if stock.Close[index] > stock.Close[index-1]:
                    obv.append(obv[-1] + stock.Volume[index])
                elif stock.Close[index] < stock.Close[index-1]:
                        obv.append(obv[-1] - stock.Volume[index]) 
                else:
                    obv.append(obv[-1])
            stock['OBV'] = obv
            stock['OBV_EMA'] = stock['OBV'].ewm(span=20).mean()
            def in_squeeze(stock):
                return stock['lower_band'] > stock['lower_keltner'] and stock['upper_band'] < stock['upper_keltner'] 
                        
            stock['squeeze_on'] = stock.apply(in_squeeze,axis=1)
            stock.to_sql('stock_price', con=connection, if_exists='append',index=False)
            connection.commit()
            st.subheader(f'Updating Stock : {symbol}')
            my_bar.progress(percent_complete)
        if percent_complete == 100:
            st.balloons()
    except Exception as e:  
        print("Exception while inserting exception {}".format(e))
    print('Successfylly Updated stocks Price')
    return 'success'


#updateStocksPrice(st,db.getConnectionCursor())