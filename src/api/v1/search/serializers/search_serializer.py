from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from ..documents import SearchDocument

__all__ = (
    'SearchDocumentSerializer',
    # 'SearchDocumentSimpleSerializer',
    # 'SearchDocumentSourceSerializer',
)


class SearchDocumentSerializer(serializers.Serializer):
    """Serializer for the Search document."""

    id = serializers.CharField(read_only=True)

    name = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    image_path = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    subCategory = serializers.CharField(read_only=True)
    articleType = serializers.CharField(read_only=True)
    baseColour = serializers.CharField(read_only=True)
    usage = serializers.CharField(read_only=True)
    season = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    price = serializers.FloatField(read_only=True)
    # name_vector = serializers.ListField(read_only=False)
    # pages = serializers.IntegerField(read_only=True)
    # stock_count = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    # tags = serializers.SerializerMethodField()


    class Meta:
        """Meta options."""

        fields = (
            'id',
            'name',
            'gender',
            'image_path',
            'category',
            'subCategory',
            'articleType',
            'baseColour',
            'usage',
            'season',
            'year',
            'price',
            # 'tags',
            'created',
        )
        exclude = (
            'name_vector',
        )
        read_only_fields = fields

    def create(self, validated_data):
        """Create.

        Do nothing.

        :param validated_data:
        :return:
        """

    def update(self, instance, validated_data):
        """Update.

        Do nothing.

        :param instance:
        :param validated_data:
        :return:
        """

    def get_tags(self, obj):
        """Get tags."""
        if obj.tags:
            return list(obj.tags)
        else:
            return []

