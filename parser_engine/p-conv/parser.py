from tables import (
    sign_input_table1,
    sign_input_table2,
    stress_input_table,
    flags,
    phoneme_length_table,
    phoneme_stressed_length_table
)

from parser_engine.constants import (
    pR,
    pD,
    pT,
    FLAG_8000,
    FLAG_4000,
    FLAG_FRICATIVE,
    FLAG_LIQUIC,
    FLAG_NASAL,
    FLAG_ALVEOLAR,
    FLAG_0200,
    FLAG_PUNCT,
    FLAG_VOWEL,
    FLAG_CONSONANT,
    FLAG_DIP_YX,
    FLAG_DIPTHONG,
    FLAG_0008,
    FLAG_VOICED,
    FLAG_STOPCONS,
    FLAG_UNVOICED_STOPCONS,
)

from common.constants import (BREAK, END)

from util.util import text_to_uint8_array


def full_match(sign1, sign2):
    Y = 0
    while Y != 81:
        # Get first character at position Y in sign_input_table
        # TODO: Should change name to phoneme_name_table1
        A = sign_input_table1[Y]

        if A == sign1:
            A = sign_input_table2[Y]
            # Check if it's not a special character and matches second character
            if A != 42 and A == sign2:
                return Y
        Y += 1
    return -1


def wild_match(sign1):
    Y = 0
    while Y != 81:
        if sign_input_table2[Y] == 42:
            if sign_input_table1[Y] == sign1:
                return Y
        Y += 1
    return -1


def parser1(input_data):
    """
    Parse an input array of phonemes and stress markers

    :param input_data: The input array of phonemes and stress markers
    :return: A dictionary containing 'phoneme_index' and 'stress' arrays, or None on failure
    """
    phoneme_index = bytearray(256)
    stress = bytearray(256)

    # Clear the stress table
    for i in range(256):
        stress[i] = 0

    position = 0
    src_pos = 0
    while input_data[src_pos] != 0x9B:  # 0x9B marks the end of the buffer
        sign1 = input_data[src_pos]
        src_pos += 1
        sign2 = input_data[src_pos]

        match = full_match(sign1, sign2)
        if match != -1:
            # Matched both characters (no wildcards)
            phoneme_index[position] = match
            position += 1
            src_pos += 1  # Skip second character of the input as we've matched it
        else:
            match = wild_match(sign1)
            if match != -1:
                # Matched just first character (with the second character matching '*')
                phoneme_index[position] = match
                position += 1
            else:
                # Should be a stress character. Search through the stress table backwards.
                match = 8  # End of stress table. FIXME: Don't hardcode this value
                while sign1 != stress_input_table[match] and match > 0:
                    match -= 1

                if match == 0:
                    return None  # Failure

                stress[position - 1] = match  # Set stress for previous phoneme

    # End of parsing, mark end of phoneme_index table with 255
    phoneme_index[position] = 255

    return {'phoneme_index': phoneme_index, 'stress': stress}


# Example usage:
input_data = bytearray([
    0x44, 0x48, 0x41, 0x58, 0x20, 0x4B,
    0x41, 0x45, 0x54, 0x20, 0x49, 0x48,
    0x5A, 0x20, 0x41, 0x48, 0x35, 0x47,
    0x4C, 0x49, 0x59, 0x2E, 0x20, 0x9B
 ])
result = parser1(input_data)
if result:
    print(result['phoneme_index'])
    print(result['stress'])
else:
    print("Parsing failed.")
