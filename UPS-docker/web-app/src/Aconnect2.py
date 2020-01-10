#! /usr/bin/python3

import world_amazon_pb2
import amazon_ups_pb2
import sys
import socket
from google.protobuf.internal.encoder import _VarintEncoder
import time 

def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, None)
    return b''.join(data)

connect=world_amazon_pb2.AConnect()



connect.worldid=1

wh1=connect.initwh.add()
wh1.id=1
wh1.x=2
wh1.y=3

wh2=connect.initwh.add()
wh2.id=2
wh2.x=3
wh2.y=4

connect.isAmazon=True



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('vcm-7844.vm.duke.edu', 23456)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
data=connect.SerializeToString()
size = encode_varint(len(data))
sock.sendall(size+data)
print(sock.recv(2048))

time.sleep(5)

sock_ups = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ups_address = ('vcm-7844.vm.duke.edu', 8888)
print('connecting to {} port {}'.format(*ups_address))
sock_ups.connect(ups_address)

command = amazon_ups_pb2.AUCommands()

request = command.get_truck
request.order_id = 1
request.ups_account = "2"
request.warehouse_id = 1
request.location_x = 2
request.location_y = 3
request.destination_x = 6
request.destination_y = 7

command_data = request.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

time.sleep(10)

command = amazon_ups_pb2.AUCommands()

request = command.get_truck
request.order_id = 1
request.ups_account = "2"
request.warehouse_id = 1
request.location_x = 2
request.location_y = 3
request.destination_x = 6
request.destination_y = 7

command_data = request.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

time.sleep(10000)

