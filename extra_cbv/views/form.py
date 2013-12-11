from django.views.generic.edit import FormView


__all__ = ['FormWithRequestView', ]


class FormWithRequestView(FormView):

    def get_form_kwargs(self):
        kwargs = FormView.get_form_kwargs(self)
        kwargs['request'] = self.request
        return kwargs
