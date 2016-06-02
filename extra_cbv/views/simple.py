from .mixins import SuperSingleObjectMixin, PreProcessMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.views.generic.base import View, RedirectView
from django.views.generic.list import ListView
import StringIO


__all__ = ['DownloadReportView', 'PaginatedListView']


class DownloadReportView(View):
    builder_class = None

    def get_builder(self):
        builder_class = self.get_builder_class()
        if builder_class is None:
            raise ImproperlyConfigured(u'You must define `builder_class` '
                                       'in your view')
        return builder_class(**self.get_builder_kwargs())

    def get_builder_class(self):
        return self.builder_class

    def get_builder_kwargs(self):
        return {}

    def get(self, *args, **kwargs):
        self.report = self.get_builder()
        output = StringIO.StringIO()
        self.report.generate(output)

        response = HttpResponse(content=output.getvalue(),
                                mimetype=self.get_mimetype())
        response['Content-Disposition'] = 'attachment;filename="%s"' % \
                                                            self.get_filename()
        return response

    def get_filename(self):
        return '%s.%s' % ('report', self.get_file_ext())

    def get_file_ext(self):
        return self.report.get_file_ext()

    def get_mimetype(self):
        return self.report.get_mimetype()


class ExportView(DownloadReportView):
    queryset = None

    def get_queryset(self):
        return self.queryset

    def get_builder_kwags(self):
        return {
            'queryset': self.get_queryset()
        }

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class PaginatedListView(ListView):

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx.update({
            'pages': self.get_pages(ctx['paginator'], ctx['page_obj'])
        })
        return ctx

    def get_pages(self, p, page):
        pags = []
        pg = page.number
        if 1 < pg - 2:
            pags.append((1, 1,))
            pags.append(('...', None,))
        #        if pg - 1 in p.page_range:
        #            pags.append(('Prev', p.page(pg - 1) ,))
        for n in range(pg - 2, pg + 2):
            if n in p.page_range:
            #                pags.append((n, p.page(n) ,))
                pags.append((n, n,))
        if p.num_pages not in range(pg - 2, pg + 3):
            pags.append(('...', None,))
            pags.append((p.num_pages, p.num_pages,))
        return pags


class ProcessView(PreProcessMixin, RedirectView):

    def pre_process(self):
        resp = super(ProcessView, self).pre_process()
        if resp:
            return resp
        else:
            return self.process()

    def process(self):
        return


class ProcessObjectView(SuperSingleObjectMixin, ProcessView):

    def get_redirect_url(self, **kwargs):
        url = super(ProcessObjectView, self).get_redirect_url(**kwargs)
        if url is None:
            try:
                return self.object.get_absolute_url()
            except:
                pass
        return url
