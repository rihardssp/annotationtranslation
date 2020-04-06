from conllu import parse_incr
from conllu.parser import DEFAULT_FIELDS, DEFAULT_FIELD_PARSERS
import typing

from Code.Configuration import PropBankPipeConfigReader, UniversalDependencyPipeConfigReader
from Code.ConlluInterface import TokenSentence, TokenWord
from Code.Container import TripletContainer
from Code.Mappings import PropbankMappings


class PipeBase:
    """This defines a pipes interface"""

    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        pass


class PropBankPipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, config_reader: PropBankPipeConfigReader, mappings: PropbankMappings):
        self.__config_reader = config_reader
        self.mappings = mappings

        # collnu parsers defaults dont contain the last field which shows arguments of propbank
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS['arg'] = lambda line, i: ('' if str(line[i]) == '_' else str(line[i]))
        self.DEFAULT_FIELDS = DEFAULT_FIELDS + ('arg',)

    def read_amr(self) -> typing.List[TokenSentence]:
        sentence_list: typing.List[TokenSentence] = []
        data_file = open(self.__config_reader.get_propbank_conllu_file_path(), "r", encoding="utf-8")

        try:
            # defaults are used to get propbank data, as parse_incr by default is pure conllu
            for token_list in parse_incr(data_file, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS):
                sentence = TokenSentence(token_list)

                # Might want to optimise this in the future, as this is O(n^2)
                same_sentence = list(x for x in sentence_list if x.sent_id == sentence.sent_id)
                if len(same_sentence) == 0:
                    sentence_list.append(sentence)
                else:
                    same_sentence[0].add_token(token_list)

        finally:

            data_file.close()

        return sentence_list

    # Use the propbank as base for our amr (root verb and its arguments).
    # Then rules add some additional information from treebank that propbank is basing on
    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:

        for sentence in self.read_amr():
            container = TripletContainer(sentence.metadata)

            # Add root verb, which is identified by existing propbank frame verb (only one exists per sentence)
            root_word = sentence.get_root()
            self.add_root(root_word, container, sentence)

            triplet_list.append(container)

        return triplet_list

    def add_root(self, root_word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        """Adds root element and """
        if container.has_instance(root_word.id):
            return

        root = root_word.misc_first_value
        container.add_root(root_word.id, root)

        # Root word isn't necessary here, as first root definitely has verb definition
        argument_words = sentence.get_arguments(root_word.id)[1]
        for argument_word in argument_words:
            self.add_argument(root_word, argument_word, container, sentence)

        # Do some extra processing and get arguments of root
        self.process_rules(root_word, container, sentence)

    def add_argument(self, root_word: TokenWord, argument_word: TokenWord, container: TripletContainer,
                     sentence: TokenSentence):
        """Recursively inserts arguments based on existing PropBank"""

        if argument_word.arg in self.mappings.argument_action_mapping:
            mapping_action = self.mappings.argument_action_mapping[argument_word.arg]

            # The argument word is already in container, just add link and don't continue
            if container.has_instance(argument_word.id):
                mapping_action.evaluate(self, root_word, argument_word, container, sentence)
                return

            # Mapping action will add argument as a verb if it has one.
            # Conveniently, we find this by searching for sub-arguments one step early
            (new_root, new_argument_list) = sentence.get_arguments(argument_word.id)
            argument_to_add = new_root if new_root is not None else argument_word

            # Rule processing happens only if mapping is default. Evaluation also adds word to container if necessary
            run_rules = mapping_action.evaluate(self, root_word, argument_to_add, container, sentence)

            for new_argument_word in new_argument_list:
                self.add_argument(argument_to_add, new_argument_word, container, sentence)

            # Rules are secondary to arguments, hence add them last (easier to detect overlaps)
            if run_rules:
                self.process_rules(argument_to_add, container, sentence)

            # If word was added then add all roots pointing to this word
            if container.has_instance(argument_word.id):
                roots = sentence.get_roots_of_argument(argument_word.id)
                for root in list(x for x in roots if x.id != root_word.id):
                    self.add_root(root, container, sentence)

        else:
            print(f"Failed to find propbank argument role mapping {argument_word.arg}")

    # All rules are evaluated for every word added, recursive adding is supported here
    def process_rules(self, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        for rule in self.mappings.rules:
            rule.evaluate(self, word, container, sentence)


class UniversalDependencyPipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, config_reader: UniversalDependencyPipeConfigReader):
        self.__config_reader = config_reader

    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        data_file = open(self.__config_reader.get_ud_conllu_file_path(), "r", encoding="utf-8")

        for token_list in parse_incr(data_file):
            sentence = TokenSentence(token_list)
            container_candidates = list(filter(lambda x: x.sent_id == sentence.sent_id, triplet_list))
            if len(container_candidates) == 1:
                container = container_candidates[0]
                words_in_container = container.get_instance_ids()

            else:
                print(f"failed to find container for sentence with id:{sentence.sent_id}")

        return triplet_list
