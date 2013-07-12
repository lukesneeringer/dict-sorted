from copy import copy, deepcopy
from sdict.utils import smart_repr
import six


class NoDefault(object):
    def __len__(self):
        return 0


class SortedDict(dict):
    """A dict subclass that always returns keys in alphabetical order,
    and iterates over keys in alphabetical order."""

    def __init__(self, __cmp, __data=None, **kwargs):
        """Create a new sorted dictionary.

        The order of the keys is determined by the first positional
        argument, which should be the appropriate comparison function.

        This is a function taking a *single* argument and returning some
        value that can be compared against other values (so, something
        supporting >, <, and ==).

        The comparison function is required. For a common use case
        (keys sorted in alphabetical order), use AlphaSortedDict.

        The second positional argument, if provided, is initial keys and
        values to compose the dictionary. Arbitrary keyword arguments are
        also accepted.
        """
        # Initialize a key order list.
        self._key_order_cache = []

        # Save the comparison function being used.
        self._cmp = __cmp

        # Create a dictionary based on the positional argument
        # (including, possibly, an empty one).
        __data = __data or []
        super(SortedDict, self).__init__(dict(__data))

        # If keyword arguments were sent, add them.
        for k, v in six.iteritems(kwargs):
            self[six.text_type(k)] = v  # We know the key is a string,
                                        # because it's a keyword argument.

    def __copy__(self):
        """Create and return a shallow copy of this instance."""

        # Attempt to figure out from the method signature whether
        # a comparison function is expected.
        args = [self]
        code = six.get_function_code(self.__class__.__init__)
        if any([i.endswith('__cmp') for i in code.co_varnames]):
            args.insert(0, self._cmp)

        # Create the shallow copy.
        return self.__class__(*args)

    def __deepcopy__(self, memo=None):
        """Create and return a deep copy of this instance."""

        # Attempt to figure out from the method signature whether
        # a comparison function is expected.
        args = []
        code = six.get_function_code(self.__class__.__init__)
        if any([i.endswith('__cmp') for i in code.co_varnames]):
            args.append(self._cmp)

        # Create an empty sorted dictionary.
        answer = self.__class__(*args)

        # Ensure that this object is in our memo list, in case
        # there is a recursive relationship.
        if not memo:
            memo = {}
        memo[id(self)] = answer

        # Deep copy the individual elements.
        for key, value in six.iteritems(self):
            answer.__setitem__(
                deepcopy(key, memo=memo),
                deepcopy(value, memo=memo),
            )

        # Done.
        return answer

    def __iter__(self):
        return six.iterkeys(self)

    def __repr__(self, object_list=None):
        """Send down a useful, unambiguous representation of the
        object.
        """
        # Sanity check: Have we rendered this object already?
        # Avoid a recursion scenario.
        if not object_list:
            object_list = []
        if self in object_list:
            return '**RECURSION**'

        # Return the repr.
        return '{%s}' % ', '.join(
            ['%s: %s' % (
                smart_repr(k, object_list=object_list + [self]),
                smart_repr(self[k], object_list=object_list + [self]),
            ) for k in six.iterkeys(self)],
        )

    def __setitem__(self, key, value):
        """Add a key and value to the dictionary, clearing out
        the cache.
        """
        # If the key isn't already in the dictionary, we'll
        #   need to destroy our key order cache.
        if key not in self:
            self._clear_key_order_cache()

        # Add the value, assigned to the key
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        # The key should be in the key order cache; remove it.
        # We can safely do this without breaking order.
        if key in self._key_order_cache:
            self._key_order_cache.remove(key)

        # Remove the item from the dictionary.
        super(SortedDict, self).__delitem__(key)

    def clear(self):
        super(SortedDict, self).clear()
        self._clear_key_order_cache()

    def _clear_key_order_cache(self):
        self._key_order_cache = []

    def index(self, key):
        """Return the index of the given key. If the key is not
        present in the dictionary, raise IndexError.
        """
        # Sanity check: Has the key order cache been generated?
        # If not, generate it.
        if not self._key_order_cache:
            [k for k in self.keys()]

        # Return the index of this key within the list.
        return self._key_order_cache.index(key)

    def items(self):
        for key in self.keys():
            yield (key, self[key])

    def keys(self):
        """Return the keys for this dictionary, ordered."""

        # Sanity check: Is there already a cache of the ordered keys?
        #   If so, we don't actually need to do anything.
        if not self._key_order_cache:
            koc = sorted(super(SortedDict, self).keys(), key=self._cmp)
            self._key_order_cache = koc

        # Iterate over the key order cache and yield each.
        for key in copy(self._key_order_cache):
            yield key

    def pop(self, key, default=NoDefault()):
        """Pop a key-value pair off the dictionary, and return the value.
        If a default value is given, return it instead of raising KeyError
        if the key was not present.
        """
        # If this key is in our key order cache, remove it.
        # (This will always be still safely sorted.)
        if key in self._key_order_cache:
            self._key_order_cache.remove(key)

        # Pop the key off the actual dictionary.
        if isinstance(default, NoDefault):
            return super(SortedDict, self).pop(key)
        return super(SortedDict, self).pop(key, default)

    def setdefault(self, key, default):
        if key not in self:
            self._clear_key_order_cache()
        return super(SortedDict, self).setdefault(key, default)

    def update(self, other):
        super(SortedDict, self).update(other)
        self._clear_key_order_cache()

    def values(self):
        for key in self.keys():
            yield self[key]

    if not six.PY3:
        iteritems = items
        iterkeys = keys
        itervalues = values

        # This is doing a four-line list creation over a loop instead
        #   of a tidier list comprehension because, for some reason,
        #   coverage can't seem to track that the list comprehension
        #   is running.
        # Oh well... :)

        def items(self):
            answer = []
            for k, v in self.iteritems():
                answer.append((k, v))
            return answer

        def keys(self):
            answer = []
            for k in self.iterkeys():
                answer.append(k)
            return answer

        def values(self):
            answer = []
            for v in self.itervalues():
                answer.append(v)
            return answer
