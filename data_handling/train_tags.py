import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from os.path import join
from config import data_dir
import pandas as pd
import gc
from tqdm import tqdm
import pickle

import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaModel, LdaMulticore
from gensim.matutils import corpus2dense




if __name__ == "__main__":
    # Load data
    print("[+] Loading data")
    if not os.path.exists(join(data_dir, 'arxiv_processed.csv')):
        print(f"[!] File {join(data_dir, 'arxiv_processed.csv')} not found. Please download the data first")
        exit()
    data = pd.read_csv(join(data_dir, 'arxiv_processed.csv'), dtype=str)
    print(f"[+] Loaded {len(data)} documents")

    # Randomly sample len/2
    data = data.sample(frac=0.1, random_state=42) # I don't have enough memory to train on the whole dataset

    print(f"[+] Randomly sampled {len(data)} documents")

    data = data['title'] + " " + data['abstract']

    # Convert text column to a list of tokenized documents
    data = data.apply(lambda x: x.split())#.tolist()

    # Remove any non-alphanumeric characters
    data = data.apply(lambda x: [token for token in x if token.isalnum()])

    # Build a dictionary from the tokenized documents
    dictionary = Dictionary(data)

    # Convert documents to bag-of-words representations
    print("[+] Converting documents to bag-of-words representations")
    bow_corpus = data.apply(lambda x: dictionary.doc2bow(x))

    # make bow_corpus iterable
    bow_corpus = bow_corpus.tolist()
    
    gc.collect()

    # Train an LDA model
    print("[+] Training LDA model")
    lda_model = LdaMulticore(corpus=tqdm(bow_corpus), num_topics=200, id2word=dictionary, passes=4, workers=os.cpu_count())

    # Save the model
    lda_model.save(join(data_dir, 'lda_model'))

    # Save dictionary
    with open(join(data_dir, 'tags_dictionary.pkl'), 'wb') as f:
        pickle.dump(dictionary, f)


