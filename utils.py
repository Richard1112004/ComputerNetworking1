import socket
from config import config
import random
import warnings
used_ports = []

def set_socket(port: int) -> socket.socket:
    # create new socket from specific port
    try:
        soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # allow to reuse this socket address
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(('localhost', port))
        used_ports.append(port)
        return soc
    except Exception as e:
        print(f"Failed to create socket on port {port}: {e}")
        raise


def create_random_port() -> int:
    available_ports = config.const["AVAILABLE_PORTS_RANGE"]
    rand_port = random.randint(available_ports[0], available_ports[1])
    while rand_port in used_ports:
        rand_port = random.randint(available_ports[0], available_ports[1])

    return rand_port

def parse_command(command: str):
    parts = command.split(' ')
    try:
        parts = command.split(maxsplit=1)  # Split the command into two parts: mode and filename
        if len(parts) == 2:
            mode, filename = parts
        else:
            mode = parts[0]  # Only the mode is provided
            filename = ""    # No filename provided
        return mode, filename
    except IndexError:
        warnings.warn("INVALID COMMAND ENTERED. TRY ANOTHER!")
        return
    
def free_socket(sock: socket.socket):
    used_ports.remove(sock.getsockname()[1])
    sock.close()

# this funtion uses to get unsued port and if needed params
def get_random_unused_port():
    hostname = socket.gethostname() 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  
        ip, port = s.getsockname()  
        return hostname, port, ip
