import sys
sys.path.insert(0, '.')

import ast
from inspect_api import inspect_file_ast

EXAMPLE_1 = '''
# case 1
import numpy
import numpy as np
from numpy import random
from numpy import random as rnd

numpy.array([1, 2])
np.sum(1, 2)
random.random()
rnd.random()
a = numpy.array([1, 2, 3])
a.sum() # would be tricky to catch
'''

# Import From needed

print(ast.dump(ast.parse(EXAMPLE_1)))
functions = inspect_file_ast(ast.parse(EXAMPLE_1), {'numpy'})

for key, value in functions.items():
    print(key, value['count'])
