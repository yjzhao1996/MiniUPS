#! /usr/bin/python3
import world_ups_pb2
import amazon_ups_pb2
import sys
import socket
import threading
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time
import database_setup
from database_operation import *

seq_num=0
acks_seq=set()


def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, None)
    return b''.join(data)



def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint32(data, 0)[0]

def recv_data(socket,message_type):
    data = b''
    #size=0
    while True:
        try:
            data += socket.recv(1)
            size = decode_varint(data)
            break
        except IndexError:
            pass
    # Receive the message data
    data = socket.recv(size)
    # Decode the message
    message=message_type()
    message.ParseFromString(data)
    return message
    ##return size
    
def send_data(socket,message):
    data=message.SerializeToString()
    size = encode_varint(len(data))
    socket.sendall(size+data)

# this method is used to change speed at the beginning
def change_speed():
    command = world_ups_pb2.UCommands()
    command.simspeed=30000
    send_data(sock_world,command)
    print("simspeed:", command)

# this method is called if command from amazon is get a truck
def handle_request_get_truck(amazon_msg,sock_world,sock_amazon):
    global seq_num
    global acks_seq
    c=amazon_msg.get_truck
    
    truck_id=find_truck()
    # create a package in database
    create_package(c,truck_id)
    
    command=world_ups_pb2.UCommands()
    go_pick_up=command.pickups.add()
    go_pick_up.truckid=truck_id
    go_pick_up.whid=c.warehouse_id
    go_pick_up.seqnum=seq_num
    temp =seq_num
    seq_num+=1
    while True:
        send_data(sock_world,command)
        time.sleep(5)
        if temp in acks_seq:
            break

# this method is called when receive a init_delivery request from amazon
def handle_request_init_delivery(amazon_msg,sock_world,sock_amazon):
    global seq_num
    global acks_seq
    c=amazon_msg.init_delivery
    command=world_ups_pb2.UCommands()
    go_deliver=command.deliveries.add()

    # find the truck to deliver this packge
    row=find_truck_id(c.package_id)
    # row 0 is truck id
    go_deliver.truckid=row[0]
    
    go_deliver.seqnum=seq_num
    temp =seq_num
    seq_num+=1
    package=go_deliver.packages.add()
    package.packageid=c.package_id
    # row 1, 2 is destination
    package.x=row[1]
    package.y=row[2]
    while True:
        send_data(sock_world,command)
        time.sleep(5)
        if temp in acks_seq:
            break

# this method is called if request from amazon is change destination
def handle_request_change_destination(amazon_msg, sock_world, sock_amazon):
    c = amazon_msg.change_destination
    command = amazon_ups_pb2.UACommands()
    response = command.destination_changed
    response.package_id = c.package_id
    response.new_destination_x = c.new_destination_x
    response.new_destination_y = c.new_destination_y
    # this method is used to change the destination in database
    response.success = db_change_destination(c)
    send_data(sock_amazon, command)
        
# this method is called if response from world is finished
def handle_response_finished(completion,sock_world,sock_amazon):
    # finished all delivery
    if completion.status=="IDLE":
        # update truck status to IDLE again
        update_truck_status(completion)
        ack = world_ups_pb2.UCommands()
        ack.acks.append(completion.seqnum)
        send_data(sock_world,ack)
        print("send to world", ack)
    # arrive at warehouse
    # update package status to loading
    else:        
        command=amazon_ups_pb2.UACommands()
        response=command.truck_arrived
        response.wh_x=completion.x
        response.wh_y=completion.y
        response.truck_id=completion.truckid
        # search the package to load and update its status
        response.package_id=search_package(completion)
        # send truck_arrived to amazon
        send_data(sock_amazon,command)
        ack = world_ups_pb2.UCommands()
        ack.acks.append(completion.seqnum)
        # send ack to world
        send_data(sock_world,ack)
        print("send to world", ack)

# this method is called if response from world is delivered
def handle_response_delivered(delivered,sock_world,sock_amazon):
    command=amazon_ups_pb2.UACommands()
    response=command.package_delivered
    response.package_id=delivered.packageid
    # this method update truck position
    delivered_update(delivered)
    # send delivered command to amazon
    send_data(sock_amazon,command)
    ack = world_ups_pb2.UCommands()
    ack.acks.append(delivered.seqnum)
    # send ack to world
    send_data(sock_world,ack)
    print("send to world", ack)
    
    
    

# this method call different handlers for different request from world
def process_request_world(world_msg,sock_world,sock_amazon):
    global acks_seq
    print(world_msg)
    # put ack in a set
    for a in world_msg.acks:
        acks_seq.add(a)
    for u in world_msg.completions:
        print(u)
        handle_response_finished(u,sock_world,sock_amazon)
    for d in world_msg.delivered:
        print(d)
        handle_response_delivered(d,sock_world,sock_amazon)
        

# this method call different handlers for different request from amazon
def process_request_amazon(amazon_msg,sock_world,sock_amazon):
    print(amazon_msg)
    if amazon_msg.HasField('get_truck'):
        handle_request_get_truck(amazon_msg,sock_world,sock_amazon)
    if amazon_msg.HasField('init_delivery'):
        handle_request_init_delivery(amazon_msg,sock_world,sock_amazon)
    if amazon_msg.HasField('change_destination'):
        handle_request_change_destination(amazon_msg,sock_world,sock_amazon)

# this method is used to receive message from world
# create new thread to handle it
def recv_msg_world(sock_world,sock_amazon):
    while True:
        world_msg=recv_data(sock_world,world_ups_pb2.UResponses)
        t=threading.Thread(target=process_request_world(world_msg,sock_world,sock_amazon))
        t.start()
    
# this method is used to receive message from amazon
# create new thread to handle it
def recv_msg_amazon(sock_world,sock_amazon):
    while True:
        amazon_msg=recv_data(sock_amazon,amazon_ups_pb2.AUCommands)
        t=threading.Thread(target=process_request_amazon(amazon_msg,sock_world,sock_amazon))
        t.start()
# this method is used to connect to the world
def connect_to_world():
    connect=world_ups_pb2.UConnect()
    world_id = int(input("please tell me world id to connect(0 to create a new world)"))
    if world_id is 0:
        count = int(input("please tell me how many trucks to init:"))
        truck_list=[]
        for c in range(0, count):
            truck = connect.trucks.add()
            truck.id = int(input("truck id:"))
            truck.x = int(input("truck x:"))
            truck.y = int(input("truck y:"))
            truck_list.append(truck)
        create_truck(truck_list)
    else:
        connect.worldid = world_id
    connect.isAmazon = False
    return connect

#initialize a world and some trucks
"""
connect=world_ups_pb2.UConnect()

#connect.worldid=1
truck_list=[]
truck1=connect.trucks.add()
truck1.id=1
truck1.x=2
truck1.y=3
truck_list.append(truck1)
truck2=connect.trucks.add()
truck2.id=2
truck2.x=70
truck2.y=80
truck_list.append(truck2)


# create a list of truck in database
create_truck(truck_list)



connect.isAmazon=False


sock_world = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('vcm-7844.vm.duke.edu', 12345)
print('connecting to {} port {}'.format(*server_address))
sock_world.connect(server_address)

send_data(sock_world,connect)
"""

"""
main entry of ups
"""

# 1. connect to the world
connect=connect_to_world()
sock_world = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('vcm-9355.vm.duke.edu', 12345)
print('connecting to {} port {}'.format(*server_address))
sock_world.connect(server_address)

send_data(sock_world,connect)


connected=recv_data(sock_world,world_ups_pb2.UConnected)

print(connected.worldid)
print(connected.result)

# change simspeed here
change_speed()


# 2. connect to amazon
sock_amazon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_amazon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (socket.gethostname(), 8888)
print('starting up on {} port {}'.format(*server_address))
sock_amazon.bind(server_address)
sock_amazon.listen(1)
print('waiting for a connection')
sock_amazon, client_address = sock_amazon.accept()
# send world id to amazon
command = amazon_ups_pb2.UACommands()
command.world_id = connected.worldid
send_data(sock_amazon, command)

# 3. open 2 threads to listen from world and amazon
t1=threading.Thread(target=recv_msg_world,args=(sock_world,sock_amazon,))
t1.start()



t2=threading.Thread(target=recv_msg_amazon,args=(sock_world,sock_amazon,))
t2.start()

"""
while True:
    if input("press q and enter to quit:") is 'q':
        command = world_ups_pb2.UCommands()
        command.disconnect = True
        send_data(sock_world, command)
        response = world_ups_pb2.UResponses()
        recv_data(sock_world, response)
        if response.HasField('finished') and response.finished is True:
            break;
    pass
"""
