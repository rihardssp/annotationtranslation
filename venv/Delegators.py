from Container import TripletContainer
from ConlluInterface import *

class RuleDelegatorPropBank:
    """These rules are run for each word to look for additional things to add, for example, nmod, polarity, etc"""
    def __init__(self, delegate):
        if (callable(delegate)):
            self.delegate = delegate
        else:
            raise Exception("Delegate initialized with non-callable argument")

    def evaluate(self, word, container: TripletContainer, sentence: TokenSentence):
        self.delegate(word, container, sentence)


class ArgumentDelegatorPropBank:
    """Rules to adding an argument. Default is simply using the default mapping available"""
    def __init__(self, delegate, default_mapping: str):
        if (delegate == None or callable(delegate)):
            self.delegate = delegate
            self.default_mapping = default_mapping
        else:
            raise Exception("Delegate initialized with non-callable argument")

    def evaluate(self, root_word: TokenWord, argument_word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        if (self.delegate != None):
            self.delegate(root_word, argument_word, container, sentence)
            return False

        container.add_instance(root_word.id, argument_word.id, self.default_mapping, argument_word.form)
        return True