from abc import ABC, abstractmethod
import typing
from enum import Enum

VARIABLE_NAME_SYMBOL = 'v'


def stat_incr(x: int):
    return x + 1


def get_variable_name(id: str):
    return f'{VARIABLE_NAME_SYMBOL}{id}'


class ContainerStatistic(Enum):
    """Defines the available opetaion categories of phrase normalizer"""
    COREFERENCE_TOTAL_COUNT = 1,
    COREFERENCE_COUNT = 2,
    HAS_COREFERENCE = 3,
    HAS_NAMED_ENTITIES = 4,
    WIKI_COUNT = 5,
    WIKI_TOTAL_COUNT = 6,
    NAMED_ENTITIES_COUNT = 7,
    NAMED_ENTITIES_TOTAL_COUNT = 8,
    SENTENCE_TOKEN_TOTAL_COUNT = 9,
    FRAME_TOTAL_COUNT = 10,
    SENTENCE_TOKEN_REMOVED_COUNT = 11,


class IContainer(ABC):
    """Implementation of graph storage that is filled by pipes"""

    @property
    @abstractmethod
    def sent_id(self):
        pass

    @property
    @abstractmethod
    def text(self):
        pass

    @property
    def property_count(self):
        """Counts all properties in AMR"""
        pass

    @property
    def token_count(self):
        """Counts all words found in sentence that AMR was generated from"""
        pass

    @property
    def frame_count(self):
        """Counts number of PropBank frames in AMR"""
        pass

    @abstractmethod
    def get_stat(self, statistic: ContainerStatistic, default_value=None):
        """Gets statistic from container"""
        pass

    @abstractmethod
    def set_stat(self, statistic: ContainerStatistic, value):
        """Sets statistic for container"""
        pass

    @abstractmethod
    def update_stat(self, statistic: ContainerStatistic, func: typing.Callable):
        """Updates statistic according to what function returns after passing the current value to it"""
        pass

    @abstractmethod
    def add_root(self, root_id: str, name_of_root):
        """Root verb of AMR"""
        pass

    @abstractmethod
    def add(self, instance_id: str, role, argument):
        """Add an argument to a instance, for ex., polarity"""
        pass

    @abstractmethod
    def add_instance(self, head_id, instance_id: str, role, argument_instance):
        """Add an instance (differs from add by defining an alias for given argument_instance)"""
        pass

    @abstractmethod
    def has_link(self, root_id: str, argument_id: str) -> bool:
        pass

    @abstractmethod
    def add_link(self, instance_id: str, role, argument_id):
        pass

    @abstractmethod
    def has_instance(self, instance_id: str) -> bool:
        pass

    @abstractmethod
    def print(self, file: typing.TextIO = None, include_debug: bool = False):
        """Printing to console/file/etc"""
        pass

    @abstractmethod
    def get_instance_ids(self):
        """Printing to console/file/etc"""
        pass

    @abstractmethod
    def get_generated_id(self):
        pass

    @abstractmethod
    def remove_instance(self, instance_id):
        """ Removes an instance. Use with caution, as this may cause a fragmented graph."""
        pass

    @abstractmethod
    def remove_link(self, root_alias: str, role: str, argument_alias: str):
        """ Removes an instance. Use with caution, as this may cause a fragmented graph."""
        pass

    @abstractmethod
    def get_instance_value(self, instance_id: str):
        """Replaces a value of an instance"""
        pass

    @abstractmethod
    def update_instance_value(self, instance_id: str, instance_value: str):
        """Replaces a value of an instance"""
        pass

    @abstractmethod
    def replace_parents_roles_to_instance(self, instance_id, old_role, new_role) -> bool:
        """Finds instance with 'instance_id', then finds all instances pointing to it with old_role
                and changes those roles to new_role"""
        pass

    @abstractmethod
    def replace_instance(self, instance_id: str, new_id: str):
        """Replaces an instance and all its references. Resource-consuming operation,
        however acceptable if low number of references"""
        pass
