import typing
from abc import ABC, abstractmethod

from conllu import parse_incr
from conllu.parser import DEFAULT_FIELDS, DEFAULT_FIELD_PARSERS

from Code.readers.base import parse_string
from Code.sentences.propbank import IPropBankSentence, PropBankTokenSentence


class IPropBankAnnotationReaderBase(ABC):
    """Defines PropBank annotation reader behaviour"""

    @abstractmethod
    def read(self) -> typing.List[IPropBankSentence]:
        pass


class PropBankFileAnnotationReader(IPropBankAnnotationReaderBase):
    """"Implements PropBank reading from file"""

    def __init__(self, file_path: str):
        self.__file_path = file_path

        # Custom format for Conllu to parse
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS['arg'] = lambda line, i: parse_string("_", line, i)
        self.DEFAULT_FIELDS = DEFAULT_FIELDS + ('arg',)

    def read(self) -> typing.List[IPropBankSentence]:
        sentence_list: typing.List[PropBankTokenSentence] = []
        data_file = open(self.__file_path, "r", encoding="utf-8")

        try:
            # defaults are used to get PropBank data, as parse_incr by default is pure conllu
            for token_list in parse_incr(data_file, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS):
                sentence = PropBankTokenSentence(token_list)

                # Might want to optimise this in the future, as this is O(n^2)
                same_sentence = list(x for x in sentence_list if x.sent_id == sentence.sent_id)
                if len(same_sentence) == 0:
                    sentence_list.append(sentence)
                else:
                    same_sentence[0].add_token(token_list)

        finally:
            if data_file is not None:
                data_file.close()

        return sentence_list
