from Container import TripletContainer
from conllu import parse, parse_incr
from conllu.parser import DEFAULT_FIELDS, DEFAULT_FIELD_PARSERS
import penman
import os
import typing
from Configuration import PropBankPipeConfigReader
from ConlluInterface import *
from Delegators import RuleDelegatorPropBank

def parse_string(value):
    valueStr = str(value)
    if (valueStr == '_'):
        return ''
    return str(value)

# Need to either define all from here https://www.aclweb.org/anthology/W04-2412.pdf or add manual check for undefined
# Maps propbank arguments to AMR notation
DEFAULT_CONLLU_ARGUMENT_MAPPING = {
    'A0': 'ARG0',
    'A1': 'ARG1',
    'A2': 'ARG2',
    'A3': 'ARG3',
    'A4': 'ARG4',
    'AM-LOC': 'location',
    'AM-DIR': 'direction',
    'AM-TMP': 'time', # this might have other meanings, investigate later
    'AM-CAU': 'cause',
    'AM-MNR' : 'manner',
    'AM-EXT' : 'extent',
}
#AM-ADV : genral-purpose
#AM-MOD : modal verb
#AM-NEG : negation marker
#AM-PNC : purpose
#AM-DIS : discourse marker
#AM-PRD : predication
#AM-REC : reciprocal

# Words related to a word in AMR will be added with given role if they have this deprel
DEFAULT_CONLLU_DEPREL_MAPPING = {
    'nmod': 'mod',
    'amod': 'mod'
}


class PipeBase:
    """This defines a pipes interface"""
    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        pass;

class PropBankPipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding some things from underlying treebank"""
    def __init__(self, config_reader: PropBankPipeConfigReader):
        self.__config_reader = config_reader
        # ToDo: add possibility to override these defaults

        # collnu parsers defaults dont contain the last field which shows arguments of propbank
        self.DEFAULT_FIELD_PARSERS = DEFAULT_FIELD_PARSERS.copy()
        self.DEFAULT_FIELD_PARSERS['arg'] = lambda line, i: parse_string(line[i])
        self.DEFAULT_FIELDS = DEFAULT_FIELDS + ('arg',)

        # Rules in the form of delegates that can easily be extended
        self.DEFAULT_RULES = {
            RuleDelegatorPropBank(self.related_word_mapping_rule),
            RuleDelegatorPropBank(self.polarity_rule)
        }

    def __map_conllu_arguments(self, value):
        if (value in DEFAULT_CONLLU_ARGUMENT_MAPPING):
            return DEFAULT_CONLLU_ARGUMENT_MAPPING[value]
        return 'Please_define_in_mapping_' + value

    # Use the propbank as base for our amr (root verb and its arguments).
    # Then rules add some additional information from treebank that propbank is basing on
    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        data_file = open(self.__config_reader.get_conllu_file(), "r", encoding="utf-8")

        try:
            # defaults are used to get propbank data, as parse_incr by default is pure conllu
            for token_list in parse_incr(data_file, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS):
                sentence = TokenSentence(token_list)
                container = TripletContainer(token_list.metadata)

                # Add root verb, which is identified by existing propbank frame verb (only one exists per sentence)
                root_word = sentence.get_root()
                root = list(root_word.misc)[0]
                root_alias = container.add_root(root)
                self.process_rules(root_alias, root_word, container, sentence)

                # Add arguments based on propbank argument field. Most propbank roles can be mapped, some can not
                for argument_word in sentence.read_root_arguments():
                    word_alias = container.add_instance(root_alias, self.__map_conllu_arguments(argument_word.arg), argument_word.form)
                    self.process_rules(word_alias, argument_word, container, sentence)

                triplet_list.append(container)
        finally:
            data_file.close()

        return triplet_list

    # All rules are evaluated for every word added, recursive adding is supported here
    def process_rules(self, word_alias: str, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        for rule in self.DEFAULT_RULES:
            rule.evaluate(word_alias, word, container, sentence)

    # Some words with treebank deprel can be mapped, so look if mapping contains entries and do it
    def related_word_mapping_rule(self, word_alias, word: TokenWord, container, sentence):
        for related_word in sentence.read_words_with_head(word.id):
            if (related_word.deprel in DEFAULT_CONLLU_DEPREL_MAPPING):
                new_alias = container.add_instance(word_alias, DEFAULT_CONLLU_DEPREL_MAPPING[related_word.deprel], related_word.form)
                self.process_rules(new_alias, related_word, container, sentence)
            else:
                print("Warning: failed to find mapping for deprel - " + related_word.deprel)

    # Check every word if it has a polarity flag and translate it to amr
    def polarity_rule(self, word_alias: str, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        if (word.feats != None and 'Polarity' in word.feats and word.feats['Polarity'] == 'Neg'):
            container.add(word_alias, ':polarity', '-')
