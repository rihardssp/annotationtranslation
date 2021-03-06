import logging
import typing
from src.configuration import config_reader
from src.container.penman_triplet_container import TripletContainer
from src.container.base import IContainer, ContainerStatistic
from src.delegates import ArgumentDelegate
from src.mapping_defaults.propbank import IPropBankMapping, PropBankMapping
from src.pipes.base import PipeBase
from src.readers.propbank import IPropBankAnnotationReaderBase, PropBankFileAnnotationReader
from src.sentences.propbank import IPropBankWord, IPropBankSentence


class PropBankPipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding
    some things from underlying treebank """

    def __init__(self, mapping: IPropBankMapping = None, annotation_reader: IPropBankAnnotationReaderBase = None):
        super().__init__()
        self.mapping: IPropBankMapping = mapping if mapping is not None \
            else PropBankMapping()
        self.annotation_reader: IPropBankAnnotationReaderBase = annotation_reader if annotation_reader is not None \
            else PropBankFileAnnotationReader(config_reader.get_propbank_resource_file_path())
        self.__logger = logging.getLogger(config_reader.get_logger_name("PropBankPipe"))

    # Use the PropBank as base for our amr (root verb and its arguments).
    # Then rules add some additional information from TreeBank that PropBank is basing on
    def _process_amr(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:

        for sentence in self.annotation_reader.read():
            # Add root verb, which is identified by existing PropBank frame verb (only one exists per sentence)
            root_word = sentence.get_root()

            # container = Sentence.GetFrameCount()
            if root_word is not None:
                container = TripletContainer(sentence.metadata)
                container.set_stat(ContainerStatistic.SENTENCE_TOKEN_TOTAL_COUNT, len(sentence.list_of_words))
                container.set_stat(ContainerStatistic.FRAME_TOTAL_COUNT, sentence.frame_count)
                self.add_root(root_word, container, sentence)
                container_list.append(container)
            else:
                self.__logger.info(f"Sentence '{sentence.text}' does not have a root")
        return container_list

    def add_root(self, root_word: IPropBankWord, container: IContainer, sentence: IPropBankSentence):
        """Adds root element and """
        if container.has_instance(root_word.id):
            return

        root = root_word.misc_first_value
        # container.FrameCount++
        container.add_root(root_word.id, root)

        # add arguments of this root
        argument_words = sentence.get_arguments(root_word.id)[1]
        for argument_word in argument_words:
            self.add_argument(root_word, argument_word, container, sentence)

        # add roots pointing to this root
        self.back_track(root_word, container, sentence)

        # Do some extra processing and get arguments of root
        self.process_rules(root_word, container, sentence)

    def add_argument(self, root_word: IPropBankWord, argument_word: IPropBankWord, container: IContainer,
                     sentence: IPropBankSentence):
        """Recursively inserts arguments based on existing PropBank"""

        if argument_word.arg in self.mapping.get_argument_action_mapping():
            mapping_action = self.mapping.get_argument_action_mapping()[argument_word.arg]

            # The argument word is already in container, just add link and don't continue
            if container.has_instance(argument_word.id):
                container.add_link(root_word.id, mapping_action.default_mapping, argument_word.id)
                return

            # Mapping action will add argument as a verb if it has one.
            # Conveniently, we find this by searching for sub-arguments one step early
            (new_root, new_argument_list) = sentence.get_arguments(argument_word.id)
            argument_to_add = new_root if new_root is not None else argument_word

            # Rule processing happens only if mapping_definitions is default. Evaluation also adds word to container if necessary
            run_rules = self.execute_action_mapping(mapping_action, root_word, argument_to_add, container, sentence)

            for new_argument_word in new_argument_list:
                self.add_argument(argument_to_add, new_argument_word, container, sentence)

            # Rules are secondary to arguments, hence add them last (easier to detect overlaps)
            if run_rules:
                self.process_rules(argument_to_add, container, sentence)

            # If word was added then add all roots pointing to this word
            if container.has_instance(argument_word.id):
                self.back_track(argument_word, container, sentence, root_word.id)
        else:
            self.__logger.info(f"Did not find propbank argument role mapping_definitions {argument_word.arg}")

    def back_track(self, child_word: IPropBankWord, container: IContainer, sentence: IPropBankSentence,
                   argument_parent_word_id: int = -1):
        """Goes back one level if there's a mapping between new parent and root"""

        roots = sentence.get_roots_of_argument(child_word.id)
        for root in list(x for x in roots if x.id != argument_parent_word_id):

            # Verify that root will be connected to an existing instance in some way
            root_link_to_graph = next((x for x in sentence.get_arguments(root.id)[1]
                                       if x.arg in self.mapping.get_argument_action_mapping()
                                       and container.has_instance(x.id)),
                                      None)

            if root_link_to_graph is not None:
                self.add_root(root, container, sentence)

    def execute_action_mapping(self, mapping_action: ArgumentDelegate, root_word: IPropBankWord,
                               argument_word: IPropBankWord, container,
                               sentence) -> bool:
        if mapping_action.delegate is None:
            is_root = argument_word.has_verb
            container.add_instance(root_word.id, argument_word.id, mapping_action.default_mapping,
                                   argument_word.misc_first_value if is_root else argument_word.lemma)
            return True

        mapping_action.evaluate(self, root_word, argument_word, container, sentence)
        return False

    # All rules are evaluated for every word added, recursive adding is supported here
    def process_rules(self, word: IPropBankWord, container: IContainer, sentence: IPropBankSentence):
        for rule in self.mapping.get_rules():
            rule.evaluate(self, word, container, sentence)
