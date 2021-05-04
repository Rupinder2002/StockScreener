


def true_range(df):
    df['previous_close']  = df['Close'].shift(1)
    df['High-Low']  = df['High'] - df['Low']
    df['High-pc']  = abs(df['High'] - df['previous_close'])
    df['Low-pc']  = abs(df['Low'] - df['previous_close'])
    df['tr'] = df[['High-Low','High-pc','Low-pc']].max(axis=1)
    
    return df

def average_truerange(df,period):
    df = true_range(df)
    the_atr  = df['tr'].rolling(period).mean()
    return the_atr

def run_supertrend(df,period=7,multplier=3):
    df['atr'] = average_truerange(df,period)
    hl2 = ((df['High']  + df['Low'])/2)
    df['upperband'] = hl2 + (multplier * df['atr'])
    df['Lowerband'] = hl2 - (multplier * df['atr'])
    return df 