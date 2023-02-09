import sys
sys.path.append("..")

import os
from os.path import join, basename, exists
import glob
import pandas as pd
import numpy as np
from config import data_dir
from tqdm import tqdm


def process_data():
    
    data_path = join(data_dir, "arxiv.json")
    n_lines = sum(1 for line in open(data_path))
    batch_size = 10000

    for df in tqdm(pd.read_json(data_path, lines=True, chunksize=batch_size), total=n_lines//batch_size, desc="Processing data", unit="batch"):
        df['url'] = df['id'].apply(lambda x: f"https://arxiv.org/abs/{x}" if len(str(x).split(".")) >= 4 else f"https://arxiv.org/abs/0{x}")

        # We only need abstract, title, and url
        df = df[['abstract', 'title', 'url']]

        # Remove rows with missing values
        df = df.dropna()

        # Remove rows with empty abstracts, titles, or urls
        df = df[(df['abstract'] != "") & (df['title'] != "") & (df['url'] != "")]

        # To csv
        df.to_csv(join(data_dir, "arxiv_processed.csv"), mode='a', header=True if not exists(join(data_dir, "arxiv_processed.csv")) else False, index=False)


def get_data():
    if not exists(join(data_dir, "arxiv_processed.csv")):
        process_data()
    return pd.read_csv(join(data_dir, "arxiv_processed.csv"))


