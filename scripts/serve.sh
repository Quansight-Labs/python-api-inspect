# serve locally
# startup will take around 10 seconds
# to parse sqlite database
datasette -i data/inspect.sqlite \
          --config sql_time_limit_ms:60000 \
          --config suggest_facets:off \
          --config allow_download:off \
          --config default_cache_ttl:60 \
          --config allow_csv_stream:off
