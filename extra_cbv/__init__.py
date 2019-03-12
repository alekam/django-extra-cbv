# major, minor, patch
VERSION = (0, 2, 1)


def get_version():
    return u'.'.join([unicode(x) for x in VERSION])
