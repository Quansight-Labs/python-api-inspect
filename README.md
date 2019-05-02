# API Usage Statistics

Currently inspected libraries:

<table>
<tr>
  <th>Library</th>
  <th>Whitelist</th>
  <th>Summary</th>
  <th>Summary without tests</th>
</tr>
<tr>
  <td>numpy</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/numpy-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/numpy-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/numpy-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>scipy</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/scipy-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/scipy-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/scipy-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>pandas</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pandas-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pandas-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pandas-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>sympy</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/sympy-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/sympy-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/sympy-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>pytorch</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pytorch-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pytorch-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pytorch-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>tensorflow</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/tensorflow-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/tensorflow-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/tensorflow-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>pyarrow</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pyarrow-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pyarrow-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/pyarrow-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>dask</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/dask-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/dask-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/dask-summary-without-tests.csv">csv</a></td>
</tr>
<tr>
  <td>matplotlib</td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/matplotlib-whitelist.ini">ini</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/matplotlib-summary.csv">csv</a></td>
  <td><a href="https://github.com/costrouc/python-api-inspect/blob/master/data/matplotlib-summary-without-tests.csv">csv</a></td>
</tr>
</table>

A whitelist is used to specify repositories that are inspected for a
specific libraries. For example `data/sympy-whitelist.ini`. Edit or
add libaries to the whitelist to get better statistics. HEAVY caching
is used for downloading repo and inspection of each file. Currently
supports introspection with the following approaches for function
usage.

```python
import numpy
import numpy as np
from numpy import random
from numpy import random as rnd

numpy.array([1, 2])
np.sum(1, 2)
random.random()
rnd.random()
```

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

## numpy

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

## scipy

Get scipy api usage

```shell
python dependant-packages.py --api-key c0....42 --namespaces=scipy --output data/numpy-whitelist.ini numpy,scipy 
python inspect.py data/scipy-whitelist.ini --output data/scipy-summary.csv
```

Get scipy api usage (exclude directories `test, tests, site-packages`)

```shell
python inspect.py data/scipy-whitelist.ini --output data/scipy-summary-without-tests.csv --exclude-dirs test,tests,site-packages
```

## pyarrow

Get pyarrow api usage. We `--include-dependant-repos` becuase pyarrow on libraries.io did not have dependant libraries but had 208 "dependant repos". By contrast numpy has `68k` so we did not use this for numpy/scipy.

```shell
python dependant-packages.py --api-key c0....42 --include-dependant-repos --namespaces=pyarrow --output data/pyarrow-whitelist.ini pyarrow
python inspect.py data/pyarrow-whitelist.ini --output data/pyarrow-summary.csv
```

```shell
python inspect.py data/pyarrow-whitelist.ini --output data/pyarrow-summary-without-tests.csv --exclude-dirs test,tests,site-packages
```

## dask

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=dask --output data/dask-whitelist.ini dask,distributed --include-dependant-repos
```

```shell
python inspect.py data/dask-whitelist.ini --output data/dask-summary.csv --exclude-dirs venv,site-packages
```

## pytorch

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=torch --output data/pytorch-whitelist.ini pytorch --include-dependant-repos
```

```shell
python inspect.py data/pytorch-whitelist.ini --output data/pytorch-summary.csv --exclude-dirs venv,site-packages
```

## tensorflow

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=tensorflow --output data/tensorflow-whitelist.ini tensorflow --include-dependant-repos
```

```shell
python inspect.py data/tensorflow-whitelist.ini --output data/tensorflow-summary.csv --exclude-dirs venv,site-packages
```

## pandas

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=pandas --output data/pandas-whitelist.ini pandas
```

```shell
python inspect.py data/pandas-whitelist.ini --output data/pandas-summary.csv --exclude-dirs venv,site-packages
```

## matplotlib

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=matplotlib --output data/matplotlib-whitelist.ini matplotlib
```

```shell
python inspect.py data/matplotlib-whitelist.ini --output data/matplotlib-summary.csv --exclude-dirs venv,site-packages
```

## sympy

```shell
python dependant-packages.py --api-key c0c...42 --namespaces=sympy --output data/sympy-whitelist.ini sympy --include-dependant-repos
```

```shell
python inspect.py data/sympy-whitelist.ini --output data/sympy-summary.csv --exclude-dirs venv,site-packages
```

# Tests

Tests to demo what `inspect.py` is able to parse from file source. The
"test" is a serious hack and doesn't deserve to be called a test.

```shell
# from root of repository
python tests/test_api_inspect.py
```
