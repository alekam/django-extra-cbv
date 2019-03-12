# coding: utf-8

from django.http.response import JsonResponse, HttpResponse


def json_response(func):
    def wrapped(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        return JsonResponse(response)
    return wrapped
