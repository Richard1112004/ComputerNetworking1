from flask import Flask, request, jsonify

app = Flask(__name__)

# A simple in-memory store for registered peers
registered_peers = {}

@app.route('/tracker', methods=['GET'])
def tracker():
    action = request.args.get('action')
    peer_id = request.args.get('peer_id')
    magnet_text = request.args.get('magnet_text')
    downloaded_bytes = request.args.get('downloaded_bytes', 0)

    if action == 'register':
        if peer_id and magnet_text:
            # Register the peer
            registered_peers[peer_id] = {
                'magnet': magnet_text,
                'downloaded_bytes': downloaded_bytes
            }
            print(f"Registered peer: {peer_id} with magnet: {magnet_text}")
            return jsonify({"status": "success", "message": "Registration successful."})
        else:
            return jsonify({"status": "error", "message": "Missing peer_id or magnet_text."}), 400

    elif action == 'started':
        print(f"Started request from {peer_id} with magnet text: {magnet_text} and downloaded bytes: {downloaded_bytes}")
        return jsonify({"status": "success", "message": "Started tracking."})
    
    elif action == 'stopped':
        print(f"Stopped request from {peer_id}.")
        return jsonify({"status": "success", "message": "Stopped tracking."})
    
    elif action == 'completed':
        print(f"Completed request from {peer_id}.")
        return jsonify({"status": "success", "message": "Completed tracking."})

    return jsonify({"status": "error", "message": "Invalid action."}), 400

if __name__ == '__main__':
    app.run(port=80)
