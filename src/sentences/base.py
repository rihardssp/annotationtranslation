from abc import abstractmethod, ABC

from conllu import TokenList


class ISentence(ABC):
    """Common logic for sentences"""

    @property
    @abstractmethod
    def sent_id(self):
        pass

    @property
    @abstractmethod
    def text(self):
        pass

    @property
    @abstractmethod
    def metadata(self):
        pass


class TokenSentenceBase(ISentence):
    """Common logic for sentences from Conllu tokens"""

    def __init__(self, token_list: TokenList):
        self.__token_list = token_list

    sent_id = property(
        lambda self: self.__token_list.metadata["sent_id"] if "sent_id" in self.__token_list.metadata else '')
    text = property(lambda self: self.__get_text())

    def __get_text(self):
        if "text" in self.__token_list.metadata:
            return self.__token_list.metadata["text"]
        if "Text" in self.__token_list.metadata:
            return self.__token_list.metadata["Text"]
        if "sentence-text" in self.__token_list.metadata:
            return self.__token_list.metadata["sentence-text"]
        # ToDo: Or just concat tokens?
        return ""

    metadata = property(lambda self: self.__token_list.metadata)