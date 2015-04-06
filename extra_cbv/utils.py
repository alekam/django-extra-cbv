try:
    import json
except:
    from django.utils import simplejson as json
from django.utils.functional import Promise


class LazyEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Promise):
            return unicode(o)
        else:
            return super(LazyEncoder, self).default(o)
