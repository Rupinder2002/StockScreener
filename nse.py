from nsetools import Nse
import insert
from datetime import date
from nsepy import get_history
import sqlite3
from datetime import date,timedelta
import db




def updateStocksList(nse):
    all_stock_codes = nse.get_stock_codes(cached=False)
    all_stock_codes.pop('SYMBOL',None)
    insert.insertStock(all_stock_codes)

def updateStocksPrice():
    nse = Nse()
    updateStocksList(nse)
    start = date.today() - timedelta(362)
    end=date.today()
    connection = db.getConnectionCursor()
    cursor = connection.cursor()
    try:
        cursor.execute('''select symbol from stock''')
        stocks_symbols = cursor.fetchall()
        for symbol in stocks_symbols:
            stock = get_history(symbol=symbol,
                   start=start,
                   end=end)
            stock.reset_index()
            stock.columns = stock.columns.str.replace(" ", "_")
            stock['Date'] = stock.index
            stock['per_change'] = ((stock['Close'] / stock['Close'].shift(1) - 1)*100).fillna(0)
            stock = stock.assign(Symbol=symbol[0])
            print(stock)
            stock.to_sql('stock_price', con=connection, if_exists='append',index=False)
            connection.commit()
    except Exception as e:  
        print("Exception while inserting company : {} and exception {}".format(symbol,e))
    print('Successfylly inserted stocks Price')
    return 'success'


updateStocksPrice()