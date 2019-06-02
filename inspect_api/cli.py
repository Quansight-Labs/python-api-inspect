import os
import configparser
import sys
import argparse
import multiprocessing

from .parse import parse_project
from .whitelist import create_whitelist


def cli(arguments):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser_inspect(subparsers)
    subparser_whitelist(subparsers)

    args = parser.parse_args()
    args.func(args)


def subparser_inspect(subparser):
    parser = subparser.add_parser('inspect', help='run filename inspection')
    parser.set_defaults(func=handle_subcommand_inspect)
    parser.add_argument('whitelist', help="whitelist filename", nargs='+')
    parser.add_argument('--cache-dir', default=os.path.expanduser('~/.cache/python-inspect-ast/'), help='download cache directory')
    parser.add_argument('--exclude-dirs', help='directories to exclude from statistics')
    parser.add_argument('--include-dirs', help='directories to include in statistics')
    parser.add_argument('--output', default='inspect.sqlite', help="output database filename")
    parser.add_argument('--extensions', default='py', help="filename extensions to parse")
    parser.add_argument('--limit', default=None, help='limit number of packages to parse for statistics')
    parser.add_argument('--workers', default=1, type=int, help='number of workers')


def handle_subcommand_inspect(args):
    # ensure cache directory exists
    os.makedirs(args.cache_dir, exist_ok=True)

    # determine filename extensions to use (e.g. .py, .ipynb)
    filename_extensions = tuple(set('.' + _ for _ in args.extensions.split(',')))

    # determine filenames to exclude/include based on directories in path
    exclude_directories = set(args.exclude_dirs.split(',')) if args.exclude_dirs else set()
    include_directories = set(args.include_dirs.split(',')) if args.include_dirs else set()

    for whitelist_filename in args.whitelist:
        whitelist = configparser.ConfigParser()
        whitelist.read(whitelist_filename)

        # limit number of packages parsed
        packages = list(whitelist['packages'])
        if args.limit:
            packages = packages[:int(args.limit)]

        pool_args = []
        for project_name in packages:
            site, owner, repo, ref = whitelist['packages'][project_name].split('/')
            pool_args.append((os.path.join(args.output), project_name,
                         site, owner, repo, ref,
                         filename_extensions,
                         exclude_directories, include_directories,
                         args.cache_dir))

        with multiprocessing.Pool(args.workers) as pool:
            pool.starmap(parse_project, pool_args)


def subparser_whitelist(subparser):
    parser = subparser.add_parser('whitelist', help='create whitelists')
    parser.set_defaults(func=handle_subcommand_whitelist)
    parser.add_argument('projects', help="whitelist pypi projects", nargs='+')
    parser.add_argument('--librariesio-db', required=True, help='path to libraries.io sqlite database created with scripts/librariesio.sh')
    parser.add_argument('--output-dir', help='directory to write whitelist files')


def handle_subcommand_whitelist(args):
    database_filename = os.path.expanduser(args.librariesio_db)
    whitelist_directory = os.path.expanduser(args.output_dir)

    os.makedirs(whitelist_directory, exist_ok=True)

    for project in args.projects:
        create_whitelist(database_filename, project, os.path.join(whitelist_directory, f'{project}-whitelist.ini'))
