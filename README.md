# Computer Networking Project

This project simulates a peer-to-peer (P2P) file sharing network. It includes the implementation of nodes and a tracker to manage the network. Nodes can join the network, search for files, download files from other nodes, and periodically inform the tracker of their status.

## Components

- **Node**: Represents a peer in the network. Nodes can request files from other nodes, share files, and communicate with the tracker.
- **Tracker**: Manages the network by keeping track of active nodes and the files they share. It helps nodes find peers that have the requested files.

## How to Run

### Running the Tracker

To start the tracker, run the following command:

python3 tracker.py


### Running the Node
To start the node, run the following command:

python3 node.py id