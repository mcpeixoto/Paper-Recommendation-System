
# This script will take advantage of the arXiv API to download all the papers in a given category.

from config import data_dir, search_terms
from config import page_size, delay_seconds, num_retries
from config import max_results, sort_by
from config import batch_size
import arxiv
import pandas as pd
from tqdm import tqdm
from os.path import join



for search_term in tqdm(search_terms, desc='Search Terms', leave=False, position=0, total=len(search_terms)):
    print('Downloading papers for search term: {}'.format(search_term))

    # Get the papers
    client = arxiv.Client(
        page_size = page_size, # 2000 is the max
        delay_seconds = delay_seconds, # arXiv's Terms of Use ask that you "make no more than one request every three seconds."
        num_retries = num_retries
    )

    search = arxiv.Search(
        query = search_term,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance,
    )

    results = client.results(search)

    # Save the papers
    pbar = tqdm(total=max_results, desc='Papers processed', leave=True, position=1, unit='papers', unit_scale=True)
    buffer = []
    search_term = search_term.replace(' ', '_')
    for i, result in enumerate(results):

        # Append to the buffer
        buffer.append(result.__dict__)

        if i % batch_size == 0:
            df = pd.DataFrame(buffer)
            buffer = []

            # Append to the csv
            with open(join(data_dir, f'{search_term}.csv'), 'a') as f:
                df.to_csv(f, mode='a', header=f.tell()==0, index=False)

            # Update the progress bar
            pbar.update(batch_size)

