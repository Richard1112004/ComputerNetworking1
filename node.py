import argparse
from transmit.data import Data
from transmit.Node_to_Tracker import *
from transmit.Node_to_Node import *
from threading import *
from utils import *
import time
from TCPlimit import TCPlimit
import datetime
import os
import math
import hashlib
import json
# from flask import Flask, request, jsonify
call = time.time()
count = 0
class Node:
    def __init__(self, node_id: int, recieve_port: int, send_port: int, socket: socket.socket, tracker_ip):
        self.node_id = node_id
        self.tracker_ip = tracker_ip
        self.receive_port = recieve_port
        self.send_port = send_port
        # self.recieve_socket = set_socket(recieve_port)
        # self.send_socket = set_socket(send_port) 
        self.send_socket = socket
        self.is_in_send_mode = False    # is thread uploading a file or not
        self.downloaded_files = {}        

    def send_segment(self, sock: socket.socket, data: bytes):
        # sock.connect((ip, track_port))
        # print(f"Connected to server at {}:{track_port}")
        segment = TCPlimit(
            data=data
        )
        print("sending segment")
        encrypted_data = segment.data  
        sock.sendall(encrypted_data)
        print("sent")
        # response = sock.recv(config.const["BUFFER_SIZE"])  
        # if response:
        #     print("Server has received the data:")
        # else:
        #     print("No response from server.")
   
    def inform_tracker_periodically(self, interval: int):
        # Update and print the current time for each call
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Node {self.node_id} is still alive in the torrent!")
        global count
        if count != 0:
            msg = Node_to_Tracker(node_id=self.node_id,
                                mode=config.tracker_requests["REQUEST"],
                                metadata="")

            self.send_segment(sock=self.send_socket,
                            data=msg.encode())

        # Schedule the next call
        count = count+1
        Timer(interval, self.inform_tracker_periodically, args=(interval,)).start()
    def go_torrent(self, ip, port):
        msg = Node_to_Tracker(node_id=self.node_id,
                           mode=config.tracker_requests["REQUEST"],
                            metadata="")

        # addr = tuple(config.const["TRACKER_ADDR"])
        # ip, track_port = addr
        # self.send_socket.connect((ip, track_port))
        # print(f"Connected to server at {ip}:{track_port}")

        # self.send_socket.connect((ip, port))
        print(f"Connected to server at {ip}:{port}")
        self.send_segment(sock=self.send_socket,
                          data=Data.encode(msg))
        # data = self.send_socket.recv(config.const["BUFFER_SIZE"])
        print("f")
        # msg = Data.decode(data)
        print("tesst")
        return msg
    def create_info_dict(self, file_name):
        with open(file_name, 'rb') as file:
            file_data = file.read()
        info_dict = {
                'name': file_name,
                'length': len(file_data),
                'piece length': 512,
                'pieces_count': math.ceil(len(file_data)/512) 
        }
        return info_dict
    def get_DotTorrent(self, directory_path):
        files = os.listdir(directory_path)
        info_arr = []
        for file in files:
            full_path = os.path.join(directory_path, file)  
            info_arr.append(self.create_info_dict(full_path))  
        torrent = {
            "IP" : "localhost",
            "info" : info_arr,
        }
        return torrent
    def update(self, directory_path):
        metadata = self.get_DotTorrent(directory_path)
        msg = Node_to_Tracker(node_id=self.node_id,
                            mode=config.tracker_requests["UPDATE"],
                            metadata=metadata)

        self.send_segment(sock=self.send_socket,
                            data=msg.encode())  
    
    def set_send_mode(self, filename: str):
        # if filename not in self.files:
            
        #     return
        message = Node_to_Tracker(node_id=self.node_id,
                               mode=config.tracker_requests['UPDATE'],
                               metadata=filename)

        self.send_segment(sock=self.send_socket,
                          data=message.encode(),
                          )
        print("test")
        if self.is_in_send_mode:    # has been already in send(upload) mode
            log_content = f"Some other node also requested a file from you! But you are already in SEND(upload) mode!"
            # log(node_id=self.node_id, content=log_content)
            return
        else:
            self.is_in_send_mode = True
            log_content = f"You are free now! You are waiting for other nodes' requests!"
            # log(node_id=self.node_id, content=log_content)
            # t = Thread(target=self.listen, args=())
            # t.setDaemon(True)
            # t.start()


        
def run (args):

    print('Connecting to: {}:{:d}'.format(args.s, args.p))
    client_socket = socket.socket()
    try:
        client_socket.connect((args.s, args.p))   
    except:
        print( "Could not connect") 
    node = Node(node_id=args.node_id,recieve_port=args.p, send_port=create_random_port(),socket= client_socket, tracker_ip=args.s)

    metadata = node.go_torrent(args.s, args.p)
    print("meta data")
    print(metadata)
    print("You're in program")
    timer_thread = Thread(target=node.inform_tracker_periodically, args=(config.const["NODE_TIME_INTERVAL"],))
    timer_thread.daemon = True
    timer_thread.start()
    
    while True:
        print("ENTER YOUR COMMAND!")
        command = input()
        mode, filename = parse_command(command)

        #################### send mode ####################
        if mode == 'update':
            print("dddd")
            node.set_send_mode(filename)
            # t = Thread(target=node.update, args=(torrent))
            # t.daemon = True
            # t.start()
        #################### download mode ####################
        # elif mode == 'download':                
        #     # phuc hung
        #     t = Thread(target=node.download, args=(torrent))
        #     t.setDaemon(True)
        #     t.start()
        #################### exit mode ####################
        elif mode == 'exit':
            print("exit")
        else:
            print("Try again. Mode(update, download, exit) <space> File_name")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='Client',
                        description='Connect to tracker',
                        epilog='!!!It requires the server is running and listening!!!')
    # Use for the client to connect to tracker
    parser.add_argument('-s', required=True, metavar="SERVER_IP",help='Địa chỉ IP của server')
    parser.add_argument('-p', type=int, required=True,metavar='SERVER_PORT', help='Cổng của server')

    parser.add_argument('node_id', type=int)
    node_args = parser.parse_args()
    server_ip = node_args.s
    port = node_args.p
    run(args=node_args)