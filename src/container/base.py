from abc import ABC, abstractmethod
import typing


def get_variable_name(id: str):
    return f'v{id}'


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
    def has_instance(self, instance_id: str) -> bool:
        pass

    @abstractmethod
    def print(self, file: typing.TextIO = None):
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


