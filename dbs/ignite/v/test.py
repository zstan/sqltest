
import jaydebeapi

conn = jaydebeapi.connect("org.apache.ignite.IgniteJdbcThinDriver", "jdbc:ignite:thin://127.0.0.1?useExperimentalQueryEngine=true", ["", ""],
    "/home/zstan/work/repo/apache-ignite/modules/core/target/ignite-core-2.10.0-SNAPSHOT.jar")
#jdbc:ignite:thin//localhost:10800


def run_test(sql):
    error = None
    try:
        with conn.cursor() as curs:
            curs.execute(sql)

        print ('done')
    except jaydebeapi.DatabaseError as e1:
        print (e1)

    return error

if __name__== "__main__":
        #print (run_test("CREATE TABLE TABLE_E061_09_01_04 ( A INT PRIMARY KEY, CC INTEGER  );"))
        #print (run_test("SELECT A FROM TABLE_E061_09_01_04 WHERE A = ( SELECT 1 );"))
        #print (run_test("SELECT A FROM TABLE_E061_09_01_04 WHERE A = ( SELECT 1 );"))
        print (run_test("CREATE TABLE TABLE_F221_01_011 ( A INTEGER DEFAULT 123 PRIMARY KEY, CC INTEGER  )"))
        print (run_test("INSERT INTO TABLE_F221_01_011 ( A ) VALUES ( DEFAULT )"))

        print (run_test("CREATE TABLE TABLE_F041_07_01_021 ( A INTEGER PRIMARY KEY, CC INTEGER  )"))
        print (run_test("SELECT TABLE_F041_07_01_021.A FROM TABLE_F041_07_01_021 INNER JOIN TABLE_F041_07_01_021 AS TABLE_F041_07_01_022 USING ( A )"))
        print (run_test("CREATE TABLE TABLE_F041_04_01_061 ( A INTEGER PRIMARY KEY, CC INTEGER  )"))
        print (run_test("CREATE TABLE TABLE_F041_04_01_062 ( A INTEGER PRIMARY KEY, CC INTEGER  )"))
        print (run_test("SELECT TABLE_F041_04_01_061.A, TABLE_F041_04_01_062.A FROM TABLE_F041_04_01_061 RIGHT OUTER JOIN TABLE_F041_04_01_062 USING ( A ) AS FOO"))
        #print (run_test(""))
        #print (run_test(""))
        #print (run_test(""))
        #print (run_test(""))

