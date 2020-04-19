import typing
from abc import abstractmethod, ABC

from Code.delegates import ArgumentDelegate, RuleDelegate


# Need to either define all from here https://www.aclweb.org/anthology/W04-2412.pdf or add manual check for undefined
# Maps propbank arguments to AMR notation
from Code.mapping_definitions.propbank import time_argument_action, related_word_mapping_rule, polarity_rule

DEFAULT_PROP_BANK_ACTION_MAPPING = {
    'A0': ArgumentDelegate(None, 'ARG0'),
    'A1': ArgumentDelegate(None, 'ARG1'),
    'A2': ArgumentDelegate(None, 'ARG2'),
    'A3': ArgumentDelegate(None, 'ARG3'),
    'A4': ArgumentDelegate(None, 'ARG4'),
    'AM-LOC': ArgumentDelegate(None, 'location'),
    'AM-DIR': ArgumentDelegate(None, 'direction'),
    'AM-CAU': ArgumentDelegate(None, 'cause'),
    'AM-MNR': ArgumentDelegate(None, 'manner'),
    'AM-EXT': ArgumentDelegate(None, 'extent'),
    'AM-TMP': ArgumentDelegate(time_argument_action, 'time')
}

# AM-ADV : genral-purpose
# AM-MOD : modal verb
# AM-NEG : negation marker
# AM-PNC : purpose
# AM-DIS : discourse marker
# AM-PRD : predication
# AM-REC : reciprocal


# Rules in the form of delegates that can easily be extended
DEFAULT_RULES = {
    RuleDelegate(related_word_mapping_rule),
    RuleDelegate(polarity_rule)
}


# Words related to a word in AMR will be added with given role if they have this deprel
DEFAULT_CONLLU_DEPREL_MAPPING = {
    'nmod': 'mod',
    'amod': 'mod'
}


class IPropBankMapping(ABC):
    """This class contains mapping_definitions and actions which propbank uses to transform PropBank to AMR"""

    @abstractmethod
    def get_argument_action_mapping(self) -> typing.Dict[str, ArgumentDelegate]:
        pass

    @abstractmethod
    def get_deprel_mapping(self) -> typing.Dict[str, str]:
        pass

    @abstractmethod
    def get_rules(self) -> typing.List[RuleDelegate]:
        pass


class PropBankMapping(IPropBankMapping):
    """This class contains mapping_definitions and actions which propbank uses to transform PropBank to AMR"""

    def __init__(self, argument_action_mapping: typing.Dict[str, ArgumentDelegate] = None,
                 deprel_mapping: typing.Dict[str, str] = None,
                 rules: typing.List[RuleDelegate] = None):
        self.__argument_action_mapping = \
            argument_action_mapping if argument_action_mapping is not None else DEFAULT_PROP_BANK_ACTION_MAPPING

        self.__deprel_mapping = \
            deprel_mapping if deprel_mapping is not None else DEFAULT_CONLLU_DEPREL_MAPPING

        self.__rules = \
            rules if rules is not None else DEFAULT_RULES

    def get_argument_action_mapping(self) -> typing.Dict[str, ArgumentDelegate]:
        return self.__argument_action_mapping

    def get_deprel_mapping(self) -> typing.Dict[str, str]:
        return self.__deprel_mapping

    def get_rules(self) -> typing.List[RuleDelegate]:
        return self.__rules