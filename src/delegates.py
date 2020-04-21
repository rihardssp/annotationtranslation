import typing
from src.container import TripletContainer

DEFAULT_DELEGATE_INIT_ERROR = "Delegate initialized with non-callable argument"


class RuleDelegate:
    """These rules are run for each word to look for additional things to add, for example, nmod, polarity, etc"""

    def __init__(self, delegate):
        if callable(delegate):
            self.delegate = delegate
        else:
            raise Exception(DEFAULT_DELEGATE_INIT_ERROR)

    def evaluate(self, pipe, word, container: TripletContainer, sentence):
        self.delegate(pipe, word, container, sentence)


class ArgumentDelegate:
    """Rules for adding an argument. Default is simply using the default mapping_definitions available"""

    def __init__(self, delegate, default_mapping: str):
        if delegate is None or callable(delegate):
            self.delegate = delegate
            self.default_mapping = default_mapping
        else:
            raise Exception(DEFAULT_DELEGATE_INIT_ERROR)

    def evaluate(self, pipe, root_word, argument_word, container: TripletContainer, sentence) -> bool:
        if self.delegate is not None:
            self.delegate(pipe, root_word, argument_word, container, sentence)


class ChunkDelegate:
    """Rules for processing chunks of words"""

    def __init__(self, delegate, default_mapping: str = None):
        if delegate is None or callable(delegate):
            self.__delegate = delegate
            self.__default_mapping = default_mapping
        else:
            raise Exception(DEFAULT_DELEGATE_INIT_ERROR)

    def evaluate(self, pipe, container_word_id: str, chunk: typing.List, container: TripletContainer):
        self.__delegate(pipe, container_word_id, chunk, container, self.__default_mapping)
