from abc import abstractmethod, ABC

from src.words.base import SimpleTokenWord


class ICoReferenceWord(ABC):
    """Interface for named entities word getters"""

    @property
    @abstractmethod
    def id(self):
        pass

    # ToDO: its form, not lemma!
    @property
    @abstractmethod
    def form(self):
        pass

    @property
    @abstractmethod
    def coreference_group(self):
        pass

    @property
    @abstractmethod
    def pos_value(self):
        pass


class CoReferenceTokenWord(SimpleTokenWord, ICoReferenceWord):
    """Conllu token implementation of ICoReferenceWord"""

    __pos_value_key = "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_PosValue"
    pos_value = property(lambda self: self._getitem(self.__pos_value_key))

    __co_reference_type_key = "de.tudarmstadt.ukp.dkpro.core.api.coref.type.CoreferenceLink_referenceType"
    coreference_group = property(lambda self: self._getitem(self.__co_reference_type_key))

    form = property(lambda self: self._getitem("form"))