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

```shell
python inspect.py whitelist.ini
```
    
