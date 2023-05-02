import hashlib
import os
import tempfile
import threading
import time
import pandas as pd

lookup_table_url = "https://example.com/lookup_table.json"
cache_filename = "lookup_table_{}.json".format(os.getpid())
cache_path = os.path.join(tempfile.gettempdir(), cache_filename)
default_cache_refresh_interval = 900  # 15 minutes
lookup_table = None


def load_data_from_json(url):
    try:
        return pd.read_json(url)
    except Exception:
        print("Unable to load data from JSON at URL: {}".format(url))
        return None


def load_data_from_cache():
    try:
        with open(cache_path) as cache_file:
            return pd.read_json(cache_file)
    except Exception:
        print("Unable to load data from cache file: {}".format(cache_path))
        return None


def save_data_to_cache(data):
    try:
        data.to_json(cache_path, orient="records")
    except Exception:
        print("Unable to save data to cache file: {}".format(cache_path))


def compute_data_hash(data):
    try:
        return hashlib.md5(data.to_json().encode()).hexdigest()
    except Exception:
        return None


def load_lookup_table():
    global lookup_table
    url_data = load_data_from_json(lookup_table_url)
    if url_data is None:
        lookup_table = None
        return
    cache_data = load_data_from_cache()
    url_hash = compute_data_hash(url_data)
    if url_hash is None:
        lookup_table = None
        return
    if cache_data is None or url_hash != compute_data_hash(cache_data):
        lookup_table = url_data
        save_data_to_cache(lookup_table)
        print("Cache updated from URL.")
    else:
        lookup_table = cache_data
        print("Cache loaded from disk.")
    print("Lookup table loaded.")


def refresh_cache(interval):
    while True:
        time.sleep(interval)
        try:
            url_data = load_data_from_json(lookup_table_url)
            if url_data is None:
                continue
            cache_data = load_data_from_cache()
            url_hash = compute_data_hash(url_data)
            if url_hash is None:
                continue
            if cache_data is None or url_hash != compute_data_hash(cache_data):
                save_data_to_cache(url_data)
                print("Cache updated from URL.")
        except Exception:
            print("Unable to refresh cache from URL.")


def get_branch_and_legal_entity(country):
    global lookup_table
    if lookup_table is None:
        load_lookup_table()
    try:
        result = lookup_table[(lookup_table["Country"] == country)]
        if result.empty:
            return None, None
        return result["Branch"].iloc[0], result["Legal Entity"].iloc[0]
    except Exception:
        return None, None


load_lookup_table()
cache_refresh_thread = threading.Thread(target=refresh_cache, args=(default_cache_refresh_interval,), daemon=True)
cache_refresh_thread.start()
