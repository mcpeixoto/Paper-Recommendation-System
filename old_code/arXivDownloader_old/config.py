from glob import glob
import os
from os.path import join, basename, exists
import arxiv

# Data location
data_dir = 'data'

# Search terms
search_terms = ['High Energy Physics', 'Quantum Physics', 'HEP', 'Quantum Computing']

# If the data directory doesn't exist, create it
if not exists(data_dir):
    os.makedirs(data_dir)



#################################
# arXivDownloader Configuration #
#################################

#### Client ####
page_size = 2000 # 2000 is the max
delay_seconds = 3 # arXiv's Terms of Use ask that you "make no more than one request every three seconds."
num_retries = 10

#### Search ####
max_results = 300000 # 300k is the max
sort_by = arxiv.SortCriterion.Relevance

#### Save ####
batch_size = 1000 # How many papers to save at a time

