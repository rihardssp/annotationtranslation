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
    def word_list(self) -> typing.List[IPropBankWord]:
        pass

    @property
    @abstractmethod
    def frame_count(self) -> int:
        pass

class PropBankTokenSentence(TokenSentenceBase, IPropBankSentence):
    """Propbank specific logic for reading sentences from Conllu"""

    def __init__(self, token_list: TokenList):
        super().__init__(token_list)
        self.sentence_list: typing.List[typing.List[IPropBankWord]] = []

    def get_root(self) -> IPropBankWord:
        """propbank root verb - verb with smallest head number.
            ToDo: This should be based on either verb with head == 0 OR biggest graph in PropBank!"""
        min_head = sys.maxsize
        root = None

        for sentence in self.sentence_list:
            for word in sentence:
                if word.has_verb and word.head < min_head:
                    min_head = word.head
                    root = word

        return root

    def get_arguments(self, head_id: int) -> (PropBankTokenWord, typing.List[IPropBankWord]):
        """If head_id is root, return root word with its arguments"""
        args = list()
        root_word: PropBankTokenWord = None

        # Look through each sentence to find one with root_id and existing PropBank verb
        for sentence in self.sentence_list:
            possible_root = list(x for x in sentence if x.id == head_id and x.has_verb)

            # Such a word exists in this sentence and we store the root_word and arguments
            if len(possible_root) > 0:
                root_word = possible_root[0]
                for token in sentence:
                    if token.has_arg:
                        args.append(token)

        # While recursively adding, the root word is necessary as instead of the word the verb is added, which does
        # not exist in returned arguments even if they're roots (as only one verb per frame, which obviously cant be
        # argument as root is one)
        return root_word, args

    def read_words_with_head(self, head_id) -> typing.List[IPropBankWord]:
        """TreeBank words with given head_id"""
        args = list()
        for token in self.sentence_list[0]:
            if token.head is not None and token.head == head_id:
                args.append(token)
        return args

    def get_roots_of_argument(self, argument_id) -> typing.List[IPropBankWord]:
        """Find roots of a given argument"""
        root_list: typing.List[IPropBankWord] = []
        for sentence in self.sentence_list:
            if len(list(x for x in sentence if x.id == argument_id and x.has_arg)) > 0:
                found_verb = list(x for x in sentence if x.has_verb)
                if len(found_verb) == 1:
                    root_list.append(found_verb[0])
        return root_list

    def add_token(self, token_list):
        """This will contain all token_lists that belong to a single sentence"""
        self.sentence_list.append(list(PropBankTokenWord(x) for x in token_list))

    @property
    def word_list(self) -> typing.List[IPropBankWord]:
        """Gets a sentence with PropBank words. Note: not all verbs might be present"""
        return self.sentence_list[0]

    @property
    def frame_count(self) -> int:
        """Gets a sentence with PropBank words. Note: not all verbs might be present"""
        return len(self.sentence_list)


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
        self.sentence_list.append(list(PropBankMergedTokenWord(x, 0) for x in token_list))

        # Emulate the multiple lists of standard PropBankToken sentence
        for i in range(1, argument_size):
            self.sentence_list.append(list(x.switch_context(i) for x in self.sentence_list[0]))
