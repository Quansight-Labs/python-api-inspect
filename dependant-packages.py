import urllib.request
import json
import os
import re
import itertools
import sys
import argparse


def query_dependant_libraries(platform, name, page, apikey):
    print(f'... libraries.io dependants platform={platform:4} name={name:16} page={page:3}')
    url = f'https://libraries.io/api/{platform}/{name}/dependents?api_key={apikey}&page={page}'
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    packages = {}
    for library in data:
        match = re.search('https://github\.com/(.*)/(.*)', library['repository_url'] or '')
        if match:
            owner, repo = match.groups()
            packages[library['name'].lower()] = f'github/{owner}/{repo}/master'
    return packages


def query_dependant_repository_libraries(platform, name, page, apikey):
    print(f'... libraries.io dependant_repositories platform={platform:4} name={name:16} page={page:3}')
    url = f'https://libraries.io/api/{platform}/{name}/dependent_repositories?api_key={apikey}&page={page}'
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    packages = {}
    for library in data:
        if library['host_type'] != 'GitHub':
            continue
        match = re.search('(.*)/(.*)', library['full_name'] or '')
        if match:
            owner, repo = match.groups()
            packages[repo.lower()] = f'github/{owner}/{repo}/master'
    return packages


def gather_dependant_libraries(name, apikey, include_dependant_repos):
    packages = {}
    include_dependant_libraries = True
    for page in itertools.count(1):
        filename = f'/tmp/depend{"-repo" if include_dependant_repos else ""}-{name}-{page}.json'
        if not os.path.isfile(filename):
            libraries = {}
            if include_dependant_libraries:
                libraries.update(query_dependant_libraries('pypi', name, page, apikey))
                if libraries == {}:
                    include_dependant_libraries = False
            if include_dependant_repos:
                libraries.update(query_dependant_repository_libraries('pypi', name, page, apikey))

            if libraries == {}:
                break
            with open(filename, 'w') as f:
                json.dump(libraries, f)
        else:
            with open(filename) as f:
                libraries = json.load(f)
        packages.update(libraries)
    return packages


def print_libraries(libraries, namespaces, output_filename):
    with open(output_filename, 'w') as f:
        f.write(f'''[config]
namespaces={namespaces}

[packages]
# site/owner/repo/ref
''')
        for key, value in libraries.items():
            f.write(f'{key}={value}\n')


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('libraries', help="libraries to gather dependants for")
    parser.add_argument('--include-dependant-repos', action="store_true", default=False, help="include libraries.io dependant repositories (warning for popular packages this can be huge)")
    parser.add_argument('--api-key', help='api key from libraries.io', required=True)
    parser.add_argument('--namespaces', help='namespaces to look for', required=True)
    parser.add_argument('--output', default='whitelist.ini', help="output filename")
    args = parser.parse_args()
    return args


def main():
    args = cli(sys.argv)
    libraries = {}
    for package in args.libraries.split(','):
        libraries.update(gather_dependant_libraries(package, args.api_key, args.include_dependant_repos))

    print_libraries(libraries, args.namespaces, args.output)


if __name__ == '__main__':
    main()
