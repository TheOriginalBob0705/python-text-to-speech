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

from common.constants import (BREAK, END, DEVELOPMENT)

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


def parser1(input_data, data):
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
    :return: A dictionary containing 'phoneme_index' and 'stress' arrays, or None on failure
    """
    phoneme_index = data['phoneme_index']
    stress = data['stress']

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


def insert(data, position, index, length, stress_value):
    """
    Insert a phoneme at the given position.

    :param data: The data to populate
    :param position: The position in the phoneme arrays to insert the phoneme
    :param index: The phoneme index to insert
    :param length: The phoneme length to insert
    :param stress_value: The stress value to insert
    :return: None
    """
    phoneme_index = data['phoneme_index']
    phoneme_length = data['phoneme_length']
    stress = data['stress']

    # Always keep last safe-guarding 255
    for i in range(253, position - 1, -1):
        phoneme_index[i + 1] = phoneme_index[i]
        phoneme_length[i + 1] = phoneme_length[i]
        stress[i + 1] = stress[i]

    phoneme_index[position] = index
    phoneme_length[position] = length
    stress[position] = stress_value


def parser2(data):
    """
    Rewrites the phonemes using the following rules:
        <DIPTHONG ENDING WITH WX> -> <DIPTHONG ENDING WITH WX> WX
        <DIPTHONG NOT ENDING WITH WX> -> <DIPTHONG NOT ENDING WITH WX> YX
        UL -> AX L
        UM -> AX M
        <STRESSED VOWEL> <SILENCE> <STRESSED VOWEL> -> <STRESSED VOWEL> <SILENCE> Q <VOWEL>
        T R -> CH R
        D R -> J R
        <VOWEL> R -> <VOWEL> RX
        <VOWEL> L -> <VOWEL> LX
        G S -> G Z
        K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
        G <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
        S P -> S B
        S T -> S D
        S K -> S G
        S KX -> S GX
        CH -> CH CH' (CH requires two phonemes to represent it)
        J -> J J' (J requires two phonemes to represent it)
        <UNSTRESSED VOWEL> T <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>
        <UNSTRESSED VOWEL> D <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>

    :param
    :return: None
    """
    phoneme_index = data['phoneme_index']
    phoneme_length = data['phoneme_length']
    stress = data['stress']

    def rule_alveolar_uw(X):
        # Alveolar flag set?
        if (flags[phoneme_index[X - 1]] & FLAG_ALVEOLAR) != 0:
            if DEVELOPMENT == 1:
                print(f"{X} RULE: <ALVEOLAR> UW -> <ALVEOLAR> UX")
            phoneme_index[X] = 16

    def rule_ch(X):
        if DEVELOPMENT == 1:
            print(f"{X} RULE: CH -> CH CH+1")
        insert(phoneme_index, X + 1, 43, 0, stress[X])

    def rule_j(X):
        if DEVELOPMENT == 1:
            print(f"{X} RULE: J -> J J+1")
        insert(phoneme_index, X + 1, 45, 0, stress[X])

    def rule_g(pos):
        # G <VOWEL ORR DIPTHONG NOT ENDING WITH IY -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
        # Example: GO

        index = phoneme_index[pos + 1]

        # If dipthong ending with YX, continue processing next phoneme
        if (index != 255) and ((flags[index] & FLAG_DIP_YX) == 0):
            if DEVELOPMENT == 1:
                print(f"{pos} RULE: G <VOWEL OR DIPTHONG NOT ENDING WITH IY> "
                      f"-> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
            # Replace G with GX and continue processing next phoneme
            phoneme_index[pos] = 63  # 'GX'

    def rule_dipthong(p, pf, pos):
        # <DIPTHONG ENDING WITH WX> -> <DIPTHONG ENDING WITH WX> WX
        # <DIPTHONG NOT ENDING WITH WX> -> <DIPTHONG NOT ENDING WITH WX> YX
        # Example: OIL, COW

        # If ends with IY, use YX, else use WX
        A = 21 if (pf & FLAG_DIP_YX) != 0 else 20  # 'WX' = 20 'YX' = 21

        # Insert at WX or YX following, copying the stress
        if A == 20 and DEVELOPMENT == 1:
            print(f"{pos} insert WX following dipthong NOT ending in IY sound")
        if A == 21 and DEVELOPMENT == 1:
            print(f"{pos} insert YX following dipthong ending in IY sound")
        insert(phoneme_index, (pos + 1) & 0xFF, A, 0, stress[pos])

        if p in (53, 42, 44):
            if p == 53:
                # Example: NEW, DEW, SUE, ZOO, THOO, TOO
                rule_alveolar_uw(pos)
            elif p == 42:
                # Example: CHEW
                rule_ch(pos)  # TODO: figure out why original code has rule_ch(pos, 0) (might just be a C thing)
            elif p == 44:
                # Example: JAY
                rule_j(pos)

    def change_rule(position, rule, mem60, stress_value):
        if DEVELOPMENT == 1:
            print(
                f"{position} RULE: {chr(sign_input_table1[phoneme_index[position]])}{chr(sign_input_table2[phoneme_index[position]])} -> AX {chr(sign_input_table1[mem60])}{chr(sign_input_table2[mem60])}")
        position = position & 0xFF
        phoneme_index[position] = rule
        insert(phoneme_index, position + 1, mem60, 0, stress_value)

    pos = 0
    p = None

    while (p := phoneme_index[pos]) != END:
        if DEVELOPMENT == 1:
            print(f"{pos}: {chr(sign_input_table1[p])}{chr(sign_input_table2[p])}")

        if p == 0:  # Is phoneme pause?
            pos += 1
            continue

        pf = flags[p]
        prior = phoneme_index[pos - 1]

        if (pf & FLAG_DIPTHONG) != 0:
            rule_dipthong(p, pf, pos, 0)
        elif p == 78:
            # Example: MEDDLE
            if DEVELOPMENT == 1:
                print(f"{pos} RULE: UL -> AX L")
            change_rule(pos, 13, 24, stress[pos])
        elif p == 79:
            # Example: ASTRONOMY
            if DEVELOPMENT == 1:
                print(f"{pos} RULE: UM -> AX M")
            change_rule(pos, 13, 27, stress[pos])
        elif p == 80:
            if DEVELOPMENT == 1:
                print(f"{pos} RULE: UN -> AX N")
            change_rule(pos, 13, 28, stress[pos])
        elif (pf & FLAG_VOWEL) and stress[pos]:
            # RULE:
            # <STRESSED_VOWEL> <SILENCE> <STRESSED_VOWEL> -> <STRESSED VOWEL> <SILENCE> Q <VOWEL>
            # EXAMPLE:: AWAY EIGHT
            if not phoneme_index[pos + 1]:  # If following phoneme is a pause, get next
                p = phoneme_index[pos + 2]
                if p != END and (flags[p] & FLAG_VOWEL) != 0 and stress[pos + 2]:
                    if DEVELOPMENT == 1:
                        print(f"{pos + 2} Insert glottal stop between two stressed vowels with space between them")
                    insert(phoneme_index, pos + 2, 31, 0, 0)  # 31 = 'Q'
        elif p == pR:  # RULES FOR PHONEMES BEFORE R
            if prior == pT:
                # Example: TRACK
                if DEVELOPMENT == 1:
                    print(f"{pos} RULE: T* R* -> CH R*")
                phoneme_index[pos - 1] = 42
            elif prior == pD:
                # Example: DRY
                if DEVELOPMENT == 1:
                    print(f"{pos} RULE: D* R* -> J* R*")
                phoneme_index[pos - 1] = 44
            elif (flags[prior] & FLAG_VOWEL) != 0:
                # Example: ART
                if DEVELOPMENT == 1:
                    print(f"{pos} <VOWEL> R* -> <VOWEL> RX")
                phoneme_index[pos] = 18
        elif (p == 24) and ((flags[prior] & FLAG_VOWEL) != 0):
            # Example: ALL
            if DEVELOPMENT == 1:
                print(f"{pos} <VOWEL> L* -> <VOWEL> LX")
            phoneme_index[pos] = 19
        elif prior == 60 and p == 32:  # 'G' 'S'
            # Can't get to fire -
            # 1. The G -> GX rule intervenes
            # 2. Reciter already replaces GS -> GZ
            if DEVELOPMENT == 1:
                print(f"{pos} G S -> G Z")
            phoneme_index[pos] = 38
        elif p == 60:
            rule_g(pos)
        else:
            if p == 72:  # 'K'
                # K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
                # Example: COW
                Y = phoneme_index[pos + 1]
                # If, at the end, replace current phoneme with KX
                if (flags[Y] & FLAG_DIP_YX) == 0 or Y == END:
                    # VOWELS AND DIPTHONGS ENDING WITH IY SOUND flag set?
                    if DEVELOPMENT == 1:
                        print(f"{pos} K <VOWEL OR DIPTHONG NOT ENDING WITH IY> "
                              f"-> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
                    phoneme_index[pos] = 75
                    p = 75
                    pf = flags[p]

                # Replace with softer version?
                if (flags[p] & FLAG_UNVOICED_STOPCONS) and (prior == 32):  # 'S'
                    # RULE:
                    # S P -> S B
                    # S T -> S D
                    # S K -> S G
                    # S KX -> S GX
                    # Examples: SPY, STY, SKY, SCOWL
                    if DEVELOPMENT == 1:
                        print(f"{pos} S* {chr(sign_input_table1[p])}{chr(sign_input_table2[p])} "
                              f"-> S* {chr(sign_input_table1[p - 12])}{chr(sign_input_table2[p - 12])}")
                    phoneme_index[pos] = p - 12
                elif (pf & FLAG_UNVOICED_STOPCONS) == 0:
                    p = phoneme_index[pos]
                    if p == 53:
                        # Example: NEW, DEW, SUE, ZOO, THOO, TOO
                        rule_alveolar_uw(pos)
                    elif p == 42:
                        rule_ch(pos)
                    elif p == 44:
                        # Example: JAY
                        rule_j(pos)

                if p in (69, 57): # 'T', 'D'
                    # RULE: Soften T following vowel
                    # NOTE: This rule fails for cases such as "ODD"
                    # <UNSTRESSED VOWEL> T <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>
                    # <UNSTRESSED VOWEL> D <PAUSE>  -> <UNSTRESSED VOWEL> DX <PAUSE>
                    # Example: PARTY, TARDY
                    if (flags[phoneme_index[pos - 1]] & FLAG_VOWEL) != 0:
                        p = phoneme_index[pos + 1]
                        if not p:
                            p = phoneme_index[pos + 2]
                        if (flags[p] & FLAG_VOWEL) and not stress[pos + 1]:
                            if DEVELOPMENT == 1:
                                print(f"{pos} Soften T or D following vowel or ER and preceding a pause -> DX")
                            phoneme_index[pos] = 30

        pos += 1  # while


def copy_stress(data):
    """
    Iterates through the phoneme buffer, copying the stress value from the following phoneme under the following
    circumstances:
        1. The current phoneme is voiced, excluding plosives and fricatives
        2. The following phoneme is voiced, excluding plosives and fricatives, and
        3. The following phoneme is stressed

    In those cases, the stress value + 1 from the following phoneme is copied.

    For example, the word LOITER is represented as LOY5TER with a stress of 5 on the dipthong OY. This routine will
    copy the stress value of 6 (5 + 1) to the L that precedes it.

    :param data: The data to populate
    :return: None
    """
    phoneme_index = data['phoneme_index']
    stress = data['stress']

    pos = 0
    Y = None

    while (Y := phoneme_index[pos]) != END:
        # if CONSONANT_FLAG set, skip - only vowels get stress
        if (flags[Y] & 64) != 0:
            Y = phoneme_index[pos + 1]
            # if the following phoneme is the end or a vowel, skip
            if (Y != END) and (flags[Y] & 128) != 0:
                # get the stress value at the next position
                Y = stress[pos + 1]
                if Y and (Y & 128) == 0:
                    # if the next phoneme is stressed and a VOWEL OR ER,
                    # copy stress from the next phoneme to this one
                    stress[pos] = Y + 1
        pos += 1


def set_phoneme_length(data):
    """
    Change phoneme_length dependent on stress

    :param data: The data to populate
    :return: None
    """
    phoneme_index = data['phoneme_index']
    phoneme_length = data['phoneme_length']
    stress = data['stress']

    position = 0

    while phoneme_index[position] != 255:
        A = stress[position]
        if A == 0 or (A & 128) != 0:
            phoneme_length[position] = phoneme_length_table[phoneme_index[position]]
        else:
            phoneme_length[position] = phoneme_stressed_length_table[phoneme_index[position]]
        position += 1



