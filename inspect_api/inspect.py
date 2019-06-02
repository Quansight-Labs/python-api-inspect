import ast
import collections
import sys

# some parsings result require more recursion
# pyinstaller is one example
# https://github.com/pyinstaller/pyinstaller/issues/2919
sys.setrecursionlimit(5000)

# https://docs.python.org/3/library/functions.html
BUILTIN_FUNCTIONS = {
    'abs', 'delattr', 'hash', 'memoryview', 'set',
    'all', 'dict', 'help', 'min', 'setattr',
    'any', 'dir', 'hex', 'next', 'slice',
    'ascii', 'divmod', 'id', 'object', 'sorted',
    'bin', 'enumerate', 'input', 'oct', 'staticmethod'
    'bool', 'eval', 'int', 'open', 'str',
    'breakpoint', 'exec', 'isinstance', 'ord', 'sum',
    'bytearray', 'filter', 'issubclass', 'pow', 'super',
    'bytes', 'float', 'iter', 'print', 'tuple',
    'callable', 'format', 'len', 'property', 'type',
    'chr', 'frozenset', 'list', 'range', 'vars',
    'classmethod', 'getattr', 'locals', 'repr', 'zip',
    'compile', 'globals', 'map', 'reversed', '__import__',
    'complex', 'hasattr', 'max', 'round',
}


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
        self.aliases = {}

    def visit_Import(self, node):
        for name in node.names:
            namespace = tuple(name.name.split('.'))
            if name.asname is None:
                self.imports.add(namespace)
            else:
                self.imports.add(namespace)
                self.aliases[name.asname] = namespace

    def visit_ImportFrom(self, node):
        if node.module is None: # relative import
            return

        partial_namespace = tuple(node.module.split('.'))
        for name in node.names:
            namespace = partial_namespace + (name.name,)
            self.imports.add(namespace)
            self.aliases[name.asname or name.name] = namespace


class APIVisitor(ast.NodeVisitor):
    def __init__(self, aliases, imports):
        self.aliases = aliases
        self.imports = imports
        self.attribute_stats = collections.defaultdict(
            lambda: collections.defaultdict(int))
        self.function_stats = collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: {
                    'count': 0,
                    'n_args': collections.defaultdict(int),
                    'kwargs': collections.defaultdict(int),
                }))

    def add_function_stats(self, namespace, path, num_args, keywords):
        self.function_stats[namespace][path]['count'] += 1
        self.function_stats[namespace][path]['n_args'][num_args] += 1
        for keyword in keywords:
            self.function_stats[namespace][path]['kwargs'][keyword] += 1

    def visit_Attribute(self, node):
        _node = node
        path = []

        while isinstance(_node, ast.Attribute):
            path.insert(0, _node.attr)
            _node = _node.value

        if isinstance(_node, ast.Name):
            if _node.id in self.aliases:
                path = list(self.aliases[_node.id]) + path
            else:
                path.insert(0, _node.id)
        else:
            # example: numpy.array().shape
            # we don't capture shape as an attribute and pass
            # further inspection down
            self.visit(_node)
            return

        for i in range(len(path)):
            if tuple(path[:i+1]) in self.imports:
                self.attribute_stats[path[0]][tuple(path)] += 1
                break

    def visit_Call(self, node):
        if not isinstance(node.func, (ast.Attribute, ast.Name)):
            return

        # functions statistics
        num_args = len(node.args) + len(node.keywords)
        keywords = {k.arg for k in node.keywords}

        _node = node.func
        path = []

        while isinstance(_node, ast.Attribute):
            path.insert(0, _node.attr)
            _node = _node.value

        if isinstance(_node, ast.Name):
            if _node.id in self.aliases:
                path = list(self.aliases[_node.id]) + path
            else:
                path.insert(0, _node.id)

        if len(path) == 1 and path[0] in BUILTIN_FUNCTIONS:
            base_namespace = '__builtins__'
            self.add_function_stats('__builtins__', tuple(path), num_args, keywords)
        else:
            for i in range(len(path)):
                if tuple(path[:i+1]) in self.imports:
                    self.add_function_stats(path[0], tuple(path), num_args, keywords)
                    break

        for arg in node.args:
            self.visit(arg)



def inspect_file_contents(filename, contents):
    if filename.endswith('.py'):
        num_newlines = contents.count(b'\n')
        stats = {'contents': {'newlines': num_newlines}}
    elif filename.endswith('.ipynb'):
        stats = {'contents': {}}
    return stats


def inspect_file_ast(file_ast):
    """Record function calls and counts for all absolute namespaces

    """
    import_visitor = ImportVisitor()
    import_visitor.visit(file_ast)

    api_visitor = APIVisitor(
        imports=import_visitor.imports,
        aliases=import_visitor.aliases)
    api_visitor.visit(file_ast)

    return {
        'function': api_visitor.function_stats,
        'attribute': api_visitor.attribute_stats
    }
