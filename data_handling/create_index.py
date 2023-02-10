import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from os.path import join
from config import data_dir
from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
import faiss
import gc
import pickle
import numpy as np

# Faiss
class FaissIdx:
    def __init__(self, dim=768, use_gpu=True):
        for key, value in locals().items():
            setattr(self, key, value)
        # Maintaining the document data
        # Load Model
        self.model = SentenceTransformer('all-mpnet-base-v2')

        # Initialize the index
        self.index = faiss.IndexFlatIP(dim)

        # Inicialize ids
        self.ids = []

        # Use GPU
        if self.use_gpu:
            self.use_gpu()
        res = faiss.StandardGpuResources()
        self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

    # TODO: Check if current index was already added
    def add_doc(self, data):
        batch_size = 128
        save_every = 10

        print(f"[+] Adding {len(data)} documents to index")

        # document_text is all the data that wasen't already added (present on self.ids)
        document_text = data[~data['id'].isin(self.ids)]['text'].values
        print(f"[INFO] {len(data) - len(document_text)} were already added, adding the remaining {len(document_text)} ({round(len(document_text)/len(data)*100, 2)}%)")
        data = data[~data['id'].isin(self.ids)]

        for i in tqdm(range(0, len(document_text), batch_size), desc="Adding documents to index", unit="batch"):
            # Add embeddings
            self.index.add(self.model.encode(document_text[i:i+batch_size]))

            # Add ids
            self.ids.extend(data['id'].values[i:i+batch_size])

            # Save index every save_every batches
            if i % (batch_size * save_every) == 0:
                self.save_index(data_dir)

    def load_index(self, index_path):
        if not os.path.exists(join(index_path, 'index.faiss')):
            print(f"[+] Index not found on {index_path} folder.")
            return

        print("[+] Loading index...")

        # Convert index to cpu
        self.switch_to_cpu()

        # Load Index
        self.index = faiss.read_index(join(index_path, 'index.faiss'))
        
        # Load Ids
        with open(join(index_path, 'ids.pkl'), 'rb') as f:
            self.ids = pickle.load(f)

        if len(self.ids) != self.index.ntotal:
            print(f"[!] Number of ids ({len(self.ids)}) doesn't match number of documents in index ({self.index.ntotal})")
            self.resolve_incosistency()

        print(f"[+] Index loaded successfully - Loaded {len(self.ids)} documents")

        # Convert index back to gpu
        if self.use_gpu:
            self.switch_to_gpu()

    # TODO: Make this keyboard interrupt safe
    def save_index(self, index_path):
        self.switch_to_cpu()

        # Save Index
        faiss.write_index(self.index, join(index_path, 'index.faiss'))

        # Save Ids
        with open(join(index_path, 'ids.pkl'), 'wb') as f:
            pickle.dump(self.ids, f)

        if self.use_gpu:
            self.switch_to_gpu()

    def switch_to_gpu(self):
        res = faiss.StandardGpuResources()
        self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
    
    def switch_to_cpu(self):
        self.index = faiss.index_gpu_to_cpu(index.index)

    def resolve_incosistency(self):
        print("[+] Resolving inconsistency..")
        n_index = self.index.ntotal
        n_ids = len(self.ids)

        if n_index > n_ids:
            print(f"[+] Removing {n_index - n_ids} documents from index")
            removed = self.index.remove_ids(np.arange(n_ids, n_index))
            assert removed == n_index - n_ids
        elif n_index < n_ids:
            print(f"[+] Removing {n_ids - n_index} ids from ids list")
            self.ids = self.ids[:n_index]
        else:
            print("[+] No inconsistency found")

        #  Save index
        self.save_index(data_dir)


# This will create the index given the arxiv_processed.csv file
# If the index already exists, it will be loaded and any new documents present on the csv will be added to the index
if __name__ == "__main__":
    # Load data
    print("[+] Loading data")
    if not os.path.exists(join(data_dir, 'arxiv_processed.csv')):
        print(f"[!] File {join(data_dir, 'arxiv_processed.csv')} not found. Please download the data first")
        exit()
    data = pd.read_csv(join(data_dir, 'arxiv_processed.csv'), dtype=str)
    print(f"[+] Loaded {len(data)} documents")

    # Initialize Faiss Index
    index = FaissIdx(use_gpu=False) # No need to use GPU

    # Load index if it exists TODO: Remove this
    index.load_index(data_dir)

    # Get data to embedd
    data['text'] = data['title'] + "\n " + data['abstract']
    data = data[['text', 'id']]

    gc.collect()

    # Add documents to index
    index.add_doc(data)

    # Save index
    index.save_index(data_dir)