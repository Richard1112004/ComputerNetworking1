import socket
import json
from ..config import config

class TCPData:
    def __init__(self, data: bytes):
        # Enforce a maximum data size for TCP segments.
        assert len(data) <= config.const["TCP_LIMIT"], print(
            f"MAXIMUM DATA SIZE OF A TCP SEGMENT IS {config.const['TCP_LIMIT']}"
        )
        self.data = data

def send_segment(sock: socket.socket, data: bytes):
    # Create a TCPData object with the data to send
    tcp_data = TCPData(data=data)

    # Send the data over the TCP socket
    sock.send(tcp_data.data)

def request_tracker(sock: socket.socket, tracker_address: tuple, filename: str):
    # Create a request to the tracker
    request_data = {
        'action': 'request_file',
        'filename': filename
    }
    sock.sendall(json.dumps(request_data).encode('utf-8'))

    # Wait for the tracker response
    response_data = sock.recv(1024).decode('utf-8')
    response = json.loads(response_data)
    return response

def main():
    tracker_address = ('localhost', 8080)  # Replace with your tracker address and port
    filename = 'example_file.txt'
    
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the tracker
        sock.connect(tracker_address)

        # Request information from the tracker
        tracker_response = request_tracker(sock, tracker_address, filename)
        print(f"Received response from tracker: {tracker_response}")

        # Check for a successful response and retrieve data
        if tracker_response.get('status') == 'success':
            data_to_send = tracker_response.get('data').encode('utf-8')  # Assuming the data is in the response
            
            # Send the segment
            send_segment(sock, data_to_send)
            print(f"Data sent to tracker: {data_to_send}")

        else:
            print(f"Error from tracker: {tracker_response.get('error')}")

    finally:
        # Close the socket
        sock.close()

if __name__ == "__main__":
    main()
