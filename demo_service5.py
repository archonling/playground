import requests
import pandas as pd
import json
import os
import time
import tempfile

class LookupTable:
    
    def __init__(self, url, pem_file=None, refresh_interval=900):
        self.url = url
        self.refresh_interval = refresh_interval
        self.cache_file = os.path.join(tempfile.gettempdir(), f"lookup_table_{os.getpid()}.json")
        self._pem_file = pem_file
        self._last_refresh_time = None
        self._cache = None
        
        self._refresh_cache()
        
    
    def _refresh_cache(self):
        try:
            r = requests.get(self.url, cert=self._pem_file)
            r.raise_for_status()
            with open(self.cache_file, 'w') as f:
                f.write(r.text)
            self._cache = pd.read_json(self.cache_file)
            self._last_refresh_time = time.monotonic()
            print("Cache successfully refreshed!")
        except Exception as e:
            print(f"Failed to refresh cache. Error: {e}")
    
    
    def _is_cache_expired(self):
        if self._last_refresh_time is None:
            return True
        elapsed_time = time.monotonic() - self._last_refresh_time
        return elapsed_time > self.refresh_interval
    
    
    def get_branch_and_legal_entity(self, country_code):
        if self._is_cache_expired():
            self._refresh_cache()
        
        try:
            data = self._cache[self._cache['country_code'] == country_code].iloc[0]
            return (data['giw_branch'], data['lvid'])
        except Exception as e:
            print(f"Error retrieving data for country code {country_code}. Error: {e}")
            return None


if __name__ == "__main__":
    url = 'https://example.com/lookup_table.json'
    pem_file = 'path/to/pem/file.pem'

    table = LookupTable(url=url, pem_file=pem_file)

    # Retrieve the branch and legal entity for country code 'US'
    giw_branch, lvid = table.get_branch_and_legal_entity('US')
    print(giw_branch, lvid)