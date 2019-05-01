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
        with urllib.request.urlopen(url) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
    return filename


def inspect_file_ast(file_ast, namespaces):
    """Record function calls and counts within namespaces

    namespaces is set of strings
    """
    namespaces = set(tuple(_.split('.')) for _ in namespaces)

    class ImportVisit(ast.NodeVisitor):
        def __init__(self, namespaces):
            self.aliases = {}
            self.namespaces = namespaces

        def visit_Import(self, node):
            for name in node.names:
                namespace = tuple(name.name.split('.'))
                for i in range(len(namespace)+1):
                    if namespace[:i+1] in self.namespaces:
                        self.aliases[name.asname] = namespace

        def visit_ImportFrom(self, node):
            if node.module is None: # relative import
                return

            partial_namespace = tuple(node.module.split('.'))
            for name in node.names:
                namespace = partial_namespace + (name.name,)
                for i in range(len(namespace)+1):
                    if namespace[:i+1] in self.namespaces:
                        self.aliases[name.asname or name.name] = namespace

    class APIVisitor(ast.NodeVisitor):
        def __init__(self, aliases, namespaces):
            self.aliases = aliases
            self.namespaces = namespaces
            self.api = collections.defaultdict(lambda: {
                'count': 0,
                'n_args': collections.defaultdict(int),
                'kwargs': collections.defaultdict(int),
            })

        def visit_Call(self, node):
            if not isinstance(node.func, (ast.Attribute, ast.Name)):
                return

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
                if tuple(path[:i+1]) in self.namespaces:
                    self.api[tuple(path)]['count'] += 1
                    self.api[tuple(path)]['n_args'][num_args] += 1
                    for keyword in keywords:
                        self.api[tuple(path)]['kwargs'][keyword] += 1
                    break

    import_visitor = ImportVisit(namespaces)
    import_visitor.visit(file_ast)
    api_visitor = APIVisitor(import_visitor.aliases, namespaces)
    api_visitor.visit(file_ast)
    return api_visitor.api


def output_api_counts(api_counts, filename):
    with open(filename, 'w') as f:
        f.write('function, function_count, top_num_args, top_num_args_count, top_keyword, top_keyword_count\n')
        for key, value in sorted(api_counts.items(), key=lambda item: item[1]['count']):
            sorted_num_args = [(num_args, count) for num_args, count in sorted(api_counts[key]['n_args'].items(), key=lambda item: item[1], reverse=True)]

            sorted_keywords = [(keyword, count) for keyword, count in sorted(api_counts[key]['kwargs'].items(), key=lambda item: item[1], reverse=True)] + [('', '')]
            f.write(f'{key}, {value["count"]}, {sorted_num_args[0][0]}, {sorted_num_args[0][1]}, {sorted_keywords[0][0]}, {sorted_keywords[0][1]}\n')


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('whitelist', help="whitelist filename")
    parser.add_argument('--cache-dir', default=os.path.expanduser('~/.cache/python-inspect-ast/'), help='download cache directory')
    parser.add_argument('--exclude-dirs', help='directories to exclude from statistics')
    parser.add_argument('--include-dirs', help='directories to include in statistics')
    parser.add_argument('--output', default='summary.csv', help="output filename")
    args = parser.parse_args()
    return args


def main():
    args = cli(sys.argv)
    os.makedirs(args.cache_dir, exist_ok=True)

    connection = sqlite3.connect(os.path.join(args.cache_dir, 'inspect.sqlite'))
    with connection:
        connection.execute('''
CREATE TABLE IF NOT EXISTS FileStats (
   file_hash TEXT,
   namespaces TEXT,
   stats BLOB,

   PRIMARY KEY (file_hash, namespaces)
)
''')

    whitelist = configparser.ConfigParser()
    whitelist.read(args.whitelist)
    total_api_counts = collections.defaultdict(lambda: {
        'count': 0,
        'n_args': collections.defaultdict(int),
        'kwargs': collections.defaultdict(int),
    })

    namespaces = set(whitelist['config']['namespaces'].split(','))
    namespaces_string = ','.join(sorted(namespaces))

    exclude_dirs = set(args.exclude_dirs.split(',')) if args.exclude_dirs else set()
    include_dirs = set(args.include_dirs.split(',')) if args.include_dirs else set()

    for project_name in whitelist['packages']:
        site, owner, repo, ref = whitelist['packages'][project_name].split('/')
        if site == 'github':
            try:
                zip_filename = download_github_repo(owner, repo, ref, args.cache_dir)
            except urllib.error.HTTPError:
                continue
        else:
            raise ValueError(f'site {site} not implemented')

        try:
            with zipfile.ZipFile(zip_filename) as f_zip:
                for filename in [_ for _ in f_zip.namelist() if _.endswith('.py')]:
                    if include_dirs and (set(filename.split(os.sep)) & include_dirs) == set():
                        continue

                    if (set(filename.split(os.sep)) & exclude_dirs) != set():
                        continue

                    print('...', filename[:64])
                    with f_zip.open(filename) as f:
                        contents = f.read()
                    contents_hash = hashlib.sha256(contents).hexdigest()

                    with connection:
                        result = connection.execute('SELECT stats FROM FileStats WHERE file_hash = ? AND namespaces = ?', (contents_hash, namespaces_string)).fetchone()

                    if result:
                        api_counts = json.loads(result[0])
                    else:
                        try:
                            file_ast = ast.parse(contents)
                        except SyntaxError:
                            continue
                        api_counts = inspect_file_ast(file_ast, namespaces)
                        api_counts = {'.'.join(key): value for key, value in api_counts.items()}
                        with connection:
                            connection.execute('INSERT INTO FileStats (file_hash, namespaces, stats) VALUES (?, ?, ?)', (contents_hash, namespaces_string, json.dumps(api_counts)))

                    for key, value in api_counts.items():
                        total_api_counts[key]['count'] += value['count']
                        for num_args, count in value['n_args'].items():
                            total_api_counts[key]['n_args'][num_args] += count
                        for keyword, count in value['kwargs'].items():
                            total_api_counts[key]['kwargs'][keyword] += count
        except zipfile.BadZipFile:
            continue

    output_api_counts(total_api_counts, args.output)


if __name__ == "__main__":
    main()
