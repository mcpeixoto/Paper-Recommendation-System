

# This will download the data from https://www.kaggle.com/datasets/Cornell-University/arxiv/versions/112?resource=download
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import os
from os.path import join, expanduser, exists
from config import data_dir

# Check if the user has the kaggle.json file
if not exists(join(expanduser("~"), ".kaggle", "kaggle.json")):
    print("\nPlease download the kaggle.json file from your account, then place it in the folder ~/.kaggle/")
    print("Instructions:")
    print("1. Go to https://www.kaggle.com/<username>/account")
    print("2. Scroll down to the API section and click \"Create New API Token\"")
    print("3. Move the kaggle.json file to the folder ~/.kaggle/")
    print("For more information, please refer to https://www.kaggle.com/docs/api\n")
    exit()


import kaggle

def download_data(final_file_name="arxiv.json"):

    # Check if the data has already been downloaded
    if exists(join(data_dir, final_file_name)):
        print("Data has already been downloaded")
        return

    # Download the data
    kaggle.api.authenticate()

    kaggle.api.dataset_download_files("Cornell-University/arxiv", path=data_dir, unzip=True) # So lame, it doesn't even have a progress bar

    # Rename the file
    os.rename(join(data_dir, "arxiv-metadata-oai-snapshot.json"), join(data_dir, final_file_name))


if __name__ == "__main__":
    download_data()