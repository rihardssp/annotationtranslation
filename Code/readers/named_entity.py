import typing
from os import walk
from os.path import join
from abc import ABC, abstractmethod

from conllu import parse_incr
from conllu.parser import DEFAULT_FIELD_PARSERS

from Code.readers.base import parse_string
from Code.sentences.named_entity import INamedEntitiesSentence, NamedEntitiesTokenSentence


class INamedEntitiesAnnotationReaderBase(ABC):
    """Defines PropBank annotation reader behaviour"""

    @abstractmethod
    def read(self) -> typing.List[INamedEntitiesSentence]:
        pass


class NamedEntitiesFileAnnotationReader(INamedEntitiesAnnotationReaderBase):
    """"Implements PropBank reading from file"""

    def __init__(self, folder_path: str):
        self.__folder_path = folder_path

        # The format is a little different from standard conllu, so we adjust to this
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS["head"] = lambda line, i: parse_string("O", line, i)
        self.DEFAULT_FIELD_PARSERS["deprel"] = lambda line, i: parse_string("O", line, i)
        self.DEFAULT_FIELD_PARSERS["deps"] = lambda line, i: parse_string("_", line, i)
        self.DEFAULT_FIELD_PARSERS["misc"] = lambda line, i: parse_string("_", line, i)

    def read(self) -> typing.List[INamedEntitiesSentence]:
        l: typing.List[NamedEntitiesTokenSentence] = []

        for (current_directory, directory_names, file_names) in walk(self.__folder_path):
            for file in file_names:
                full_file_name = join(current_directory, file)
                data_file = open(full_file_name, "r", encoding="utf-8")
                try:
                    for token_list in parse_incr(data_file, field_parsers=self.DEFAULT_FIELD_PARSERS):
                        l.append(NamedEntitiesTokenSentence(token_list))
                finally:
                    if data_file is not None:
                        data_file.close()

        return l