import sqlite3
import pandas as pd
import patterns
import strategies
import sectors


def insertStock(companies,connection):
    cursor = connection.cursor()    
    rows = []      
    for key, value in companies.items():
        rows.append((key,value))      
    try:
        cursor.executemany('''Insert into stock(symbol,name) values (?,?)''', (rows))
        connection.commit()
    except Exception as e:
        print("Exception while inserting company : {} and exception {}".format(value,e))
    print('Successfylly inserted stocks symbol')
    
def insertStockPrice(company,connection):
    try:
        
        company.to_sql('stock_price', con=connection, if_exists='append',index=False)
    except Exception as e:
        print("Exception while inserting companyexception : {}".format(e))
    connection.commit()

def insertPattern(connection):
    cursor = connection.cursor()        
    for key, value in patterns.patterns.items():
        cursor.execute('''INSERT into patterns (key,name) values (?,?)''',(key,value))
        connection.commit()
    print('Successfylly inserted pattern')
        
def insertsectors(connection):
    cursor = connection.cursor()        
    for key, value in sectors.sectors.items():
        cursor.execute('''INSERT into sectors (name,sector_id) values (?,?)''',(key,value))
        connection.commit()
    print('Successfylly inserted sectors')

def insertstrategies(connection):
    cursor = connection.cursor()        
    for key, value in strategies.strategies.items():
        cursor.execute('''INSERT into strategy (id,name) values (?,?)''',(key,value))
        connection.commit()
    print('Successfylly inserted strategies')
    
