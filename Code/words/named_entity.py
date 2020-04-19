from abc import abstractmethod

from Code.words.base import IWord, TokenWord


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


class NamedEntitiesTokenWord(TokenWord, INamedEntitiesWord):
    """Conllu token implementation of INamedEntitiesWord"""

    bio_tag1 = property(lambda self: self.head)
    bio_tag2 = property(lambda self: self.deprel)
    wiki1 = property(lambda self: self.token['deps'])
    wiki2 = property(lambda self: self.misc)