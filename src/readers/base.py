import typing


def parse_string(empty_symbol: str, line, i):
    return parse_string([empty_symbol], line, i)


def parse_string(empty_symbols: typing.List, line, i):
    value = str(line[i])
    return '' if value in empty_symbols else value