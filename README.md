# Inspect API

Inspect API of given libraries and number of times functions called

```shell
usage: inspect.py [-h] [--cache-dir CACHE_DIR] [--output OUTPUT] whitelist

positional arguments:
  whitelist             whitelist filename

optional arguments:
  -h, --help            show this help message and exit
  --cache-dir CACHE_DIR
                        download cache directory
  --output OUTPUT       output filename
```

See `whitelist.ini` for namespaces and libraries that are searched. A
sqlite cache is used to speed up previously inspected files. For
example `namespaces=numpy,scipy.linalg` will record all python
function calls within these namespaces.

## usage

```shell
python inspect.py whitelist.ini
```
    
# Gather Library Dependent Packages

```shell
usage: dependant-packages.py [-h] --api-key API_KEY [--output OUTPUT] libraries

positional arguments:
  libraries          libraries to gather dependants for

optional arguments:
  -h, --help         show this help message and exit
  --api-key API_KEY  api key from libraries.io
  --output OUTPUT    output filename
```

## usage

```shell
python dependant-packages.py --api-key c0c....342 numpy,scipy
```
