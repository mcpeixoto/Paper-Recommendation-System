# Streamlit app to display the results of the model

import streamlit as st
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


use_gpu = False
device = 'cuda' if use_gpu else 'cpu'


@st.cache
def load_data():
    data = pd.read_csv('data/arxiv_processed.csv')
    data['text'] = data['title'] + " " + data['abstract']
    return data




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
                self.save_index('index.faiss')

        #self.doc_map[self.ctr] = document_text # store the original document text

        #def search_doc(self, query, k=3):
        #    D, I = self.index.search(self.model.encode(query).reshape(1, -1), k)
        #    return [{self.doc_map[idx]: score} for idx, score in zip(I[0], D[0]) if idx in self.doc_map]

    def load_index(self, index_path):
        print("Loading index!")
        # Convert index to cpu
        if use_gpu:
            self.index = faiss.index_gpu_to_cpu(self.index)

        self.index = faiss.read_index(index_path)
        self.ctr = self.index.ntotal

        if use_gpu:
            # Convert index back to gpu
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)



    def save_index(self, index_path):
        if use_gpu:
            # Convert index to cpu
            self.index = faiss.index_gpu_to_cpu(self.index)

        faiss.write_index(self.index, index_path)

        # Convert index back to gpu
        if use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)


@st.cache
def load_index():
    model = SentenceTransformer('all-mpnet-base-v2', device=device)
    index = FaissIdx(model)
    index.load_index('index.faiss')
    return index


if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.index = load_index()

def main():
    st.title("Arxiv Search Engine")
    query = st.text_input("Search query")
    k = st.slider("Number of results", 1, 10, 3)

    index = st.session_state.index
    data = st.session_state.data


    if query:
        D, I = index.index.search(index.model.encode(query).reshape(1, -1), k)

        df = pd.DataFrame()
        for idx, score in zip(I[0], D[0]):
            df = df.append(data.iloc[idx])

        st.write(df[['title', 'abstract', 'url']])
        st.balloons()
        

if __name__ == "__main__":
    main()