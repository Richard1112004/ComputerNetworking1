import os

file_path = input("Nhập đường dẫn của file: ").strip()
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File '{file_path}' không tồn tại.")
else:
    print(f"File '{file_path}' tồn tại.")
