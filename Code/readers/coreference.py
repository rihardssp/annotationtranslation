import typing
from os import walk
from os.path import join
from abc import ABC, abstractmethod

from conllu import parse_incr

from Code.readers.base import parse_string
from Code.sentences.coreference import ICoReferenceSentence, CoReferenceTokenSentence


class ICoReferenceAnnotationReaderBase(ABC):
    """Defines PropBank annotation reader behaviour"""

    @abstractmethod
    def read(self) -> typing.List[ICoReferenceSentence]:
        pass


class CoReferenceFileAnnotationReader(ICoReferenceAnnotationReaderBase):
    """"Implements PropBank reading from file"""

    CO_REFERENCE_SUPPORTED_FORMAT = "#FORMAT=WebAnno TSV 3.2"

    def __init__(self, folder_path: str):
        self.__folder_path = folder_path

        self.default_fields = ["id", "range", "lemma"]
        self.default_parsers = dict()
        self.default_parsers[self.default_fields[0]] = lambda line, i: line[i].split('-')[1]
        self.default_parsers[self.default_fields[1]] = lambda line, i: str(line[i])
        self.default_parsers[self.default_fields[2]] = lambda line, i: str(line[i])

    def read(self) -> typing.List[ICoReferenceSentence]:
        l: typing.List[CoReferenceTokenSentence] = []

        for (current_directory, directory_names, file_names) in walk(self.__folder_path):
            for file in file_names:
                full_file_name = join(current_directory, file)
                data_file = open(full_file_name, "r", encoding="utf-8")
                try:
                    fields, parsers = self.read_headers(data_file)
                    for token_list in parse_incr(data_file, fields=fields, field_parsers=parsers):
                        sentence = CoReferenceTokenSentence(token_list)
                        l.append(sentence)

                        # Double-check that this sentence respects format defined in header
                        if len(fields) != len(sentence.sentence[0].token):
                            raise Exception(
                                f"tsv file '{full_file_name}' defines a total of '{len(fields)}' features (including id). "
                                f"Currently present in the first word of first sentence: {len(sentence.sentence[0].token)}.")


                finally:
                    if data_file is not None:
                        data_file.close()

        return l

    def read_headers(self, data_file: typing.TextIO):
        """Find out what fields/parsers we need to parse following sentences using conllu.
           later the headers are used as keys to get specific annotation."""

        # header marker - version check
        tsv_format = data_file.readline().rstrip()

        if "#FORMAT=" not in tsv_format:
            raise Exception(f"First line does not define co references format: '{tsv_format}'")

        if tsv_format != self.CO_REFERENCE_SUPPORTED_FORMAT:
            raise Exception(f"CoReferenceFileAnnotationReader does not support format '{tsv_format}'. "
                            f"Only '{self.CO_REFERENCE_SUPPORTED_FORMAT}' supported")

        # Start reading the header layers
        column_format = data_file.readline().rstrip()
        fields = list()

        while column_format != "":
            # Example: #T_%category%=%layer_name%|%feature_name1%|%feature_name2%
            layer_and_features = column_format.split("=")[1].split("|")
            layer_name = layer_and_features[0]
            features = layer_and_features[1:]

            # fields are identified by their full name: layer_feature
            for field in features:
                fields.append(f"{layer_name}_{field}")

            column_format = data_file.readline().rstrip()

        # All parsers parse string (could define a mapping_definitions with lambdas for particular cases)
        parsers = dict()
        for field in fields:
            parsers[field] = lambda line, i: parse_string(["*", "_"], line, i)

        # fields/parsers that are always present and not defined in header
        fields = self.default_fields + fields
        parsers.update(self.default_parsers)

        return fields, parsers
