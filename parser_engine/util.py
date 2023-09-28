from common.constants import DEV_MODE
from parser_engine.tables import phoneme_flags
from util_package.util_file import matches_bitmask


def dev_print(message):
    if DEV_MODE:
        print(message)


def phoneme_has_flag(phoneme, flag):
    # if out of bounds
    if phoneme < 0 or phoneme >= len(phoneme_flags):
        return False
    return matches_bitmask(phoneme_flags[phoneme], flag)


def set_list(l, i, v):
    try:
        l[i] = v
    except IndexError:
        for _ in range(i - len(l) + 1):
            l.append(None)
        l[i] = v
