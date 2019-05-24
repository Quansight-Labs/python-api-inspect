import re
import ast
import glob
import os
import sys
import argparse
import urllib.request
import urllib.error
import zipfile
import configparser
import collections
import sqlite3
import hashlib
import json


def download_github_repo(owner, repo, ref, cache_dir=None):
    filename = os.path.join(cache_dir, f'{owner}-{repo}-{ref}.zip')
    if not os.path.isfile(filename):
        url = f'https://github.com/{owner}/{repo}/archive/{ref}.zip'
        print(f'downloading: {url}')
        try:
            with urllib.request.urlopen(url) as response:
                with open(filename, 'wb') as f:
                    f.write(response.read())
        except urllib.error.HTTPError:
            print(f'failed to download: {url}')
            return None
    else:
        print(f'cached: {filename:64}')
    return filename


def parse_filename(filename, contents):
    try:
        if filename.endswith('.ipynb'):
            try:
                data = json.loads(contents)
            except json.decoder.JSONDecodeError:
                print(f'error decoding json {filename:64}')
                return None

            if data.get('metadata', {}).get('kernelspec', {}).get('language') != 'python':
                print(f'unable to parse non python notebook {filename:64}')
                return None

            if not 'cells' in data:
                print(f'notebook does not have any cells {filename:64}')
                return None

            source_cells = []
            for i, cell in enumerate(data['cells']):
                if cell['cell_type'] != 'code':
                    continue

                source = re.sub('%{1,2}.*', '', '\n'.join(cell['source']))
                try:
                    ast.parse(source)
                    source_cells.append(source)
                except SyntaxError:
                    print(f'{filename:64} notebook cell {i} failed to parse')
            return ast.parse('\n'.join(source_cells))
        elif filename.endswith('.py'):
            return ast.parse(contents)
        else:
            raise ValueError(f'unknown how to handle extension {filename[-10:]}')
    except SyntaxError:
        print(f'syntax error parsing: {filename:64}')


def inspect_file_ast(file_ast):
    """Record function calls and counts for all absolute namespaces

    """
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
                if name.asname is None:
                    self.imports.add(namespace)
                else:
                    self.imports.add(namespace)
                    self.aliases[name.asname or name.name] = namespace

    class APIVisitor(ast.NodeVisitor):
        def __init__(self, aliases, imports):
            self.aliases = aliases
            self.imports = imports
            self.api = collections.defaultdict(lambda:
                collections.defaultdict(lambda: {
                    'count': 0,
                    'n_args': collections.defaultdict(int),
                    'kwargs': collections.defaultdict(int),
                }))

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

            for i in range(len(path)):
                if tuple(path[:i+1]) in self.imports:
                    base_namespace = path[0]

                    self.api[base_namespace][tuple(path)]['count'] += 1
                    self.api[base_namespace][tuple(path)]['n_args'][num_args] += 1
                    for keyword in keywords:
                        self.api[base_namespace][tuple(path)]['kwargs'][keyword] += 1
                    break

    import_visitor = ImportVisitor()
    import_visitor.visit(file_ast)
    api_visitor = APIVisitor(imports=import_visitor.imports, aliases=import_visitor.aliases)
    api_visitor.visit(file_ast)
    return api_visitor.api


# def output_api_counts(api_counts, filename):
#     print(f'writing {len(api_counts)} function calls to {filename:64}')
#     with open(filename, 'w') as f:
#         f.write('function, function_count, top_num_args, top_num_args_count, top_keyword, top_keyword_count\n')
#         for key, value in sorted(api_counts.items(), key=lambda item: item[1]['count']):
#             sorted_num_args = [(num_args, count) for num_args, count in sorted(api_counts[key]['n_args'].items(), key=lambda item: item[1], reverse=True)]

#             sorted_keywords = [(keyword, count) for keyword, count in sorted(api_counts[key]['kwargs'].items(), key=lambda item: item[1], reverse=True)] + [('', '')]
#             f.write(f'{key}, {value["count"]}, {sorted_num_args[0][0]}, {sorted_num_args[0][1]}, {sorted_keywords[0][0]}, {sorted_keywords[0][1]}\n')


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('whitelist', help="whitelist filename")
    parser.add_argument('--cache-dir', default=os.path.expanduser('~/.cache/python-inspect-ast/'), help='download cache directory')
    parser.add_argument('--exclude-dirs', help='directories to exclude from statistics')
    parser.add_argument('--include-dirs', help='directories to include in statistics')
    parser.add_argument('--output', default='summary.csv', help="output filename")
    parser.add_argument('--extensions', default='py', help="filename extensions to parse")
    parser.add_argument('--limit', default=None, help='limit number of packages to parse for statistics')
    args = parser.parse_args()

    return args


def _create_database(connection):
    with connection:
        connection.execute('''
CREATE TABLE IF NOT EXISTS FileStats (
   project TEXT,
   filename TEXT,
   filename_hash TEXT,
   namespace TEXT,
   stats BLOB,

   PRIMARY KEY (filename_hash, namespace)
)
''')


def _database_check_file_previously_parsed(connection, filename_hash):
    with connection:
        result = connection.execute('SELECT filename_hash FROM FileStats WHERE filename_hash = ?', (filename_hash,)).fetchone()
    return result is not None


def _database_insert_file_namespaces(connection, project_name, filename, filename_hash, api_stats):
    for namespace in api_stats:
        stats = {'.'.join(key): value for key, value in api_stats[namespace].items()}
        with connection:
            result = connection.execute('''
INSERT INTO FileStats (project, filename, filename_hash, namespace, stats)
VALUES (?, ?, ?, ?, ?)
''', (project_name, filename, filename_hash, namespace, json.dumps(stats)))


def main():
    args = cli(sys.argv)

    # ensure cache directory exists
    os.makedirs(args.cache_dir, exist_ok=True)

    connection = sqlite3.connect(os.path.join(args.cache_dir, 'inspect.sqlite'))
    _create_database(connection)

    whitelist = configparser.ConfigParser()
    whitelist.read(args.whitelist)

    # determine filename extensions to use (e.g. .py, .ipynb)
    filename_extensions = tuple(set('.' + _ for _ in args.extensions.split(',')))

    # determine filenames to exclude/include based on directories in path
    exclude_dirs = set(args.exclude_dirs.split(',')) if args.exclude_dirs else set()
    include_dirs = set(args.include_dirs.split(',')) if args.include_dirs else set()

    # limit number of packages parsed
    packages = list(whitelist['packages'])
    if args.limit:
        packages = packages[:int(args.limit)]

    for project_name in packages:
        site, owner, repo, ref = whitelist['packages'][project_name].split('/')
        if site == 'github':
            zip_filename = download_github_repo(owner, repo, ref, args.cache_dir)
            if zip_filename is None:
                continue # failed to download
        else:
            raise NotImplmentedError(f'site {site} not implemented')

        try:
            with zipfile.ZipFile(zip_filename) as f_zip:
                filenames = [_ for _ in f_zip.namelist() if _.endswith(filename_extensions)]
                for filename in filenames:
                    if include_dirs and (set(filename.split(os.sep)) & include_dirs) == set():
                        continue

                    if (set(filename.split(os.sep)) & exclude_dirs) != set():
                        continue

                    print(f'... {filename[:64]}')
                    with f_zip.open(filename) as f:
                        contents = f.read()
                    contents_hash = hashlib.sha256(contents).hexdigest()

                    if not _database_check_file_previously_parsed(connection, contents_hash):
                        file_ast = parse_filename(filename, contents)

                        if file_ast is None:
                            continue # parsing error/syntax error

                        api_stats = inspect_file_ast(file_ast)
                        _database_insert_file_namespaces(connection, project_name, filename, contents_hash, api_stats)
        except zipfile.BadZipFile:
            continue


if __name__ == "__main__":
    main()
