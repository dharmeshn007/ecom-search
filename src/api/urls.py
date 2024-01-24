from django.urls import re_path, include
from django.urls import path
from rest_framework import routers

from api.v1.search.viewsets import SearchDocumentViewSet

from api.v1.elastic_search.views import ElasticSearchCreateCommand

from api.v1.elastic_search.views.elastic_search_upload import ElasticSearchUploadDataCommand

router = routers.DefaultRouter()
router.register(r'product', SearchDocumentViewSet, basename='product')
router.register(r'create-index', ElasticSearchCreateCommand, basename='create_index')
router.register(r'upload-data', ElasticSearchUploadDataCommand, basename='upload_data')

urlpatterns = [
    path('v1/', include(router.urls)),
]
