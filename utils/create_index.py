import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from os.path import join
from config import data_dir
from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm.notebook import tqdm
import faiss
import gc
import pickle


# Faiss
class FaissIdx:
    def __init__(self, model, dim=768, use_gpu=True):
        # Maintaining the document data
        # Load Model
        self.model = SentenceTransformer('all-mpnet-base-v2')

        # Initialize the index
        self.index = faiss.IndexFlatIP(dim)

        # Inicialize ids
        self.ids = []

        # Use GPU
        if use_gpu:
            self.use_gpu()
        res = faiss.StandardGpuResources()
        self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

    # TODO: Check if current index was already added
    def add_doc(self, data):
        batch_size = 256

        print(f"[+] Adding {len(data)} documents to index")

        # document_text is all the data that wasen't already added (present on self.ids)
        document_text = data[~data['id'].isin(self.ids)]['text'].values

        if already_added := len(data) - len(document_text):
            print(f"[+] {already_added} were already added, adding the remaining {len(document_text)} (%{round(len(document_text)/len(data)*100, 2)})")

        for i in tqdm(range(0, len(document_text), batch_size), desc="Adding documents to index", unit="batch"):
            self.index.add(self.model.encode(document_text[i:i+batch_size]))

    def load_index(self, index_path):
        # Convert index to cpu
        self.switch_to_cpu()

        # Load Index
        self.index = faiss.read_index(join(index_path, 'index.faiss'))
        
        # Load ids
        with open(join(index_path, 'ids.pkl'), 'rb') as f:
            self.ids = pickle.load(f)

        # Convert index back to gpu
        if self.use_gpu:
            self.switch_to_gpu()

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


# This will create the index and overwrite any existing one
if __name__ == "__main__":
    # Load data
    print("[+] Loading data")
    data = pd.read_csv(join(data_dir, 'arxiv_processed.csv'), dtype=str)
    print(f"[+] Loaded {len(data)} documents")

    # Initialize Faiss Index
    index = FaissIdx(model=None, use_gpu=False) # No need to use GPU

    # Get data to embedd
    data['text'] = data['title'] + "\n " + data['abstract']
    data = data[['text', 'id']]

    gc.collect()

    # Add documents to index
    index.add_doc(data)

    # Save index
    index.save_index(data_dir)