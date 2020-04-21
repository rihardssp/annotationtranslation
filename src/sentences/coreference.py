import typing
from abc import abstractmethod

from conllu import TokenList

from src.sentences.base import ISentence, TokenSentenceBase
from src.words.coreference import CoReferenceTokenWord, ICoReferenceWord


class ICoReferenceSentence(ISentence):
    """Interface for CoReference sentence logic"""

    @abstractmethod
    def get_co_references(self) -> typing.Dict[str, typing.List[ICoReferenceWord]]:
        pass


class CoReferenceTokenSentence(TokenSentenceBase, ICoReferenceSentence):
    """CoReference specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.sentence: typing.List[CoReferenceTokenWord] = list(CoReferenceTokenWord(x) for x in token_list)

    def get_co_references(self) -> typing.Dict[str, typing.List[ICoReferenceWord]]:
        dictionary = {}

        for word in self.sentence:
            if word.coref != "":
                if word.coref not in dictionary:
                    dictionary.update({word.coref: [word]})
                else:
                    dictionary[word.coref].append(word)
            else:
                # print("corref empty for")
                pass

        return dictionary
