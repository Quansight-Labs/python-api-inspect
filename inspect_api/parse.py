import os
import json
import zipfile
import hashlib
import ast
import re

from .download import download_github_repo
from .db import create_connection, check_file_previously_parsed, insert_file_stats
from .inspect import inspect_file_ast, inspect_file_contents


def parse_filename(filename, contents):
    if filename.endswith('.ipynb'):
        try:
            data = json.loads(contents)
        except Exception:
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

            source = re.sub('%{1,2}.*', '', ''.join(cell['source']))
            try:
                ast.parse(source)
                source_cells.append(source)
            except Exception:
                print(f'{filename:64} notebook cell {i} failed to parse')
        contents = '\n'.join(source_cells)
    elif not filename.endswith('.py'):
        raise ValueError(f'unknown how to handle extension {filename[-10:]}')

    try:
        return ast.parse(contents)
    except Exception:
        print(f'syntax error parsing: {filename:64}')


def parse_project(db_filename, project, site, owner, repo, ref, filename_extensions, include_directories, exclude_directories, cache_directory):
    connection = create_connection(db_filename)

    if site == 'github':
        zip_filename = download_github_repo(owner, repo, ref, cache_directory)
        if zip_filename is None:
            return # failed to download
    else:
        raise NotImplmentedError(f'site {site} not implemented')

    batch_stats = {}

    try:
        with zipfile.ZipFile(zip_filename) as f_zip:
            filenames = [_ for _ in f_zip.namelist() if _.endswith(filename_extensions)]
            for filename in filenames:
                if include_directories and (set(filename.split(os.sep)) & include_directories) == set():
                    continue

                if (set(filename.split(os.sep)) & exclude_directories) != set():
                    continue

                with f_zip.open(filename) as f:
                    contents = f.read()
                filename_hash = hashlib.sha256(contents).hexdigest()

                if check_file_previously_parsed(connection, project, filename, filename_hash):
                    pass
                    # print(f'CACHED {filename[:64]}')
                else:
                    # print(f'... {filename[:64]}')
                    file_ast = parse_filename(filename, contents)

                    if file_ast is None:
                        continue # parsing error/syntax error

                    stats = {}
                    stats.update(inspect_file_contents(filename, contents))
                    stats.update(inspect_file_ast(file_ast))
                    batch_stats[(project, filename, filename_hash)] = stats
    except zipfile.BadZipFile:
        return # invalid zipfile

    if batch_stats:
        insert_file_stats(connection, batch_stats)
