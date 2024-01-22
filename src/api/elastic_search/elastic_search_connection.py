from django.conf import settings
from elasticsearch import Elasticsearch
ELASTIC_CON = dict()


def get_elastic_connection(type):
    if type not in ELASTIC_CON:
        es_url = settings.ELASTIC_SEARCH_URL
        print(es_url)
        elastic_connection = make_local_connection_object(es_url)
        if elastic_connection.ping():
            ELASTIC_CON.update({type: elastic_connection})
            print('Connected to Elasticsearch')
        else:
            print('Could not connect to elasticsearch')
        return elastic_connection
    else:
        return ELASTIC_CON[type]


def make_local_connection_object(es_url):
    return Elasticsearch(es_url)


def elastic_search(index_name='product', body={}, connection_type='localhost'):
    elastic_client = get_elastic_connection(connection_type)
    return elastic_client.search(index=index_name, body=body)
