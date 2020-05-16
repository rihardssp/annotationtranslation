import re
import sys
import typing
from io import TextIOBase

import penman
from src.container.base import get_variable_name, IContainer, VARIABLE_NAME_SYMBOL, ContainerStatistic

WORD_INSTANCE_REGEX = re.compile("^v\\d+$")
FRAME_INSTANCE_REGEX = re.compile("^[A-z]+\\.\\d+$")


class TripletContainer(IContainer):
    """Implementation of intermediate storage using triplets that will be later serializet to graph"""
    sent_id = property(lambda self: self.__g.metadata["sent_id"] if "sent_id" in self.__g.metadata else "")
    text = property(lambda self: self.__get_text())

    @property
    def property_count(self):
        """Counts all triplets that are not instance declarations but are in the form
        (instance_name, role, not_instance_name) """
        return len(list(x for x in self.__g.triples if
                        x[0][0] == VARIABLE_NAME_SYMBOL and x[1] != self.instance_role and x[2][
                            0] != VARIABLE_NAME_SYMBOL))

    @property
    def token_count(self):
        """Counts all triplets that are have a non-generated id and instance role"""
        return len(list(x for x in self.__g.triples if WORD_INSTANCE_REGEX.match(x[0]) and x[1] == self.instance_role)) + \
           self.get_stat(ContainerStatistic.SENTENCE_TOKEN_REMOVED_COUNT, 0)


    @property
    def frame_count(self):
        """Counts all frames by using frame identifying regex and instance role"""
        return len(list(x for x in self.__g.triples if x[1] == self.instance_role and FRAME_INSTANCE_REGEX.match(x[2])))

    def get_stat(self, statistic: ContainerStatistic, default_value=None):
        """Gets statistic from container"""
        return self.__statistics[statistic] if statistic in self.__statistics else default_value

    def set_stat(self, statistic: ContainerStatistic, value):
        """Sets statistic for container"""
        self.__statistics[statistic] = value

    def update_stat(self, statistic: ContainerStatistic, func: typing.Callable):
        """Updates statistic according to what function returns after passing the current value to it"""
        self.set_stat(statistic, func(self.get_stat(statistic)))

    def __get_text(self):
        if "text" in self.__g.metadata:
            return self.__g.metadata["text"]
        if "Text" in self.__g.metadata:
            return self.__g.metadata["Text"]
        return ""

    def __init__(self, metadata):
        """Metadata will be printed with AMR sentences"""
        self.__g = penman.Graph()
        self.__g.metadata = metadata
        self.instance_role = ':instance'
        self.__statistics = {}
        self.__generated_id = 0
        self.set_stat(ContainerStatistic.SENTENCE_TOKEN_REMOVED_COUNT, 0)

    def add_root(self, root_id: str, name_of_root):
        """Root verb of AMR"""
        root_alias = get_variable_name(root_id)
        self.__g.triples.append(penman.Triple(root_alias, self.instance_role, name_of_root))

    def add(self, instance_id: str, role, argument: str):
        """Add an argument to a instance, for ex., polarity"""
        self.__inner_add(get_variable_name(instance_id), role, argument)

    def __inner_add(self, instance_alias: str, role, argument: str):
        """Add an argument to a instance, for ex., polarity"""
        self.__g.triples.append(penman.Triple(instance_alias, role, argument))

    def add_instance(self, head_id, instance_id: str, role, argument_instance):
        """Add an instance (differs from add by defining an alias for given argument_instance)"""
        argument_alias = get_variable_name(instance_id)

        # If an instance of a word already exists, then it should not get added
        if not self.has_instance(instance_id):
            self.__g.triples.append(penman.Triple(argument_alias, self.instance_role, argument_instance))

        self.__g.triples.append(penman.Triple(get_variable_name(head_id), role, argument_alias))

    def has_link(self, root_id: str, argument_id: str) -> bool:
        argument_name = get_variable_name(argument_id)
        root_name = get_variable_name(root_id)
        instances = list(x for x in self.__g.triples if x[0] == root_name and x[2] == argument_name)
        return len(instances) > 0

    def add_link(self, instance_id: str, role, argument_id):
        """Add an argument to a instance, for ex., polarity"""
        self.__inner_add(get_variable_name(instance_id), role, get_variable_name(argument_id))

    def has_instance(self, instance_id: str) -> bool:
        instance_name = get_variable_name(instance_id)
        instances = list(x for x in self.__g.triples if x[1] == self.instance_role and x[0] == instance_name)
        return len(instances) > 0

    def print(self, text_stream: TextIOBase = None, include_debug: bool = False):
        """Printing to console/file/etc"""
        if text_stream is None:
            text_stream = sys.stdout

        if include_debug:
            if self.get_stat(ContainerStatistic.HAS_NAMED_ENTITIES, False):
                text_stream.write(f"# ::debug_comment_1 = This sentence has respective named entity entry\n")
            if self.get_stat(ContainerStatistic.HAS_COREFERENCE, False):
                text_stream.write(f"# ::debug_comment_2 = This sentence has respective co-reference entry\n")

            text_stream.write(f"# ::amr_property_count = {self.property_count}\n")
            text_stream.write(f"# ::token_count = in amr {self.token_count} "
                              f"out of {self.get_stat(ContainerStatistic.SENTENCE_TOKEN_TOTAL_COUNT, 0)}\n")
            text_stream.write(f"# ::frame_count = in amr {self.frame_count} "
                              f"out of {self.get_stat(ContainerStatistic.FRAME_TOTAL_COUNT, 0)}\n")

        text_stream.write(penman.encode(self.__g, indent=4))
        text_stream.write("\n\n")

    def get_instance_ids(self):
        """Printing to console/file/etc"""
        l = list()

        for triplet in self.__g.triples:
            if triplet[1] == self.instance_role:
                l.append(triplet[1][1:])

        return l

    def get_generated_id(self):
        generated_id = f'g{self.__generated_id}'
        self.__generated_id += 1
        return generated_id

    def remove_instance(self, instance_id):
        """ Removes an instance. Use with caution, as this may cause a fragmented graph."""
        instance_alias = get_variable_name(instance_id)
        potential_instances = list(
            x for x in self.__g.triples if x[0] == instance_alias and x[1] == self.instance_role)

        if len(potential_instances) != 1:
            raise Exception(f"Failed attempt to modify container instance: Found "
                            f"'{len(potential_instances)}' count of instances with id '{instance_id}'. Expected only 1.")

        self.__g.triples.remove(potential_instances[0])

    def remove_link(self, root_alias: str, role: str, argument_alias: str):
        """ Removes an instance. Use with caution, as this may cause a fragmented graph."""
        item_to_remove = None
        for i in range(len(self.__g.triples)):
            if self.__g.triples[i][0] == root_alias and self.__g.triples[i][1] == role and self.__g.triples[i][
                2] == argument_alias:
                item_to_remove = self.__g.triples[i]
                break

        if item_to_remove is not None:
            self.__g.triples.remove(item_to_remove)
            return

        raise Exception(f"Failed to find link ({root_alias}, {role}, {argument_alias})")

    def get_instance_value(self, instance_id: str):
        """Replaces a value of an instance"""
        instance_alias = get_variable_name(instance_id)
        for i in range(len(self.__g.triples)):
            if self.__g.triples[i][0] == instance_alias and self.__g.triples[i][1] == self.instance_role:
                return self.__g.triples[i][2]
        raise Exception(f"Failed to find instance with alias {instance_alias}")

    def update_instance_value(self, instance_id: str, instance_value: str):
        """Replaces a value of an instance"""
        if not instance_value:
            raise Exception("Can't update container with instance value that is empty!")

        instance_alias = get_variable_name(instance_id)
        for i in range(len(self.__g.triples)):
            if self.__g.triples[i][0] == instance_alias and self.__g.triples[i][1] == self.instance_role:
                self.__g.triples[i] = penman.Triple(instance_alias, self.instance_role, instance_value)
                return
        raise Exception(f"Failed to find instance with alias '{instance_alias}'")

    def replace_parents_roles_to_instance(self, instance_id, old_role, new_role) -> bool:
        """Finds instance with 'instance_id', then finds all instances pointing to it with old_role
        and changes those roles to new_role"""
        instance_alias = get_variable_name(instance_id)
        for i in range(len(self.__g.triples)):
            if self.__g.triples[i][1] == old_role and self.__g.triples[i][2] == instance_alias:
                self.__g.triples[i] = penman.Triple(self.__g.triples[i][0], new_role, instance_alias)
                return True
        return False

    def replace_instance(self, instance_id: str, new_id: str):
        """Replaces an instance and all its references. Resource-consuming operation, however acceptable if low number of references"""
        self.remove_instance(instance_id)
        instance_alias = get_variable_name(instance_id)
        new_alias = get_variable_name(new_id)

        # now replace all references
        for reference in list(x for x in self.__g.triples if x[0] == instance_alias or x[2] == instance_alias):
            self.remove_link(reference[0], reference[1], reference[2])
            if reference[0] == instance_alias:
                if len(list(x for x in self.__g.triples if
                            x[0] == new_alias and x[1] == reference[1] and x[2] == reference[2])) == 0 and new_alias != \
                        reference[2]:
                    self.__inner_add(new_alias, reference[1], reference[2])
            else:
                if len(list(x for x in self.__g.triples if
                            x[2] == new_alias and x[1] == reference[1] and x[0] == reference[0])) == 0 and new_alias != \
                        reference[0]:
                    self.__inner_add(reference[0], reference[1], new_alias)

    def __str__(self):
        return penman.encode(self.__g, indent=4)
