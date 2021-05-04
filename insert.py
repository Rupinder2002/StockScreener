import sqlite3
import pandas as pd



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
    
    
