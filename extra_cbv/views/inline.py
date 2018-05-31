'''
Created on 05.03.2012

@author: alekam
'''
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.http import Http404
from django.utils.encoding import smart_str
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormMixin, UpdateView
from django.views.generic.list import ListView


__all__ = ['InlineListView', 'CreateView', 'InlineUpdateView']


class InlineMixin(object):
    master_model = None
    context_master_object_name = None

    # like Django SingleObjectMixin
    master_slug_field = 'slug'
    master_slug_url_kwarg = 'slug'
    master_pk_url_kwarg = 'pk'
    master_query_pk_and_slug = False

    def get_master_object_queryset(self):
        return self.master_model._default_manager.all()

    def get_master_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_master_object_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.master_pk_url_kwarg)
        slug = self.kwargs.get(self.master_slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.master_query_pk_and_slug):
            slug_field = self.master_slug_field
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic inline view %s must be called with "
                                 "either a master object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_master_object_name(self):
        if self.context_master_object_name:
            return self.context_master_object_name
        elif hasattr(self.master_object, 'model'):
            return smart_str(self.master_object.model._meta.object_name.lower())
        elif self.master_model is not None:
            return smart_str(self.master_model._meta.object_name.lower())
        else:
            return None

    def get_context_data(self, **kwargs):
        context = {}
        if self.master_object:
            context['master_object'] = self.master_object
            master_name = self.get_context_master_object_name()
            if master_name:
                context[master_name] = self.master_object
        context.update(kwargs)
        return super(InlineMixin, self).get_context_data(**context)


class InlineListView(InlineMixin, ListView):

    def get(self, *args, **kwargs):
        self.master_object = self.get_master_object()
        return super(InlineListView, self).get(*args, **kwargs)


class InlineFormMixin(InlineMixin):
    success_redirect_on_master = True
    master_field_name = None  # required field
    allow_empty_master = False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.save_object()
        return FormMixin.form_valid(self, form)

    def save_object(self):
        setattr(self.object, self.master_field_name, self.get_master_object())
        self.object.save()

    def get_master_object(self):
        try:
            return InlineMixin.get_master_object(self)
        except ObjectDoesNotExist as e:
            if self.allow_empty_master:
                return None
            else:
                raise e

    def get_success_url(self):
        if self.success_redirect_on_master:
            return self.get_master_object().get_absolute_url()
        return self.object.get_absolute_url()


class InlineCreateView(InlineFormMixin, CreateView):

    def get(self, request, *args, **kwargs):
        self.master_object = self.get_master_object()
        return CreateView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.master_object = self.get_master_object()
        return CreateView.post(self, request, *args, **kwargs)


class InlineUpdateView(InlineFormMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        self.master_object = self.get_master_object()
        return UpdateView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.master_object = self.get_master_object()
        return UpdateView.post(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(**self.get_lookup())
        return UpdateView.get_object(self, queryset)

    def get_lookup(self):
        if self.master_field_name is None:
            raise ImproperlyConfigured('You need setup `master_field_name` attribute in child class')
        return {
            '%s__id' % self.master_field_name: \
                                self.kwargs.get(self.master_pk_url_kwarg)
        }


class InlineDetailView(InlineMixin, DetailView):

    def get(self, *args, **kwargs):
        self.master_object = self.get_master_object()
        return super(InlineDetailView, self).get(*args, **kwargs)
