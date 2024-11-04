from transmit.data import Data

class Node_to_Tracker(Data):
    def __init__(self, node_id: int, mode: int, filename: str, metadata: dict):

        super().__init__()
        self.node_id = node_id
        self.filename = filename
        self.mode = mode
        self.metadata = metadata





