from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    HighlightBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    PostFilterFilteringFilterBackend,
    SearchFilterBackend, SuggesterFilterBackend, FunctionalSuggesterFilterBackend, FacetedFilterSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import (
    BaseDocumentViewSet, DocumentViewSet,
)

from elasticsearch_dsl import DateHistogramFacet, RangeFacet, A, TermsFacet

__all__ = (
    'BaseSearchDocumentViewSet',
)

from api.v1.search.documents import SearchDocument
# from api.v1.search.serializers import SearchDocumentSimpleSerializer


class BaseSearchDocumentViewSet(DocumentViewSet):
    """Base SearchDocument ViewSet."""

    document = SearchDocument
    # serializer_class = SearchDocumentSerializer
    # serializer_class = SearchDocumentSimpleSerializer
    lookup_field = '_id'
    filter_backends = [
        FilteringFilterBackend,
        PostFilterFilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
        FacetedSearchFilterBackend,
        SuggesterFilterBackend,
        FunctionalSuggesterFilterBackend,
        FacetedFilterSearchFilterBackend
        # HighlightBackend,
    ]
    # Define search fields
    # search_fields = (
    #     'name',
    #     'description',
    # )
    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_FILTER_TERMS,
            ],
        },
        'description': {
            'field': 'description',
            'lookups': [
                LOOKUP_QUERY_IN,
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_FILTER_PREFIX
            ],
        },
        'name': {
            'field': 'name',
            'lookups': [
                LOOKUP_QUERY_IN,
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_FILTER_PREFIX
            ],
        },
        'price': {
            'field': 'price',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'baseColour': {
            'field': 'baseColour',
            'lookups': [
                LOOKUP_QUERY_IN,
                LOOKUP_FILTER_TERMS
            ],
        },
	'gender': {
            'field': 'gender',
            'lookups': [
                LOOKUP_QUERY_IN,
                LOOKUP_FILTER_TERMS
            ],
        }
    }
    # Post filter fields, copy filters as they are valid
    post_filter_fields = {
    }
    # Define ordering fields
    ordering_fields = {
        'id': '_id',
        'name': 'name',
        'price': 'price',
        'created_at': 'created_at',
    }
    # Specify default ordering
    # ordering = ('id',  'price',)
    faceted_search_fields = {
        # 'creation_date': {
        #     'field': 'created_at',
        #     'facet': DateHistogramFacet,
        #     'enabled': True,
        #     'global': True,
        #     'options': {
        #         'interval': 'year',
        #     }
        # },
        'year': {
            'field': 'year',
            'facet': TermsFacet,
            'enabled': True,
        },
        'gender': {
            'field': 'gender',
            'facet': TermsFacet,
            'global': True,
            'enabled': True,
        },
        'baseColour': {
            'field': 'baseColour',
            'facet': TermsFacet,
            'global': True,
            'enabled': True,
        },
        'price_metric': {
            "field": "price",
            'options': {
                'metric': A('max', field='price'),
            },
            'enabled': True,
        },
        'price': {
            'field': 'price',
            'facet': RangeFacet,
            'enabled': True,
            'global': True,
            'options': {
                'ranges': [
                    ("<300", (None, 300)),
                    ("300-500", (300, 500)),
                    ("500-1000", (500, 1000)),
                    ("1000-1500", (1000, 1500)),
                    (">1500", (1500, None)),
                ]
            }
        }
    }
