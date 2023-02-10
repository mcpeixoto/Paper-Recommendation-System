# This will download the data from https://www.kaggle.com/datasets/Cornell-University/arxiv/versions/112?resource=download
import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import os
from os.path import join, expanduser, exists
from config import data_dir
from tqdm import tqdm
import pandas as pd

# Check if the user has the kaggle.json file
if not exists(join(expanduser("~"), ".kaggle", "kaggle.json")):
    print("\nPlease download the kaggle.json file from your account, then place it in the folder ~/.kaggle/")
    print("Instructions:")
    print("1. Go to https://www.kaggle.com/<username>/account")
    print('2. Scroll down to the API section and click "Create New API Token"')
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

    kaggle.api.dataset_download_files("Cornell-University/arxiv", path=data_dir, unzip=True)  # So lame, it doesn't even have a progress bar

    # Rename the file
    os.rename(join(data_dir, "arxiv-metadata-oai-snapshot.json"), join(data_dir, final_file_name))


def process_data(processed_data_path=join(data_dir, "arxiv_processed.csv")):

    data_path = join(data_dir, "arxiv.json")
    n_lines = sum(1 for line in open(data_path))
    batch_size = 10000

    # Check if the data has already been processed
    if exists(processed_data_path):
        print("Data has already been processed")
        return

    for df in tqdm(pd.read_json(data_path, lines=True, chunksize=batch_size), total=n_lines // batch_size, desc="Processing data", unit="batch"):
        # Set datatype as string
        df = df.astype(str)
        # replace nan with empty string
        df = df.replace("nan", "")

        # All the features:
        # ['id', 'submitter', 'authors', 'title', 'comments', 'journal-ref', 'doi',
        #'report-no', 'categories', 'license', 'abstract', 'versions',
        # 'update_date', 'authors_parsed']
        #
        # But we only some
        df = df[["id", "abstract", "title", "doi", "categories", "update_date", "authors_parsed"]]

        # Remove rows with empty abstracts, titles, or ids
        df = df[(df["abstract"] != "") & (df["title"] != "") & (df["id"] != "")]

        # To csv
        df.to_csv(processed_data_path, mode="a", header=True if not exists(processed_data_path) else False, index=False)


if __name__ == "__main__":
    print("[+] Downloading data using kaggle API..")
    download_data()
    print("[+] Processing data..")
    process_data()
    print("[+] Done!")

    # Delete join(data_dir, final_file_name)
    os.remove(join(data_dir, "arxiv.json"))
