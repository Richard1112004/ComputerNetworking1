import hashlib
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulated tracker storage
tracker_storage = {}

def create_info_dict(file_name, file_length, piece_length):
    num_pieces = (file_length + piece_length - 1) // piece_length
    pieces = b''.join(hashlib.sha1(b'piece' + bytes(i)).digest() for i in range(num_pieces))
    pieces_hex = pieces.hex()  # Convert bytes to hexadecimal representation
    info_dict = {
        'name': file_name,
        'piece length': piece_length,
        'pieces': pieces_hex,
        'length': file_length,
        'files': [{
            'length': file_length,
            'path': [file_name]
        }]
    }
    return info_dict

def generate_torrent_metadata(file_name, file_length, piece_length, tracker_url):
    info_dict = create_info_dict(file_name, file_length, piece_length)
    serialized_info = json.dumps(info_dict, sort_keys=True).encode()
    info_hash = hashlib.sha1(serialized_info).hexdigest()
    tracker_storage[info_hash] = {
        "announce": tracker_url,
        "info": info_dict,
        "comment": "This is an example .torrent file for demonstration purposes.",
        "created by": "ExampleTorrentMaker"
    }
    return info_hash

@app.route('/announce', methods=['GET'])
def announce():
    info_hash = request.args.get('info_hash')
    if info_hash in tracker_storage:
        return jsonify(tracker_storage[info_hash])
    else:
        return jsonify({"error": "Info hash not found"}), 404

# Example of generating torrent metadata and storing it in the tracker
tracker_url = "http://localhost:5000/announce"
file_name = "MyExampleFile.txt"
file_length = 2097152  # 2 MB
piece_length = 524288  # 512 KB
info_hash = generate_torrent_metadata(file_name, file_length, piece_length, tracker_url)

# Simulating a peer requesting metadata using a magnet link
def simulate_peer_request():
    magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={file_name}&tr={tracker_url}"
    
    # Extract info_hash from the magnet link
    extracted_info_hash = magnet_link.split('btih:')[1].split('&')[0]
    print("hi", info_hash)
    print("hi", extracted_info_hash)
    
    # Simulate contacting the tracker
    response = request_tracker_metadata(extracted_info_hash)
    return response

def request_tracker_metadata(info_hash):
    with app.test_request_context('/announce?info_hash=' + info_hash):
        return announce().get_json()

# Run the Flask app in a separate thread for testing
if __name__ == '__main__':
    from threading import Thread
    Thread(target=app.run, kwargs={'port': 5000}).start()
    
    # Simulate peer request
    peer_response = simulate_peer_request()
    print("Peer Response from Tracker:")
    print(json.dumps(peer_response, indent=4))
