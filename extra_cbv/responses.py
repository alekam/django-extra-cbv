from .utils import LazyEncoder


class JsonResponse(HttpResponse):
    def __init__(self, data):
        HttpResponse.__init__(
            self, content=simplejson.dumps(data, cls=LazyEncoder),
            content_type="application/json",
        )
