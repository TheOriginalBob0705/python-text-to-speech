from common.constants import END
from parser_engine.constants import FLAG_VOWEL, FLAG_CONSONANT
from parser_engine.util import phoneme_has_flag


def copy_stress(get_phoneme, get_stress, set_stress):
    """
    Iterates through the phoneme buffer, copying the stress value from the following phoneme under the following
    circumstances:
        1. The current phoneme is voiced, excluding plosives and fricatives
        2. The following phoneme is voiced, excluding plosives and fricatives, and
        3. The following phoneme is stressed

    In those cases, the stress value + 1 from the following phoneme is copied

    For example, the word LOITER is represented as LOY5TER, with a stress of 5 on the dipthong OY. This routine will
    copy the stress value of 6 (5 + 1) to the L that precedes it

    :param get_phoneme: Callback for retrieving phonemes
    :param get_stress: Callback for retrieving phoneme stress
    :param set_stress: Callback for setting phoneme stress
    :return:
    """
    position = 0
    phoneme = None

    while (phoneme := get_phoneme(position)) != END:
        if phoneme_has_flag(phoneme, FLAG_CONSONANT):
            following_phoneme = get_phoneme(position + 1)
            if following_phoneme != END and phoneme_has_flag(following_phoneme, FLAG_VOWEL):
                stress = get_stress(position + 1)
                if stress != 0 and stress < 0x80:
                    set_stress(position, stress + 1)
        position += 1
