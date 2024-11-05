from transmit.Tracker_to_Node import *
from utils import *
import datetime
from threading import *
from collections import defaultdict
from transmit.data import Data
import time
import json
from TCPlimit import TCPlimit
call = time.time()
class Tracker:
    def __init__(self):
        self.port = get_random_unused_port()[1]
        self.tracker_socket = set_socket(config.const["TRACKER_ADDR"][1])
        self.has_informed_tracker = defaultdict(bool)
        self.file_owners_list = defaultdict(list)
        self.send_freq_list = defaultdict(int)
        self.send_peer_list = []
        self.info_peers = []
    def search_file(self, msg: dict, addr: tuple):
        print(f"Node{msg['node_id']} is searching for {msg['filename']}")
        # fix this
        matched_entries = []
        for json_entry in self.file_owners_list[msg['filename']]:
            entry = json.loads(json_entry)
            matched_entries.append((entry, self.send_freq_list[entry['node_id']]))

        tracker_response = Tracker_to_Node(dest_node_id=msg['node_id'],
                                        result=matched_entries)

        self.send_segment(sock=self.tracker_socket,
                          data=tracker_response.encode(),
                          addr=addr)
    def create_info_peer(self, msg: dict, addr: tuple):
        info_peer = {
                'peer_id': msg['node_id'],
                'ip': addr[0],
                'port': addr[1],
                'metadata': msg['metadata'] 
        }
        self.info_peers.append(info_peer)
    def add_file_owner(self, msg: dict, addr: tuple):
        entry = {
            'node_id': msg['node_id'],
            'addr': addr
        }
        metadata_key = json.dumps(msg['metadata'], sort_keys=True)  
        if metadata_key not in self.file_owners_list:
            self.file_owners_list[metadata_key] = []  
        self.file_owners_list[metadata_key].append(json.dumps(entry))
        self.file_owners_list[metadata_key] = list(set(self.file_owners_list[metadata_key]))
        if msg['node_id'] not in self.send_freq_list:
            self.send_freq_list[msg['node_id']] = 0  
        self.send_freq_list[msg['node_id']] += 1
        self.create_info_peer(msg, addr)
        if msg['node_id'] not in self.send_peer_list:
            self.send_peer_list.append(msg['node_id'])
        print(self.file_owners_list)
    
    def handle(self, data: bytes, addr: tuple, conn: socket.socket):
        msg = Data.decode(data)
        mode = msg['mode']
        if mode == config.tracker_requests["UPDATE"]:
            self.add_file_owner(msg=msg, addr=addr)
        if mode == config.tracker_requests["DOWNLOAD"]:
            self.search_file(msg=msg, addr=addr)
        # elif mode == config.tracker_requests_mode.UPDATE:
        #     self.update_db(msg=msg)
        if mode == config.tracker_requests["REQUEST"]:
            self.has_informed_tracker[(msg['node_id'], addr)] = True
            self.respond_tracker(msg['node_id'], conn=conn)
        # elif mode == config.tracker_requests_mode.EXIT:
        #     self.remove_node(node_id=msg['node_id'], addr=addr)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Node {msg['node_id']} in torrent")
    def remove_node(self, node_id: int, addr: tuple):
        entry = {
            'node_id': node_id,
            'addr': addr
        }
        try:
            self.send_freq_list.pop(node_id)
        except KeyError:
            pass
        self.has_informed_tracker.pop((node_id, addr))
        node_files = self.file_owners_list.copy()
        for nf in node_files:
            if json.dumps(entry) in self.file_owners_list[nf]:
                self.file_owners_list[nf].remove(json.dumps(entry))
            if len(self.file_owners_list[nf]) == 0:
                self.file_owners_list.pop(nf)
    def send_segment(self, sock: socket.socket, data: bytes):
        # sock.connect((ip, track_port))
        # print(f"Connected to server at {ip}:{track_port}")
        segment = TCPlimit(
            data=data
        )
        encrypted_data = segment.data  
        sock.sendall(encrypted_data)
    def createResDict(self):
        torrent = {
            "fail" : "",
            "warning": "",
            "peers" : self.info_peers
        }
        return torrent

    def respond_tracker(self, node_id: int, conn: socket.socket):
        torrent = self.createResDict()
        msg = Tracker_to_Node(dest_node_id=node_id, result=torrent)
        self.send_segment(sock=conn,data=msg.encode())

        
    def check_nodes_periodically(self, interval: int):
        alive_nodes = set()
        dead_nodes = set()

        # Create a copy to safely iterate over
        has_informed_tracker_copy = self.has_informed_tracker.copy()

        for node, has_informed in has_informed_tracker_copy.items():
            node_id, node_addr = node
            if has_informed:
                # Node is alive, reset its informed status
                self.has_informed_tracker[node] = False
                alive_nodes.add(node_id)
            else:
                # Node has not informed, mark it as dead
                dead_nodes.add(node_id)
                self.remove_node(node_id=node_id, addr=node_addr)

        # Log active and inactive nodes if there were any changes
        if alive_nodes or dead_nodes:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} - Node(s) {list(alive_nodes)} is in the torrent and Node(s) {list(dead_nodes)} have left.")

        # Schedule the next call using Timer
        Timer(interval, self.check_nodes_periodically, args=(interval,)).start()

    def handle_client(self, conn, addr):
        """Handle individual client connections in separate threads."""
        with conn:
            while True:
                data = conn.recv(config.const["BUFFER_SIZE"])
                if not data:
                    break  # Exit loop if no data (client closed connection)

                # Process the data in a new thread
                t = Thread(target=self.handle, args=(data, addr, conn))
                t.start()
        print(f"Connection closed with {addr}")
    def listen(self):
        timer_thread = Thread(target=self.check_nodes_periodically, args=(config.const["TRACKER_TIME_INTERVAL"],))
        timer_thread.daemon = True
        timer_thread.start()
        self.tracker_socket.listen() 
        # print(f"Tracker server listening on {config.const['TRACKER_ADDR'][1]}")

        
        while True:
            # Accept a new connection
            
            # code này kp của t nên cmt lại
            # conn, addr = self.tracker_socket.accept()
            hostname = socket.gethostname()
            hostip = get_host_default_interface_ip()
            print("Listening on: {}:{}:{}".format(hostname,hostip,self.port))
            serversocket = socket.socket()
            serversocket.bind((hostname, self.port))

            serversocket.listen(10)
            conn, addr = serversocket.accept()
            print(f"Connection established with {addr, conn}")

            # Start a new thread to handle the connection
            client_thread = Thread(target=self.handle_client, args=(conn, addr))
            client_thread.daemon = True  # This ensures threads exit when main program exits
            client_thread.start()
    def run(self):
        
        # print("Tracker start at", config.const["TRACKER_ADDR"][1])
        t = Thread(target=self.listen())
        t.daemon = True
        t.start()
        t.join()

# get_host_default_interface_ip uses UDP socket to check if the socket is working
def get_host_default_interface_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
       s.connect(('8.8.8.8',1))
       ip = s.getsockname()[0]
    except Exception:
       ip = '127.0.0.1'
    finally:
       s.close()
    return ip    

if __name__ == '__main__':
    t = Tracker()
    t.run()