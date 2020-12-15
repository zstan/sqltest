import jaydebeapi

conn = jaydebeapi.connect("org.apache.ignite.IgniteJdbcThinDriver", "jdbc:ignite:thin://127.0.0.1?useExperimentalQueryEngine=true", ["", ""],
    "/home/zstan/work/repo/apache-ignite/modules/core/target/ignite-core-2.10.0-SNAPSHOT.jar")

exclude = ['GRANT', 'CREATE SCHEMA', 'CREATE ROLE', 'PRIVILEGES ON', 'REFERENCES ON', 'CREATE VIEW', 'CREATE ROLE', '( A ) VALUES ( DEFAULT )']

def run_test(test):
    error = None
    try:
        for sql in test['sql']:
            skip = False
            for ex in exclude:
                if (sql.find(ex) != -1):
                    print ('skip: ' + sql)
                    skip = True
                    break

            if skip:
                raise NotImplementedError("not supported")

            if (sql.find("CREATE TABLE") != -1 and sql.find('PRIMARY KEY') == -1):
                pos1 = sql.rfind(")")
                sql = sql[:pos1-1] + " PRIMARY KEY, CC INTEGER " + sql[pos1-1:]
            print ("start execute: " + sql)
            with conn.cursor() as curs:
                curs.execute(sql)
        print("complete: " + sql)
    except Exception as e:
        print (e)
        error = e
    except NotImplementedError as e1:
        error = e1

    return error
