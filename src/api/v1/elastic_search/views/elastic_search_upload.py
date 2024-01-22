from rest_framework import viewsets, permissions, response
from rest_framework.response import Response


class ElasticSearchUploadDataCommand(viewsets.ViewSet):
    model = None

    def list(self, request, *args, **kwargs):
        from django.core.management import call_command
        page_no = int(self.request.GET.get("page",1))
        call_command('upload_data',page_no)
        return Response({
            "message": "data upload successfully",
        })



