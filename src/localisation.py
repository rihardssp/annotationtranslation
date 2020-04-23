import typing
import i18n

from src.configuration import config_reader

DEFAULT_SEPARATOR = ';'


class Localisation:

    def __init__(self):
        i18n.load_path.append(config_reader.get_localisation_resource_path())
        i18n.set("locale", config_reader.get_localisation_locale())
        i18n.set("fallback", config_reader.get_localisation_fallback())

    def get_localised_list(self, key: str, separator: str = DEFAULT_SEPARATOR) -> typing.List[str]:
        """Simple way of getting dictionary from string. Format: 'key;value;key;value;key;value'"""
        value = i18n.t(key)
        if value == key:
            raise Exception(f"key '{key}' not found in resource files")
        return value.split(separator)


localisation = Localisation()
