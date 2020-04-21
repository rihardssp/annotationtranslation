import typing
from abc import ABC, abstractmethod

DEFAULT_REPLACEABLE_POS_VALUES = ["pp", "px", "pd"]


class ICoReferenceMapping(ABC):

    @abstractmethod
    def get_replaceable_pos_values(self):
        pass


class CoReferenceMapping:
    """This class contains mapping_definitions and actions which propbank uses to transform PropBank to AMR"""

    def __init__(self, replaceable_pos_values: typing.List = None):
        self.replaceable_pos_values = \
            replaceable_pos_values if replaceable_pos_values is not None else DEFAULT_REPLACEABLE_POS_VALUES

    def get_replaceable_pos_values(self):
        return self.replaceable_pos_values
