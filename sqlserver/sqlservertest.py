import pyodbc as p
import argparse
import time
import requests
import json
import ConfigParser
import datetime


def check_for_stop(conn):
    config = ConfigParser.ConfigParser()
    config.read("file.conf")
    stop = config.get('params','stop')
    if (stop=="true"):
        print ("Stop issued")
        conn.close()
        exit()
    else:
        return "false"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-db','--database', help='Database name', required=True)
    parser.add_argument('-u','--username', help='Username of SQL server', required=True)
    parser.add_argument('-p','--password', help='Password of SQL server', required=True)
    parser.add_argument('-dsn','--datasource', help='Data source of SQL server', required=True)
    parser.add_argument('-i', '--interval', help='Interval to sleep in seconds', required=True)
    parser.add_argument('-t', '--tag', help='Tag for the run', required=True)
    args = parser.parse_args()

    database = args.database
    user = args.username
    password = args.password
    dsn = args.datasource
    interval = args.interval

    connStr = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
    conn = p.connect(connStr)

    while(1):
        stop = check_for_stop(conn)
        if(stop=="false"):
            print("Pass Issued")
            if(int(interval)>=5):
                print("Getting new connection")
                conn.close()
                connStr = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
                conn = p.connect(connStr)

            query1 = "SELECT * FROM information_schema.tables"
            dbCursor1 = conn.cursor()
            dbCursor1.execute(query1)
            tables = []
            for row1 in dbCursor1:
                tables.append(str(row1[0])+"."+str(row1[1])+"."+str(row1[2]))
            payload = {}
            row_dict = []
            ts = time.time()
            payload['timestamp'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
            payload['Tag'] = args.tag
            payload['Database'] = args.database

            for table in tables:
                query = "exec sp_spaceused '"+ table +"'"
                dbCursor = conn.cursor()
                dbCursor.execute(query)
                for row in dbCursor:
                    row_json = {}
                    row_json['Table_Name']= str(row[0])
                    row_json['Number_of_Rows'] = str(row[1])                
                    row_json['Reserved'] = str(row[2])
                    row_json['Data'] = str(row[3])
                    row_json['Index_Size'] = str(row[4])
                    row_json['Unused'] = str(row[5])
                    row_dict.append(row_json)

            payload['Table_Size'] = row_dict
            #print json.dumps(payload)
            url = "http://localhost:9200/sqlserver/size"
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if(int(interval)>=5):
                conn.close()
        time.sleep(int(interval)*60)
    conn.close()

if __name__ == "__main__":
    main()
