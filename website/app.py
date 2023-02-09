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
from gensim.models import LdaModel, LdaMulticore

from config import data_dir, thumbnail_dir, testing
from utils import get_thumbnail, get_url

# Make page width a little wider
st.set_page_config(
    page_title="Paper Recommendation Engine", 
    # Icon from web
    page_icon="https://www.flaticon.com/svg/static/icons/svg/25/25231.svg",
    layout="wide", 
    initial_sidebar_state="auto", 
    menu_items={
        'Get Help': 'https://github.com/mcpeixoto/PaperRecomenderSystem',
        'About': "A simple paper recommendation engine using sentence embeddings, faiss, streamlit and gensim. ",
    }
)


# TODO: https://blog.streamlit.io/make-dynamic-filters-in-streamlit-and-show-their-effects-on-the-original-dataset/

@st.experimental_singleton
def load_data():
    print("Loading data!")
    if testing:
        data = pd.read_csv(join(data_dir, 'arxiv_processed_test.csv'), dtype=str)
    else:
        data = pd.read_csv(join(data_dir, 'arxiv_processed.csv'), dtype=str)
    return data


@st.experimental_singleton
def load_model():
    print("Loading model!")
    model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
    return model

@st.experimental_singleton
def load_LDA():
    print("Loading LDA model!")
    lda_model = LdaMulticore.load(join(data_dir, 'lda_model'))

    # load the dictionary
    with open(join(data_dir, 'tags_dictionary.pkl'), 'rb') as f:
        tags_dictionary = pickle.load(f)
    return lda_model, tags_dictionary


@st.experimental_singleton
def load_index():
    print("Loading index!")

    if testing:
        index = faiss.read_index(join(data_dir, 'index_test.faiss'))
    else:
        index = faiss.read_index(join(data_dir, 'index.faiss'))

    return index

def get_tags(query, lda_model, dictionary):
    query = query.split()
    query = [token for token in query if token.isalnum()]
    bows =  dictionary.doc2bow(query)
    topics = lda_model.get_document_topics(bows)
    # Sort topics
    topics = sorted(topics, key=lambda x: x[1], reverse=True)
    topic_lists = [(dictionary.get(id), prob) for id, prob in topics]
    return topic_lists # (topic, prob)


model = load_model()
data = load_data()
index = load_index()
lda_model, tags_dictionary = load_LDA()


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

            title = row['title'].replace("\n", " ").replace("\t", " ").replace("[", " ").replace("]", " ").replace('\'', " ")
            url = get_url(row['id'])
            thumbnail = get_thumbnail(url)
            authors = eval(row['authors_parsed'])
            authors = [x[1] + " " + x[0] for x in authors]
            tag_list = get_tags(title, lda_model, tags_dictionary)
            

            if len(authors) > 3:
                authors = ", ".join(authors[:3]) + " et al."
            else:
                authors = ", ".join(authors)


            # Add Score and Title with link
            # Author, date, categories
            # categories should be blue


            # Add tags
            html = f"""
                ### [**{round(row['score']*100)}**] - :red[[{title}]({url})]  
                <font size="5"> *{authors}*  <br>
                {row['update_date']} - :blue[{row['categories'].replace(' ', ', ')}] <br>
                <font size="4"> Tags: """

            for tag, prob in tag_list:
                html += f":blue[[{tag} ({round(prob*100)}%)]] "

            st.markdown(html, unsafe_allow_html=True)

   

            # Add thumbnail
            if thumbnail:
                st.image(thumbnail, use_column_width=True)

            # Add abstract with normal text
            st.markdown(f"""
            <font size="4.5">
                {row['abstract']}
            """, unsafe_allow_html=True)


            st.markdown("---")






       
        # Show sucessful query message and tell how many documents we passed
        st.success(f"Found {len(I[0])} results in {end_time - start_time:.2f} seconds on database of {len(data)} papers.")

    

if __name__ == "__main__":
    main()