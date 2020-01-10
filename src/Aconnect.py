#! /usr/bin/python3

import world_amazon_pb2
import amazon_ups_pb2
import sys
import socket
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time

def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint32(data, 0)[0]


def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, None)
    return b''.join(data)

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



sock_ups = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ups_address = ('vcm-7844.vm.duke.edu', 8888)
print('connecting to {} port {}'.format(*ups_address))
sock_ups.connect(ups_address)
time.sleep(2)

"""
request two trucks
"""
command = amazon_ups_pb2.AUCommands()

request = command.get_truck
request.order_id = 1
request.ups_account = "Jiaran"
request.warehouse_id = 1
request.location_x = 2
request.location_y = 3
request.destination_x = 6
request.destination_y = 7

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

response = amazon_ups_pb2.UACommands()
recv_data(sock_ups, response)
print(response)


command = amazon_ups_pb2.AUCommands()

request = command.get_truck
request.order_id = 2
request.ups_account = "Yanjia"
request.warehouse_id = 2
request.location_x = 3
request.location_y = 4
request.destination_x = 6
request.destination_y = 7

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

response = amazon_ups_pb2.UACommands()
recv_data(sock_ups, response)
print(response)

"""
init 2 delivery
"""

"""
purchase, pack a package and load it
"""
command = world_amazon_pb2.ACommands()
pack = command.buy.add()
pack.whnum = 2
pack.seqnum = 1
product = pack.things.add()
product.id = 1
product.description = "MacBook"
product.count = 1500

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock.sendall(command_size+command_data)
response = world_amazon_pb2.AResponses()
recv_data(sock, response)
print(response)


command = world_amazon_pb2.ACommands()
pack = command.topack.add()
pack.whnum = 2
pack.shipid = 2
pack.seqnum = 2
product = pack.things.add()
product.id = 1
product.description = "MacBook"
product.count = 1

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock.sendall(command_size+command_data)
response = world_amazon_pb2.AResponses()
recv_data(sock, response)
print(response)
#recv_data(sock, response)
#print(response)


command = world_amazon_pb2.ACommands()
pack = command.load.add()
pack.whnum = 2
pack.truckid = 2
pack.shipid = 2
pack.seqnum = 3

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock.sendall(command_size+command_data)
response = world_amazon_pb2.AResponses()
recv_data(sock, response)
print(response)
#recv_data(sock, response)
#print(response)


command = amazon_ups_pb2.AUCommands()

request = command.init_delivery
request.package_id = 2

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

response = amazon_ups_pb2.UACommands()
recv_data(sock_ups, response)
print(response)
"""
command = amazon_ups_pb2.AUCommands()

request = command.init_delivery
request.package_id = 2

command_data = command.SerializeToString()
command_size = encode_varint(len(command_data))
print(command_size+command_data)
sock_ups.sendall(command_size+command_data)

response = amazon_ups_pb2.UACommands()
recv_data(sock_ups, response)
print(response)
"""

time.sleep(10000)

