import six


def smart_repr(obj, object_list=None):
    """Return a repr of the object, using the object's __repr__ method.
    Be smart and pass the depth value if and only if it's accepted.
    """
    # If this object's `__repr__` method has a `__code__` object *and*
    #   the function signature contains `object_list` and `depth`, then
    #   include the object list.
    # Otherwise, just call the stock repr.
    try:
        code = six.get_function_code(obj.__repr__)
        if all(['object_list' in obj.__repr__.__code__.co_varnames]):
            return obj.__repr__(object_list=object_list)
    except AttributeError:
        pass
    return repr(obj)
