import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from os.path import join
import requests
from tqdm import tqdm

from config import data_dir





to_download = ['ids_test.pkl',
 'arxiv_processed.csv',
 'ids.pkl',
 'index.faiss',
 'index_test.faiss',
 'arxiv_processed_test.csv']

# Download files
base_url = "https://miguelpeixoto.net/paper_recommendation_system/"

for file in to_download:
    url = join(base_url, file)
    print(f"[+] Downloading {url}")
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(join(data_dir, file), "wb") as f:
        for chunk in tqdm(r.iter_content(chunk_size=1024)):
            if chunk:
                f.write(chunk)

