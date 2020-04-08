import typing

from Code.ConlluInterface import TokenWord, TokenSentence
from Code.Container import TripletContainer
from Code.Delegators import ArgumentDelegatorPropBank, RuleDelegatorPropBank


from Code.I18uExtensions import string_to_dictionary


def time_argument_rule(pipe, root_word: TokenWord, argument_word: TokenWord, container: TripletContainer,
                       sentence: TokenSentence):
    related_words = sentence.read_words_with_head(argument_word.id)

    time_mapping = string_to_dictionary('mappings.general.time_argument_rule_year')
    if argument_word.lemma in time_mapping.keys():
        ordinal_number = list(filter(lambda x: x.num_type == 'Ord', related_words))
        if len(ordinal_number) == 1:
            new_id = container.get_generated_id()
            container.add_instance(root_word.id, new_id, "time", "date-entity")
            container.add(new_id, "year", ordinal_number[0].lemma)


# Need to either define all from here https://www.aclweb.org/anthology/W04-2412.pdf or add manual check for undefined
# Maps propbank arguments to AMR notation
DEFAULT_CONLLU_ARGUMENT_ACTIONS_MAPPING = {
    'A0': ArgumentDelegatorPropBank(None, 'ARG0'),
    'A1': ArgumentDelegatorPropBank(None, 'ARG1'),
    'A2': ArgumentDelegatorPropBank(None, 'ARG2'),
    'A3': ArgumentDelegatorPropBank(None, 'ARG3'),
    'A4': ArgumentDelegatorPropBank(None, 'ARG4'),
    'AM-LOC': ArgumentDelegatorPropBank(None, 'location'),
    'AM-DIR': ArgumentDelegatorPropBank(None, 'direction'),
    'AM-CAU': ArgumentDelegatorPropBank(None, 'cause'),
    'AM-MNR': ArgumentDelegatorPropBank(None, 'manner'),
    'AM-EXT': ArgumentDelegatorPropBank(None, 'extent'),
    'AM-TMP': ArgumentDelegatorPropBank(time_argument_rule, 'time')
}

# AM-ADV : genral-purpose
# AM-MOD : modal verb
# AM-NEG : negation marker
# AM-PNC : purpose
# AM-DIS : discourse marker
# AM-PRD : predication
# AM-REC : reciprocal

# Words related to a word in AMR will be added with given role if they have this deprel
DEFAULT_CONLLU_DEPREL_MAPPING = {
    'nmod': 'mod',
    'amod': 'mod'
}


# Some words with treebank deprel can be mapped, so look if mapping contains entries and do it
def related_word_mapping_rule(pipe, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
    for related_word in sentence.read_words_with_head(word.id):
        # argument might already have a different role for this word
        if container.has_link(word.id, related_word.id):
            continue

        if related_word.deprel in pipe.mappings.deprel_mapping:
            container.add_instance(word.id, related_word.id, pipe.mappings.deprel_mapping[related_word.deprel],
                                   related_word.form)
            pipe.process_rules(related_word, container, sentence)
        else:
            print("Warning: failed to find mapping for deprel - " + related_word.deprel)


# Check every word if it has a polarity flag and translate it to amr
def polarity_rule(pipe, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
    if word.feats is not None and 'Polarity' in word.feats and word.feats['Polarity'] == 'Neg':
        container.add(word.id, ':polarity', '-')


# Rules in the form of delegates that can easily be extended
DEFAULT_RULES = {
    RuleDelegatorPropBank(related_word_mapping_rule),
    RuleDelegatorPropBank(polarity_rule)
}


class PropbankMappings:
    """This class contains mappings and actions which propbank uses to transform PropBank to AMR"""

    def __init__(self, argument_action_mapping: typing.Dict[str, ArgumentDelegatorPropBank] = None,
                 deprel_mapping: typing.Dict[str, str] = None,
                 rules: typing.List[RuleDelegatorPropBank] = None):
        self.argument_action_mapping = \
            argument_action_mapping if argument_action_mapping is not None else DEFAULT_CONLLU_ARGUMENT_ACTIONS_MAPPING

        self.deprel_mapping = \
            deprel_mapping if deprel_mapping is not None else DEFAULT_CONLLU_DEPREL_MAPPING

        self.rules = \
            rules if rules != None else DEFAULT_RULES