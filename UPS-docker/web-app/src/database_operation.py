import psycopg2
import sys
import threading
import time
import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = 'dukeupsofficial@gmail.com'
PASSWORD = 'UpsOfficial+1s'

def d_connect():
    database = 'ups'
    retry = 5
    while retry:
        try:
            conn = psycopg2.connect(database='postgres', 
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


# this method create a list a truck in database
def create_truck(truck_list):
    conn=d_connect()
    cur = conn.cursor()
    for truck in truck_list:
        cur.execute('''INSERT INTO service_truck
        (truck_id,x,y,status)
        VALUES (%s,%s,%s,%s);'''
                    ,(truck.id,truck.x,truck.y,"IDLE"))
        conn.commit()
    conn.close()

# this method is used to search an available truck
# and update truck status
def find_truck():
    conn=d_connect()
    cur = conn.cursor()
    while True:
        cur.execute('''SELECT truck_id FROM service_truck WHERE status = 'IDLE' OR status = 'DELIVERING';''')
        row=cur.fetchone()
        if row:
            break
    cur.execute('''UPDATE service_truck SET status = 'TRAVELING' WHERE truck_id = %s;''',row)
    conn.commit()
    conn.close()
    return row[0]

# this method create a package in database
def create_package(package,truck_id):
    conn=d_connect()
    cur = conn.cursor()
    if package.HasField('ups_account') and package.ups_account is not "":
        cur.execute('''INSERT INTO service_package
        (package_id,wh_id,w_x,w_y,d_x,d_y,truck_id,loaded,acc_id,status,waiting,waiting_t)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
                    ,(package.order_id,package.warehouse_id,package.location_x,package.location_y,package.destination_x,package.destination_y,truck_id,'False',package.ups_account, "WAITING",'True',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    elif package.HasField('ups_account') and package.ups_account is "":
        cur.execute('''INSERT INTO service_package
        (package_id,wh_id,w_x,w_y,d_x,d_y,truck_id,loaded,status,waiting,waiting_t)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
                    ,(package.order_id,package.warehouse_id,package.location_x,package.location_y,package.destination_x,package.destination_y,truck_id,'False', "WAITING",'True',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    else:
        cur.execute('''INSERT INTO service_package
        (package_id,wh_id,w_x,w_y,d_x,d_y,truck_id,loaded,status,waiting,waiting_t)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
                    ,(package.order_id,package.warehouse_id,package.location_x,package.location_y,package.destination_x,package.destination_y,truck_id,'False', "WAITING",'True',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    conn.commit()
    conn.close()


# this method is used to change destination in database
def db_change_destination(c):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT status FROM service_package WHERE package_id = %s;''',(c.package_id,))
    row=cur.fetchone()
    if not row:
        return False
    if row[0] == "WAITING" or row[0] == "LOADING":
        cur.execute('''UPDATE service_package SET d_x = %s, d_y = %s WHERE package_id = %s;''',(c.new_destination_x, c.new_destination_y, c.package_id))
        conn.commit()
        conn.close()
        return True
    else:
        return False
    
# search the package to load
# update its status to loading
def search_package(finished):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT package_id FROM service_package WHERE truck_id = %s AND loaded = %s;''',(finished.truckid, "False"))
    row=cur.fetchone()
    cur.execute('''UPDATE service_package SET loaded = 'True', status = 'LOADING' , loading = 'True', loading_t = %s WHERE package_id = %s;''',(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),row[0]))
    cur.execute('''UPDATE service_truck SET x = %s, y = %s WHERE truck_id = %s;''',(finished.x,finished.y,finished.truckid))
    conn.commit()
    conn.close()
    return row[0]

# this method is used to find truck id and destination for a package
# also update truck and package status
def find_truck_id(package_id):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT truck_id, d_x, d_y FROM service_package WHERE package_id = %s;''',(package_id,))
    row=cur.fetchone()
    cur.execute('''UPDATE service_truck SET status = 'DELIVERING' WHERE truck_id = %s;''',(row[0],))
    cur.execute('''UPDATE service_package SET status = 'DELIVERING' ,delivering = 'True', delivering_t = %s WHERE package_id = %s;''',(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),package_id))
    conn.commit()
    conn.close()
    return row

# this method is called to update truck position and status
# after arriving warehouse or finish all delivery
def update_truck_status(finished):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''UPDATE service_truck SET x = %s, y = %s, status = 'IDLE' WHERE truck_id = %s;''',(finished.x,finished.y,finished.truckid))
    conn.commit()
    conn.close()


# this method is used to send email
def send_delivered(email, packageid):
    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)
    # create a message
    msg = MIMEMultipart()
    with open('/code/src/message.txt', 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    message_template =  Template(template_file_content)
    message = message_template.substitute(PACKAGE_ID=packageid)
    # setup the parameters of the message
    msg['From']=MY_ADDRESS
    msg['To']=email
    msg['Subject']="UPS: Package Arrived"
    msg.attach(MIMEText(message, 'plain'))
    try:
        s.send_message(msg)
    except:
        print("wrong email address")
    s.quit()
    
# this method is called to update truck position after delivery
def delivered_update(delivered):
    conn=d_connect()
    cur = conn.cursor()
    cur.execute('''SELECT d_x, d_y FROM service_package WHERE package_id = %s;''',(delivered.packageid,))
    row=cur.fetchone()
    cur.execute('''UPDATE service_package SET status = 'DELIVERED', delivered = 'True', delivered_t = %s WHERE package_id = %s;''', (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),delivered.packageid))
    cur.execute('''UPDATE service_truck SET x = %s, y = %s WHERE truck_id = %s;''',(row[0],row[1],delivered.truckid))
    cur.execute('''SELECT acc_id FROM service_package WHERE package_id = %s;''',(delivered.packageid,))
    row = cur.fetchone()
    if row:
        acc_id = row[0]
        cur.execute('''SELECT email FROM service_account WHERE username = %s;''',(acc_id,))
        col = cur.fetchone()
        if col:
            email = col[0]
            # this method is used to send email
            send_delivered(email, delivered.packageid)
    conn.commit()
    conn.close()
    
    
