import db
import nse

def updateStocks(st,connection):
    try:
        print(f'Inside update stock')
        createTables(connection)
        deleteTableRows(connection)
        updateTables(st,connection)
    except Exception as e:
        print("Exception while updating stocks  and exception {}".format(e))
    return "Success"
    
    
def createTables(connection):
    print(f'Inside createTables')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS "stock" ( "id" INTEGER, "symbol" text NOT NULL UNIQUE, "name" text NOT NULL, "sector" TEXT, PRIMARY KEY("id" AUTOINCREMENT) )')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS "analysis" ("date"	TEXT,"symbol"	TEXT,"strategy_id"	INTEGER,"total_trades"	INTEGER,"total_won"	INTEGER,"total_lost"	INTEGER,"strike_rate"	INTEGER,"win_streak"	INTEGER,"losing_streak"	INTEGER,"pnl_net"	INTEGER,FOREIGN KEY("symbol") REFERENCES "stock"("symbol"))')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS "sectors" ( "name" TEXT NOT NULL, "sector_id" INTEGER NOT NULL, PRIMARY KEY("sector_id") )')
    connection.commit()
    cursor.execute('CREATE TABLE  IF NOT EXISTS "order_book" ("id"	INTEGER,"datetime"	TEXT,"order_type"	TEXT,"price"	INTEGER,"value"	INTEGER,"pandl"	INTEGER,PRIMARY KEY("id" AUTOINCREMENT))')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS "patterns" ( "key" TEXT, "name" TEXT )')
    connection.commit() 
    cursor.execute('CREATE TABLE IF NOT EXISTS "stock_price" ( "Symbol" TEXT, "Series" TEXT, "Prev_Close" INTEGER, "Open" INTEGER, "High" INTEGER, "Low" INTEGER, "Last" INTEGER, "Close" INTEGER, "VWAP" INTEGER, "Volume" INTEGER, "Turnover" INTEGER, "Trades" INTEGER, "Deliverable_Volume" INTEGER, "%Deliverble" INTEGER, "Date" TEXT, "per_change" INTEGER, "20sma" INTEGER, "21ema" INTEGER, "50ema" INTEGER, "200ema" INTEGER, "stddev" INTEGER, "lower_band" INTEGER, "upper_band" INTEGER, "TR" INTEGER, "ATR" INTEGER, "lower_keltner" INTEGER, "upper_keltner" INTEGER, "OBV" INTEGER, "OBV_EMA" INTEGER, "squeeze_on" INTEGER )')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS "stock_strategy" ( "symbol" TEXT NOT NULL, "strategy_id" INTEGER NOT NULL, "id" INTEGER, FOREIGN KEY("symbol") REFERENCES "stock"("id"), PRIMARY KEY("id") )')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS "strategy" ( "Id" INTEGER NOT NULL, "Name" TEXT NOT NULL UNIQUE, PRIMARY KEY("Id" AUTOINCREMENT) )')
    connection.commit()

def deleteTableRows(connection):
    print(f'Inside deleteTableRows')
    cursor = connection.cursor()
    cursor.execute('DELETE from stock')
    connection.commit()
    cursor.execute('DELETE from stock_price')
    connection.commit()
    
def updateTables(st,connection):
    print(f'Inside updateTables')
    nse.updateStocksPrice(st,connection)        
