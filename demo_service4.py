import os
import pandas as pd
import requests
import time
import tempfile

class LookupTable:
    def __init__(self, url, pem_file=None, cache_file=None, default_expiry=900):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.pem_file = pem_file
        self.default_expiry = default_expiry
        self.cache_file = cache_file if cache_file else os.path.join(
            tempfile.gettempdir(), f"lookup_table_{os.getpid()}.csv"
        )
        self.cache = None
        self.last_refresh_time = None
        self.is_cache_valid = False
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            self.cache = pd.read_csv(self.cache_file)
            self.last_refresh_time = time.monotonic()
            self.is_cache_valid = True
        else:
            self.refresh_cache()

    def refresh_cache(self):
        try:
            start_time = time.monotonic()
            response = requests.get(self.url, headers=self.headers, cert=self.pem_file)
            if response.status_code == 200:
                data = response.json()
                self.cache = pd.json_normalize(data)
                self.cache.to_csv(self.cache_file, index=False)
                end_time = time.monotonic()
                self.last_refresh_time = end_time
                self.is_cache_valid = True
                elapsed_time = end_time - start_time
                print(f"Cache refreshed in {elapsed_time:.2f} seconds.")
            else:
                print(f"Error refreshing cache. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error refreshing cache: {e}")

    def get_branch_and_legal_entity(self, country_code):
        if not self.is_cache_valid or (
            time.monotonic() - self.last_refresh_time > self.default_expiry
        ):
            self.refresh_cache()

        if self.cache is None:
            return None

        rows = self.cache.loc[self.cache["country_code"] == country_code]
        if not rows.empty:
            return rows[["giw_branch", "lvid"]].iloc[0].to_dict()
        else:
            return None

if __name__ == "__main__":
    url = 'https://example.com/lookup_table.json'
    pem_file = 'path/to/pem/file.pem'

    table = LookupTable(url=url, pem_file=pem_file)

    # Retrieve the branch and legal entity for country code 'US'
    giw_branch, lvid = table.get_branch_and_legal_entity('US')
    print(giw_branch, lvid)