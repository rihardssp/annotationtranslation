import typing
from abc import abstractmethod

from conllu import TokenList

from src.sentences.base import ISentence, TokenSentenceBase
from src.words.named_entity import INamedEntitiesWord, NamedEntitiesTokenWord


class INamedEntitiesSentence(ISentence):
    """Interface for Named Entities sentence logic"""

    @property
    @abstractmethod
    def bio1(self) -> typing.List[INamedEntitiesWord]:
        pass

    @property
    @abstractmethod
    def bio1_count(self) -> int:
        pass

    @property
    def wiki1_count(self) -> int:
        pass


class NamedEntitiesTokenSentence(TokenSentenceBase, INamedEntitiesSentence):
    """Named entities specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.sentence: typing.List[NamedEntitiesTokenWord] = list(NamedEntitiesTokenWord(x) for x in token_list)

    @property
    def bio1(self) -> typing.List[INamedEntitiesWord]:
        """Gets tokens with bio-tags in sentence token order"""
        return list(x for x in self.sentence if x.bio_tag1 != '')

    @property
    def bio1_count(self) -> int:
        return len(list(x for x in self.sentence if x.bio_tag1 and x.bio_tag1[0] == 'B'))

    @property
    def wiki1_count(self) -> int:
        return len(list(x for x in self.sentence if x.wiki1))
