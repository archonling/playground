import os
import pandas as pd
import requests
import tempfile
from datetime import datetime, timedelta

class LookupTable:
    def __init__(self, url, pem_file=None, expiration=timedelta(minutes=15)):
        self.url = url
        self.pem_file = pem_file
        self.expiration = expiration
        self.cache_file = os.path.join(tempfile.gettempdir(), f'cache_{os.getpid()}.json')
        self.cache_last_updated = datetime.min

    def _refresh_cache(self):
        try:
            if self.pem_file:
                response = requests.get(self.url, headers={'verify': f'{self.pem_file}'})
            else:
                response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()
            pd.DataFrame(data).to_json(self.cache_file, orient='records')
            self.cache_last_updated = datetime.now()
            print("Cache refreshed at:", self.cache_last_updated)
        except Exception as e:
            print("Error refreshing cache:", e)

    def _load_cache(self):
        try:
            data = pd.read_json(self.cache_file, orient='records')
            return data.set_index('country_code')
        except Exception as e:
            print("Error loading cache:", e)
            return pd.DataFrame(columns=['country_code', 'giw_branch', 'lvid']).set_index('country_code')

    def _get_cache(self):
        if not os.path.isfile(self.cache_file) or (datetime.now() - self.cache_last_updated) > self.expiration:
            self._refresh_cache()
        return self._load_cache()

    def get_branch_and_legal_entity(self, country_code):
        cache = self._get_cache()
        row = cache.loc[country_code]
        return (row['giw_branch'], row['lvid'])

if __name__ == "__main__":
    url = 'https://example.com/lookup_table.json'
    pem_file = 'path/to/pem/file.pem'

    table = LookupTable(url=url, pem_file=pem_file)

    # Retrieve the branch and legal entity for country code 'US'
    giw_branch, lvid = table.get_branch_and_legal_entity('US')
    print(giw_branch, lvid)