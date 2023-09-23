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


def parser1(input_data, phoneme_index, stress):
    """
    Parse an input array of phonemes and stress markers.

    The input[] buffer contains a string of phonemes and stress markers along the lines of:
        DHAX KAET IHZ AH5GLIY. <0x9B>

    The byte 0x9B marks the end of the buffer.

    Some phonemes are 2 bytes long, such as "DH" and "AX". Others are 1 byte long, such as "T" and "Z".
    There are also stress markers, such as "5" and ".".

    The first character of the phonemes are stored in the table sign_input_table1[]
    The second character of the phonemes are stored in the table sign_input_table2[]
    The stress characters are arranged in low to high stress order in stress_input_table[]

    The following process is used to parse the input[] buffer:

    Repeat until the <0x9B> character:
        First, a search is made for a 2 character match to phonemes that do not end with the '*' (wildcard) character.
        On a match, the index of the phoneme is added to phoneme_index[] and the buffer position is advanced 2 bytes.

        If this fails, a search is made for a 1 character match against all phonemes ending with a '*'. If this
        succeeds, the phoneme is added to phoneme_index[] and the buffer position is advanced 1 byte.

        If this fails, search for a 1 character match in the stress_input_table[]. If this succeeds, the stress value
        is placed in the last stress[] table at the same index of the last added phoneme, and the buffer position is
        advanced by 1 byte.

        If this fails, return a 0.

    On success:
        1. phoneme_index[] will contain the index of all the phonemes.
        2. The last index in phoneme_index will be 255.
        3. stress[] will contain the stress value for each phoneme

    input[] holds the string of phonemes, each two bytes wide
    sign_input_table1[] holds the first character of each phoneme
    sign_input_table2[] holds the second character of each phoneme
    phoneme_index[] holds the indexes of the phonemes after parsing input[]

    The parser scans through the input[], finding the names of the phonemes by searching sign_input_table1[] and
    sign_input_table2[]. On a match, it copies the index of the phoneme into the phoneme_index_table[]

    The character <0x9B> marks the end of text in input[]. When it is reached, the index 255 is placed at the end of
    the phoneme_index_table[], and the function returns with a 1 indicating success


    :param input_data: The input array of phonemes and stress markers
    :param phoneme_index: Uint8Array
    :param stress: Uint8Array
    :return: A dictionary containing 'phoneme_index' and 'stress' arrays, or None on failure
    """
    # Clear the stress table
    for i in range(256):
        stress[i] = 0

    position = 0
    src_pos = 0
    while input_data[src_pos] != 155:  # 155 (\233) is the end-of-line marker
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
                    return 0  # Failure

                stress[position - 1] = match  # Set stress for previous phoneme

    # End of parsing, mark end of phoneme_index table with 255
    phoneme_index[position] = 255

    return 1


