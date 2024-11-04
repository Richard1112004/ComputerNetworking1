import hashlib
import json

def create_info_dict(file_name, file_length, piece_length):
    # Calculate the number of pieces
    num_pieces = (file_length + piece_length - 1) // piece_length

    # Create a placeholder for piece hashes (example only, replace with actual file piece hashes)
    pieces = b''.join(hashlib.sha1(b'piece' + bytes(i)).digest() for i in range(num_pieces))
    
    # Convert pieces from bytes to hex string
    pieces_hex = pieces.hex()  # Convert bytes to hexadecimal representation

    # Create the info dictionary
    info_dict = {
        'name': file_name,
        'piece length': piece_length,
        'pieces': pieces_hex,  # Use the hexadecimal representation
        'length': file_length,
        'files': [{
            'length': file_length,
            'path': [file_name]
        }]
    }

    return info_dict

def create_magnet_link(info_hash, file_name, tracker_url):
    # Construct the magnet link
    magnet_link = (
        f"magnet:?xt=urn:btih:{info_hash}&dn={file_name}&tr={tracker_url}"
    )
    return magnet_link

def generate_torrent_metadata():
    # Torrent file details
    file_name = "MyExampleFile.txt"
    file_length = 2097152  # 2 MB
    piece_length = 524288  # 512 KB
    tracker_url = "http://your-tracker-portal.local/announce"

    # Create the info dictionary
    info_dict = create_info_dict(file_name, file_length, piece_length)

    # Serialize info dict to create info hash
    serialized_info = json.dumps(info_dict, sort_keys=True).encode()
    info_hash = hashlib.sha1(serialized_info).hexdigest()

    # Create the magnet link
    magnet_link = create_magnet_link(info_hash, file_name, tracker_url)

    # Create the metadata for the .torrent file
    torrent_metadata = {
        "announce": tracker_url,
        "info": info_dict,
        "comment": "This is an example .torrent file for demonstration purposes.",
        "created by": "ExampleTorrentMaker"
    }

    return torrent_metadata, magnet_link

# Generate the torrent metadata and magnet link
metadata, magnet = generate_torrent_metadata()

# Print results
print("Torrent Metadata:")
print(json.dumps(metadata, indent=4))

print("\nMagnet Link:")
print(magnet)
