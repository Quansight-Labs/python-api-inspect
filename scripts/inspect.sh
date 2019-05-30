# results in about 527 GB of downloads
# downloads take the majority of time
# actual parsing takes 1 hour
# over 26,261 projects

python -m inspect_api inspect \
       --limit 4000 \
       --output data/inspect.sqlite \
       --cache-dir=/scratch/cache/python-api-inspect/ \
       --extensions=py,ipynb \
       --workers=4 \
       data/whitelist/astropy-whitelist.ini      \
       data/whitelist/dask-whitelist.ini         \
       data/whitelist/example.ini                \
       data/whitelist/ipython-whitelist.ini      \
       data/whitelist/ipywidgets-whitelist.ini   \
       data/whitelist/matplotlib-whitelist.ini   \
       data/whitelist/numpy-whitelist.ini        \
       data/whitelist/pandas-whitelist.ini       \
       data/whitelist/pyarrow-whitelist.ini      \
       data/whitelist/pymapd-whitelist.ini       \
       data/whitelist/pymc3-whitelist.ini        \
       data/whitelist/pytorch-whitelist.ini      \
       data/whitelist/requests-whitelist.ini     \
       data/whitelist/scikit-image-whitelist.ini \
       data/whitelist/scikit-learn-whitelist.ini \
       data/whitelist/scipy-whitelist.ini        \
       data/whitelist/statsmodels-whitelist.ini  \
       data/whitelist/sympy-whitelist.ini        \
       data/whitelist/tensorflow-whitelist.ini
