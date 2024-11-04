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
call = time.time()
count = 0
class Node:
    def __init__(self, node_id: int, recieve_port: int, send_port: int):
        self.node_id = node_id
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
    # def ask_file_size(self, filename: str, file_owner: tuple) -> int:
    #     temp_port = create_random_port()
    #     temp_sock = set_socket(temp_port)
    #     dest_node = file_owner[0]

    #     msg = Node_to_Node(src_node_id=self.node_id,
    #                     dest_node_id=dest_node["node_id"],
    #                     filename=filename)
    #     self.send_segment(sock=temp_sock,
    #                       data=msg.encode(),
    #                       addr=tuple(dest_node["addr"]))
    #     while True:
    #         data, addr = temp_sock.recvfrom(config.constants.BUFFER_SIZE)
    #         dest_node_response = Data.decode(data)
    #         size = dest_node_response["size"]
    #         free_socket(temp_sock)

    #         return size
    # def split(self, file_owners: list, filename: str):
    #     owners = []
    #     for owner in file_owners:
    #         if owner[0]['node_id'] != self.node_id:
    #             owners.append(owner)
    #     if len(owners) == 0:
    #         print(f"NoOne has {filename}")
    #         return
    #     # sort owners based on their sending frequency
    #     owners = sorted(owners, key=lambda x: x[1], reverse=True)
    #     # if MAX_SPLITTNES_RATE is 3, then to_be_used_owners will 
    #     # contain only the top 3 owners with the highest send frequency.
    #     to_be_used_owners = owners[:config.const["MAX_SPLITTNES_RATE"]]
    #     # stop here
    #     # 1. first ask the size of the file from peers
    #     print(f"You are going to download {filename} from Node(s) {[o[0]['node_id'] for o in to_be_used_owners]}")
    #     file_size = self.ask_file_size(filename=filename, file_owner=to_be_used_owners[0])
    #     print(f"The file {filename} which you are about to download, has size of {file_size} bytes")

    #     # 2. Now, we know the size, let's split it equally among peers to download chunks of it from them
    #     step = file_size / len(to_be_used_owners)
    #     chunks_ranges = [(round(step*i), round(step*(i+1))) for i in range(len(to_be_used_owners))]

    #     # 3. Create a thread for each neighbor peer to get a chunk from it
    #     self.downloaded_files[filename] = []
    #     neighboring_peers_threads = []
    #     for idx, obj in enumerate(to_be_used_owners):
    #         t = Thread(target=self.receive_chunk, args=(filename, chunks_ranges[idx], obj))
    #         t.setDaemon(True)
    #         t.start()
    #         neighboring_peers_threads.append(t)
    #     for t in neighboring_peers_threads:
    #         t.join()

    #     print("All the chunks of {} has downloaded from neighboring peers. But they must be reassembled!".format(filename))

    #     # 4. Now we have downloaded all the chunks of the file. It's time to sort them.
    #     sorted_chunks = self.sort_downloaded_chunks(filename=filename)
    #     print(f"All the pieces of the {filename} is now sorted and ready to be reassembled.")

    #     # 5. Finally, we assemble the chunks to re-build the file
    #     total_file = []
    #     file_path = f"{config.directory.node_files_dir}node{self.node_id}/{filename}"
    #     for chunk in sorted_chunks:
    #         for piece in chunk:
    #             total_file.append(piece["chunk"])
    #     self.reassemble_file(chunks=total_file,
    #                          file_path=file_path)
    #     print(f"{filename} has successfully downloaded and saved in my files directory.")
    #     self.files.append(filename)
    # def search(self, filename: str) -> dict:
    #     msg = Node_to_Tracker(node_id=self.node_id,
    #                        mode=config.tracker_requests["DOWNLOAD"],
    #                        filename=filename)
    #     port = create_random_port()
    #     search_sock = set_socket(port)
    #     self.send_segment(sock=search_sock,
    #                       data=msg.encode(),
    #                       addr=tuple(config.const["TRACKER_ADDR"]))
    #     while True:
    #         data, addr = search_sock.recvfrom(config.const["BUFFER_SIZE"])
    #         from_tracker = Data.decode(data)
    #         return from_tracker
    # def download(self, filename: str):
    #     # I will fix later
    #     file_path = f"{config.dir["node_dir"]}node{self.node_id}/{filename}"
    #     if os.path.isfile(file_path):
    #         print(f"You already have this one!")
    #         return
    #     else:
    #         print(f"Let's search file in torrent!")
    #         response = self.search(filename=filename)
    #         file_owners = response['result']
    #         # stop here
    #         self.split(file_owners=file_owners, filename=filename)
    def inform_tracker_periodically(self, interval: int):
        # Update and print the current time for each call
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Node {self.node_id} is still alive in the torrent!")
        global count
        if count != 0:
            msg = Node_to_Tracker(node_id=self.node_id,
                                mode=config.tracker_requests["REQUEST"],
                                filename="", metadata="")

            self.send_segment(sock=self.send_socket,
                            data=msg.encode())

        # Schedule the next call
        count = count+1
        Timer(interval, self.inform_tracker_periodically, args=(interval,)).start()
    def go_torrent(self):
        msg = Node_to_Tracker(node_id=self.node_id,
                           mode=config.tracker_requests["REQUEST"],
                           filename="", metadata="")

        addr = tuple(config.const["TRACKER_ADDR"])
        ip, track_port = addr
        self.send_socket.connect((ip, track_port))
        print(f"Connected to server at {ip}:{track_port}")
        self.send_segment(sock=self.send_socket,
                          data=Data.encode(msg))
        

        
def run (args):
    node = Node(node_id=args.node_id,recieve_port=create_random_port(), send_port=create_random_port())
    node.go_torrent()
    print("You're in program")
    timer_thread = Thread(target=node.inform_tracker_periodically, args=(config.const["NODE_TIME_INTERVAL"],))
    timer_thread.daemon = True
    timer_thread.start()
    print("ENTER YOUR COMMAND!")
    while True:
        command = input()
        mode, filename = command(command)

        #################### send mode ####################
        if mode == 'update':
            print("update")
        #################### download mode ####################
        elif mode == 'download':                
            # phuc hung
            t = Thread(target=node.download, args=(filename,))
            t.setDaemon(True)
            t.start()
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