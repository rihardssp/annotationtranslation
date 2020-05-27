import sys
import typing
from abc import abstractmethod

from conllu import TokenList

from src.sentences.base import ISentence, TokenSentenceBase
from src.words.propbank import PropBankTokenWord, IPropBankWord, PropBankMergedTokenWord


class IPropBankSentence(ISentence):
    """Interface for PropBank sentence logic"""

    @abstractmethod
    def get_root(self) -> IPropBankWord:
        pass

    @abstractmethod
    def get_arguments(self, head_id: int) -> (IPropBankWord, typing.List[IPropBankWord]):
        pass

    @abstractmethod
    def read_words_with_head(self, head_id) -> typing.List[IPropBankWord]:
        pass

    @abstractmethod
    def get_roots_of_argument(self, argument_id) -> typing.List[IPropBankWord]:
        pass

    @property
    @abstractmethod
    def list_of_words(self) -> typing.List[IPropBankWord]:
        pass

    @property
    @abstractmethod
    def frame_count(self) -> int:
        pass


class PropBankTokenSentence(TokenSentenceBase, IPropBankSentence):
    """Propbank specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.word_list: typing.List[IPropBankWord] = None
        self.frame_list: typing.List[(IPropBankWord, typing.List[IPropBankWord])] = []

    def get_root(self) -> IPropBankWord:
        """propbank root verb - verb with smallest head number.
            ToDo: This should be based on either verb with head == 0 OR biggest graph in PropBank!"""
        #for verb_args_tuple in self.frame_list:
        #    if verb_args_tuple[0].id == 0:
        #        return verb_args_tuple[0]

        # ToDo: first verb instead?
        min_head = sys.maxsize
        for verb_args_tuple in self.frame_list:
            if verb_args_tuple[0].head < min_head:
                min_head = verb_args_tuple[0].head
                root = verb_args_tuple[0]

        return root

    def get_arguments(self, head_id: int) -> (PropBankTokenWord, typing.List[IPropBankWord]):
        """If head_id is root, return root word with its arguments"""

        # While recursively adding, the root word is necessary as instead of the word the verb is added, which does
        # not exist in returned arguments even if they're roots (as only one verb per frame, which obviously cant be
        # argument as root is one)
        for verb_args_tuple in self.frame_list:
            if verb_args_tuple[0].id == head_id:
                return verb_args_tuple[0], verb_args_tuple[1]

        return None, []

    def read_words_with_head(self, head_id) -> typing.List[IPropBankWord]:
        """TreeBank words with given head_id"""
        args = list()
        for token in self.word_list:
            if token.head is not None and token.head == head_id:
                args.append(token)
        return args

    def get_roots_of_argument(self, argument_id) -> typing.List[IPropBankWord]:
        """Find roots of a given argument"""
        root_list: typing.List[IPropBankWord] = []

        for verb_args_tuple in self.frame_list:
            for argument in verb_args_tuple[1]:
                if argument.id == argument_id:
                    root_list.append(verb_args_tuple[0])

        return root_list

    def add_token(self, token_list):
        """This will contain all token_lists that belong to a single sentence"""
        temp_word_list = list(PropBankTokenWord(x) for x in token_list)

        # The rest are stored as frame_argument tuples
        if self.word_list is None:
            self.word_list = temp_word_list

        frame_verb = next(x for x in temp_word_list if x.has_verb)
        if frame_verb is None:
            raise Exception(f"A frame without a verb? '{token_list}'")

        arguments = list(x for x in temp_word_list if x.has_arg)
        self.frame_list.append((frame_verb, arguments))

    @property
    def list_of_words(self) -> typing.List[IPropBankWord]:
        """Gets a sentence with PropBank words. Note: not all verbs might be present"""
        return self.word_list

    @property
    def frame_count(self) -> int:
        """Gets a sentence with PropBank words. Note: not all verbs might be present"""
        return len(self.frame_list)


class PropBankMergedTokenSentence(PropBankTokenSentence, IPropBankSentence):
    """ Uses the super class logic and transforms the merged format into logical structure that would be perceived as superclasses case"""

    def __init__(self, token_list: TokenList, argument_size: int):
        super().__init__(token_list)
        verb_number = 0
        for token in token_list:
            word = PropBankMergedTokenWord(token, 0)

            # This word is a PropBank verb, so we add a symbol to represent it in the respective context
            if word.inner_verb != "":
                word.add_symbol(verb_number)
                verb_number += 1
        self.word_list.append(list(PropBankMergedTokenWord(x, 0) for x in token_list))

        # Emulate the multiple lists of standard PropBankToken sentence
        for i in range(1, argument_size):
            self.word_list.append(list(x.switch_context(i) for x in self.word_list[0]))
