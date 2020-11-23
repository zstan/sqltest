from pyignite import Client
import sqlite3
import pyignite

client = Client()
client.connect('127.0.0.1', 10800)

def run_test():
    error = None
    try:
        #client.sql("CREATE TABLE TABLE_F051_01_01_011 ( A DATE PRIMARY KEY, CC INTEGER  )")
        #client.sql("SELECT DATE '2016-03-26'")
        client.sql("SELECT CAST ( '2016-03-26' AS DATE )")
        #client.sql("CREATE TABLE TABLE_F051_02_01_011 ( A TIME PRIMARY KEY, CC INTEGER  )")
        print ('done')
        # conn.commit()
        #conn.close()
    except pyignite.exceptions.SQLError as e:
        error = e
    except pyignite.exceptions.ParseError as e1:
        print (e1)
        client.connect('127.0.0.1', 10800)

    return error

if __name__== "__main__":
  print (run_test())
