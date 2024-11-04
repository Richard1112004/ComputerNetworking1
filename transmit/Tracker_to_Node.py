from transmit.data import Data

class Tracker_to_Node(Data):
    def __init__(self, dest_node_id: int, result: list, filename: str):

        super().__init__()
        self.dest_node_id = dest_node_id
        self.result = result
        self.filename = filename
