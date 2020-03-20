import penman
import typing
from conllu import TokenList

class TripletContainer:
    """Implementation of intermediate storage using triplets that will be later serializet to graph"""

    def __init__(self, metadata):
        """Metadata will be printed with AMR sentences"""
        self.__g = penman.Graph()
        self.__g.metadata = metadata
        self.__variable_count = 0;
        self.instance_role = ':instance'
        pass;

    def generate_variable_name(self):
        self.__variable_count += 1
        return f'v{self.__variable_count}'

    def add_root(self, name_of_root):
        """Root verb of AMR"""
        root_alias = self.generate_variable_name()
        self.__g.triples.append(penman.Triple(root_alias, self.instance_role, name_of_root))
        return root_alias

    def add(self, name_alias, role, argument):
        """Add an argument to a instance, for ex., polarity"""
        self.__g.triples.append(penman.Triple(name_alias, role, argument))

    def add_instance(self, name_alias, role, argument_instance):
        """Add an instance (differs from add by defining an alias for given argument_instance)"""
        argument_alias = self.generate_variable_name()
        self.__g.triples.append(penman.Triple(argument_alias, self.instance_role, argument_instance))
        self.__g.triples.append(penman.Triple(name_alias, role, argument_alias))
        return argument_alias

    def print(self, file: typing.TextIO = None):
        """Printing to console/file/etc"""
        result = str(penman.encode(self.__g, indent=4))
        if (file != None):
            file.write(result + '\n\n')

        print(result)