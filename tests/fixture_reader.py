import os
import json

def load_fixture(file_name):
    folder_path = 'fixtures'
    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    else:
        print(f"The file '{file_name}' does not exist in the folder '{folder_path}'.")
        return None
