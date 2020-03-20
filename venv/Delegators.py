from Container import TripletContainer
from ConlluInterface import TokenSentence

class RuleDelegatorPropBank:
    """These rules are run for each word to look for additional things to add, for example, nmod, polarity, etc"""
    def __init__(self, delegate):
        if (callable(delegate)):
            self.delegate = delegate
        else:
            raise Exception("Delegate initialized with non-callable argument")

    def evaluate(self, word_alias: str, token, container: TripletContainer, sentence: TokenSentence):
        self.delegate(word_alias, token, container, sentence)
