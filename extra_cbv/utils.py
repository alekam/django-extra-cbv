from django.utils import simplejson
from django.utils.functional import Promise


class LazyEncoder(simplejson.JSONEncoder):

    def default(self, o):
        if isinstance(o, Promise):
            return unicode(o)
        else:
            return super(LazyEncoder, self).default(o)
