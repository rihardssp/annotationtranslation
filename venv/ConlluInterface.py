import typing

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

    NumType = property(lambda self: self.feats['NumType'])

    def __getitem__(self, key):
        return self.token[key]

class TokenSentence:
    """Logic for getting certain things from conllu sentence"""

    sent_id = property(lambda self: self.__token_list.metadata['sent_id'])

    def __init__(self, token_list):
        l = list()
        for token in token_list:
            l.append(TokenWord(token))

        self.word_list = l
        self.__token_list = token_list

    def get_root(self) -> TokenWord:
        """propbank root verb"""
        for token in self.word_list:
            if (token.misc != None and token.misc != ''):
                return token

    def read_root_arguments(self) -> typing.List[TokenWord]:
        """Root verbs arguments"""
        args = list()
        for token in self.word_list:
            if (token.arg != None and token.arg != ''):
                args.append(token)
        return args

    def read_words_with_head(self, head_id) -> typing.List[TokenWord]:
        """TreeBank words with given head_id"""
        args = list()
        for token in self.word_list:
            if (token.head != None and token.head == head_id):
                args.append(token)
        return args