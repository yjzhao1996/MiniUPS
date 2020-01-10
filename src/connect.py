#! /usr/bin/python3

import world_ups_pb2
import amazon_ups_pb2
import sys
import socket
import threading
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time

seq_num=0

def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, None)
    return b''.join(data)



def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint32(data, 0)[0]

def recv_data(socket,message):
    data = b''
    #size=0
    while True:
        try:
            data += socket.recv(1)
            size = decode_varint(data)
            """
            if(size==0):
                return size
            """
            break
        except IndexError:
            pass
    # Receive the message data
    data = socket.recv(size)
    # Decode the message
    message.ParseFromString(data)
    ##return size
    
def send_data(socket,message):
    data=message.SerializeToString()
    size = encode_varint(len(data))
    socket.sendall(size+data)
    


def process_request(sock_world,connection, client_address):
    global seq_num
    print('connection from', client_address)
    
    req_truck=amazon_ups_pb2.request_get_truck()
    recv_data(connection,req_truck)
    print(req_truck.order_id)
    print(req_truck.ups_account)
    
    command=world_ups_pb2.UCommands()
    go_pick_up=command.pickups.add()
    go_pick_up.truckid=2
    go_pick_up.whid=req_truck.warehouse_id
    go_pick_up.seqnum=seq_num
    seq_num+=1
    #while True:
    send_data(sock_world,command)
    seqnum=0
    while True:
        response=world_ups_pb2.UResponses()
        recv_data(sock_world,response)
        print(response);
        if response.HasField('completions'):
            break
        
        
        """
        if response.HasField('acks'):
            print(response)
            continue
        else:
            for r in response.completions:
                seqnum=r.seqnum
            print(response)
            break
        """
    """    
    command=world_ups_pb2.UCommands()
    acks=command.acks.add()
    acks=seqnum
    send_data(sock_world,command)
    """
    
            

    
    
    

    
    

connect=world_ups_pb2.UConnect()

#connect.worldid=1

truck1=connect.trucks.add()
truck1.id=1
truck1.x=2
truck1.y=3

truck2=connect.trucks.add()
truck2.id=2
truck2.x=70
truck2.y=80

connect.isAmazon=False

sock_world = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock_world.settimeout(5.0)
server_address = ('vcm-7844.vm.duke.edu', 12345)
print('connecting to {} port {}'.format(*server_address))
sock_world.connect(server_address)

send_data(sock_world,connect)

connected=world_ups_pb2.UConnected()

recv_data(sock_world,connected)

print(connected.worldid)
print(connected.result)

sock_amazon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_amazon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (socket.gethostname(), 12345)
print('starting up on {} port {}'.format(*server_address))
sock_amazon.bind(server_address)
sock_amazon.listen(1)

while True:
    print('waiting for a connection')
    connection, client_address = sock_amazon.accept()
    t=threading.Thread(target=process_request(sock_world,connection,client_address))
    t.start()

