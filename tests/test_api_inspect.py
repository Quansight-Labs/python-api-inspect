import ast

import pytest

from inspect_api.inspect import inspect_file_ast, inspect_file_contents

def test_example_functions():
    source = '''
import numpy
import numpy as np
from numpy import random
from numpy import random as rnd

numpy.array([1, 2])
np.sum(1, 2, axis=0)
random.random(np.array([1, 2, 3]).shape)
rnd.random()
a = numpy.array([1, 2, 3])

## will not catch anything this sadly...
a.sum()
'''
    result = inspect_file_ast(ast.parse(source))

    expected_result = {
        'def_class': {
            'count': 0,
            'n_attr': {},
            'n_func': {},
            'dunder': {},
            'inherit': {}
        },
        'def_function': {'count': 0, 'n_args': {}},
        'attribute': {},
        'function': {
            'numpy': {
                ('numpy', 'sum'): {
                    'count': 1,
                    'd_count': 0,
                    'n_args': {3: 1},
                    'kwargs': {'axis': 1}},
                ('numpy', 'random', 'random'): {
                    'count': 2,
                    'd_count': 0,
                    'n_args': {0: 1, 1: 1},
                    'kwargs': {}},
                ('numpy', 'array'): {
                    'count': 3,
                    'd_count': 0,
                    'n_args': {1: 3},
                    'kwargs': {}}
            }
        }
    }

    import pprint
    pprint.pprint(dict(result['function']))

    assert result == expected_result


def test_example_attribute():
    source = '''
import numpy
import numpy as np
from numpy import random
from numpy import random as rnd

np.asdf
numpy.array(np.asdf)
random.random
rnd.random
'''

    result = inspect_file_ast(ast.parse(source))

    expected_result = {
        'def_class': {
            'count': 0,
            'n_attr': {},
            'n_func': {},
            'dunder': {},
            'inherit': {}
        },
        'def_function': {'count': 0, 'n_args': {}},
        'function': {
            'numpy': {
                ('numpy', 'array'): {
                    'count': 1,
                    'd_count': 0,
                    'n_args': {1: 1},
                    'kwargs': {}
                }
            }
        },
        'attribute': {
            'numpy': {
                ('numpy', 'asdf'): {'count': 2, 'd_count': 0},
                ('numpy', 'random', 'random'): {'count': 2, 'd_count': 0},
            }
        }
    }

    assert result == expected_result


def test_example_decorator():
    source = '''
import contextlib
from contextlib import contextmanager
from contextlib import contextmanager as cxtm

@contextmanager
def foo():
    pass

@contextlib.contextmanager
def bar():
    pass

cxtm

contextlib.contextmanager()

@cxtm(a=2)
def biz():
    pass
'''
    result = inspect_file_ast(ast.parse(source))

    expected_result = {
        'def_class': {
            'count': 0,
            'n_attr': {},
            'n_func': {},
            'dunder': {},
            'inherit': {}
        },
        'def_function': {
            'count': 3,
            'n_args': {0: 3},
        },
        'function': {
            'contextlib': {
                ('contextlib', 'contextmanager'): {
                    'count': 2,
                    'd_count': 1,
                    'kwargs': {'a': 1},
                    'n_args': {0: 1, 1: 1}
                }
            }
        },
        'attribute': {
            'contextlib': {
                ('contextlib', 'contextmanager'): {'count': 3, 'd_count': 2}
            }
        }
    }

    import pprint
    pprint.pprint(result)

    assert result == expected_result


def test_example_def_class():
    source = '''
import numpy as np
import numpy

def qwerqwer(a, b):
    pass

class Foo(np.array, asdf):
    qwer = 1

    def __init__(self, a, b):
        pass

    def __getattr__(self):
        pass

    def foo():
        pass

class Bar(numpy.matrix):
    def asdf(self):
        pass
    '''

    expected_result = {
        'function': {},
        'attribute': {
            'numpy': {
                ('numpy', 'array'): {'count': 1, 'd_count': 0},
                ('numpy', 'matrix'): {'count': 1, 'd_count': 0},
            }
        },
        'def_function': {
            'count': 5,
            'n_args': {3: 1, 2: 1, 1: 2, 0: 1}
        },
        'def_class': {
            'count': 2,
            'n_func': {3: 1, 1: 1},
            'n_attr': {1: 1, 0: 1},
            'dunder': {'__init__': 1, '__getattr__': 1},
            'inherit': {('numpy', 'matrix'): 1, ('numpy', 'array'): 1},
        }
    }

    result = inspect_file_ast(ast.parse(source))

    import pprint
    pprint.pprint(result)

    assert result == expected_result


def test_example_contents_python():
    source = b'''import numpy as np

a = np.array()
   # hello world
a.sum()
'''

    result = inspect_file_contents('example.py', source)

    expected_result = {
        'contents': {
            'num_newlines': 6,
            'num_whitespace_lines': 2,
            'num_comment_lines': 1,
            'min_line_length': 7,
            'max_line_length': 18,
            'avg_line_length': 9.0,
        }
    }

    assert result == expected_result
