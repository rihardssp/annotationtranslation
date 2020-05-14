import typing
from abc import abstractmethod

from conllu import TokenList

from src.sentences.base import ISentence, TokenSentenceBase
from src.words.coreference import CoReferenceTokenWord, ICoReferenceWord


class ICoReferenceSentence(ISentence):
    """Interface for CoReference sentence logic"""

    @property
    @abstractmethod
    def co_references(self) -> typing.Dict[str, typing.List[ICoReferenceWord]]:
        pass

    @property
    @abstractmethod
    def co_reference_count(self) -> int:
        pass


class CoReferenceTokenSentence(TokenSentenceBase, ICoReferenceSentence):
    """CoReference specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.sentence: typing.List[CoReferenceTokenWord] = list(CoReferenceTokenWord(x) for x in token_list)
        self.__co_reference_dictionary = None

    @property
    def co_references(self) -> typing.Dict[str, typing.List[ICoReferenceWord]]:
        if not self.__co_reference_dictionary:
            self.__co_reference_dictionary = {}

            for word in self.sentence:
                if word.coreference_group != "":
                    if word.coreference_group not in self.__co_reference_dictionary:
                        self.__co_reference_dictionary.update({word.coreference_group: [word]})
                    else:
                        self.__co_reference_dictionary[word.coreference_group].append(word)

        return self.__co_reference_dictionary

    @property
    def co_reference_count(self) -> int:
        return len(self.co_references)