from transmit.data import Data
import os
class Node_to_Tracker(Data):
    def __init__(self, node_id: int, mode: int, metadata: dict):

        super().__init__()
        self.node_id = node_id
        self.mode = mode
        if metadata =="":
            self.metadata = metadata
        else:
            self.metadata = os.path.basename(metadata)
            print(self.metadata)

    def test_fileName(self, file_path:str):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_path}' không tồn tại.")
    
        else:
            print(f"File '{file_path}' tồn tại.")
            return True




