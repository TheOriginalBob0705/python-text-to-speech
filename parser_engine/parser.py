from common.constants import BREAK, END, DEV_MODE
from parser_engine.util import dev_print
from parser_engine.tables import phoneme_name_table
from parser_engine.parse1 import parser1
from parser_engine.parse2 import parser2
from parser_engine.adjust_lengths import adjust_lengths
from parser_engine.copy_stress import copy_stress
from parser_engine.set_phoneme_length import set_phoneme_length
from parser_engine.insert_breath import insert_breath
from parser_engine.prolong_plosive_stop_consonants import prolong_plosive_stop_consonants_code_41240


def parser(input_string):
    if not input_string:
        return False

    stress = []  # numbers from  0 to 8
    phoneme_length = []
    phoneme_index = []

    pos = 0

    def get_phoneme(pos):
        if DEV_MODE:
            if pos < 0 or pos >= len(phoneme_index):
                raise ValueError('Out of bounds: ' + str(pos))
        return END if pos == len(phoneme_index) - 1 else phoneme_index[pos]

    def set_phoneme(pos, value):
        dev_print(f"{pos} CHANGE: {phoneme_name_table[phoneme_index[pos]]} -> {phoneme_name_table[value]}")
        phoneme_index[pos] = value

    def insert_phoneme(pos, value, stress_value, length = 0):
        dev_print(f"{pos} INSERT: {phoneme_name_table[value]}")
        for i in range(len(phoneme_index) - 1, pos - 1, -1):
            phoneme_index[i + 1] = phoneme_index[i]
            phoneme_length[i + 1] = phoneme_length[i]
            stress[i + 1] = get_stress(i)
        phoneme_index[pos] = value
        phoneme_length[pos] = length
        stress[pos] = stress_value

    def get_stress(pos):
        return stress[pos] if pos < len(stress) else 0

    def set_stress(pos, stress_value):
        dev_print(f"{pos} \"{phoneme_name_table[phoneme_index[pos]]}\" SET STRESS: {stress[pos]} -> {stress_value}")
        stress[pos] = stress_value

    def get_length(pos):
        return phoneme_length[pos] if pos < len(phoneme_length) else 0

    def set_length(pos, length):
        dev_print(f"{pos} \"{phoneme_name_table[phoneme_index[pos]]}\" SET LENGTH: {phoneme_length[pos]} -> {length}")
        if DEV_MODE:
            if (length & 128) != 0:
                raise ValueError("Got the flag 0x80, see CopyStress() and SetPhonemeLength() comments!")
            if pos < 0 or pos > len(phoneme_index):
                raise ValueError("Out of bounds: " + str(pos))
        phoneme_length[pos] = length

    def process_phoneme(value):
        stress.append(0)
        phoneme_length.append(0)
        phoneme_index.append(value)
        pos = len(phoneme_index) - 1  # Update pos to the index of the newly added phoneme

    def process_stress(value):
        if DEV_MODE:
            if (value & 128) != 0:
                raise ValueError('Got the flag 0x80, see CopyStress() and SetPhonemeLength() comments!')
        stress[-1] = value  # Set stress for the prior phoneme

    parser1(
        input,
        process_phoneme,
        process_stress
    )
    phoneme_index.append(END)

    if DEV_MODE:
        print_phonemes(phoneme_index, phoneme_length, stress)

    parser2(insert_phoneme, set_phoneme, get_phoneme, get_stress)
    copy_stress(get_phoneme, get_stress, set_stress)
    set_phoneme_length(get_phoneme, get_stress, set_length)
    adjust_lengths(get_phoneme, set_length, get_length)
    prolong_plosive_stop_consonants_code_41240(get_phoneme, insert_phoneme, get_stress)

    for i in range(len(phoneme_index)):
        if phoneme_index[i] > 80:
            phoneme_index[i] = END
            break  # error: delete all behind it

    insert_breath(get_phoneme, set_phoneme, insert_phoneme, get_stress, get_length, set_length)

    if DEV_MODE:
        print_phonemes(phoneme_index, phoneme_length, stress)

    return [(v, phoneme_length[i], stress[i]) for i, v in enumerate(phoneme_index)]


def print_phonemes(phoneme_index, phoneme_length, stress):
    def pad(num):
        s = "000" + str(num)
        return s[-3:]

    print("==================================")
    print("Internal Phoneme presentation:")
    print(" pos  idx  phoneme  length  stress")
    print("----------------------------------")
    for i in range(len(phoneme_index)):
        def name(phoneme):
            if phoneme_index[i] < 81:
                return phoneme_name_table[phoneme_index[i]]
            if phoneme == BREAK:
                return "  "
            return "??"

        print(
            f" {pad(i)}  {pad(phoneme_index[i])}  {name(phoneme_index[i])}       {pad(phoneme_length[i])}     {pad(stress[i])}"
        )
    print("==================================")
