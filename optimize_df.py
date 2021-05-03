import db
import pandas as pd

def optimizedb():
    try:
        connection = db.getConnectionCursor()
        cursor = connection.cursor() 
        cursor.execute('''select symbol from stock''')
        stocks = cursor.fetchall()
        stocks = [item for t in stocks for item in t]  
        for stock in stocks:     
            df = pd.read_sql("select * from stock_price where symbol= '"+stock+"'", connection)
            if df.empty:
                continue
            df['20sma'] = df['Close'].rolling(window=20).mean()
            df['21ema'] = df['Close'].ewm(span=21,min_periods=0,adjust=False,ignore_na=False).mean()
            df['50ema'] = df['Close'].ewm(span=50,min_periods=0,adjust=False,ignore_na=False).mean()
            df['200ema'] = df['Close'].ewm(span=200,min_periods=0,adjust=False,ignore_na=False).mean()
            df['stddev'] = df['Close'].rolling(window=20).std()
            df['lower_band'] = df['20sma'] - (2* df['stddev'])
            df['upper_band'] = df['20sma'] + (2* df['stddev'])
            df['TR'] = abs(df['High']) - df['Low']
            df['ATR'] = df['TR'].rolling(window=20).mean()

            df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
            df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)
            obv = [] 
            obv.append(0)
            for index in range(1,len(df.Close)):   
                if df.Close[index] > df.Close[index-1]:
                    obv.append(obv[-1] + df.Volume[index])
                elif df.Close[index] < df.Close[index-1]:
                        obv.append(obv[-1] - df.Volume[index]) 
                else:
                    obv.append(obv[-1])
            df['OBV'] = obv
            df['OBV_EMA'] = df['OBV'].ewm(span=20).mean()
            def in_squeeze(df):
                return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner'] 
                        
            df['squeeze_on'] = df.apply(in_squeeze,axis=1)
            df.to_sql('stock_price', con=connection, if_exists='append',index=False)
            connection.commit()
    except Exception as e:  
        print("Exception while inserting company : {} and exception {}".format(stock,e))
    print('Successfully optimised!')
optimizedb()      
                  
