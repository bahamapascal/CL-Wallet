import sys
from pretty_print import colors, PrettyPrint
from keyboard_interceptor import KeyboardInterruptHandler

_ver = sys.version_info

is_py2 = (_ver[0] == 2)

is_py3 = (_ver[0] == 3)


def fetch_user_input(text):
    if is_py2:
        return raw_input(text)

    return input(text)


def pretty_print(text, *args, **kwargs):
    if 'color' in kwargs:
        # Might need to check if its a supported color
        return PrettyPrint(text, *args, **dict(kwargs, color=colors[kwargs['color']]))

    return PrettyPrint(text, *args, **kwargs)


def intercept_keyboard_interrupts(callback):
    return KeyboardInterruptHandler(callback)


def is_string(string):
    return isinstance(string, basestring) if is_py2 else isinstance(string, str)


def confirms(value):
    """
    :param value: string
    :return boolean: 
    """
    as_lower = value.lower() if is_string(value) else str(value).lower()
    return as_lower == 'y' or as_lower == 'yes'
