import typing
import i18n

DEFAULT_SEPARATOR = ';'


def get_i18n_list(key: str, separator: str = DEFAULT_SEPARATOR) -> typing.List[str]:
    """Simple way of getting dictionary from string. Format: 'key;value;key;value;key;value'"""
    value = i18n.t(key)
    if value == key:
        raise Exception(f"key '{key}' not found in resource files")
    return value.split(separator)
