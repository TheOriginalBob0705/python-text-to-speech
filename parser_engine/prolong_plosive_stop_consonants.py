from common.constants import END
from parser_engine.tables import combined_phoneme_length_table
from parser_engine.constants import FLAG_0008, FLAG_STOPCONS, FLAG_UNVOICED_STOPCONS
from parser_engine.util import phoneme_has_flag


def prolong_plosive_stop_consonants_code_41240(get_phoneme, insert_phoneme, get_stress):
    pos = -1
    index = None
    while (index := get_phoneme(pos + 1)) != END:
        # Not a stop consonant, move to the next one
        if not phoneme_has_flag(index, FLAG_STOPCONS):
            pos += 1
            continue
        # If plosive, move to the next non-empty phoneme and validate the flags
        if phoneme_has_flag(index, FLAG_UNVOICED_STOPCONS):
            next_non_empty = None
            X = pos
            while  (next_non_empty := get_phoneme(X + 1)) == 0:
                X += 1
            # If not END and either flag 0x0008 or '/H' or '/X'
            if (
                next_non_empty != END
                and (
                    phoneme_has_flag(next_non_empty, FLAG_0008)
                    or next_non_empty == 36
                    or next_non_empty == 37
                )
            ):
                pos += 1
                continue
        insert_phoneme(pos + 1, index + 1, get_stress(pos), combined_phoneme_length_table[index + 1] & 0xFF)
        insert_phoneme(pos + 2, index + 2, get_stress(pos), combined_phoneme_length_table[index + 2] & 0xFF)
        pos += 2
