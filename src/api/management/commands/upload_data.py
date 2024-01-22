from django.core.management.base import BaseCommand
import logging
import re
import random
from datetime import datetime
from elasticsearch import helpers
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from api.elastic_search.elastic_search_connection import get_elastic_connection

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load Data into elastic Search'

    def add_arguments(self, parser):
        parser.add_argument('page',type=int,help="Page no")

    def handle(self, *args, **kwargs):
        self.index_name = 'product'
        self.csv_file = 'api/elastic_search/product_data.csv'
        self.stop_word_file = 'api/elastic_search/stop_words.txt'
        self.stop_words_set = self.stop_words()
        self.es_obj = get_elastic_connection("localhost")
        self.page_no = kwargs.get("page",1)
        self.per_page_data = 1000
        self.read_csv()

    def remove_special_chars(self, text):
        '''This function removes the special chars from the text'''
        text = str(text)
        text = re.sub('[^A-Za-z0-9]+', ' ', text)
        text = text.lower()
        return text

    def stop_words(self):
        words = []
        with open(self.stop_word_file, 'r') as f:
            for word in f:
                word = word.split('\n')
                words.append(word[0])
        return words

    def generate_N_grams(self, text, ngram=1):
        words = [word for word in text.split(" ") if word not in set(self.stop_words_set)]
        # print("Sentence after removing stopwords:", words)
        temp = zip(*[words[i:] for i in range(0, ngram)])
        ans = [' '.join(ngram) for ngram in temp]
        return ans

    def process(self, csv_df,ids_list):
        csv_df['productDisplayName'] = csv_df['productDisplayName'].apply(lambda text: self.remove_special_chars(text))
        csv_df['price'] = [ random.randint(200,2000)  for k in csv_df.index]
        csv_df['id'] = ids_list
        name_vector_list = model.encode(csv_df['productDisplayName'].to_list())
        # inject name vector
        es_data = csv_df.to_dict('records')
        es_complete_data = []
        for index, es_data_one in enumerate(es_data):
            n_gram_sentence = [es_data_one["productDisplayName"]]
            for ngram in range(1,4):
                n_gram_sentence = n_gram_sentence+(self.generate_N_grams(es_data_one["productDisplayName"], ngram))
            temp_data = {
                "id":es_data_one["id"],
                "name":es_data_one["productDisplayName"],
                "name_suggester":{
                    "input": n_gram_sentence
                },
                "category":es_data_one["category"],
                "gender":es_data_one["gender"],
                "price":es_data_one["price"],
                "subCategory":es_data_one["subCategory"],
                "articleType":es_data_one["articleType"],
                "baseColour":es_data_one["baseColour"],
                "image_path":es_data_one["image_path"],
                "season":es_data_one["season"],
                "year":es_data_one["year"],
                "usage":es_data_one["usage"],
                "name_vector":name_vector_list[index],
            }
            es_complete_data.append(temp_data)
        helpers.bulk(self.es_obj,self.get_data(es_complete_data), stats_only=False)

    def get_data(self,json_list):
        for doc in json_list:
            yield {
                "_index": self.index_name,
                # "_type": "_doc",
                # "_id": uuid.uuid4(),
                "_source": doc
            }

    def read_csv(self):
        skip_rows = ((self.page_no-1) * self.per_page_data)+1
        chunksize = self.per_page_data
        df = pd.read_csv(self.csv_file, header=0,chunksize=chunksize,skiprows=range(1,skip_rows))
        counter = 0
        for data in df:
            ids = list(self.generate_unique_ids(chunksize))
            self.process(data,ids)
            counter += 1
            if counter >=1:
                break

    def get_unique_id(self):
        mynow = datetime.now
        sft = datetime.strftime
        # store old datetime each time in order to check if we generate during same microsecond (glucky wallet !)
        # or if daylight savings event occurs (when clocks are adjusted backward) [rarely detected at this level]
        old_time = mynow()  # fake init - on very speed machine it could increase your seed to seed + 1... but we have our contingency :)
        # manage seed
        seed_range_bits = 3  # max range for seed
        seed_max_value = 2 ** seed_range_bits - 1  # seed could not exceed 2**nbbits - 1
        # get random seed
        seed = random.getrandbits(seed_range_bits)
        current_seed = str(seed)
        # producing new ids
        while True:
            # get current time
            current_time = mynow()
            if current_time <= old_time:
                # previous id generated in the same microsecond or Daylight saving time event occurs (when clocks are adjusted backward)
                seed = max(1, (seed + 1) % seed_max_value)
                current_seed = str(seed)
            # generate new id (concatenate seed and timestamp as numbers)
            # newid=hex(int(''.join([sft(current_time,'%f%S%M%H%d%m%Y'),current_seed])))[2:-1]
            newid = ''.join([sft(current_time, '%f%S%M%H%d%m%Y'), current_seed])
            # save current time
            old_time = current_time
            # return a new id
            yield newid

    def generate_unique_ids(self,no_of_ids):
        ids = set()
        for i in range(no_of_ids):
            id_ = next(self.get_unique_id())
            ids.add(id_)
        return ids



