from django.conf import settings
from django_elasticsearch_dsl_drf.constants import (
    SUGGESTER_COMPLETION,
    SUGGESTER_PHRASE,
    SUGGESTER_TERM,
)
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    PostFilterFilteringFilterBackend,
    SuggesterFilterBackend, CompoundSearchFilterBackend, SourceBackend
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import (
    SuggestMixin,
    MoreLikeThisMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response

# from api.elastic_search.elastic_search_connection import elastic_search
from .base import BaseSearchDocumentViewSet

__all__ = (
    'SearchDocumentViewSet',
)

from api.v1.search.serializers import SearchDocumentSerializer
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')


class SearchDocumentViewSet(BaseSearchDocumentViewSet,
                            SuggestMixin,
                            MoreLikeThisMixin):
    """The SearchDocument view."""

    filter_backends = [
        SourceBackend,
        FilteringFilterBackend,
        PostFilterFilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        FacetedSearchFilterBackend,
        SuggesterFilterBackend,
    ]
    serializer_class = SearchDocumentSerializer
    pagination_class = PageNumberPagination
    # Suggester fields
    suggester_fields = {
        'name_suggest': {
            'field': 'name_suggester',
            'default_suggester': SUGGESTER_COMPLETION,
            'options': {
                'size': 3,
                'd': True,
            },
        },
        'name_suggest_edge_ngram': {
            'field': 'name_suggester',
            'default_suggester': SUGGESTER_TERM,
            'suggesters': [
                SUGGESTER_PHRASE,
                SUGGESTER_TERM,
            ],
            'serializer_field': 'name',
        },
        'name_suggest_mlt': {
            'field': 'name_suggester',
            # 'default_suggester': SUGGESTER_TERM,
            'suggesters': [
                SUGGESTER_PHRASE,
                SUGGESTER_TERM,
            ],
            'completion_options': {
                "field": "name_suggester"
            },
            'options': {
                'size': 5,
            },
        },
        'description_suggest': 'description.suggest',
    }
    search_fields = {
        'name': {'fuzziness': 'AUTO'},
        'name_vector': {'fuzziness': 'AUTO'},
        'price': None,
        'baseColour': None,
        'description': None,
    }
    # search_fields = (
    #     'name',
    #     'price',
    #     'baseColour',
    #     'description',
    #     # 'state_province',
    #     # 'country',
    # )
    source = {
        "excludes": ["name_vector"]
    }

    def parser_data(self,res):
        for one_res in res:

           yield {
               "id":one_res["id"],
               "name":one_res["name"],
               "articleType":one_res["articleType"],
               "category":one_res["category"],
               "subCategory":one_res["subCategory"],
               "baseColour":one_res["baseColour"],
               "image_path":one_res["image_path"],
               "price":one_res["price"],
               "gender":one_res["gender"],
               "season":one_res["season"],
               "year":one_res["year"],
               "usage":one_res["usage"],
           }

    def parser_aggregations(self,aggregations_result):
        left_filter = {}
        left_filter["gender"] = aggregations_result["_filter_gender"]["gender"]["buckets"]
        left_filter["year"] = aggregations_result["_filter_year"]["year"]["buckets"]
        left_filter["color"] = aggregations_result["_filter_baseColour"]["baseColour"]["buckets"]
        left_filter["price"] = aggregations_result["_filter_price"]["price"]["buckets"]
        # max_price = 0
        # min_price = 0
        # if aggregations_result["_filter_price_metric"]["price_metric"]["buckets"]:
        #     min_price = min(aggregations_result["_filter_price_metric"]["price_metric"]["buckets"],key=lambda ele:ele["key"])["key"]
        #     max_price = max(aggregations_result["_filter_price_metric"]["price_metric"]["buckets"],key=lambda ele:ele["key"])["key"]
        max_price = 2000
        min_price = 200
        left_filter["price_min"] = min_price
        left_filter["price_max"] = max_price
        #left_filter["price_metric_min"] = aggregations_result["_filter_price_metric_min"]["price_metric_min"]["buckets"]
        return left_filter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        custom_query_doc = queryset.to_dict()
        search_query = request.query_params.get('query', '')
        if search_query:
            query_vector = model.encode(search_query)
            custom_query_doc['min_score'] = settings.COSINE_SIMILARITY
            custom_query_doc['query'] = {
                "script_score": {
                    "query": custom_query_doc['query'],
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'name_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        custom_query_set = queryset.from_dict(custom_query_doc)
        pagination_query = self.paginate_queryset(custom_query_set)
        res = self.get_paginated_response(pagination_query)
        new_res= self.parser_data(res.data['results'])
        left_filter = self.parser_aggregations(res.data['facets'])
        return Response({
            "total_products": res.data['count'],
            "result": new_res,
            "filter": left_filter
        })
        # return Response(res)

    def suggestor_parser_data(self,res):
        return [one_res["name"] for one_res in res]

    @action(detail=False)
    def suggest(self, request):
        # Used for suggest routes, like
        # http://localhost:8000/search/books-custom/suggest/?title_suggest=A
        # print('suggest')
        # print('request: ', request)
        # queryset = self.filter_queryset(self.get_queryset())
        # is_suggest = getattr(queryset, '_suggest', False)
        # if not is_suggest:
        #     return Response(
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        # custom_query_doc = queryset.to_dict()
        # suggest_query = {
        #     "suggest":custom_query_doc.get('suggest'),
        #     "_source":{'includes': ['name']}
        # }
        # res = elastic_search(index_name='product', body=suggest_query)
        queryset = self.filter_queryset(self.get_queryset())
        custom_query_doc = queryset.to_dict()
        search_query = request.query_params.get('query', '')
        query_vector = model.encode(search_query)
        if search_query:
            custom_query_doc = {
                "min_score": settings.COSINE_SIMILARITY,
                "size": 5,
                "_source": {'includes': ['name']},
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'name_vector') + 1.0",
                            "params": {"query_vector": query_vector}
                        }
                    }
                }
            }
        custom_query_set = queryset.from_dict(custom_query_doc)
        pagination_query = self.paginate_queryset(custom_query_set)
        res = self.get_paginated_response(pagination_query)
        # res = elastic_search(index_name='product', body=custom_query_doc)
        new_res = self.suggestor_parser_data(res.data['results'])
        return Response({
            "result": new_res,
        })
