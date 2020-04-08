import penman
import typing


def get_variable_name(id: str):
    return f'v{id}'


class TripletContainer:
    """Implementation of intermediate storage using triplets that will be later serializet to graph"""
    sent_id = property(lambda self: self.__g.metadata['sent_id'])

    def __init__(self, metadata):
        """Metadata will be printed with AMR sentences"""
        self.__g = penman.Graph()
        self.__g.metadata = metadata
        self.instance_role = ':instance'
        self.__generated_id = 0

    def add_root(self, root_id: str, name_of_root):
        """Root verb of AMR"""
        root_alias = get_variable_name(root_id)
        self.__g.triples.append(penman.Triple(root_alias, self.instance_role, name_of_root))

    def add(self, instance_id: str, role, argument):
        """Add an argument to a instance, for ex., polarity"""
        self.__g.triples.append(penman.Triple(get_variable_name(instance_id), role, argument))

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

    def has_instance(self, instance_id: str) -> bool:
        instance_name = get_variable_name(instance_id)
        instances = list(x for x in self.__g.triples if x[1] == self.instance_role and x[0] == instance_name)
        return len(instances) > 0

    def print(self, file: typing.TextIO = None):
        """Printing to console/file/etc"""
        result = str(penman.encode(self.__g, indent=4))
        if file is not None:
            file.write(result + '\n\n')
        else:
            print(result)

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
