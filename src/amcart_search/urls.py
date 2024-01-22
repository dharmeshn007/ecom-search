"""swisspacer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view

from api import urls as api_url


class SchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, request=None, public=False):
        schema = super(SchemaGenerator, self).get_schema(request, public)
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="AmCart SearchAPI",
        default_version='v1',
    ),
    public=True,
    # permission_classes=(permissions.IsAuthenticated,),
    generator_class=SchemaGenerator,
)

urlpatterns = [
                  # path('product/api/admin/', admin.site.urls),
                  path('api/', include(api_url)),
                  path('health-check/', TemplateView.as_view(template_name='health_check/message.html'), name='home'),
                  # path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                  path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('', TemplateView.as_view(template_name='health_check/message.html'), name='home'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [url(r'^product/', include(urlpatterns))]