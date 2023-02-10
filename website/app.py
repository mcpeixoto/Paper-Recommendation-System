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
import json
import multiprocessing
from multiprocessing import Pool


from config import data_dir, thumbnail_dir, testing
from utils import get_thumbnail, get_url


# Explicitly set the environment variable TOKENIZERS_PARALLELISM to false
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Make page width a little wider
st.set_page_config(
    page_title="Paper Recommendation Engine",
    # Icon from web
    page_icon="https://www.flaticon.com/svg/static/icons/svg/25/25231.svg",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://github.com/mcpeixoto/PaperRecomenderSystem",
        "About": "Web interface to search ArXiv papers using NLP Sentence-Transformers, Faiss and Streamlit ",
    },
)

if not hasattr(st.session_state, "selected_categories"):
    st.session_state.selected_categories = []

@st.experimental_singleton
def load_data():
    print("Loading data!")
    if testing:
        data = pd.read_csv(join(data_dir, "arxiv_processed_test.csv"), dtype=str)
    else:
        data = pd.read_csv(join(data_dir, "arxiv_processed.csv"), dtype=str)
    return data


@st.experimental_singleton
def load_model():
    print("Loading model!")
    model = SentenceTransformer("all-mpnet-base-v2", device="cuda")
    return model


@st.experimental_singleton
def load_index():
    print("Loading index!")

    if testing:
        index = faiss.read_index(join(data_dir, "index_test.faiss"))
    else:
        index = faiss.read_index(join(data_dir, "index.faiss"))

    return index


def load_user_tags():
    print("Loading user tags!")
    with open("tags.json", "r") as f:
        user_tags = json.load(f)

    return user_tags


def get_user_tags_from_query(query, user_tag_keys, model):
    # This will embedd the query and then compare it to the user tags (key + values)

    # Get the embeddings of the query
    query_embedding = model.encode(query, convert_to_tensor=True).cpu()

    # Get the embeddings of the user tags
    to_encode = [f"{key} - {','.join(value)}" for key, value in load_user_tags().items() if key in user_tag_keys]
    user_tags_embeddings = model.encode(to_encode, convert_to_tensor=True).cpu()

    # Compute the dot product
    dot_product = np.dot(query_embedding, user_tags_embeddings.T)

    # Get the tags and probabilities
    return [(tag, prob) for tag, prob in zip(user_tag_keys, dot_product)]


model = load_model()
data = load_data()
index = load_index()
user_tags = load_user_tags()


def draw_sidebar():
    """Should include dynamically generated filters"""

    with st.sidebar:
        # Filter by category of our data
        categories = data["categories"].unique()

        # Sidebar
        st.sidebar.header("Filters")
        st.sidebar.subheader("By Category")

        # multiselect
        selected_categories = st.sidebar.multiselect("Select categories", categories)

        # Add a button to apply the filters
        if st.sidebar.button("Apply filters"):
            st.session_state.selected_categories = selected_categories

            # Reload the page
            st.experimental_rerun()

        # Show user tags
        st.sidebar.markdown("---")
        st.sidebar.header("User Tags")

        # Show the user tags
        st.sidebar.subheader("Your tags:")
        st.sidebar.write(", ".join(user_tags.keys()))

        # Add a new user tag
        st.sidebar.subheader("Add a new User Tag")
        new_tag = st.sidebar.text_input("Tag name")
        new_tag_values = st.sidebar.text_input("Tag values (comma separated)")

        if st.sidebar.button("Add tag"):
            user_tags[new_tag] = new_tag_values.split(",")
            with open("tags.json", "w") as f:
                json.dump(user_tags, f)

            # Reload the page
            st.experimental_rerun()

        # Remove a user tag
        st.sidebar.subheader("Remove a User Tag")
        remove_tag = st.sidebar.selectbox("Select tag to remove", list(user_tags.keys()))

        if st.sidebar.button("Remove tag"):
            user_tags.pop(remove_tag)
            with open("tags.json", "w") as f:
                json.dump(user_tags, f)

            # Reload the page
            st.experimental_rerun()

        # Remove all user tags
        st.sidebar.subheader("Remove **ALL** User Tags (Dangerous)")
        if st.sidebar.button("Remove all tags"):
            user_tags.clear()
            with open("tags.json", "w") as f:
                json.dump(user_tags, f)

            # Reload the page
            st.experimental_rerun()

        # Notes:
        st.sidebar.subheader("Notes")
        st.sidebar.write("**You can directly edit the tags.json file to add or remove new tags**")


def main():
    st.title("Paper Recommendation Engine")
    query = st.text_input("Search query")

    draw_sidebar()

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
            to_add["score"] = score

            df = pd.concat([df, to_add], axis=1)

        df = df.T

        # df.columns - # ['id', 'abstract', 'title', 'doi', 'categories', 'update_date', 'authors_parsed', 'score']

        ##########################################
        # Show results
        ##########################################

        # Iterate over rows to multiprocess the get_thumbnail function
        pool = Pool(len(df))
        processes = []
        for _, row in df.iterrows():
            processes.append(pool.apply_async(get_thumbnail, (get_url(row["id"]),)))
        pool.close()  # no more tasks

        i = 0
        for _, row in df.iterrows():

            title = row["title"].replace("\n", " ").replace("\t", " ").replace("[", " ").replace("]", " ").replace("'", " ")
            url = get_url(row["id"])
            authors = eval(row["authors_parsed"])
            authors = [x[1] + " " + x[0] for x in authors]

            # If category not in st.session_state.selected_categories
            categories = row["categories"].split()
            if len(st.session_state.selected_categories) > 0:
                c = True
                for cat in categories:
                    if cat in st.session_state.selected_categories:
                        c = False
                if c:
                    continue

            if len(authors) > 3:
                authors = ", ".join(authors[:3]) + " et al."
            else:
                authors = ", ".join(authors)

            # Add Score and Title with link
            # Author, date, categories
            # categories should be blue

            html = f"""
                ### [**{round(row['score']*100)}**] - :red[[{title}]({url})]  
                <font size="5"> *{authors}*  <br>
                {row['update_date']} - :blue[{row['categories'].replace(' ', ', ')}]"""

            ###################
            #### User Tags ####
            ###################

            user_tag_list = get_user_tags_from_query(row["title"] + " " + row["abstract"], user_tags, model)
            if any([prob > 0.5 for tag, prob in user_tag_list]):
                html += f"""<br> <font size="4"> User Tags: """
                for tag, prob in user_tag_list:
                    if prob > 0.5:
                        html += f":red[[{tag}] ({round(prob*100)}%)], "
                # Remove last ,
                html = html[:-2]

            # Show html
            st.markdown(html, unsafe_allow_html=True)

            ###################
            #### Thumbnail ####
            ###################

            thumbnail = processes[i].get()  # get the result from the process
            i += 1

            # Add thumbnail
            if thumbnail:
                st.image(thumbnail, use_column_width=True)

            ##################
            #### Abstract ####
            ##################

            # Add abstract with normal text
            st.markdown(
                f"""
            <font size="4.5">
                {row['abstract']}
            """,
                unsafe_allow_html=True,
            )

            st.markdown("---")

        # Show sucessful query message and tell how many documents we passed
        st.success(f"Found {len(I[0])} results in {end_time - start_time:.2f} seconds on database of {len(data)} papers.")


if __name__ == "__main__":
    main()
