from django.conf import settings

from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl_drf.compat import KeywordField, StringField
from django_elasticsearch_dsl_drf.analyzers import edge_ngram_completion
from django_elasticsearch_dsl_drf.versions import ELASTICSEARCH_GTE_5_0


from api.models import Product
from .analyzers import html_strip


__all__ = ('SearchDocument',)

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1,
    blocks={'read_only_allow_delete': None},
    # read_only_allow_delete=False
)


@INDEX.doc_type
class SearchDocument(Document):
    """Search Elasticsearch document."""

    # In different parts of the code different fields are used. There are
    # a couple of use cases: (1) more-like-this functionality, where `title`,
    # `description` and `summary` fields are used, (2) search and filtering
    # functionality where all of the fields are used.

    # ID
    id = fields.IntegerField(attr='_id')

    # ********************************************************************
    # *********************** Main data fields for search ****************
    # ********************************************************************
    __title_fields = {
        'raw': KeywordField(),
        'suggest': fields.CompletionField(),
        'edge_ngram_completion': StringField(
            analyzer=edge_ngram_completion
        ),
        'mlt': StringField(analyzer='english'),
    }

    if ELASTICSEARCH_GTE_5_0:
        __title_fields.update(
            {
                'suggest_context': fields.CompletionField(
                    contexts=[
                        {
                            "name": "name",
                            "type": "keyword",
                            "path": "name",
                        },
                    ]
                ),
            }
        )

    name = StringField(
        analyzer=html_strip,
        fields=__title_fields
    )

    description = StringField(
        analyzer=html_strip,
        fields={
            'raw': KeywordField(),
            'mlt': StringField(analyzer='english'),
        }
    )
    name_vector = StringField(attr='name_vector')


    # ********************************************************************
    # ********** Additional fields for search and filtering **************
    # ********************************************************************


    # Price
    price = fields.FloatField()

    # Date created
    created = fields.DateField(attr='created_indexing')

    null_field = StringField(attr='null_field_indexing')

    class Django(object):
        model = Product  # The model associate with this Document

    class Meta:
        parallel_indexing = True
        # queryset_pagination = 50  # This will split the queryset
        #                           # into parts while indexing

    def prepare_summary(self, instance):
        """Prepare summary."""
        return instance.summary[:32766] if instance.summary else None

    def prepare_authors(self, instance):
        """Prepare authors."""
        return [author.name for author in instance.authors.all()]
