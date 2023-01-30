# Streamlit app to display the results of the model

import streamlit as st
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


use_gpu = True
device = 'cuda' if use_gpu else 'cpu'

# Streamlit - Wait for the model to load
st.title("Arxiv Search Engine")
st.write("Loading model...")


# Load the model
model = SentenceTransformer('all-mpnet-base-v2', device=device)

# Load the data
data = pd.read_csv('data/arxiv_processed.csv')
data['text'] = data['title'] + " " + data['abstract']
# Load the index
class FaissIdx:
    def __init__(self, model, dim=768, batch_size=64):
        # Maintaining the document data
        # self.doc_map = dict()
        self.model = model
        self.batch_size = batch_size

        # Initialize the index
        self.index = faiss.IndexFlatIP(dim)

        # Use GPU
        if use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

        # Counter for number of documents
        self.ctr = 0

    def add_doc(self, document_text):
        save_every = 10

        if self.ctr >= len(document_text):
            print("No more documents to add!")
            return

        for i in tqdm(range(self.ctr, len(document_text), self.batch_size), desc="Adding documents to index", unit="batch"):
            self.index.add(self.model.encode(document_text[i:i+self.batch_size]))

            if i % save_every == 0:
                self.save_index('index_copy.faiss')

        #self.doc_map[self.ctr] = document_text # store the original document text

        #def search_doc(self, query, k=3):
        #    D, I = self.index.search(self.model.encode(query).reshape(1, -1), k)
        #    return [{self.doc_map[idx]: score} for idx, score in zip(I[0], D[0]) if idx in self.doc_map]

    def load_index(self, index_path):
        print("Loading index!")
        # Convert index to cpu
        if use_gpu:
            index.index = faiss.index_gpu_to_cpu(index.index)

        self.index = faiss.read_index(index_path)
        self.ctr = self.index.ntotal

        if use_gpu:
            # Convert index back to gpu
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

        print("Index loaded! Position: ", self.ctr)
        print("Documents in index: ", self.index.ntotal)
        print("Documents total: ", len(data['text'].values))


    def save_index(self, index_path):
        if use_gpu:
            # Convert index to cpu
            index.index = faiss.index_gpu_to_cpu(index.index)

        faiss.write_index(self.index, index_path)

        # Convert index back to gpu
        if use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

index = FaissIdx(model)
index.load_index('index_copy.faiss')

# Remove the loading message
st.empty()
# Baloon message
st.balloons()

# Streamlit app
st.title("Arxiv Search Engine")
query = st.text_input("Search query")
k = st.slider("Number of results", 1, 10, 3)

if query:
    D, I = index.index.search(index.model.encode(query).reshape(1, -1), k)
    for idx, score in zip(I[0], D[0]):
        st.write(f"Score: {score}")
        st.write(data['title'].values[idx])
        st.write(data['abstract'].values[idx])
        st.write(data['url'].values[idx])
        st.write("")

