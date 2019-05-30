# create whitelist of packages that depends on the following packages (its alot)

python -m inspect_api whitelist \
       --output-dir data/whitelist-test/ \
       --librariesio-db /home/costrouc/data/librariesio/libraries.db \
      astropy dask ipython ipywidgets matplotlib numpy pandas pyarrow \
      pymapd pymc3 pytorch requests scikit-image scikit-learn scipy \
      statsmodels sympy tensorflow
