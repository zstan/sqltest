import jaydebeapi

conn = jaydebeapi.connect("org.apache.ignite.IgniteJdbcThinDriver", "jdbc:ignite:thin://127.0.0.1?queryEngine=calcite", ["", ""],
    "/home/zstan/work/repo/apache-ignite/modules/core/target/ignite-core-2.13.0-SNAPSHOT.jar")

exclude = ['ON UPDATE', 'FOREIGN KEY', 'GRANT', 'CREATE SCHEMA', 'CREATE ROLE', 'PRIVILEGES ON', 'REFERENCES ON', 'CREATE VIEW', 'CREATE ROLE']

def run_test(test):
    error = None
    try:
        for sql in test['sql']:
            sql = sql.upper()
            skip = False
            for ex in exclude:
                if (sql.find(ex) != -1):
                    print ('skip: ' + sql)
                    skip = True
                    break

            if skip:
                raise NotImplementedError("not supported")

            print ("start execute: " + sql)
            with conn.cursor() as curs:
                curs.execute(sql)
        print("complete: " + sql,  flush=True)
    except Exception as e:
        print (e)
        error = e
    except NotImplementedError as e1:
        error = e1

    return error
