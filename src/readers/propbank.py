import logging
import typing
from abc import ABC, abstractmethod
from io import StringIO

from conllu import parse_incr, string_to_file
from conllu.parser import DEFAULT_FIELDS, DEFAULT_FIELD_PARSERS

from src.configuration import config_reader
from src.readers.base import parse_string
from src.sentences.propbank import IPropBankSentence, PropBankTokenSentence, PropBankMergedTokenSentence
from src.words.propbank import PropBankTokenWord


class IPropBankAnnotationReaderBase(ABC):
    """Defines PropBank annotation reader behaviour"""

    @abstractmethod
    def read(self) -> typing.List[IPropBankSentence]:
        pass


class PropBankFileAnnotationReader(IPropBankAnnotationReaderBase):
    """"Implements PropBank reading from file.
    Assumes multiple sentences can have the same sent_id and joins them"""

    def __init__(self, file_path: str):
        self.__file_path = file_path

        # Custom format for Conllu to parse
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS['arg'] = lambda line, i: parse_string("_", line, i)
        self.DEFAULT_FIELDS = DEFAULT_FIELDS + ('arg',)

    def read(self) -> typing.List[IPropBankSentence]:
        data_file = open(self.__file_path, "r", encoding="utf-8")

        try:
            return self._get_sentence_list(data_file)
        finally:
            if data_file is not None:
                data_file.close()

    def _get_sentence_list(self, content: StringIO):
        sentence_list: typing.List[PropBankTokenSentence] = []

        # defaults are used to get PropBank data, as parse_incr by default is pure conllu
        for token_list in parse_incr(content, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS):
            sentence = PropBankTokenSentence(token_list)

            # ToDo: Might want to optimise this in the future, as this is O(n^2)
            same_sentence = list(x for x in sentence_list if x.sent_id == sentence.sent_id)

            if len(same_sentence) == 0:
                sentence.add_token(token_list)
                sentence_list.append(sentence)
            else:
                same_sentence[0].add_token(token_list)

        return sentence_list


class PropBankContentAnnotationReader(PropBankFileAnnotationReader, IPropBankAnnotationReaderBase):
    """"Implements PropBank reading from passed string.
    Reuses the file logic because library calls the string_to_file either way when passing string"""

    def __init__(self, content: str):
        self._content = content

        # init with empty file path
        super().__init__("")

    def read(self) -> typing.List[IPropBankSentence]:
        return self._get_sentence_list(string_to_file(self._content))


class PropBankMergedContentFormatAnnotationReader(IPropBankAnnotationReaderBase):
    """"Implements PropBank reading from content. Merged format - each entry can have different format"""

    def __init__(self, content: str, additional_field: bool = False):
        self._content = content
        self.__logger = logging.getLogger(config_reader.get_logger_name("PropBankMergedContentFormatAnnotationReader"))

        # Custom format for Conllu to parse
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()

        # Each entry of data will have custom row count, however these are always present
        self.FIELDS = ("id", "form", "lemma", "upostag", "xpostag", "feats", "head", "deprel", "deps")

        # If there's an additional field before misc
        if additional_field:
            self.FIELDS += ("ignore",)
            self.DEFAULT_FIELD_PARSERS['ignore'] = lambda line, i: None

        self.FIELDS += ("misc",)

    def read(self) -> typing.List[IPropBankSentence]:
        sentence_list: typing.List[PropBankTokenSentence] = []

        # split the entries because we need to treat them separately
        for entry in self._content.split('\n\n'):
            if entry != "":
                argument_count = -1

                # Get row format and adjust parser on first row
                for row in entry.split('\n'):
                    if row != "" and row[0] != '#':
                        argument_count = len(row.split('\t')) - len(self.FIELDS)
                        entry_argument_fields = list()

                        for i in range(argument_count):
                            argName = f"arg{i}"
                            entry_argument_fields.append(argName)

                            # only fields require to be precisely defined, parser will be updated only if necessary
                            # and additional fields won't hurt parser
                            if argName not in self.DEFAULT_FIELD_PARSERS:
                                self.DEFAULT_FIELD_PARSERS[f"arg{i}"] = lambda line, i: parse_string("_", line, i)

                        self.DEFAULT_FIELDS = self.FIELDS + tuple(entry_argument_fields)
                        break

            # Actual parsing
            if argument_count > 0:
                entry_io = string_to_file(entry)
                token_lists = list(x for x in parse_incr(entry_io, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS))

                for token_list in token_lists:
                    try:
                        sentence_list.append(PropBankMergedTokenSentence(token_list, argument_count))
                    except Exception as ex:
                        self.__logger.debug(
                            f"Sentence '{token_list}' failed to initialize. Exception: '{ex}'")

        return sentence_list


class PropBankMergedFileFormatAnnotationReader(PropBankMergedContentFormatAnnotationReader,
                                               IPropBankAnnotationReaderBase):
    def __init__(self, file_path: str, additional_field: bool = False):
        data_file = open(file_path, "r", encoding="utf-8")
        try:
            content = data_file.read()
        finally:
            if data_file is not None:
                data_file.close()

        super().__init__(content, additional_field)
        pass
