import ast
import glob
import os
import sys
import argparse
import urllib.request
import zipfile
import configparser


def download_github_repo(owner, repo, ref, cache_dir=None):
    cache_dir = cache_dir or os.path.expanduser('~/.cache/python-inspect-ast/')
    os.makedirs(cache_dir, exist_ok=True)

    filename = os.path.join(cache_dir, f'{owner}-{repo}-{ref}.zip')
    if not os.path.isfile(filename):
        with urllib.request.urlopen(f'https://github.com/{owner}/{repo}/archive/{ref}.zip') as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
    return filename


def find_python_file_paths(zip_filename):
    with zipfile.ZipFile(zip_filename) as f_zip:
        return [_ for _ in f_zip.namelist() if _.endswith('.py')]


def parse_python_filename(zip_filename, python_filename):
    with zipfile.ZipFile(zip_filename) as f_zip:
        with f_zip.open(python_filename) as f:
            return ast.parse(f.read())


def inspect_file_ast(file_ast, namespaces):
    """Record function calls and counts within namespaces

    """
    class NamespaceVisit(ast.NodeVisitor):
        def visit_Import(self, node):
            for name in node.names:
                if name.name == 'numpy':
                    print('numpy', name.asname)

    vistor = NamespaceVisit()
    vistor.visit(file_ast)


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('whitelist', help="whitelist filename")
    args = parser.parse_args()
    return args


def main():
    args = cli(sys.argv)

    whitelist = configparser.ConfigParser()
    whitelist.read(args.whitelist)
    for project_name in whitelist.keys():
        if project_name == 'DEFAULT':
            continue
        project = whitelist[project_name]
        print(project['owner'], project['repo'], project['ref'])
        zip_filename = download_github_repo(project['owner'], project['repo'], project['ref'])
        python_files = find_python_file_paths(zip_filename)
        for filename in python_files:
            file_ast = parse_python_filename(zip_filename, filename)
            inspect_file_ast(file_ast, {'numpy'})


if __name__ == "__main__":
    main()
