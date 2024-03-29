import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class JSONField(models.TextField):
    """
    JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly.
    Django snippet #1478

    example:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)

        # save dict type
        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()

        # save list type
        page = Page.objects.get(pk=5)
        page.data = [{'title': 'test', 'type': 3}, {'title': 'test_test', 'type': 4}]
        page.save()

    """

    def to_python(self, value):
        if value == "":
            return None

        try:
            if isinstance(value, str):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def from_db_value(self, value, *args):
        return self.to_python(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        if value == "":
            return None
        if isinstance(value, (list, dict)):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return value
