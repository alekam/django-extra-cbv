'''
Created on 05.03.2012

@author: alekam
'''
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.views.generic.edit import CreateView, FormMixin, UpdateView, \
    ProcessFormView
from django.views.generic.list import ListView


__all__ = ['InlineListView', 'CreateView', 'InlineUpdateView']


class InlineListView(ListView):
    context_master_object_name = None
    master_model = None

    def get(self, *args, **kwargs):
        self.master = self.get_master_object(self.kwargs['pk'])
        return super(InlineListView, self).get(*args, **kwargs)

    def get_master_object(self, pk):
        return get_object_or_404(self.master_model, pk=pk)

    def get_context_master_object_name(self):
        if self.context_master_object_name:
            return self.context_master_object_name
        elif hasattr(self.master, 'model'):
            return smart_str(self.master.model._meta.object_name.lower())
        elif self.master_model is not None:
            return smart_str(self.master_model._meta.object_name.lower())
        else:
            return None

    def get_context_data(self, **kwargs):
        kwargs.update({
            'master': self.master,
            self.get_context_master_object_name(): self.master
        })
        return super(InlineListView, self).get_context_data(**kwargs)


class InlineMixin(object):
    master_model = None
    success_redirect_on_master = True
    master_field_name = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.save_object()
        return FormMixin.form_valid(self, form)

    def save_object(self):
        setattr(self.object, self.master_field_name, self.get_master_object())
        self.object.save()

    def get_master_object(self):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return self.master_model.objects.get(pk=pk)
        return None

    def get_success_url(self):
        if self.success_redirect_on_master:
            return self.get_master_object().get_absolute_url()
        return self.object.get_absolute_url()


class InlineCreateView(InlineMixin, CreateView):

    def get(self, request, *args, **kwargs):
        self.maste_object = self.get_master_object()
        return CreateView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.maste_object = self.get_master_object()
        return CreateView.post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = CreateView.get_context_data(self, **kwargs)
        ctx['object'] = self.get_master_object()
        return ctx


class InlineUpdateView(InlineMixin, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = UpdateView.get_context_data(self, **kwargs)
        ctx['object'] = self.get_master_object()
        return ctx

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk is None:
            raise Http404
        return self.get_queryset().get(**self.get_lookup())

    def get_lookup(self):
        return {
            '%s__id' % self.master_field_name : self.kwargs.get('pk')
        }
