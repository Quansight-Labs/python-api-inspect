# Inspect API

Inspect API of given libraries and number of times functions called

```shell
usage: inspect.py [-h] [--cache-dir CACHE_DIR] [--exclude-dirs EXCLUDE_DIRS]
                  [--include-dirs INCLUDE_DIRS] [--output OUTPUT]
                  whitelist

positional arguments:
  whitelist             whitelist filename

optional arguments:
  -h, --help            show this help message and exit
  --cache-dir CACHE_DIR
                        download cache directory
  --exclude-dirs EXCLUDE_DIRS
                        directories to exclude from statistics
  --include-dirs INCLUDE_DIRS
                        directories to include in statistics
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
usage: dependant-packages.py [-h] [--include-dependant-repos] --api-key API_KEY
                             --namespaces NAMESPACES [--output OUTPUT]
                             libraries

positional arguments:
  libraries             libraries to gather dependants for

optional arguments:
  -h, --help            show this help message and exit
  --include-dependant-repos
                        include libraries.io dependant repositories (warning for
                        popular packages this can be huge)
  --api-key API_KEY     api key from libraries.io
  --namespaces NAMESPACES
                        namespaces to look for
  --output OUTPUT       output filename
```

## usage

```shell
python dependant-packages.py --api-key c0c....342 numpy,scipy
```


# Examples

Get libraries that depend on `numpy`.

```shell
python dependant-packages.py --api-key c0....42 --namespaces=numpy --output data/numpy-whitelist.ini numpy,scipy 
```

Get numpy api usage

```shell
python inspect.py data/numpy-whitelist.ini --output data/numpy-summary.csv
```

Get numpy api usage (exclude directories `test, tests, site-packages`)

```shell
python inspect.py data/numpy-whitelist.ini --output data/numpy-summary-without-tests.csv --exclude-dirs test,tests,site-packages
```

Get scipy api usage

```shell
python dependant-packages.py --api-key c0....42 --namespaces=scipy --output data/numpy-whitelist.ini numpy,scipy 
python inspect.py data/scipy-whitelist.ini --output data/scipy-summary.csv
```

Get scipy api usage (exclude directories `test, tests, site-packages`)

```shell
python inspect.py data/scipy-whitelist.ini --output data/scipy-summary-without-tests.csv --exclude-dirs test,tests,site-packages
```

Get pyarrow api usage. We `--include-dependant-repos` becuase pyarrow on libraries.io did not have dependant libraries but had 208 "dependant repos". By contrast numpy has `68k` so we did not use this for numpy/scipy.

```shell
python dependant-packages.py --api-key c0....42 --include-dependant-repos --namespaces=pyarrow --output data/pyarrow-whitelist.ini pyarrow
python inspect.py data/pyarrow-whitelist.ini --output data/pyarrow-summary.csv
```

```shell
python inspect.py data/pyarrow-whitelist.ini --output data/pyarrow-summary-without-tests.csv --exclude-dirs test,tests,site-packages
```

# Tests

Tests to demo what `inspect.py` is able to parse from file source.
