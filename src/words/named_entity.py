from abc import abstractmethod

from src.words.base import IWord, TokenWord


class INamedEntitiesWord(IWord):
    """Interface for named entities word getters"""

    @property
    @abstractmethod
    def bio_tag1(self):
        pass

    @property
    @abstractmethod
    def bio_tag2(self):
        pass

    @property
    @abstractmethod
    def wiki1(self):
        pass

    @property
    @abstractmethod
    def wiki2(self):
        pass

    @property
    @abstractmethod
    def upostag(self):
        pass

    @property
    @abstractmethod
    def is_punct(self):
        pass

class NamedEntitiesTokenWord(TokenWord, INamedEntitiesWord):
    """Conllu token implementation of INamedEntitiesWord"""

    bio_tag1 = property(lambda self: self.head)
    bio_tag2 = property(lambda self: self.deprel)
    wiki1 = property(lambda self: self._getitem("deps"))
    wiki2 = property(lambda self: self.misc)
    upostag = property(lambda self: self._getitem("upostag"))
    is_punct = property(lambda self: self.upostag == "PUNCT")