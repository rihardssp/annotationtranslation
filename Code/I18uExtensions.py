import typing
import i18n

separator = ';'


def string_to_dictionary(key: str) -> typing.Dict[str, str]:
    """Simple way of getting dictionary from string. Format: 'key;value;key;value;key;value'"""
    value = i18n.t(key)
    values_arr = value.split(separator)
    return {values_arr[i]: values_arr[i+1] for i in range(0, len(values_arr), 2)}
