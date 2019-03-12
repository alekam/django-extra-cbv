# coding: utf-8
import inspect

from django.core.serializers.python import Serializer
from django.utils.encoding import force_text

from simplejson import OrderedDict


class PythonSerializer(Serializer):
    def get_dump_object(self, obj):
        data = OrderedDict()
        if not self.use_natural_primary_keys or not hasattr(obj, 'natural_key'):
            data["pk"] = force_text(obj._get_pk_val(), strings_only=True)
        data.update(self._current)

        # TODO: обработка методов
#             for field in concrete_model._meta.many_to_many:
#                 if field.serialize:
#                     if self.selected_fields is None or field.attname in self.selected_fields:
#                         self.handle_m2m_field(obj, field)

        return data


def simple_serialize(queryset, context=None, **options):
    """
    Serialize a queryset (or any iterator that returns database objects) using
    a certain serializer.
    """
    s = PythonSerializer()
    s.serialize(queryset, **options)
    return s.getvalue()


def serialize(obj, serializer_class=None, many=False, context=None):
    """
    Serialize an object or queryset (or any iterator that returns database objects)
    using serializer from Djangp REST Framework or our `simple_serialize`
    function
    """
    if serializer_class is None:
        if not many:
            obj = [obj, ]
        return simple_serialize(obj, context=context)
    if inspect.isclass(serializer_class):
        serializer = serializer_class(obj, many=many, context=context)
        return serializer.data
    elif many:
        return [serializer_class(o, context=context) for o in obj]
    else:
        return serializer_class(obj, context=context)
