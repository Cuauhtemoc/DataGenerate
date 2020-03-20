import mysql.connector as mariaDB
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import argparse
import csv
import os
import configparser
import sys
from utils import bqueries
import datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./config/bqconfig.json"


def getCreds(env):
    try:
        config = configparser.ConfigParser()
        config.read("./config/dbconfig.ini")
        creds = (dict(config.items(env)))
        return creds
    except:
        print('Could not find dbconfig.ini')

def getData(query, cursor):
    cursor.execute(query)
    res = cursor.fetchall()
    return res

def makeFile(res,cursor,table):
    col_names = [i[0] for i in cursor.description]
    tablename = f'{table}.csv'
    output_file = csv.writer(open(f'./output/{tablename}', 'w', newline=''))
    output_file.writerow(col_names)
    for row in res:
        output_file.writerow(row)

def connectData(dbName, creds):
    try: 
        db_conn = mariaDB.connect(host=creds['host'], user=creds['user'], passwd=creds['passwrd'])
        print(f'Connetected to {dbName} sucessfully')
    except:
        print(f'Could not connect to {dbName}')
    else:    
        cur = db_conn.cursor()
        copyTables(cur,dbName)

def copyTables(cur,dbName):
    tablenames = getTableNames(cur,dbName)
    for table in tablenames:
        query = f'SELECT * FROM {dbName}.{table}'
        makeFile(getData(query, cur), cur, table)
        sendtobq(table,dbName)

def getTableNames(cursor, dbName):
    query = f'SHOW TABLES from {dbName}'
    cursor.execute(query)
    tablenames = [i[0] for i in cursor.fetchall()]
    return tablenames

def sendtobq(table, dbName):
    try:
        client = bigquery.Client()
    except:
        print("Could not connect to Big Query")
        sys.exit()
    else:
        print("Connected to Big Query successfully")
        filename = f'./output/{table}.csv'
        dataset_id = f'{client.project}.{dbName}'
        table_id = table
        dataset = bigquery.Dataset(dataset_id)
        try:
            client.get_dataset(dataset_id)
            print(f'Dataset {dataset_id} exists: inserting data')
        except NotFound:
            print(f'Dataset {dataset_id} is not found:creating dataset')
            dataset = client.create_dataset(dataset)
        else:
            table_ref = dataset.table(table_id)
            job_config = bigquery.LoadJobConfig()
            job_config.autodetect = True
            job_config.source_format = bigquery.SourceFormat.CSV
            with open(filename, "rb") as source_file:
                job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
            job.result()  
            print(f'Loaded {job.output_rows} rows into {dataset_id}:{table_id}.')

def sendQuery(query,dbName,dataset,func):
    client = bigquery.Client()
    table_id = f"{client.project}.{dbName}.{func}-{datetime.date.today()}"
    job_config = bigquery.QueryJobConfig(destination=table_id)
    query_job = client.query(query,job_config=job_config)
    results = query_job.result()
    for row in results:
        print(row)

def main():
    parser = argparse.ArgumentParser(description="CL app to connect MySQL to BigQuery")
    parser.add_argument("--envName", help="Name of the enviroment you would like to copy from")
    parser.add_argument("--dbName", help="Name of the database you would like to copy")
    parser.add_argument("--q", help="Query function to call on dataset")
    parser.add_argument("--dataset", help="dataset to run query on")
    args = parser.parse_args()
    if args.dbName and args.envName:
        credentials = getCreds(args.envName)
        if(credentials):
            connectData(args.dbName, credentials)
    if args.q and args.dataset:
        query = getattr(bqueries, args.q)(args.dataset)
        sendQuery(query,args.dbName,args.dataset,args.q)
    
if __name__=="__main__":
    main()
