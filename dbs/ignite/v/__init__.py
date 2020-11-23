from pyignite import Client
import sqlite3
import pyignite

client = Client()
client.connect('127.0.0.1', 10800)

exclude = ['CREATE SCHEMA', 'CREATE ROLE', 'PRIVILEGES ON', 'REFERENCES ON', 'CREATE VIEW', 'CREATE ROLE']

def run_test(test):
    error = None
    try:
        for sql in test['sql']:
            for ex in exclude:
                if (sql.find(ex) != -1):
                    continue

            if (sql.find("CREATE TABLE") != -1 and sql.find('PRIMARY KEY') == -1):
                pos1 = sql.rfind(")")
                sql = sql[:pos1-1] + " PRIMARY KEY, CC INTEGER " + sql[pos1-1:]
            print (sql)
            client.sql(sql)
        print('complete')

        # conn.commit()
        #conn.close()
    except pyignite.exceptions.SQLError as e:
        error = e
    except pyignite.exceptions.ParseError as e1:
        print (e1)
        client.connect('127.0.0.1', 10800)

    return error