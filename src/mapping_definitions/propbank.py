import logging

from src.configuration import config_reader
from src.container.base import IContainer
from src.localisation import localisation
from src.words.base import IWord
from src.sentences.propbank import IPropBankWord, IPropBankSentence

__logger = logging.getLogger(config_reader.get_logger_name("PropBankMappingDefinitions"))

def time_argument_action(pipe, root_word: IPropBankWord, argument_word: IPropBankWord,
                         container: IContainer, sentence: IPropBankSentence):

    related_words = sentence.read_words_with_head(argument_word.id)
    mapping_keys_template = "mapping.time_argument_action."
    mapping_value = ["year", "month", "day", "century", "decade", "era", "quarter"]
    mapping_value_month = range(1, 13)

    # TODO: what about calendar, dayperiod, season, timezone, weekday, year-year2
    ordinal_number = list(filter(lambda x: x.is_num_type_ordinal, related_words))
    cardinal_number = list(filter(lambda x: x.is_num_type_cardinal, related_words))

    if len(ordinal_number) > 0:
        # We map language specific terms to AMR date-entity arguments. Simple case
        for key in mapping_value:
            if argument_word.lemma.lower() in localisation.get_localised_list(mapping_keys_template + key):
                time_argument_action_date_entity(key, root_word.id, argument_word.id, container,
                                                 ordinal_number[0].lemma)
                return

        # Special cases
        # This is the 'september 22nd' format
        for key in mapping_value_month:
            if argument_word.lemma.lower() in localisation.get_localised_list(f"{mapping_keys_template}month_{key}"):
                time_argument_action_date_entity('month', root_word.id, argument_word.id, container, str(key))
                container.add(argument_word.id, ':day', ordinal_number[0].lemma)
                return

        # All else has failed, so just treat it as ordinal number
        if len(cardinal_number) == 0:
            cardinal_number = ordinal_number
            __logger.warning(f"word '{cardinal_number[0].form}' was treated as cardinal number "
                      f"even though it is ordinal. Perhaps {mapping_keys_template} mapping_definitions needs update?")

    # Temporal-quantity
    if len(cardinal_number) > 0:
        time_argument_action_card(root_word.id, argument_word.id, container, argument_word.lemma,
                                  cardinal_number[0].lemma)
        return

    # all other cases just use :time
    container.add_instance(root_word.id, argument_word.id, "time", argument_word.lemma)


def time_argument_action_date_entity(mapping_value: str, root_id: str, argument_id: str, container: IContainer,
                                     ordinal_value: str):
    container.add_instance(root_id, argument_id, "time", "date-entity")
    container.add(argument_id, mapping_value, ordinal_value)


def time_argument_action_card(root_id: str, argument_id: str, container: IContainer, cardinal_unit: str,
                              quantity: str):
    container.add_instance(root_id, argument_id, "time", "temporal-quantity")
    container.add_instance(argument_id, container.get_generated_id(), "unit", cardinal_unit)
    container.add(argument_id, 'quant', quantity)


# Some words with treebank deprel can be mapped, so look if mapping_definitions contains entries and do it
def related_word_mapping_rule(pipe, word: IWord, container: IContainer, sentence: IPropBankSentence):
    for related_word in sentence.read_words_with_head(word.id):
        # argument might already have a different role for this word
        if container.has_link(word.id, related_word.id):
            continue

        if related_word.deprel in pipe.mapping.get_deprel_mapping():
            container.add_instance(word.id, related_word.id, pipe.mapping.get_deprel_mapping()[related_word.deprel],
                                   related_word.lemma)
            pipe.process_rules(related_word, container, sentence)


# Check every word if it has a polarity flag and translate it to amr
def polarity_rule(pipe, word: IWord, container: IContainer, sentence: IPropBankSentence):
    if word.feats is not None and 'Polarity' in word.feats and word.feats['Polarity'] == 'Neg':
        container.add(word.id, ':polarity', '-')