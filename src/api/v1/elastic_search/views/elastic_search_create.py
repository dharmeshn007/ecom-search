from rest_framework import viewsets, permissions, response
from rest_framework.response import Response


class ElasticSearchCreateCommand(viewsets.ViewSet):
    model = None

    def list(self, request, *args, **kwargs):
        from django.core.management import call_command
        # call_command('collectstatic')
        call_command('create_index')

        return Response({
            "message": "index created successfully",
        })



