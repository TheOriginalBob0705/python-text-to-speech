from parser_engine.tables import phoneme_name_table, phoneme_flags
from common.constants import END
from parser_engine.constants import (
    FLAG_PUNCT, FLAG_NASAL, FLAG_LIQUIC, FLAG_FRICATIVE,
    FLAG_UNVOICED_STOPCONS, FLAG_STOPCONS, FLAG_VOICED,
    FLAG_CONSONANT, FLAG_VOWEL
)
from parser_engine.util import phoneme_has_flag, dev_print, matches_bitmask


def adjust_lengths(get_phoneme, set_length, get_length):
    """
    Applies various rules that adjust the lengths of phonemes.

    Lengthen <!FRICATIVE> or <VOICED> between <VOWEL> and <PUNCTUATION> by 1.5
    <VOWEL> <RX | LX>  <CONSONANT> - decrease <VOWEL> length by 1
    <VOWEL> <UNVOICED PLOSIVE> - decrease vowel by 1/8th
    <VOWEL> <VOICED CONSONANT> - increase vowel by 1/4 + 1
    <NASAL> <STOP CONSONANT> - set nasal = 5, consonant = 6
    <STOP CONSONANT> {optional silence} <STOP CONSONANT> - shorten both to 1/2 + 1
    <STOP CONSONANT> <LIQUID> - decrease <LIQUID> by 2

    :param get_phoneme: Callback for retrieving phonemes
    :param set_length:  Callback for setting phoneme length
    :param get_length: Callback for getting phoneme length
    :return: None
    """
    dev_print("adjust_lengths()")

    '''
    LENGTHEN VOWELS PRECEDING PUNCTUATION
    
    Search for punctuation. If found, back up to the first vowel, then process all phonemes between there and up to
    (but not including) the punctuation. If any phoneme is found that is a either a fricative or voiced, the duration
    is increased by (length * 1.5) + 1
    '''

    for position in range(len(get_phoneme)):
        # Not punctuation?
        if not phoneme_has_flag(get_phoneme(position), FLAG_PUNCT):
            continue
        loop_index = position
        while position > 1 and not phoneme_has_flag(get_phoneme(position), FLAG_VOWEL):
            position -= 1
        # If beginning of phonemes, exit loop
        if position == 0:
            break

        # Now handle everything between position and loop_index
        for vowel in range(position, loop_index):
            # Test for not fricative/unvoiced or not voiced
            if (
                not phoneme_has_flag(get_phoneme(position), FLAG_FRICATIVE)
                or phoneme_has_flag(get_phoneme(position), FLAG_VOICED)
            ):
                A  = get_length(position)
                # Change phoneme length to (length * 1.5) + 1
                dev_print(f"{position} RULE: Lengthen <!FRICATIVE> or <VOICED> "
                          f"{phoneme_name_table[get_phoneme(position)]} between VOWEL:"
                          f"{phoneme_name_table[get_phoneme(vowel)]} and PUNCTUATION:"
                          f"{phoneme_name_table[get_phoneme(position)]} by 1.5")
                set_length(position, (A >> 1) + A + 1)

    # Similar to the above routine, but shorten vowels under some circumstances
    # Loop through all phonemes
    loop_index = -1
    while True:
        phoneme = get_phoneme(loop_index + 1)
        position = loop_index

        # Vowel?
        if phoneme_has_flag(phoneme, FLAG_VOWEL):
            # Get next phoneme
            phoneme = get_phoneme(position + 1)
            # Not a consonant
            if not phoneme_has_flag(phoneme, FLAG_CONSONANT):
                # 'RX' or 'LX'?
                if (phoneme == 18 or phoneme == 19)  and phoneme_has_flag(get_phoneme(position + 2), FLAG_CONSONANT):
                    # Followed by consonant?
                    dev_print(f"{loop_index} RULE: <VOWEL {phoneme_name_table[get_phoneme(loop_index)]}> "
                              f"{phoneme_name_table[phoneme]} "
                              f"<CONSONANT: {phoneme_name_table[get_phoneme(position + 2)]}> "
                              f"- decrease length of vowel by 1")
                    # Decrease length of vowel by 1 frame
                    set_length(loop_index, get_length(loop_index) - 1)
                continue
            # Got here if not <VOWEL>
            # FIXME: the case when  phoneme == END is taken over by !phoneme_has_flag(phoneme, FLAG_CONSONANT)
            flags = FLAG_CONSONANT | FLAG_UNVOICED_STOPCONS if phoneme == END else phoneme_flags[phoneme]
            # Unvoiced
            if not matches_bitmask(flags, FLAG_VOICED):
                # *, .*, ? *, , *, - *, DX, S *, SH, F *, TH, / H, / X, CH, P *, T *, K *, KX

                # Unvoiced plosive
                if matches_bitmask(flags, FLAG_UNVOICED_STOPCONS):
                    # RULE: <VOWEL> <UNVOICED PLOSIVE>
                    # <VOWEL> <P*, T*, K*, KX>
                    dev_print(f"{loop_index} <VOWEL> <UNVOICED PLOSIVE> - decrease vowel by 1/8th")
                    A = get_length(loop_index)
                    set_length(loop_index, A - (A >> 3))
                continue

            # RULE: <VOWEL> <VOWEL or VOICED CONSONANT>
            # < VOWEL > < IY, IH, EH, AE, AA, AH, AO, UH, AX, IX, ER, UX, OH, RX, LX, WX, YX, WH, R *, L *, W *,
            # Y *, M *, N *, NX, Q *, Z *, ZH, V *, DH, J *, EY, AY, OY, AW, OW, UW, B *, D *, G *, GX >
            dev_print(f"{loop_index} RULE: <VOWEL> <VOWEL or VOICED CONSONANT> - increase vowel by 1/4 + 1")
            A = get_length(loop_index)
            set_length(loop_index, (A >> 2) + A + 1)
            continue

        # *, .*, ?*, ,*, -*, WH, R*, L*, W*, Y*, M*, N*, NX, DX, Q*, S*, SH, F*,
        # TH, /H, /X, Z*, ZH, V*, DH, CH, J*, B*, D*, G*, GX, P*, T*, K*, KX

        # Nasal?
        if phoneme_has_flag(phoneme, FLAG_NASAL):
            # RULE: <NASAL> <STOP CONSONANT>
            # Set punctuation length to 6
            # Set stop consonant length to 5

            #  M*, N*, NX
            phoneme = get_phoneme(position + 1)
            # Is next phoneme a stop consonant?
            if phoneme != END and phoneme_has_flag(phoneme, FLAG_STOPCONS):
                # B*, D*, G*, GX, P*, T*, K*, KX
                dev_print(f"{position} RULE: <NASAL> <STOP CONSONANT> - set nasal = 5, consonant = 6")
                set_length(position + 1, 6) # Set stop consonant length to 6
                set_length(position, 5) # Set nasal length to 5
            continue

        # *, .*, ? *, , *, - *, WH, R *, L *, W *, Y *, DX, Q *, S *, SH, F *, TH,
        # / H, / X, Z *, ZH, V *, DH, CH, J *, B *, D *, G *, GX, P *, T *, K *, KX

        # Stop consonant?
        if phoneme_has_flag(phoneme, FLAG_STOPCONS):
            # B*, D*,  G*, GX

            # RULE: <STOP CONSONANT> {optional silence} <STOP CONSONANT>
            # Shorten both to (length / 2 + 1)
            while (phoneme := get_phoneme(position + 1)) == 0:
                position += 1
            # If another stop consonant, process
            if phoneme != END and phoneme_has_flag(phoneme, FLAG_STOPCONS):
                # RULE: <STOP CONSONANT> {optional silence} <STOP CONSONANT>
                dev_print(f"{position} RULE: <STOP CONSONANT> {{optional silence}} "
                          f"<STOP CONSONANT> - shorten both to 1/2 + 1")
                set_length(position, (get_length(position) >> 1) + 1)
                set_length(loop_index, (get_length(loop_index) >> 1) + 1)
            continue

        # *, .*, ? *, , *, - *, WH, R *, L *, W *, Y *, DX, Q *, S *, SH, F *, TH,
        # / H, / X, Z *, ZH, V *, DH, CH, J *

        # Liquic consonant?
        if (
            position > 0
            and phoneme_has_flag(phoneme, FLAG_LIQUIC)
            and phoneme_has_flag(get_phoneme(position - 1), FLAG_STOPCONS)
        ):
            # RULE: <STOP CONSONANT> <LIQUID>
            # Decrease <LIQUID> by 2
            # Prior phoneme is a stop consonant
            dev_print(f"{position} RULE: <STOP CONSONANT> <LIQUID> - decrease by 2")
            set_length(position, get_length(position) - 2)
            # Decrease the phoneme length by 2 frames (20 ms)

        loop_index += 1
