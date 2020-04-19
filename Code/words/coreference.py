from abc import abstractmethod

from Code.words.base import SimpleTokenWord


class ICoReferenceWord:
    """Interface for named entities word getters"""

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
    def coref(self):
        pass

    @property
    @abstractmethod
    def pos_value(self):
        pass


class CoReferenceTokenWord(SimpleTokenWord, ICoReferenceWord):
    """Conllu token implementation of ICoReferenceWord"""

    __pos_value_key = "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_PosValue"
    pos_value = property(lambda self: self.token[self.__pos_value_key] if self.__pos_value_key in self.token else "")

    __co_reference_type_key = "de.tudarmstadt.ukp.dkpro.core.api.coref.type.CoreferenceLink_referenceType"
    coref = property(lambda self: self.token[self.__co_reference_type_key] if self.__co_reference_type_key in self.token else "")