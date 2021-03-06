import configparser
import logging


def format_url_ending(value):
    """ During a configurato"""
    if value[-1:] != "/":
        value += "/"
    return value


def is_true(value: str) -> bool:
    return value.upper() == "TRUE"


class ConfigReader:
    """This class provides config reading functionality"""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("../config.ini")

    def __get_value(self, section, key):
        return self.config.get(section, key)

    def __get_default_value(self, key):
        return self.__get_value("Default", key)

    def get_output_file_path(self) -> str:
        return self.__get_default_value("OutputFile")

    def get_logger_name(self, child_logger_path: str = None):
        if child_logger_path:
            return f"{self.__get_default_value('LoggerName')}.{child_logger_path}"

        return self.__get_default_value('LoggerName')

    def get_logger_severity_level(self):
        # https://docs.python.org/3/howto/logging.html
        level = getattr(logging, self.__get_default_value('LoggerSeverityLevel').upper(), None)
        if not isinstance(level, int):
            raise ValueError(f"Invalid log level: {level}")
        return level

    # PropBank
    def __get_prop_bank_pipe_value(self, key):
        return self.__get_value("PropBankPipe", key)

    def get_propbank_resource_file_path(self):
        return self.__get_prop_bank_pipe_value("ResourceFile")

    # NamedEntities
    def __get_named_entities_pipe_value(self, key):
        return self.__get_value("NamedEntitiesPipe", key)

    def get_named_entities_resource_folder_path(self):
        return self.__get_named_entities_pipe_value("ResourceFolder")

    # CoReference
    def __get_co_reference_pipe_value(self, key):
        return self.__get_value("CoReferencePipe", key)

    def get_co_reference_resource_folder_path(self):
        return self.__get_co_reference_pipe_value("ResourceFolder")

    def get_co_reference_are_file_coreferences_cross_sentence(self) -> bool:
        return is_true(self.__get_co_reference_pipe_value("AreFileCoreferencesCrossSentence"))

    # RestletPhraseNormalizer
    def __get_restlet_phrase_normalizer_value(self, key):
        return self.__get_value("RestletPhraseNormalizer", key)

    def get_phrase_normalizer_cache_path(self):
        return self.__get_restlet_phrase_normalizer_value("CachePath")

    def get_phrase_normalizer_base_url(self):
        return format_url_ending(self.__get_restlet_phrase_normalizer_value("Url"))

    # Localisation
    def __get_localisation_value(self, key):
        return self.__get_value("Localisation", key)

    def get_localisation_resource_path(self):
        return self.__get_localisation_value("LocalisationResourcePath")

    def get_localisation_locale(self):
        return self.__get_localisation_value("Locale")

    def get_localisation_fallback(self):
        return self.__get_localisation_value("Fallback")


config_reader = ConfigReader()