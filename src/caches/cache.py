from abc import ABC, abstractmethod

from diskcache import Cache


class ICache(ABC):

    @abstractmethod
    def get(self, key: str) -> object:
        pass

    @abstractmethod
    def put(self, key: str, value: object):
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        pass


class FileCache(ICache):

    def __init__(self, cache_path):
        self._cache = Cache(cache_path)

    def get(self, key: str) -> object:
        return self._cache[key]

    def put(self, key: str, value: object):
        self._cache[key] = value

    def has(self, key: str) -> bool:
        return key in self._cache