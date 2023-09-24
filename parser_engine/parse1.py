from parser_engine.util import dev_print
from parser_engine.tables import phoneme_name_table, stress_table


def full_match(sign1, sign2):
    """
    Match both characters but not with wildcards.

    :param sign1:
    :param sign2:
    :return: Number
    """
    index = next((i for i, value in enumerate(phoneme_name_table) if value == sign1 + sign2 and value[1] != '*'), -1)
    return index if index != -1 else False


def wild_match(sign1):
    index = next((i for i, value in enumerate(phoneme_name_table) if value == sign1 + '*'), -1)
    return index if index != -1 else False


def parser1(input_str, add_phoneme, add_stress):
    """
    The input[] buffer contains a string of phonemes and stress markers along the lines of:
        DHAX KAET IHZ AH5GLIY.

    Some phonemes are 2 bytes long, such as "DH" and "AX".
    Others are 1 byte long, such as "T" and "Z".
    There are also stress markers, such as "5" and ".".

    The characters of the phonemes are stored in the table PhonemeNameTable.
    The stress characters are arranged in low to high stress order in StressTable[].

    The following process is used to parse the input buffer:

    Repeat until the end is reached:
        1. First, a search is made for a 2 character match for phonemes that do not end with the '*' (wildcard)
        character. On a match, the index of the phoneme is added to the result and the buffer position is advanced
        2 bytes.
        2. If this fails, a search is made for a 1 character match against all phoneme names ending with a '*'. If
        this succeeds, the phoneme is added to result and the buffer position is advanced 1 byte.
        3.If this fails, search for a 1 character match in the stressInputTable[]. If this succeeds, the stress
        value is placed in the last stress[] table at the same index of the last added phoneme, and the buffer
        position is advanced by 1 byte.

    If this fails, return false.

    On success:
        1. phonemeIndex[] will contain the index of all the phonemes.
        2. The last index in phonemeIndex[] will be 255.
        3. stress[] will contain the stress value for each phoneme

    input holds the string of phonemes, each two bytes wide
    signInputTable1[] holds the first character of each phoneme
    signInputTable2[] holds the second character of each phoneme
    phonemeIndex[] holds the indexes of the phonemes after parsing input[]

    The parser scans through the input[], finding the names of the phonemes
    by searching signInputTable1[] and signInputTable2[]. On a match, it
    copies the index of the phoneme into the phonemeIndexTable[].

    :param input_str: Holds the string of phonemes, each two bytes wide
    :param add_phoneme: The callback to use to store phoneme index values
    :param add_stress: The callback to use to store stress index values
    :return: None
    """
    src_pos = 0
    while src_pos < len(input_str):
        tmp = input_str.lower()
        dev_print(f"processing \"{tmp[:src_pos]}%c{tmp[src_pos:src_pos+2].upper()}%c{tmp[src_pos+2:]}\"")

        sign1 = input_str[src_pos]
        sign2 = input_str[src_pos + 1] if src_pos + 1 < len(input_str) else ''
        match = full_match(sign1, sign2)

        if match is not False:
            # Matched both characters (no wildcards)
            src_pos += 1  # Skip the second character of the input as we have matched it already
            add_phoneme(match)
            continue

        match = wild_match(sign1)

        if match is not False:
            # Matched the first character and the second is '*'
            add_phoneme(match)
            continue

        # Should be a stress character. Search through the stress table backwards
        match = len(stress_table)
        while sign1 != stress_table[match] and match > 0:
            match -= 1

        if match == 0:
            dev_print(f"Could not parse char {sign1}")
            raise Exception()

        add_stress(match)  # Set the stress for the prior phoneme
        src_pos += 1

