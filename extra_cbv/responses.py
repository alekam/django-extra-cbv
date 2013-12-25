from .utils import LazyEncoder
from django.http.response import HttpResponse
import json


class JsonResponse(HttpResponse):
    def __init__(self, data):
        HttpResponse.__init__(
            self, content=json.dumps(data, cls=LazyEncoder),
            content_type="application/json",
        )
