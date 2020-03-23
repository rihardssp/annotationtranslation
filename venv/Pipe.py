from Container import TripletContainer
from conllu import parse, parse_incr
from conllu.parser import DEFAULT_FIELDS, DEFAULT_FIELD_PARSERS
import penman
import os
import typing
from Configuration import *
from ConlluInterface import *
from Delegators import RuleDelegatorPropBank, ArgumentDelegatorPropBank

def parse_string(value):
    valueStr = str(value)
    if (valueStr == '_'):
        return ''
    return str(value)

# Need to either define all from here https://www.aclweb.org/anthology/W04-2412.pdf or add manual check for undefined
# Maps propbank arguments to AMR notation
DEFAULT_CONLLU_ARGUMENT_MAPPING = {
    'A0': ArgumentDelegatorPropBank(None, 'ARG0'),
    'A1': ArgumentDelegatorPropBank(None, 'ARG1'),
    'A2': ArgumentDelegatorPropBank(None, 'ARG2'),
    'A3': ArgumentDelegatorPropBank(None, 'ARG3'),
    'A4': ArgumentDelegatorPropBank(None, 'ARG4'),
    'AM-LOC': ArgumentDelegatorPropBank(None, 'location'),
    'AM-DIR': ArgumentDelegatorPropBank(None, 'direction'),
    'AM-CAU': ArgumentDelegatorPropBank(None, 'cause'),
    'AM-MNR' : ArgumentDelegatorPropBank(None, 'manner'),
    'AM-EXT' : ArgumentDelegatorPropBank(None, 'extent')
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

        self.DEFAULT_ARGUMENT_MAPPING = DEFAULT_CONLLU_ARGUMENT_MAPPING
        self.DEFAULT_ARGUMENT_MAPPING.update({'AM-TMP': ArgumentDelegatorPropBank(self.time_argument_rule, 'time')})

        # Rules in the form of delegates that can easily be extended
        self.DEFAULT_RULES = {
            RuleDelegatorPropBank(self.related_word_mapping_rule),
            RuleDelegatorPropBank(self.polarity_rule)
        }

    # Use the propbank as base for our amr (root verb and its arguments).
    # Then rules add some additional information from treebank that propbank is basing on
    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        data_file = open(self.__config_reader.get_propbank_conllu_file_path(), "r", encoding="utf-8")

        try:
            # defaults are used to get propbank data, as parse_incr by default is pure conllu
            for token_list in parse_incr(data_file, self.DEFAULT_FIELDS, self.DEFAULT_FIELD_PARSERS):
                sentence = TokenSentence(token_list)
                container = TripletContainer(token_list.metadata)

                # Add root verb, which is identified by existing propbank frame verb (only one exists per sentence)
                root_word = sentence.get_root()
                root = list(root_word.misc)[0]
                container.add_root(root_word.id, root)
                self.process_rules(root_word, container, sentence)

                # Add arguments based on propbank argument field. Most propbank roles can be mapped, some can not
                for argument_word in sentence.read_root_arguments():
                    if argument_word.arg in DEFAULT_CONLLU_ARGUMENT_MAPPING:
                        mapping = DEFAULT_CONLLU_ARGUMENT_MAPPING[argument_word.arg]

                        # Rule processing happens only if mapping is default
                        if (mapping.evaluate(root_word, argument_word, container, sentence)):
                            self.process_rules(argument_word, container, sentence)
                    else:
                        print(f"Failed to find propbank argument role mapping {argument_word.arg}")


                triplet_list.append(container)
        finally:
            data_file.close()

        return triplet_list

    def time_argument_rule(self, root_word: TokenWord, argument_word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        related_words = sentence.read_words_with_head(argument_word.id)
        if argument_word.lemma == 'gads':
            ordinal_number = list(filter(lambda x: x.NumType == 'Ord', related_words))
            if len(ordinal_number) == 1:
                container.add_instance(root_word.id, 55, "time", "date-entity")
                container.add(55, "year", ordinal_number[0].form)
        #container.add_instance(root_word.id, argument_word.id, "time", argument_word.form)

    # All rules are evaluated for every word added, recursive adding is supported here
    def process_rules(self, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        for rule in self.DEFAULT_RULES:
            rule.evaluate(word, container, sentence)

    # Some words with treebank deprel can be mapped, so look if mapping contains entries and do it
    def related_word_mapping_rule(self, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        for related_word in sentence.read_words_with_head(word.id):
            if (related_word.deprel in DEFAULT_CONLLU_DEPREL_MAPPING):
                container.add_instance(word.id, related_word.id, DEFAULT_CONLLU_DEPREL_MAPPING[related_word.deprel], related_word.form)
                self.process_rules(related_word, container, sentence)
            else:
                print("Warning: failed to find mapping for deprel - " + related_word.deprel)

    # Check every word if it has a polarity flag and translate it to amr
    def polarity_rule(self, word: TokenWord, container: TripletContainer, sentence: TokenSentence):
        if (word.feats != None and 'Polarity' in word.feats and word.feats['Polarity'] == 'Neg'):
            container.add(word.id, ':polarity', '-')

class UniversalDependencyPipe(PipeBase):
    """This is the initial pipe, which creates the base of AMR by using propbank verb and its arguments and adding some things from underlying treebank"""
    def __init__(self, config_reader: UniversalDependencyPipeConfigReader):
        self.__config_reader = config_reader

    def process_amr(self, triplet_list: typing.List[TripletContainer]) -> typing.List[TripletContainer]:
        data_file = open(self.__config_reader.get_ud_conllu_file_path(), "r", encoding="utf-8")

        for token_list in parse_incr(data_file):
            sentence = TokenSentence(token_list)
            container_candidates = list(filter(lambda x: x.sent_id == sentence.sent_id , triplet_list))
            if len(container_candidates) == 1:
                container = container_candidates[0]
                words_in_container = container.get_instance_ids()
                
            else:
                print(f"failed to find container for sentence with id:{sentence.sent_id}")


        return triplet_list