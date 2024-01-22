import re
import sys

import numpy as np
import pandas as pd
from es_pandas import es_pandas
from sentence_transformers import SentenceTransformer

from api.elastic_search.elastic_search_connection import get_elastic_connection

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

es = get_elastic_connection("localhost")

if es.ping():
    print('Connected to Elasticsearch')
else:
    print('Could not connect to elasticsearch')
    sys.exit()

lst = [6043, 6568, 7398, 7938, 9025, 10263, 10426, 10904, 11372, 11944, 14111, 14531, 15075, 29905, 31624, 33019, 35747,
       35961, 37769, 38104, 38274, 38403, ]  # This lines were corrupted in the data file.

INDEX_NAME = 'product'
TYPE = "record"

ep = es_pandas("localhost:9200")


def remove_special_chars(text):
    '''This function removes the special chars from the text'''
    text = str(text)
    text = re.sub('[^A-Za-z0-9]+', ' ', text)
    text = text.lower()
    return text


def process(train):
    train['productDisplayName'] = train['productDisplayName'].apply(lambda text: remove_special_chars(text))
    train['price'] = np.random.randint(200, 2000)
    train['name_vector'] = train['productDisplayName'].apply(lambda text: model.encode(text))
    train.rename({'productDisplayName': 'name'}, inplace=True, axis=1)
    ep.to_es(train, INDEX_NAME, use_index=True)


def read_csv():
    chunksize = 10 ** 3
    df = pd.read_csv("styles.csv", chunksize=chunksize)
    counter = 0
    for data in df:
        process(data)
        counter += 1
        if counter > 4:
            break

read_csv()
