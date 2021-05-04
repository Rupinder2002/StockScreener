import streamlit as st
import requests as req
import sqlite3
from nsepy import *
import db
import patterns
import pandas as pd
import streamlit.components.v1 as components
import ttm
import plotly.graph_objects as go
import time
import numpy as np
import json
import streamlit.components.v1 as components
from pypfopt.efficient_frontier import EfficientFrontier,EfficientSemivariance
from pypfopt import risk_models,plotting
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.risk_models import CovarianceShrinkage
from strategies import supertrend 
from SessionState import get
import update_stock

connection = db.getConnectionCursor()

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link rel="stylesheet" href="https://fonts.google.com/icons?selected=Material+Icons">', unsafe_allow_html=True)    

def icon(icon_name):
    st.markdown(f'<span class="material-icons-outlined">{icon_name}</span>', unsafe_allow_html=True)



def main():
    dashboard = st.sidebar.selectbox(
        'Which Dashboard to open?', ('All Stocks','Strategies','Analysis','Portfolio','Pattern','Update Stocks'))
    cursor = connection.cursor()
    if dashboard == 'All Stocks':
        st.title(dashboard)
        print(f'Inside dashboard : {dashboard}')

        cursor.execute('''select symbol from stock''')
        stocks_symbols = cursor.fetchall()
        stocks = [item for t in stocks_symbols for item in t]
        symbol_search = st.sidebar.text_input("Stock name ")
        symbol = st.sidebar.selectbox("Select the Stock",stocks) 
        if symbol_search != "":
            symbol = symbol_search
        result = get_quote(symbol)
        #data = json.loads(result['data'][0])
        #df = pd.json_normalize(data['data']) 
        st.dataframe(pd.DataFrame(result['data']))
        
        
    elif dashboard == 'Pattern':
        stocks= {}
        print(f'Inside dashboard : {dashboard}')
        st.title(dashboard)
        cursor.execute('''select symbol from stock''')
        stocks_symbols = cursor.fetchall()
        stocks = [item for t in stocks_symbols for item in t]
        symbol = st.sidebar.selectbox("Select the Stock",stocks) 
        df = pd.read_sql("select open,high,low,close,symbol from stock_price where symbol ='"+symbol+"'", connection)
        cursor.execute('''select key,name from patterns''')
        patterns = cursor.fetchall()
        # patterns = [item for t in patterns for item in t]
        for pattern in patterns:
            pattern_function = getattr(tb,pattern[0])
            result = pattern_function(df['Open'],df['High'],df['Low'],df['Close'])
            last = result.tail(1).values[0]
            if last>0:
                st.write("Patter name : "+pattern[1])
                st.write("BULLISH")
            elif last<0:
                st.write("Patter name : "+pattern[1])
                st.write("BEARISH")

    elif dashboard == 'Strategies':  
        print(f'Inside dashboard : {dashboard}')
        st.title(dashboard)
        cursor.execute('''select name from strategy''')
        strategies = cursor.fetchall()
        strategies = [item for t in strategies for item in t]
        strategy = st.sidebar.selectbox("Select the Strategy",strategies)
        cursor.execute('''select name from sectors''')
        sectors = cursor.fetchall()
        sectors = [item for t in sectors for item in t]
        sector = st.sidebar.selectbox("Select the Sector",sectors)
        if sector == 'All':
            cursor.execute('''select symbol from stock''')
            stocks = cursor.fetchall()
            stock_in_sector = [item for t in stocks for item in t]       
        else:    
            df = pd.read_csv("nifty Sectors/"+sector+".csv")
            stock_in_sector = pd.Series(df['Symbol'])
            st.header("Strategy selected: "+strategy) 
        if strategy == 'TTM Squeeze':
                if sector != "":
                    my_bar = st.progress(0)
                    percent_complete = 1 
                    i = 1   
                    for stock in stock_in_sector:
                        percent_complete =  int( (i/len(stock_in_sector)) * 100)  
                        i=i+1    
                        df = pd.read_sql("select * from stock_price where symbol= '"+stock+"'", connection)
                        if df.empty:
                            continue
                    # st.dataframe(df)
                        #if len(df.squeeze_on.tail()) > 3:
                        if df.iloc[-3]['squeeze_on'] and df.iloc[-1]['OBV'] > df.iloc[-1]['OBV_EMA']:
                                mess = "{} is coming out of squeezer".format(stock)
                                st.subheader(mess)                           
                                st.dataframe(df.sort_values(by=['Date'], ascending=False))
                                newdf = df
                                candlestick = go.Candlestick(x=newdf['Date'],open=newdf['Open'],high=newdf['High'],low=newdf['Low'],close=newdf['Close'])
                                upper_band = go.Scatter(x=newdf['Date'],y=newdf['upper_band'],name = 'Upper Bollinger Band',line = {'color':'red'})
                                lower_band = go.Scatter(x=newdf['Date'],y=newdf['lower_band'],name = 'Lower Bollinger Band',line = {'color':'red'})
                                upper_keltner = go.Scatter(x=newdf['Date'],y=newdf['upper_keltner'],name = 'Upper Keltner Channel',line = {'color':'blue'})
                                lower_keltner = go.Scatter(x=newdf['Date'],y=newdf['lower_keltner'],name = 'Lower Keltner Channel',line = {'color':'blue'})
                                OBV = go.Scatter(x=newdf['Date'],y=newdf['OBV'],name = 'On Balace Volume',line = {'color':'black'})
                                OBV_EMA = go.Scatter(x=newdf['Date'],y=newdf['OBV_EMA'],name = 'On Balace Volume EMA',line = {'color':'green'})
                                
                                fig_vol = go.Figure(data=[OBV,OBV_EMA])
                                fig = go.Figure(data=[candlestick,upper_band,lower_band,upper_keltner,lower_keltner])
                                fig.layout.xaxis.type = 'category'
                                fig.layout.xaxis.rangeslider.visible = False
                                first,last = st.beta_columns(2)
                                first.plotly_chart(fig)
                                last.plotly_chart(fig_vol)
                        my_bar.progress(percent_complete)
                        if percent_complete == 100:
                            st.balloons()
        elif  strategy == 'On Balance Volume(OBV)':
                if sector != "":
                    my_bar = st.progress(0)
                    percent_complete = 1
                    i = 1     
                    for stock in stock_in_sector:
                        percent_complete =  int( (i/len(stock_in_sector)) * 100)  
                        i=i+1
                        df = pd.read_sql("select * from stock_price where symbol= '"+stock+"'", connection)
                        if df.empty:
                            continue                     
                        newdf = df 
                        if newdf.iloc[-1]['OBV'] > newdf.iloc[-1]['OBV_EMA'] and newdf.iloc[-1]['Close'] > newdf.iloc[-1]['21ema'] and newdf.iloc[-1]['Close'] > newdf.iloc[-1]['VWAP']:
                            mess = "{}  is above OBV, 20EMA and VWAP ".format(stock)
                            st.subheader(mess)
                            candlestick = go.Candlestick(x=newdf['Date'],open=newdf['Open'],high=newdf['High'],low=newdf['Low'],close=newdf['Close'])                         
                            OBV = go.Scatter(x=newdf['Date'],y=newdf['OBV'],name = 'Volume',line = {'color':'yellow'})
                            OBV_EMA = go.Scatter(x=newdf['Date'],y=newdf['OBV_EMA'],name = 'Volume EMA',line = {'color':'green'})
                            fig = go.Figure(data=[OBV,OBV_EMA])
                            fig.layout.xaxis.type = 'category'
                            fig.layout.xaxis.rangeslider.visible = False
                            figPrice = go.Figure(data=[candlestick])
                            figPrice.layout.xaxis.type = 'category'
                            figPrice.layout.xaxis.rangeslider.visible = False
                            st.plotly_chart(figPrice)
                            st.plotly_chart(fig)
                    

                            my_bar.progress(percent_complete)
                    if percent_complete == 100:
                        st.balloons()
        elif strategy == 'SuperTrend':
            if sector != "":
                my_bar = st.progress(0)
                percent_complete = 1
                i = 1     
                for stock in stock_in_sector[:3]:
                    st.subheader(stock)
                    percent_complete =  int( (i/len(stock_in_sector)) * 100)  
                    i=i+1
                    df = pd.read_sql("select * from stock_price where symbol= '"+stock+"'", connection)
                    if df.empty:
                        continue    
                    df = supertrend.run_supertrend(df,10,3)
                    df['in_uptrend']= True
                    for current in range(1,len(df.Close)):
                        previous = current - 1
                        
                        if df['Close'][current] > df['upperband'][previous]:
                            df['in_uptrend'][current] = True
                        elif df['Close'][current] < df['Lowerband'][previous]:
                            df['in_uptrend'][current] = False
                        else:
                            df['in_uptrend'][current] = df['in_uptrend'][previous]
                            
                            if df['in_uptrend'][current] and df['Lowerband'][current]  < df['Lowerband'][previous]:
                                df['Lowerband'][current] =  df['Lowerband'][previous]

                            if not df['in_uptrend'][current] and df['upperband'][current]  > df['upperband'][previous]:
                                df['upperband'][current] =  df['upperband'][previous]

                    candlestick = go.Candlestick(x=df['Date'],open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
                    upper_band = go.Scatter(x=df['Date'],y=df['upperband'],name = 'Upper  Band',line = {'color':'red'})
                    lower_band = go.Scatter(x=df['Date'],y=df['Lowerband'],name = 'Lower  Band',line = {'color':'red'})
                    fig = go.Figure(data=[candlestick,upper_band,lower_band])
                    fig.layout.xaxis.type = 'category'
                    fig.layout.xaxis.rangeslider.visible = False
                    st.plotly_chart(fig)
                    
                

                    my_bar.progress(percent_complete)
                    if percent_complete == 100:
                        st.balloons()

    elif dashboard == 'Portfolio':
        print(f'Inside dashboard : {dashboard}')
        st.title(dashboard)
        cursor.execute('''select name from sectors''')
        sectors = cursor.fetchall()
        sectors = [item for t in sectors for item in t]
        sector = st.sidebar.selectbox("Select the Sector",sectors)
        alldf = pd.read_sql("select * from stock_price", connection)
        if sector == 'All':
            cursor.execute('''select symbol from stock''')
            stocks = cursor.fetchall()
            stock_in_sector = [item for t in stocks for item in t] 
            alldf = alldf.loc[alldf['Symbol'].isin(stock_in_sector)]              
        else:    
            df = pd.read_csv("nifty Sectors/"+sector+".csv")
            alldf = alldf.loc[alldf['Symbol'].isin(df['Symbol'])]        
            
        #alldf = alldf.set_index(pd.DatetimeIndex(df['Date'].values))
        #alldf.drop(columns = ['Date'], axis =1, inplace=True)
        assets = alldf.Symbol.unique()
        alldf = alldf.set_index('Date')
        alldf = alldf.pivot_table(index='Date', columns=['Symbol'], values='Close')
        alldf = alldf.set_index(pd.DatetimeIndex(alldf.index.values))
        alldf = alldf.dropna(axis=1)
        #medals.reindex_axis(['Gold', 'Silver', 'Bronze'], axis=1)
        st.subheader("Stocks")
        st.write(alldf)
        #mu = expected_returns.mean_historical_return(alldf)
        #s = risk_models.sample_cov(alldf)
        span = st.slider('Slide me to select span', min_value=1, max_value=500)
        mu = expected_returns.ema_historical_return(alldf,span=span)
        st.subheader("Returns")
        st.write(mu)
        s = CovarianceShrinkage(alldf).shrunk_covariance()   
        ef = EfficientFrontier(mu,s) 
        weight = ef.max_sharpe()
        clean_weight = ef.clean_weights()
        expectedreturn, volatility, Sharperatio = ef.portfolio_performance(verbose=False)
        st.subheader("Expected annual return: " +str(round(expectedreturn,2)*100)+'%')
        st.subheader("Annual volatility: "+str(round(volatility,2)*100)+'%')
        st.subheader("Sharpe Ratio: "+str(round(Sharperatio,2)))
        funds = st.slider('PortFolio Value:',min_value=50000,max_value=500000)
        latest_prices = get_latest_prices(alldf)
        weights = clean_weight

        da = DiscreteAllocation(weights,latest_prices,total_portfolio_value=funds)
        allocation,leftover = da.lp_portfolio() 
        st.subheader("Weight")
        st.write(pd.DataFrame(weights, columns=weights.keys(), index=[0]))
        st.subheader("Discreate Allocation")
        st.write(pd.DataFrame(allocation, columns=allocation.keys(), index=[0]))
        st.subheader("Funds Reamaning:"+str(round(leftover,2)))
    
    elif dashboard == 'Update Stocks':
        print(f'Inside dashboard : {dashboard}')
        st.title(dashboard)
        icon('update')
        if st.button('Update Stocks'):
            status = update_stock.updateStocks(st,connection)
            if status == 'Success':
                st.balloons()
 
 

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons') 
    
session_state = get(password='')

if session_state.password != 'pwd123':
    pwd_placeholder = st.sidebar.empty()
    pwd = pwd_placeholder.text_input("Password:", value="", type="password")
    session_state.password = pwd
    if session_state.password == 'pwd123':
        pwd_placeholder.empty()
        main()
    elif session_state.password != '':
        st.error("the password you entered is incorrect")
else:
    main()   

    