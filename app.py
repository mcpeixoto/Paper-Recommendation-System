# Streamlit app to display the results of the model

import streamlit as st
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import gc



#@st.cache(persist=True, max_entries=1)
@st.experimental_singleton
def load_data():
    print("Loading data!")
    data = pd.read_csv('data/arxiv_processed.csv')
    # Prune abstract to 50 characters
    data['abstract'] = data['abstract'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x)
    #data['text'] = data['title'] + " " + data['abstract']
    return data



#@st.cache(persist=True, max_entries=1)
@st.experimental_singleton

def load_model():
    print("Loading model!")
    model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
    return model


#@st.cache(persist=True, max_entries=1)
@st.experimental_singleton
def load_index():
    print("Loading index!")
    index = faiss.read_index('index.faiss')


    return index



model = load_model()
data = load_data()
index = load_index()


def main():
    st.title("Arxiv Search Engine")
    query = st.text_input("Search query")
    k = st.slider("Number of results", 1, 10, 3)


    if query:
        D, I = index.search(model.encode(query).reshape(1, -1), k)

        df = pd.DataFrame()
        for idx, score in zip(I[0], D[0]):
            df = pd.concat([df, data.iloc[idx:idx+1]])

        st.table(df[['title', 'abstract', 'url']])
        #st.balloons()
        del df
        gc.collect()

        

if __name__ == "__main__":
    main()