from common.constants import BREAK, END
from parser_engine.constants import FLAG_PUNCT
from parser_engine.util import phoneme_has_flag


def insert_breath(get_phoneme, set_phoneme, insert_phoneme, set_stress, get_length, set_length):
    """
    :param get_phoneme: Callback for retrieving phonemes
    :param set_phoneme: Callback for setting phonemes
    :param insert_phoneme: Callback for inserting phonemes
    :param set_stress: Callback for setting phoneme stress
    :param get_length: Callback for getting phoneme length
    :param set_length: Callback for setting phoneme length
    :return:
    """
    mem54 = 255
    len_val = 0  # mem55
    pos = -1

    while True:
        pos += 1
        index = get_phoneme(pos)
        if index == END:
            break

        len_val += get_length(pos)

        if len_val < 232:
            if phoneme_has_flag(index, FLAG_PUNCT):
                len_val = 0
                insert_phoneme(pos + 1, BREAK, 0, 0)
                continue

            if index == 0:
                mem54 = pos

            continue

        pos = mem54
        set_phoneme(pos, 31)  # 'Q*' (glottal stop)
        set_length(pos, 4)
        set_stress(pos, 0)
        len_val = 0
        insert_phoneme(pos + 1, BREAK, 0, 0)
