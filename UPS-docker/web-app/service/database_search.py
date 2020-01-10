import psycopg2                                                                                    
import sys                                                                                         
import threading                                                                                   
import time

def d_connect():
    database = 'ups'
    retry = 5
    while retry:
        try:
            conn = psycopg2.connect(database='postgres', \
                                    user='postgres', 
                                    host='db', port='5432')
            print("Opened database %s successfully." % database)
            break
        except:
            print("Failed to connect to database ", database)
            time.sleep(3)
            retry = retry - 1
            print("retries left: ", retry)
    return conn

def search_waiting_packages(username):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM service_package WHERE acc_id = %s AND status = 'WAITING';''',(username,))
    row=cur.fetchall()
    conn.close()
    return row

def search_loading_packages(username):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM service_package WHERE acc_id = %s AND status = 'LOADING';''',(username,))
    row=cur.fetchall()
    conn.close()
    return row

def search_delivering_packages(username):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM service_package WHERE acc_id = %s AND status = 'DELIVERING';''',(username,))
    row=cur.fetchall()
    conn.close()
    return row

def search_delivered_packages(username):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM service_package WHERE acc_id = %s AND status = 'DELIVERED';''',(username,))
    row=cur.fetchall()
    conn.close()
    return row

def change_destination(id,d_x,d_y):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''UPDATE service_package SET d_x = %s, d_y = %s WHERE package_id = %s;''',(d_x,d_y,id))
    conn.commit()
    conn.close()

def search_package(id):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM service_package WHERE package_id = %s;''',(id,))
    row=cur.fetchone()
    conn.close()
    return row
