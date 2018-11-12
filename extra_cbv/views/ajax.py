# coding: utf-8

from django.http.response import JsonResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin


class AjaxResponseMixin(TemplateResponseMixin):
    status = True

    def render_to_response(self, context, **response_kwargs):
        if self.is_ajax():
            return self.get_ajax_response(context, **response_kwargs)
        return TemplateResponseMixin.render_to_response(self, context,
                                                        **response_kwargs)

    def serialize_context(self, context=None):
        return {'status': self.status}

    def get_ajax_response(self, context, **response_kwargs):
        return JsonResponse(self.serialize_context(context))

    def is_ajax(self):
        return self.request.is_ajax()


class AjaxFormMixin(AjaxResponseMixin, FormMixin):
    form_key_name = 'form'

    def serialize_context(self, context=None):
        if not self.status:
            return {
                'status': False,
                'errors': context[self.form_key_name].errors
            }
        else:
            return {'status': True}

    def form_valid(self, form):
        self.status = True
        if self.is_ajax():
            return self.get_ajax_response({'form': form})
        return FormMixin.form_valid(self, form)

    def form_invalid(self, form):
        self.status = False
        return FormMixin.form_invalid(self, form)


class UpdateAjaxFormMixin(AjaxFormMixin):

    def form_valid(self, form):
        self.object = form.save()
        return AjaxFormMixin.form_valid(self, form)
