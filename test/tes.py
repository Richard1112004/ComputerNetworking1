import requests

tracker_url = 'http://localhost/tracker'

# Function to register a peer
def register_peer(peer_id, magnet_text):
    params = {
        'action': 'register',
        'peer_id': peer_id,
        'magnet_text': magnet_text,
        'downloaded_bytes': 0
    }
    response = requests.get(tracker_url, params=params)
    print("Registration Response:", response.json())
    return response

# Function to simulate starting tracking
def start_tracking(peer_id, magnet_text, downloaded_bytes):
    params = {
        'action': 'started',
        'peer_id': peer_id,
        'magnet_text': magnet_text,
        'downloaded_bytes': downloaded_bytes
    }
    response = requests.get(tracker_url, params=params)
    print("Started Response:", response.json())
    return response

# Function to simulate completing tracking
def complete_tracking(peer_id):
    params = {
        'action': 'completed',
        'peer_id': peer_id
    }
    response = requests.get(tracker_url, params=params)
    print("Completed Response:", response.json())
    return response

# Function to simulate stopping tracking
def stop_tracking(peer_id):
    params = {
        'action': 'stopped',
        'peer_id': peer_id
    }
    response = requests.get(tracker_url, params=params)
    print("Stopped Response:", response.json())
    return response

# Example usage
if __name__ == '__main__':
    # Register a peer
    register_peer('peer123', 'magnet:?xt=urn:btih:1234567890abcdef')

    # Start tracking
    start_tracking('peer123', 'magnet:?xt=urn:btih:1234567890abcdef', 1024)

    # Complete tracking
    complete_tracking('peer123')

    # Stop tracking
    stop_tracking('peer123')
