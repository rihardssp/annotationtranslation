import typing
from conllu import TokenList


class TokenWord:
    """Simplifies usage of tokens as they're tuples -- Gui hints needed with these awful names"""

    def __init__(self, token):
        self.token = token

    misc = property(lambda self: self.token['misc'])
    lemma = property(lambda self: self.token['lemma'])
    arg = property(lambda self: self.token['arg'])
    head = property(lambda self: self.token['head'])
    id = property(lambda self: self.token['id'])
    deprel = property(lambda self: self.token['deprel'])
    form = property(lambda self: self.token['form'])
    feats = property(lambda self: self.token['feats'])

    misc_first_value = property(lambda self: list(self.misc)[0])
    num_type = property(lambda self: (self.feats['NumType'] if self.feats != None and 'NumType' in self.feats else None))
    has_verb = property(lambda self: self.misc is not None and self.misc != '')
    has_arg = property(lambda self: self.arg is not None and self.arg != '')
    has_misc = property(lambda self: self.misc is not None and len(self.misc) > 0)


    def __getitem__(self, key):
        return self.token[key]


class TokenSentence:
    """Logic for getting certain things from conllu sentence"""

    sent_id = property(lambda self: self.__token_list.metadata['sent_id'])
    metadata = property(lambda self: self.__token_list.metadata)

    def __init__(self, token_list: TokenList):
        self.sentence_list: typing.List[typing.List[TokenWord]] = []
        self.add_token(token_list)
        self.__token_list = token_list

    def add_token(self, token_list: TokenList):
        """This will contain all token_lists that belong to a single sentence"""
        self.sentence_list.append(list(TokenWord(x) for x in token_list))

    def get_root(self) -> TokenWord:
        """propbank root verb - verb with smallest head number"""
        min_head = 10000
        root = None

        for sentence in self.sentence_list:
            for word in sentence:
                if word.has_verb and word.head < min_head:
                    min_head = word.head
                    root = word

        return root

    def get_arguments(self, head_id: int) -> (TokenWord, typing.List[TokenWord]):
        """If head_id is root, return root word with its arguments"""

        args = list()
        root_word: TokenWord = None

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
        return (root_word, args)

    def read_words_with_head(self, head_id) -> typing.List[TokenWord]:
        """TreeBank words with given head_id"""
        args = list()
        for token in self.sentence_list[0]:
            if token.head is not None and token.head == head_id:
                args.append(token)
        return args

    def get_roots_of_argument(self, argument_id) -> typing.List[TokenWord]:
        """Find roots of a given argument"""
        l: typing.List[TokenWord] = []
        for sentence in self.sentence_list:
            if len(list(x for x in sentence if x.id == argument_id and x.has_arg)) > 0:
                l.append(list(x for x in sentence if x.has_verb)[0])
        return l

