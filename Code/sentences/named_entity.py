import typing
from abc import abstractmethod

from conllu import TokenList

from Code.sentences.base import ISentence, TokenSentenceBase
from Code.words.named_entity import INamedEntitiesWord, NamedEntitiesTokenWord


class INamedEntitiesSentence(ISentence):
    """Interface for Named Entities sentence logic"""

    @abstractmethod
    def get_wiki1(self) -> typing.List[INamedEntitiesWord]:
        pass

    @abstractmethod
    def get_wiki2(self) -> typing.List[INamedEntitiesWord]:
        pass

    @abstractmethod
    def get_bio1(self) -> typing.List[INamedEntitiesWord]:
        pass

    @abstractmethod
    def get_bio2(self) -> typing.List[INamedEntitiesWord]:
        pass


class NamedEntitiesTokenSentence(TokenSentenceBase, INamedEntitiesSentence):
    """Named entities specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.sentence: typing.List[NamedEntitiesTokenWord] = list(NamedEntitiesTokenWord(x) for x in token_list)

    def get_wiki1(self) -> typing.List[INamedEntitiesWord]:
        return list(x for x in self.sentence if x.wiki1 != '')

    def get_wiki2(self) -> typing.List[INamedEntitiesWord]:
        return list(x for x in self.sentence if x.wiki2 != '')

    def get_bio1(self) -> typing.List[INamedEntitiesWord]:
        return list(x for x in self.sentence if x.bio_tag1 != '')

    def get_bio2(self) -> typing.List[INamedEntitiesWord]:
        return list(x for x in self.sentence if x.bio_tag2 != '')