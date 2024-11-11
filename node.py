import argparse
from transmit.data import Data
from transmit.Node_to_Tracker import *
from transmit.Node_to_Node import *
from threading import *
from utils import *
import time
from TCPlimit import TCPlimit
import datetime
from collections import defaultdict
import os
import math
import hashlib
import json
from flask import Flask, request, jsonify
call = time.time()
count = 0
class Node:
    def __init__(self, node_id: int, recieve_port: int, send_port: int):
        self.node_id = node_id
        self.downloaded_files= {}
        self.recieve_socket = set_socket(recieve_port)
        self.send_socket = set_socket(send_port) 
    def send_segment(self, sock: socket.socket, data: bytes):
        # sock.connect((ip, track_port))
        # print(f"Connected to server at {ip}:{track_port}")
        segment = TCPlimit(
            data=data
        )
        encrypted_data = segment.data  
        sock.sendall(encrypted_data)
    
    
    def inform_tracker_periodically(self, interval: int):
        # Update and print the current time for each call
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Node {self.node_id} is still alive in the torrent!")
        global count
        if count != 0:
            msg = Node_to_Tracker(node_id=self.node_id,
                                mode=config.tracker_requests["REQUEST"],
                                metadata="", name="")

            self.send_segment(sock=self.send_socket,
                            data=msg.encode())

        # Schedule the next call
        count = count+1
        Timer(interval, self.inform_tracker_periodically, args=(interval,)).start()
    def go_torrent(self):
        msg = Node_to_Tracker(node_id=self.node_id,
                           mode=config.tracker_requests["REQUEST"],
                            metadata="", name="")

        addr = tuple(config.const["TRACKER_ADDR"])
        ip, track_port = addr
        self.send_socket.connect((ip, track_port))
        print(f"Connected to server at {ip}:{track_port}")
        self.send_segment(sock=self.send_socket,
                          data=Data.encode(msg))
        data = self.send_socket.recv(config.const["BUFFER_SIZE"])
        msg = Data.decode(data)
        return msg
    def create_info_dict(self, file_name):
        with open(file_name, 'rb') as file:
            file_data = file.read()
        info_dict = {
                'name': os.path.basename(file_name),
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
                            metadata=metadata,name=os.path.basename(directory_path))

        self.send_segment(sock=self.send_socket,
                            data=msg.encode())  
        
    def download(self, name: str):
            print("Downloading")
            tracker_response = self.search_torrent(name=name)
            file_owners = tracker_response['result']
            print(file_owners)
            self.split_file_owners(file_owners=file_owners, name=name)
    
    def search_torrent(self, name: str) -> dict:
        msg = Node_to_Tracker(node_id=self.node_id,
                           mode=config.tracker_requests['DOWNLOAD'],
                           metadata="",name=name)
        self.send_segment(sock=self.send_socket,
                          data=msg.encode(),
                         )
        # now we must wait for the tracker response
        while True:
            data, addr = self.send_socket.recvfrom(config.const['BUFFER_SIZE'])
            tracker_msg = Data.decode(data)
            print(tracker_msg)
            print("aaaaaaaaaaaaaaaaaaaa")
            return tracker_msg
    # def receive_chunk(self, filename: str, range: tuple, file_owner: tuple):
        dest_node = file_owner[0]
        # we set idx of ChunkSharing to -1, because we want to tell it that we
        # need the chunk from it
        msg = ChunkSharing(src_node_id=self.node_id,
                           dest_node_id=dest_node["node_id"],
                           filename=filename,
                           range=range)
        temp_port = generate_random_port()
        temp_sock = set_socket(temp_port)
        self.send_segment(sock=temp_sock,
                          data=msg.encode(),
                          addr=tuple(dest_node["addr"]))
        log_content = "I sent a request for a chunk of {0} for node{1}".format(filename, dest_node["node_id"])
        log(node_id=self.node_id, content=log_content)

        while True:
            data, addr = temp_sock.recvfrom(config.constants.BUFFER_SIZE)
            msg = Message.decode(data) # but this is not a simple message, it contains chunk's bytes
            if msg["idx"] == -1: # end of the file
                free_socket(temp_sock)
                return

            self.downloaded_files[filename].append(msg)
    
    # thread chạy nhiều file đồng bộ
    def down(self, info1, peers):
        print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        print(info1)
             # 2. Now, we know the size, let's split it equally among peers to download chunks of it from them
        step = info1['length'] / len(peers)
        chunks_ranges = [(round(step*i), round(step*(i+1))) for i in range(len(peers))]

        # 3. Create a thread for each neighbor peer to get a chunk from it
        self.downloaded_files[info1['name']] = []
        neighboring_peers_threads = []
        print("donald trump")
        # for idx, obj in enumerate(len(peers)):
        #     t = Thread(target=self.receive_chunk, args=(info1['name'], chunks_ranges[idx], obj))
        #     t.setDaemon(True)
        #     t.start()
        #     neighboring_peers_threads.append(t)
        # for t in neighboring_peers_threads:
        #     t.join()
            
    def split_file_owners(self, file_owners: list, name: str):
        # owners = []
        # for owner in file_owners:
        #     if owner[0]['node_id'] != self.node_id:
        #         owners.append(owner)
        if file_owners == []:
            print(f"No one has {name}")
            return
        # ? We do not implement algorithms here 
        # sort owners based on their sending frequency
        # owners = sorted(owners, key=lambda x: x[1], reverse=True)

        # to_be_used_owners = owners[:config.constants.MAX_SPLITTNES_RATE]
        
        # 1. first ask the size of the file from peers
        print(f"You are going to download {name} from Node(s) {[o['node_id'] for o in file_owners[0]['peers']]}")
        print("aaa")
                # log(node_id=self.node_id, content=log_content)
        file_threads = []
        # file_count = len(file_owners[0]['metadata']['info'])
        for i in file_owners[0]['metadata']['info']:
            thread = Thread(target = self.down, args=(i, file_owners[0]['peers'],))
            thread.daemon=True
            thread.start()
            file_threads.append(thread)
        for t in file_threads:
            t.join()
        

        # # 4. Now we have downloaded all the chunks of the file. It's time to sort them.
        # sorted_chunks = self.sort_downloaded_chunks(filename=filename)
        # log_content = f"All the pieces of the {filename} is now sorted and ready to be reassembled."
        # log(node_id=self.node_id, content=log_content)

        # # 5. Finally, we assemble the chunks to re-build the file
        # total_file = []
        # file_path = f"{config.directory.node_files_dir}node{self.node_id}/{filename}"
        # for chunk in sorted_chunks:
        #     for piece in chunk:
        #         total_file.append(piece["chunk"])
        # self.reassemble_file(chunks=total_file,
        #                      file_path=file_path)
        # log_content = f"{filename} has successfully downloaded and saved in my files directory."
        # log(node_id=self.node_id, content=log_content)
        # self.files.append(filename)
        
def run (args):

    node = Node(node_id=args.node_id,recieve_port=create_random_port(), send_port=create_random_port())
    metadata = node.go_torrent()
    print("meta data")
    print(metadata)
    print("You're in program")
    timer_thread = Thread(target=node.inform_tracker_periodically, args=(config.const["NODE_TIME_INTERVAL"],))
    timer_thread.daemon = True
    timer_thread.start()
    print("ENTER YOUR COMMAND!")
    while True:
        command = input()
        mode, torrent = parse_command(command)

        #################### send mode ####################
        if mode == 'update':
            t = Thread(target=node.update, args=(torrent,))
            t.daemon = True
            t.start()
        ################### download mode ####################
        elif mode == 'a':                
            # phuc hung
            t = Thread(target=node.download, args=(torrent,))
            t.daemon = True
            t.start()
        # update C:\\Clone\\ddd\\ComputerNetworking1\\node\\node1\\hung.txt
        #################### exit mode ####################
        elif mode == 'exit':
            print("exit")
        else:
            print("Try again. Mode(update, download, exit) <space> File_name")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('node_id', type=int)
    node_args = parser.parse_args()
    run(args=node_args)