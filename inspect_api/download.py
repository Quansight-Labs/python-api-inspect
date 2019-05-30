import os
import urllib.error
import urllib.request


def download_github_repo(owner, repo, ref, cache_dir=None):
    filename = os.path.join(cache_dir, f'{owner}-{repo}-{ref}.zip')
    if not os.path.isfile(filename):
        url = f'https://github.com/{owner}/{repo}/archive/{ref}.zip'
        print(f'downloading: {url}')
        try:
            with urllib.request.urlopen(url) as response:
                with open(filename, 'wb') as f:
                    f.write(response.read())
        except urllib.error.HTTPError:
            print(f'failed to download: {url}')
            return None
    else:
        print(f'cached: {filename:64}')
    return filename
