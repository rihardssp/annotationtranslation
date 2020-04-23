from abc import ABC, abstractmethod
from enum import Enum
from src.configuration import config_reader
from diskcache import Cache

import requests


class PhaseNormalizerCategory(Enum):
    """Defines the available opetaion categories of phrase normalizer"""
    NONE = "none",
    NOCATEGORY = "no_category",
    PERSON = "pers",
    LOCATION = "loc",
    ORGANIZATION = "org"


class IPhraseNormalizer(ABC):

    @abstractmethod
    def normalize(self, category: PhaseNormalizerCategory, value: str):
        pass
    

class RestletPhraseNormalizer(IPhraseNormalizer):

    def __init__(self, debug_mode: bool = False):
        self.__cache = Cache(config_reader.get_phrase_normalizer_cache_path())
        self.__base_url = config_reader.get_phrase_normalizer_base_url()
        self.__debug_mode = debug_mode

    def normalize(self, category: PhaseNormalizerCategory, value: str):
        if category == PhaseNormalizerCategory.NONE:
            return value

        # Cache the result on disk for repeated calls
        cache_key = f"{category}_{value}"
        if cache_key in self.__cache:
            item = self.__cache[cache_key]

            if self.__debug_mode:
                print(f"Got value '{item}' with key '{cache_key}' from PhraseNormalizer cache")

            return item

        response = requests.get(f"{self.__base_url}{value}",
                                {"category": category.value} if category != PhaseNormalizerCategory.NOCATEGORY else None)

        if response.status_code != 200:
            raise Exception(f"'{response.url}' returned code '{response.status_code}'. ")

        # A simple check that we're getting data instead of html
        result = response.text
        if "<" in result or ">" in result:
            raise Exception(f"Restlet normaliser service '{response.url}' returned text with html: '{result}'")

        # Not to forget cache
        self.__cache[cache_key] = result
        if self.__debug_mode:
            print(f"Got value '{result}' from '{value}' by using phrase normalizer service")

        return result
