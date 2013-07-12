#!/usr/bin/env python
from copy import copy, deepcopy
from sdict import sdict, adict
from sdict.base import NoDefault
import types
import six

# Import unittest2 if we have it, unittest otherwise.
# unittest2 is required for Python 2.6, optional thereafter.
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class BaseSuite(unittest.TestCase):
    def setUp(self):
        fx = lambda x: tuple([-ord(i) for i in six.text_type(x).lower()])
        self.x = sdict(fx, { 'a': 0, 'B': 1, 'x': object(), 'z': 10 })

    def test_ordering(self):
        """Test initialization of a sorted dictionary."""
        self.assertEqual([k for k in self.x], ['z', 'x', 'B', 'a'])

    def test_copy(self):
        y = copy(self.x)
        self.assertEqual(self.x, y)
        self.assertNotEqual(id(self.x), id(y))
        self.assertEqual(self.x['x'], y['x'])
        self.assertEqual([k for k in y], ['z', 'x', 'B', 'a'])

    def test_deepcopy(self):
        y = deepcopy(self.x)
        self.assertNotEqual(self.x, y)
        self.assertNotEqual(id(self.x), id(y))
        self.assertNotEqual(self.x['x'], y['x'])
        self.assertEqual([k for k in y], ['z', 'x', 'B', 'a'])


class AlphaSuite(unittest.TestCase):
    def test_init_dict(self):
        """Test initialzation of alpha sorted dictionaries using
        a plain dictionary.
        """
        x = adict({ 'z': 5, 'y': '0', 'a': 'x', 'B': [] })
        self.assertEqual([k for k in x.keys()], ['a', 'B', 'y', 'z'])
        self.assertEqual([v for v in x.values()], ['x', [], '0', 5])

    def test_init_kwargs(self):
        """Test initialization of alpha sorted dictionaries using
        keyword arguments.
        """
        x = adict(z=5, y='0', a='x', B=[])
        self.assertEqual([k for k in x.keys()], ['a', 'B', 'y', 'z'])
        self.assertEqual([v for v in x.values()], ['x', [], '0', 5])

    def test_init_assignment(self):
        """Test initialization of alpha sorted dictionaries using
        assignment, and going out of order.
        """
        x = adict()
        x['z'] = 2
        x['y'] = 1
        x['x'] = 0
        self.assertEqual([k for k in x.keys()], ['x', 'y', 'z'])

    def test_setitem(self):
        """Test setting of an item, ensuring that we get the results
        we expect.
        """
        x = adict(x=0, y=1, z=2)
        self.assertEqual([k for k in x.keys()], ['x', 'y', 'z'])
        x['a'] = 10
        self.assertEqual([k for k in x.keys()], ['a', 'x', 'y', 'z'])
        self.assertEqual([v for v in x.values()], [10, 0, 1, 2])
        x['a'] = 20
        self.assertEqual([k for k in x.keys()], ['a', 'x', 'y', 'z'])
        self.assertEqual([v for v in x.values()], [20, 0, 1, 2])

    def test_getitem(self):
        """Test item retrieval, ensuring that we get the results
        we expect.
        """
        x = adict(x=0, y=1, z=2)
        self.assertEqual(x['y'], 1)
        self.assertEqual(x.get('y'), 1)
        self.assertEqual(x.get('y', None), 1)
        self.assertEqual(x.get('w', None), None)
        with self.assertRaises(KeyError):
            x['w']

    def test_delitem(self):
        """Test item deletion, ensuring that we get the results
        we expect.
        """
        x = adict(x=0, y=1, z=2)
        del x['y']
        self.assertEqual([k for k in x.keys()], ['x', 'z'])

    def test_setdefault(self):
        """Test setting default, ensuring that we get the results
        we expect.
        """
        x = adict(x=0, y=1, z=2)
        x.setdefault('y', 10)
        self.assertEqual(x['y'], 1)
        x.setdefault('w', 10)
        self.assertEqual(x['w'], 10)

    def test_update(self):
        """Test updating a dictionary, ensuring that we get the results
        that we expect.
        """
        x = adict(y=1, z=2)
        x.update({ 'a': 0, 'b': -1 })
        self.assertEqual([k for k in x.keys()], ['a', 'b', 'y', 'z'])
        self.assertEqual([v for v in x.values()], [0, -1, 1, 2])

    def test_equality(self):
        """Test equality with plain dictionaries, ensuring they act like
        regular dicitonaries.
        """
        x = adict(a=1, b=2)
        y = adict(x=object(), y=object())
        self.assertEqual(
            x == { 'a': 1, 'b': 2 },
            { 'a': 1, 'b': 2 } == { 'a': 1, 'b': 2 },
        )
        self.assertEqual(
            y == { 'x': object(), 'y': object() },
            { 'x':object(), 'y':object() } == { 'x':object(), 'y':object() },
        )

    def test_clear(self):
        """Test clearing, ensuring that it acts as we expect."""
        x = adict(i=1, j=2)
        self.assertEqual(x, { 'i': 1, 'j': 2 })
        x.clear()
        self.assertEqual(x, {})
        self.assertEqual([k for k in x.keys()], [])
        x['a'] = 3
        self.assertEqual(x, { 'a': 3 })
        self.assertEqual([k for k in x.keys()], ['a'])

    def test_key_coersion(self):
        """Test key coersion, ensuring that all dictionary keys
        in an alpha-sorted dictionary are unicode.
        """
        x = adict({ 1: 2, 3: 4 })
        self.assertEqual([k for k in x.keys()], ['1', '3'])
        for key in x.keys():
            self.assertIsInstance(key, six.text_type)

    def test_index(self):
        """Test the index method."""
        x = adict(x=0, y=10, z=20)
        self.assertEqual(x.index('y'), 1)
        with self.assertRaises(ValueError):
            x.index('w')
        x['w'] = 40
        self.assertEqual(x.index('y'), 2)

    def test_keys(self):
        """Test the keys (and iterkeys) method."""
        x = adict(x=0, y=10, z=2)
        keys = x.keys()
        if six.PY3:
            self.assertIsInstance(keys, types.GeneratorType)
        else:
            self.assertNotIsInstance(keys, types.GeneratorType)
            self.assertIsInstance(x.iterkeys(), types.GeneratorType)
        self.assertEqual([k for k in keys], ['x', 'y', 'z'])

    def test_values(self):
        """Test the values (and itervalues) method."""
        x = adict(x=0, y=10, z=2)
        values = x.values()
        if six.PY3:
            self.assertIsInstance(values, types.GeneratorType)
        else:
            self.assertNotIsInstance(values, types.GeneratorType)
            self.assertIsInstance(x.itervalues(), types.GeneratorType)
        self.assertEqual([v for v in values], [0, 10, 2])

    def test_items(self):
        """Test the items (and iteritems) method."""
        x = adict(x=0, y=10, z=2)
        items = x.items()
        if six.PY3:
            self.assertIsInstance(items, types.GeneratorType)
        else:
            self.assertNotIsInstance(items, types.GeneratorType)
            self.assertIsInstance(x.iteritems(), types.GeneratorType)
        self.assertEqual([i for i in items], [('x', 0), ('y', 10), ('z', 2)])

    def test_copy(self):
        """Test copying of the dictionary."""
        x = adict(x=0, y=object())
        y = copy(x)
        self.assertNotEqual(id(x), id(y))
        self.assertEqual(x['y'], y['y'])

    def test_deepcopy(self):
        x = adict(x=0, y=object(), z=adict(foo='bar'))
        y = deepcopy(x)
        self.assertNotEqual(id(x), id(y))
        self.assertNotEqual(x['y'], y['y'])
        self.assertEqual(x['z'], y['z'])
        self.assertNotEqual(id(x['z']), id(y['z']))

    def test_del_after_keys(self):
        """Test that we can delete after generating a key cache."""
        x = adict(a='x', b='y', c='z')
        self.assertEqual([k for k in x], ['a', 'b', 'c'])
        del x['b']
        self.assertEqual([k for k in x], ['a', 'c'])

    def test_pop_without_default(self):
        """Test the `pop` method with no default provided."""
        x = adict(a='x', b='y', c='z')
        self.assertEqual([k for k in x], ['a', 'b', 'c'])
        val = x.pop('b')
        self.assertEqual(val, 'y')
        self.assertEqual([k for k in x], ['a', 'c'])
        with self.assertRaises(KeyError):
            x.pop('d')

    def test_pop_with_default(self):
        """Test the `pop` method with a default provided."""
        x = adict(a='x', b='y', c='z')
        val = x.pop('b', 'w')
        self.assertEqual(val, 'y')
        val = x.pop('d', 'w')
        self.assertEqual(val, 'w')

    def test_repr(self):
        """Test the included __repr__ method."""
        x = adict(a=0, b=1, c=2, x=-1, z=-2)
        if six.PY3:
            output = "{'a': 0, 'b': 1, 'c': 2, 'x': -1, 'z': -2}"
        else:
            output = "{u'a': 0, u'b': 1, u'c': 2, u'x': -1, u'z': -2}"
        self.assertEqual(repr(x), output)

    def test_recursive_repr(self):
        """Test that a recursive repr behaves nicely."""
        x = adict()
        x['y'] = adict()
        x['y']['x'] = x
        if six.PY3:
            output = "{'y': {'x': **RECURSION**}}"
        else:
            output = "{u'y': {u'x': **RECURSION**}}"
        self.assertEqual(repr(x), output)

    def test_plain_code_repr(self):
        """Test a case with a __repr__ method with a code object,
        but which does not support `object_list`.
        """
        class Foo(object):
            def __repr__(self):
                return '<foo>'
        x = adict(foo=Foo())
        if six.PY3:
            output = "{'foo': <foo>}"
        else:
            output = "{u'foo': <foo>}"
        self.assertEqual(repr(x), output)

    def test_py2_non_generators(self):
        """Test that keys, items, and values come back as generators
        in Python 3 and lists in Python 2.
        """
        x = adict(foo='bar', spam='eggs')
        if six.PY3:
            self.assertIsInstance(x.keys(), types.GeneratorType)
            self.assertIsInstance(x.values(), types.GeneratorType)
            self.assertIsInstance(x.items(), types.GeneratorType)
        else:
            self.assertIsInstance(x.keys(), list)
            self.assertIsInstance(x.values(), list)
            self.assertIsInstance(x.items(), list)


class SupportSuite(unittest.TestCase):
    def test_no_default(self):
        """Establish that my NoDefault special object is falsy
        (in case it ever actually matters).
        """
        nd = NoDefault()
        self.assertEqual(bool(nd), False)


if __name__ == '__main__':
    unittest.main()
