import pandas as pd
import requests
import hashlib
import tempfile
import threading
import time
import os 

# Define the URL for the lookup table
lookup_table_url = "https://example.com/lookup_table.json"

# Define a filename for the cached version of the lookup table
cache_filename = "lookup_table_{}.json".format(os.getpid())

# Define the path for the cached version of the lookup table
cache_path = os.path.join(tempfile.gettempdir(), cache_filename)

# Define the default cache refresh interval in seconds
default_cache_refresh_interval = 900  # 15 minutes

# Define a global variable to hold the lookup table
lookup_table = None

# Define a function to retrieve the lookup table either from the cache or the URL
def get_lookup_table():
    global lookup_table
    if lookup_table is not None:
        return lookup_table
    if os.path.isfile(cache_path):
        with open(cache_path, "r") as f:
            cached_data = f.read()
        cached_hash = hashlib.md5(cached_data.encode()).hexdigest()
        response = requests.get(lookup_table_url)
        url_data = response.text
        url_hash = hashlib.md5(url_data.encode()).hexdigest()
        if cached_hash == url_hash:
            lookup_table = pd.read_json(cached_data)
            return lookup_table
    response = requests.get(lookup_table_url)
    lookup_table = pd.read_json(response.text)
    with open(cache_path, "w") as f:
        f.write(response.text)
    return lookup_table

# Define a function that takes in a country and returns the corresponding branch and legal entity
def get_branch_and_legal_entity(country):
    lookup_table = get_lookup_table()
    result = lookup_table[lookup_table['Country'] == country]
    if result.empty:
        return None, None
    else:
        branch = result["Branch"].iloc[0]
        legal_entity = result["Legal Entity"].iloc[0]
        return branch, legal_entity

# Define a function to periodically refresh the cache
def refresh_cache(cache_refresh_interval):
    while True:
        time.sleep(cache_refresh_interval)
        with threading.Lock():
            with open(cache_path, "r") as f:
                cached_data = f.read()
            cached_hash = hashlib.md5(cached_data.encode()).hexdigest()
            response = requests.get(lookup_table_url)
            url_data = response.text
            url_hash = hashlib.md5(url_data.encode()).hexdigest()
            if cached_hash != url_hash:
                lookup_table = pd.read_json(response.text)
                with open(cache_path, "w") as f:
                    f.write(response.text)
                print("Cache refreshed.")
            
# Load the lookup table into cache when the library is loaded
lookup_table = get_lookup_table()

# Start the cache refresh thread with the default interval
cache_refresh_thread = threading.Thread(target=refresh_cache, args=(default_cache_refresh_interval,), daemon=True)
cache_refresh_thread.start()
