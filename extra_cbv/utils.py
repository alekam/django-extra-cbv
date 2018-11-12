# coding: utf-8
from django.shortcuts import _get_queryset


def get_object_or_None(klass, *args, **kwargs):
    queryset = _get_queryset(klass).default_manager().get(**kwargs)
    try:
        return queryset.get(*args, **kwargs)
    except AttributeError:
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    except queryset.model.DoesNotExist:
        return None
