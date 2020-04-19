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


class SimpleTokenWord:
    """The most simple Conllu implementation of a word"""

    def __init__(self, token):
        self.token = token

    id = property(lambda self: self.token["id"])
    lemma: str = property(lambda self: self.token["lemma"])

    def __getitem__(self, key):
        return self.token[key]

    def __str__(self):
        return self.lemma


class TokenWord(SimpleTokenWord, IWord):
    """Conllu token implementation of IWord"""

    misc = property(lambda self: self.token["misc"])
    arg = property(lambda self: self.token["arg"])
    head = property(lambda self: self.token["head"])
    deprel = property(lambda self: self.token["deprel"])
    form = property(lambda self: self.token["form"])
    feats = property(lambda self: self.token["feats"])

    def __str__(self):
        return self.form