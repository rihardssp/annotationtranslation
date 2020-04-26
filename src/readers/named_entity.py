import typing
from io import StringIO
from os import walk
from os.path import join
from abc import ABC, abstractmethod

from conllu import parse_incr, string_to_file
from conllu.parser import DEFAULT_FIELD_PARSERS

from src.readers.base import parse_string
from src.sentences.named_entity import INamedEntitiesSentence, NamedEntitiesTokenSentence


class INamedEntitiesAnnotationReaderBase(ABC):
    """Defines PropBank annotation reader behaviour"""

    @abstractmethod
    def read(self) -> typing.List[INamedEntitiesSentence]:
        pass


class NamedEntitiesFilesAnnotationReader(INamedEntitiesAnnotationReaderBase):
    """Implements Named entities reading from passed path (recursively adding all files under path)"""

    def __init__(self, folder_path: str):
        self.__folder_path = folder_path

        # The format is a little different from standard conllu, so we adjust to this
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS["head"] = lambda line, i: parse_string("O", line, i)
        self.DEFAULT_FIELD_PARSERS["deprel"] = lambda line, i: parse_string("O", line, i)
        self.DEFAULT_FIELD_PARSERS["deps"] = lambda line, i: parse_string("_", line, i)
        self.DEFAULT_FIELD_PARSERS["misc"] = lambda line, i: parse_string("_", line, i)

    def read(self) -> typing.List[INamedEntitiesSentence]:
        sentence_list: typing.List[NamedEntitiesTokenSentence] = []

        for (current_directory, directory_names, file_names) in walk(self.__folder_path):
            for file in file_names:
                full_file_name = join(current_directory, file)
                data_file = open(full_file_name, "r", encoding="utf-8")
                try:
                    sentence_list += self._get_sentence_list(data_file)
                finally:
                    if data_file is not None:
                        data_file.close()

        return sentence_list

    def _get_sentence_list(self, content: StringIO):
        sentence_list: typing.List[NamedEntitiesTokenSentence] = []

        for token_list in parse_incr(content, field_parsers=self.DEFAULT_FIELD_PARSERS):
            sentence_list.append(NamedEntitiesTokenSentence(token_list))

        return sentence_list


class NamedEntitiesContentAnnotationReader(NamedEntitiesFilesAnnotationReader, INamedEntitiesAnnotationReaderBase):
    """Implements Named entities reading from passed string"""

    def __init__(self, content: str):
        self._content = content
        super().__init__("")

    def read(self) -> typing.List[INamedEntitiesSentence]:
        return self._get_sentence_list(string_to_file(self._content))