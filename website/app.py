# Streamlit app
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import streamlit as st
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import gc
import time
from os.path import join
import pickle

from config import data_dir, thumbnail_dir
from utils import get_thumbnail, get_url

#st.set_page_config(layout="wide")

# TODO: https://blog.streamlit.io/make-dynamic-filters-in-streamlit-and-show-their-effects-on-the-original-dataset/

@st.experimental_singleton
def load_data():
    print("Loading data!")
    data = pd.read_csv(join(data_dir, 'arxiv_processed.csv'), dtype=str)
    return data


@st.experimental_singleton
def load_model():
    print("Loading model!")
    model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
    return model



@st.experimental_singleton
def load_index():
    print("Loading index!")
    index = faiss.read_index(join(data_dir, 'index.faiss'))
    

    return index


model = load_model()
data = load_data()
index = load_index()


def main():
    st.title("Paper Recommendation Engine")
    query = st.text_input("Search query")

    # make the num result a input box
    k = st.number_input("Number of results", 1, 50, 10)


    if query:
        start_time = time.time()
        D, I = index.search(model.encode(query).reshape(1, -1), k)
        end_time = time.time()

        df = pd.DataFrame()
        for idx, score in zip(I[0], D[0]):
            to_add = data.iloc[idx]

            # Add score
            to_add['score'] = score

            df = pd.concat([df, to_add], axis=1)

        df = df.T

        #print(df.columns) # ['id', 'abstract', 'title', 'doi', 'categories', 'update_date', 'authors_parsed', 'score']

        ##########################################
        # Show results
        ##########################################

        
        for i, row in df.iterrows():

            url = get_url(row['id'])
            thumbnail = get_thumbnail(row['id'])
            authors = eval(row['authors_parsed'])
            authors = [x[1] + " " + x[0] for x in authors]

            if len(authors) > 3:
                authors = ", ".join(authors[:3]) + " et al."
            else:
                authors = ", ".join(authors)


            # Add Score and Title with link
            # Author, date, categories
            # categories should be blue

            st.markdown(f"""
                ### [**{row['score']:2f}**] - :red[[{row['title']}]({url})]
                #### *{authors}*
                #### {row['update_date']} - :blue[{row['categories']}]
            """)

   

            # Add thumbnail
            if thumbnail:
                st.image(thumbnail)

            # Add abstract with normal text
            st.markdown(f"""
                {row['abstract']}
            """)


            st.markdown("---")






       
        # Show sucessful query message and tell how many documents we passed
        st.success(f"Found {len(I[0])} results in {end_time - start_time:.2f} seconds on database of {len(data)} papers.")

    

if __name__ == "__main__":
    main()