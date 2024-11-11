from transmit.data import Data

class Node_to_Tracker(Data):
    def __init__(self, node_id: int, mode: int, metadata: dict, name:str):

        super().__init__()
        self.node_id = node_id
        self.name = name
        self.mode = mode
        self.metadata = metadata





