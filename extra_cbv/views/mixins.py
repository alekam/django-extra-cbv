'''
Created on 12.11.2011

@author: alekam
'''
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.views.generic.detail import SingleObjectMixin


__all__ = ['SuperSingleObjectMixin', 'ShowSuccessMessageMixin']


class PreProcessMixin(object):
    """
    Mixin to do some actions before start processing GET, PUT or POST request
    """

    def dispatch(self, request, *args, **kwargs):
        # prevent call many times
        if not hasattr(self, '_is_pre_processed'):
            self.request = request
            self.args = args
            self.kwargs = kwargs
            response = self.pre_process()
            if isinstance(response, HttpResponseBase):
                return response
            self._is_pre_processed = True
        return super(PreProcessMixin, self).dispatch(request, *args, **kwargs)

    def pre_process(self):
        """
        Can be overridden in child class
        You need manual control overload of this method in inheritance
        """
        return


class SuperSingleObjectMixin(PreProcessMixin, SingleObjectMixin):
    """
    This mixin is the same as SingleObjectMixin, but it set up
    `object` property before start processing request in GET or POST methods
    """
    def pre_process(self):
        self.object = self.get_object()
        return super(SuperSingleObjectMixin, self).pre_process()


class ShowSuccessMessageMixin(object):
    success_message = None

    def show_success_message(self):
        message = self.get_success_message()
        if message is not None:
            messages.success(self.request, message)

    def get_success_message(self):
        if self.success_message is not None:
            return self.success_message
        return None


class GetQuerysetMixin(object):
    queryset = None
    model = None

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset


class NextRedirectMixin(object):
    next_url_field_name = 'next'

    def get_success_url(self):
        return self.request.REQUEST.get(self.next_url_field_name)

    def is_safe_url(self, url):
        return is_safe_url(url=url, host=self.request.get_host())


class MassActionMixin(object):
    actions = {}

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get('action', False)
        if action:
            ids = self.request.POST.getlist('id')
            qs = self.get_queryset().filter(id__in=ids)
            action = self.actions.get(action, False)
            if action:
                action(self, qs)
            if not request.is_ajax():
                return HttpResponseRedirect(reverse('report_list'))
        return self.get(request, *args, **kwargs)


class FilteredListMixin(object):
    filter_class = None

    def get_filter_class(self):
        return self.filter_class

    def get_filter_kwargs(self, qs=None):
        if qs is None:
            qs = self.get_queryset()
        return {
            'data': self.request.REQUEST,
            'queryset': qs
        }

    def get_filter_object(self, qs=None):
        return self.get_filter_class()(**self.get_filter_kwargs(qs))

    def get_context_data(self, **kwargs):
        qs = kwargs.get('object_list')
        if qs is None:
            qs = self.get_queryset()
        f = self.get_filter_object(qs)
        kwargs['filter'] = f
        kwargs['object_list'] = f.qs
        return kwargs


class SearchMixin(object):
    search_field = 'search'
    search_fields = []

    def get_queryset(self, qs):
        query = self.request.GET.get(self.search_field)
        if query not in EMPTY_VALUES:
            query = query.strip()
            if query not in EMPTY_VALUES and len(self.search_fields) > 0:
                lookup = None
                for field in self.search_fields:
                    if lookup is None:
                        lookup = Q(**{'%s__icontains' % field: query})
                    else:
                        lookup = lookup | Q(**{'%s__icontains' % field: query})
                qs = qs.filter(lookup)
        return qs

    def get_context_data(self, **kwargs):
        kwargs[self.search_field] = self.request.GET.get(self.search_field)
        return kwargs
