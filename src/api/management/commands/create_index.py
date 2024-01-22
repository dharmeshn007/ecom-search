import json
import logging
import sys

from django.core.management.base import BaseCommand

from api.elastic_search.elastic_search_connection import get_elastic_connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create Index of elastic Search'

    def handle(self, *args, **kwargs):
        with open('api/elastic_search/mapping.json') as json_file:
            elastic_search_mapping = json.load(json_file)
        es = get_elastic_connection("localhost")
        index_name = 'product'

        ret = es.indices.create(index=index_name, ignore=400, body=elastic_search_mapping)
        print(json.dumps(ret, indent=4))
