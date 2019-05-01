import urllib.request
import json
import os
import re
import itertools
import sys
import argparse


def query_dependant_libraries(platform, name, page, apikey):
    url = f'https://libraries.io/api/{platform}/{name}/dependents?api_key={apikey}&page={page}'
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def gather_dependant_libraries(name, apikey):
    packages = {}
    for page in itertools.count(1):
        filename = f'/tmp/depend-{name}-{page}.json'
        if not os.path.isfile(filename):
            dependant = query_dependant_libraries('pypi', name, page, apikey)
            if dependant == []:
                break
            with open(filename, 'w') as f:
                json.dump(dependant, f)
        else:
            with open(filename) as f:
                dependant = json.load(f)

        for library in dependant:
            match = re.search('https://github\.com/(.*)/(.*)', library['repository_url'] or '')
            if match:
                owner, repo = match.groups()
                packages[library['name'].lower()] = f'github/{owner}/{repo}/master'
    return packages


def print_libraries(libraries, output_filename):
    with open(output_filename, 'w') as f:
        f.write('''[config]
namespaces=numpy,scipy

[packages]
# site/owner/repo/ref
''')
        for key, value in libraries.items():
            f.write(f'{key}={value}\n')


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('libraries', help="libraries to gather dependants for")
    parser.add_argument('--api-key', help='api key from libraries.io', required=True)
    parser.add_argument('--output', default='whitelist.ini', help="output filename")
    args = parser.parse_args()
    return args


def main():
    args = cli(sys.argv)
    libraries = {}
    for package in args.libraries.split(','):
        libraries.update(gather_dependant_libraries(package, args.api_key))

    print_libraries(libraries, args.output)


if __name__ == '__main__':
    main()
