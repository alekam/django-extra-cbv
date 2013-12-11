from django.views.generic.base import TemplateView, View


def direct_to_template(request, template):
    return TemplateView.as_view(template_name=template)(request)


class ProxyView(View):
    '''
    Proxy to another views
    It allows to choose between some different view depends on conditions.
    Show different views for users from different groups for example.
    '''

    def dispatch(self, request, *args, **kwargs):
        return self.get_view(request, *args, **kwargs)

    def get_view(self, request, *args, **kwargs):
        raise NotImplementedError('You must override `get_view` method in '
                                  'child view')
