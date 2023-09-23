from common.constants import DEV_MODE
from tables import phoneme_flags
from util.util import matches_bitmask


def dev_print(message):
    if DEV_MODE:
        print(message)


def phoneme_has_flag(phoneme, flag):
    return matches_bitmask(phoneme_flags[phoneme], flag)
