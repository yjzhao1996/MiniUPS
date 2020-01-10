#!/usr/bin/python3
import psycopg2
import sys

retry=5
while retry:
    try:
        database='ups'
        conn = psycopg2.connect(database='ups',\
                                user='postgres', password='passw0rd',\
                                host='0.0.0.0', port='5432')

        print("Opened database %s successfully." % database)
        break
    except:
        print("Failed to connect to database %s.", database)
        time.sleep(3)
        retry-=1


try:    
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS service_package CASCADE;''')
    cur.execute('''DROP TABLE IF EXISTS service_truck CASCADE;''')
    # cur.execute('''DROP TABLE IF EXISTS service_account CASCADE;''')

    conn.commit()
except:
    print (sys.exc_info())
    print ('Error: Drop tables')
    pass


"""
try:
    cur = conn.cursor()
    cur.execute('''CREATE TABLE service_account(
    user_id int,
    username TEXT PRIMARY KEY
    );''')

    # cur.execute('''INSERT INTO service_account VALUES ('Jiaran');''')
    # cur.execute('''INSERT INTO service_account VALUES ('Yanjia');''')
    
    conn.commit()

except:
    print (sys.exc_info())
    print ('Table  may already exist.')
    pass
"""

try:
    cur.execute('''CREATE TABLE service_truck(
    truck_id int PRIMARY KEY,
    x int,
    y int,
    status TEXT
    );''')
    
    conn.commit()

except:
    print (sys.exc_info())
    print ('Table may already exist.')
    pass

try:
    cur.execute('''CREATE TABLE service_package(
    package_id int PRIMARY KEY,
    wh_id int,
    w_x int,
    w_y int,
    d_x int,
    d_y int,
    truck_id int,
    loaded boolean,
    acc_id TEXT,
    status TEXT,
    waiting boolean,
    loading boolean,
    delivering boolean,
    delivered boolean,
    waiting_t TEXT,
    loading_t TEXT,
    delivering_t TEXT,
    delivered_t TEXT,
    FOREIGN KEY(acc_id) REFERENCES service_account(username),
    FOREIGN KEY(truck_id) REFERENCES service_truck(truck_id)
    );''')
    
    conn.commit()

except:
    print (sys.exc_info())
    print ('Table may already exist.')
    pass

conn.close()
