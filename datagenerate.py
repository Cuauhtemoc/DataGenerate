import mysql.connector as mariaDB
import argparse
import csv


def getData(Query, cursor):
    cursor.execute(Query)
    res = cursor.fetchall()
    return res

def makeFile(res, cursor):
    col_names = [i[0] for i in cursor.description]
    output_file = csv.writer(open('sqldump.csv', 'w', newline=''))
    output_file.writerow(col_names)
    for x in res:
        output_file.writerow(x)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fileName", help="Name of the SQL file you would like to run")
    args = parser.parse_args()
    db_conn = mariaDB.connect(host='localhost', user='root', passwd="password")
    fd = open(args.fileName, 'r')
    Query = fd.read()
    fd.close()
    cur = db_conn.cursor()
    makeFile(getData(Query, cur), cur)   

if __name__=="__main__":
    main()
