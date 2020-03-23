import penman
import typing
from conllu import TokenList

class TripletContainer:
    """Implementation of intermediate storage using triplets that will be later serializet to graph"""
    sent_id = property(lambda self: self.__g.metadata['sent_id'])

    def __init__(self, metadata):
        """Metadata will be printed with AMR sentences"""
        self.__g = penman.Graph()
        self.__g.metadata = metadata
        self.instance_role = ':instance'
        pass;

    def get_variable_name(self, id):
        return f'v{id}'

    def add_root(self, root_id:int, name_of_root):
        """Root verb of AMR"""
        root_alias = self.get_variable_name(root_id)
        self.__g.triples.append(penman.Triple(root_alias, self.instance_role, name_of_root))

    def add(self, head_id, role, argument):
        """Add an argument to a instance, for ex., polarity"""
        self.__g.triples.append(penman.Triple(self.get_variable_name(head_id), role, argument))

    def add_instance(self, head_id, id: int, role, argument_instance):
        """Add an instance (differs from add by defining an alias for given argument_instance)"""
        argument_alias = self.get_variable_name(id)
        self.__g.triples.append(penman.Triple(argument_alias, self.instance_role, argument_instance))
        self.__g.triples.append(penman.Triple(self.get_variable_name(head_id), role, argument_alias))

    def print(self, file: typing.TextIO = None):
        """Printing to console/file/etc"""
        result = str(penman.encode(self.__g, indent=4))
        if (file != None):
            file.write(result + '\n\n')
        else:
            print(result)

    def get_instance_ids(self):
        """Printing to console/file/etc"""
        l = list()

        for triplet in self.__g.triples:
            if (triplet[1] == ':instance'):
                l.append(triplet[1][1:])

        return l