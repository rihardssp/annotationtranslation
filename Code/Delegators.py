from Code.ConlluInterface import TokenSentence, TokenWord
from Code.Container import TripletContainer


class RuleDelegatorPropBank:
    """These rules are run for each word to look for additional things to add, for example, nmod, polarity, etc"""

    def __init__(self, delegate):
        if callable(delegate):
            self.delegate = delegate
        else:
            raise Exception("Delegate initialized with non-callable argument")

    def evaluate(self, pipe, word, container: TripletContainer, sentence: TokenSentence):
        self.delegate(pipe, word, container, sentence)


class ArgumentDelegatorPropBank:
    """Rules to adding an argument. Default is simply using the default mapping available"""

    def __init__(self, delegate: RuleDelegatorPropBank, default_mapping: str):
        if delegate is None or callable(delegate):
            self.delegate = delegate
            self.default_mapping = default_mapping
        else:
            raise Exception("Delegate initialized with non-callable argument")

    def evaluate(self, pipe, root_word: TokenWord, argument_word: TokenWord, container: TripletContainer,
                 sentence: TokenSentence):
        if self.delegate is not None:
            self.delegate(pipe, root_word, argument_word, container, sentence)
            return False

        # ToDo: test whether adding link works with a defined delegate above ^
        is_root = argument_word.has_misc
        container.add_instance(root_word.id, argument_word.id, self.default_mapping,
                               argument_word.misc_first_value if is_root else argument_word.lemma)

        return True
