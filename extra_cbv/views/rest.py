# coding:utf-8
from django.views.generic.base import View


class RestView(View):
    get_view = None
    post_view = None

    def get(self, request, *args, **kwargs):
        return self.get_view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.post_view(request, *args, **kwargs)
