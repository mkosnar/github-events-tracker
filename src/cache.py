import logging
import os
import pickle


class CacheData:
    CACHE_FILE_NAME = 'github_events.cache'

    def __init__(self, cache_file_dir: str):
        self._cache_file_path = os.path.join(cache_file_dir, self.CACHE_FILE_NAME)
        if os.path.isfile(self._cache_file_path):
            with open(self._cache_file_path, 'rb') as cf:
                self.data = pickle.load(cf)
        else:
            logging.info('Cache file not found')
            self.data = dict()

    def store(self, data: dict):
        self.data.update(data)
        self._save()

    def _save(self):
        with open(self._cache_file_path, 'wb') as cf:
            pickle.dump(self.data, cf)
