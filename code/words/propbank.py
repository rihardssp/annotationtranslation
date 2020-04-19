from abc import abstractmethod

from code.words.base import TokenWord, IWord


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
    num_type = property(
        lambda self: (self.feats["NumType"] if self.feats is not None and "NumType" in self.feats else None))
    is_num_type_ordinal: bool = property(lambda self: self.num_type == "Ord")
    is_num_type_cardinal: bool = property(lambda self: self.num_type == "Card")

    has_verb = property(lambda self: self.misc is not None and self.misc != "")
    has_arg = property(lambda self: self.arg is not None and self.arg != "")