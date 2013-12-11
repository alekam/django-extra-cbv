'''
Generic views for formsets processing

Created on 08.01.2012

@author: alekam <alex@kamedov.ru>
'''
from .mixins import GetQuerysetMixin, SuperSingleObjectMixin
from django.core.exceptions import ImproperlyConfigured
from django.forms.formsets import BaseFormSet, formset_factory
from django.forms.models import ModelForm, BaseModelFormSet, \
    modelformset_factory, inlineformset_factory, BaseInlineFormSet
from django.utils.encoding import smart_str
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormMixin


class FormsetMixin(FormMixin):
    """
    A mixin that provides a way to show and handle a formset in a request.
    """
    formset_class = BaseFormSet
    formset_extra = 1
    can_order = False
    can_delete = False
    max_num = None
    initial = {}

    def get_formset_class(self):
        """
        Returns an instance of the formset to be used in this view.
        """
        kwargs = self.get_formset_class_kwargs()
        return formset_factory(**kwargs)

    def get_formset_class_kwargs(self):
        """
        Returns keywords arguments to create the formset class
        """
        return {
            'form': self.get_form_class(),
            'formset': self.formset_class,
            'extra': self.formset_extra,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'max_num': self.max_num
        }

    def get_formset_kwargs(self):
        return FormMixin.get_form_kwargs(self)

    def get_formset(self, formset_class=None):
        if formset_class is None:
            formset_class = self.get_formset_class()
        return formset_class(**self.get_formset_kwargs())


class MultipleObjectWithoutPaginationMixin(GetQuerysetMixin):
    context_object_name = None

    def get_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, 'model'):
            return smart_str('%s_list' % object_list.model._meta.object_name.lower())
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list')
        context_object_name = self.get_context_object_name(queryset)
        context = {
            'object_list': queryset
        }
        context.update(kwargs)
        if context_object_name is not None:
            context[context_object_name] = queryset
        return context


class BaseModelFormsetMixin(FormsetMixin):
    """
    Helpful class to process model formsets
    """
    model = None
    form_class = ModelForm
    formset_class = BaseModelFormSet
    formfield_callback = None
    fields = None
    exclude = None
    use_queryset = False

    def get_formset_class_kwargs(self):
        kwargs = FormsetMixin.get_formset_class_kwargs(self)
        kwargs.update({
            'model': self.model,
            'formfield_callback': self.formfield_callback,
            'fields': self.fields,
            'exclude': self.get_excluded_fields()
        })
        return kwargs

    def get_excluded_fields(self):
        return self.exclude

    def form_valid(self, formset):
        # TODO: this not work sometimes
        formset.save()
        return FormMixin.form_valid(self, formset)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class ModelFormsetMixin(BaseModelFormsetMixin, GetQuerysetMixin):
    use_queryset = True

    def get_formset_class(self):
        """
        Returns an instance of the formset to be used in this view.
        """
        kwargs = self.get_formset_class_kwargs()

        model = kwargs['model']
        del kwargs['model']

        return modelformset_factory(model, **kwargs)

    def get_formset_kwargs(self):
        kwargs = FormsetMixin.get_formset_kwargs(self)
        if self.use_queryset:
            kwargs['queryset'] = self.get_queryset()
        return kwargs


class InlineModelFormsetMixin(BaseModelFormsetMixin, SuperSingleObjectMixin):
    # parent model
    model = None
    # model
    inline_model = None
    fk_name = None
    form_class = ModelForm
    formset_class = BaseInlineFormSet

    def get_formset_class_kwargs(self):
        kwargs = BaseModelFormsetMixin.get_formset_class_kwargs(self)
        kwargs.update({
            'parent_model': self.model,
            'model': self.inline_model,
            'fk_name': self.fk_name,
        })
        return kwargs

    def get_formset_class(self):
        """
        Returns an instance of the formset to be used in this view.
        """
        kwargs = self.get_formset_class_kwargs()

        parent_model = kwargs['parent_model']
        del kwargs['parent_model']

        model = kwargs['model']
        del kwargs['model']

        return inlineformset_factory(parent_model, model, **kwargs)

    def get_formset_kwargs(self):
        kwargs = FormsetMixin.get_formset_kwargs(self)
        kwargs['instance'] = self.get_object()
        if 'initial' in kwargs:
            del kwargs['initial']
        if self.use_queryset:
            kwargs['queryset'] = self.get_inline_queryset()
        return kwargs

    def get_inline_queryset(self):
        if self.inline_queryset is None:
            if self.model:
                return self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(u"%(cls)s is missing a inline queryset. Define "
                                           u"%(cls)s.model, %(cls)s.inline_queryset, or override "
                                           u"%(cls)s.get_inline_queryset()." % {
                                                'cls': self.__class__.__name__
                                        })
        return self.inline_queryset._clone()

    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def get_context_data(self, **kwargs):
        context = kwargs
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        return context


class ProcessFormsetView(View):
    """
    A mixin that processes a formset on POST.
    """
    def get(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class UpdateInlineView(InlineModelFormsetMixin, ProcessFormsetView,
                       TemplateResponseMixin):
    """
    Undate existing inline objects and may be add new
    """
    template_name_suffix = '_formset'


class CreateInlineView(UpdateInlineView):
    """
    Create new inline objects
    """
    use_queryset = True

    def get_inline_queryset(self):
        return UpdateInlineView.get_queryset(self).none()
