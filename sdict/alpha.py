from sdict.base import SortedDict
import six


class AlphaSortedDict(SortedDict):
    """A dictionary subclass where keys are always sorted in
    alphabetical order (case-insensitive).
    """
    def __init__(self, __data=None, **kwargs):
        # Coerce all keys in the __data dict to strings.
        data_dict = {}
        if __data:
            for key, value in six.iteritems(dict(__data)):
                data_dict[six.text_type(key)] = value

        # The superclass' construction otherwise works fine
        # for this case.
        return super(AlphaSortedDict, self).__init__(six.text_type.lower,
                                                     data_dict,
                                                     **kwargs)

    def __setitem__(self, key, value):
        key = six.text_type(key)
        return super(AlphaSortedDict, self).__setitem__(key, value)

    def setdefault(self, key, default):
        key = six.text_type(key)
        return super(AlphaSortedDict, self).setdefault(key, default)

    def update(self, other):
        # Coerce every key on the `other` dictionary to unicode.
        coerced_other = {}
        for key, value in six.iteritems(dict(other)):
            coerced_other[six.text_type(key)] = value

        # Run the superclass `update` function.
        return super(AlphaSortedDict, self).update(coerced_other)
