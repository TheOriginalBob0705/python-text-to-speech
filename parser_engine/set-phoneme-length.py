from tables import combined_phoneme_length_table
from common.constants import END


def set_phoneme_length(get_phoneme, get_stress, set_length):
    position = 0
    phoneme = None
    while (phoneme := get_phoneme(position)) != END:
        stress = get_stress(position)
        if stress == 0 or stress > 0x7F:
            set_length(position, combined_phoneme_length_table[phoneme] & 0xFF)
        else:
            set_length(position, combined_phoneme_length_table[phoneme] >> 8)
        position += 1
