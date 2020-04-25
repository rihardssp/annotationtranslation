from abc import abstractmethod, ABC


class IWord(ABC):
    """Interface for word properties"""

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def lemma(self):
        pass

    @property
    @abstractmethod
    def head(self):
        pass

    @property
    @abstractmethod
    def deprel(self):
        pass

    @property
    @abstractmethod
    def form(self):
        pass

    @property
    @abstractmethod
    def feats(self):
        pass

    @property
    @abstractmethod
    def feats(self):
        pass

    @property
    @abstractmethod
    def is_num_type_cardinal(self):
        pass

class SimpleTokenWord:
    """The most simple Conllu implementation of a word"""

    def __init__(self, token):
        self.token = token

    id = property(lambda self: self._getitem("id"))

    def _getitem(self, key):
        return self.token[key] if key in self.token else ""

    def __str__(self):
        return self.lemma


class TokenWord(SimpleTokenWord, IWord):
    """Conllu token implementation of IWord"""

    misc = property(lambda self: self._getitem("misc"))
    arg = property(lambda self: self._getitem("arg"))
    head = property(lambda self: self._getitem("head"))
    deprel = property(lambda self: self._getitem("deprel"))
    form = property(lambda self: self._getitem("form"))
    feats = property(lambda self: self._getitem("feats"))
    lemma: str = property(lambda self: self._getitem("lemma"))

    num_type = property(
        lambda self: (self.feats["NumType"] if self.feats is not None and "NumType" in self.feats else None))

    is_num_type_cardinal: bool = property(lambda self: self.num_type == "Card")

    def __str__(self):
        return self.form