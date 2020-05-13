import logging
from abc import abstractmethod

from src.configuration import config_reader
from src.words.base import TokenWord, IWord


DEFAULT_MERGED_SYNTAX_VERB_SYMBOL = "V"


class IPropBankWord(IWord):
    @property
    @abstractmethod
    def arg(self):
        pass

    @property
    @abstractmethod
    def misc(self):
        pass

    @property
    @abstractmethod
    def has_verb(self):
        pass

    @property
    @abstractmethod
    def has_arg(self):
        pass


class PropBankTokenWord(TokenWord, IPropBankWord):
    """Conllu token implementation of IPropBankWord"""

    misc_first_value = property(lambda self: list(self.misc)[0])
    is_num_type_ordinal: bool = property(lambda self: self.num_type == "Ord")

    has_verb = property(lambda self: self.misc is not None and self.misc != "")
    has_arg = property(lambda self: self.arg is not None and self.arg != "")


class PropBankMergedTokenWord(PropBankTokenWord, IPropBankWord):
    """Word that is used by merged syntax of conllu. Only difference so far is that it has context for its arguments"""

    def __init__(self, token, current_context: int):
        # Store the token copied from previous instance
        super().__init__(token)

        # Store the context
        self.current_context = current_context
        self.__logger = logging.getLogger(config_reader.get_logger_name("PropBankMergedTokenWord"))

    # To avoid rewriting logic in PropBankTokenSentence we simulate 'contexts' (place in sentence_list array)
    current_context = 0
    inner_arg = property(lambda self: self._getitem(f"arg{self.current_context}"))
    inner_verb = property(lambda self: self._getitem("misc"))

    # The 'V' indicates whether we should return misc (verb), but its not an argument
    arg = property(lambda self: self.inner_arg if self.inner_arg != "V" else "")

    @property
    def misc(self):
        verb = ""

        if self.inner_arg == DEFAULT_MERGED_SYNTAX_VERB_SYMBOL:
            verb = self.inner_verb

            if verb == "":
                self.__logger.fatal(f"Word '{self.token}' has a 'V' argument but no corresponding verb - data is faulty?")

        return verb

    def add_symbol(self, context):
        key = f"arg{context}"
        if key not in self.token:
            raise Exception(f"key '{key}' not found in 'PropBankMergedTokenWord'. That means there are more verbs then verb columns. Wrong format?")

        self.token[key] = DEFAULT_MERGED_SYNTAX_VERB_SYMBOL

    # Context must be immutable otherwise we have to watch the order of operations
    def switch_context(self, current_context):
        return PropBankMergedTokenWord(self.token, current_context)