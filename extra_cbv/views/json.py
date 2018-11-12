# coding: utf-8
from django.http.response import JsonResponse
from django.views.generic.base import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from react.serializers import serialize


class JsonMixin(object):

    def render_to_response(self, context, **response_kwargs):
        data = self.serialize_context(context)
        return JsonResponse(data, **response_kwargs)

    def serialize_context(self, context):
        return context


class JsonView(JsonMixin, View):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {}


class SerializePaginationMixin(object):

    def serialize_context(self, context):
        data = super(SerializePaginationMixin, self).serialize_context(context)

        if 'page_obj' in context and 'paginator' in context:
                # if context['is_paginated']:
            data['pagination'] = self.get_pagination_data(context)

        return data

    def get_pagination_data(self, context):
        """
        Serialize django pagination data from context of ListView like views
        """
        return {
            "next": context['page_obj'].next_page_number() \
                        if context['page_obj'].has_next() else None,
            "previous": context['page_obj'].previous_page_number() \
                        if context['page_obj'].has_previous() else None,
            "count": context['paginator'].num_pages,
        }


class JsonListView(SerializePaginationMixin, JsonMixin, BaseListView):

    def get_serializer(self):
        return None

    def serialize_object_list(self, object_list, context):
        return serialize(object_list, self.get_serializer(), many=True, context=context)

    def serialize_context(self, context):
        data = super(JsonListView, self).serialize_context(context)
        object_list = self.serialize_object_list(context['object_list'], context)
        data[self.context_object_name or 'object_list'] = object_list
        return data


class JsonDetailView(JsonMixin, BaseDetailView):

    def get_serializer(self):
        return None

    def serialize_object(self, obj, context):
        return serialize(obj, self.get_serializer(), many=False, context=context)

    def serialize_context(self, context):
        data = super(JsonListView, self).serialize_context(context)
        obj = self.serialize_object(context['object_list'], context)
        data[self.context_object_name or 'object'] = obj
        return data
