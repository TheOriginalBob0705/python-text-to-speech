from common.constants import END
from tables import phoneme_name_table
from parser_engine.util import (phoneme_has_flag, dev_print)
from constants import (
    pR,
    pD,
    pT,
    FLAG_ALVEOLAR,
    FLAG_UNVOICED_STOPCONS,
    FLAG_DIPTHONG,
    FLAG_DIP_YX,
    FLAG_VOWEL
)


def parser2(insert_phoneme, set_phoneme, get_phoneme, get_stress):
    def handle_uw_ch_j(phoneme, pos):
        # 'UW' Example: NEW, DEW, SUE, ZOO, THOO, TOO
        if phoneme == 53:
            # ALVEOLAR flag set?
            if phoneme_has_flag(get_phoneme(pos - 1), FLAG_ALVEOLAR):
                dev_print(f"{pos} RULE: <ALVEOLAR> UW -> <ALVEOLAR> UX")
                set_phoneme(pos, 16)  # UX

        # 'CH' Example: CHEW
        elif phoneme == 42:
            dev_print(f"{pos} RULE: CH -> CH CH+1")
            insert_phoneme(pos + 1, 43, get_stress(pos))  # '**'

        # 'J' Example: JAY
        elif phoneme == 44:
            dev_print(f"{pos} RULE: J -> J J+1")
            insert_phoneme(pos + 1, 45, get_stress(pos))  # '**'

    def change_ax(position, suffix):
        phoneme = phoneme_name_table[get_phoneme(position)]
        suffix_phoneme = phoneme_name_table[suffix]
        dev_print(f"{position} RULE: {phoneme} -> AX {suffix_phoneme}")

        set_phoneme(position, 13)  # 'AX'
        insert_phoneme(position + 1, suffix, get_stress(position))

    pos = -1
    phoneme = None

    while True:
        pos += 1
        phoneme = get_phoneme(pos)

        if phoneme == END:
            break

        # Is phoneme pause?
        if phoneme == 0:
            continue

        if phoneme_has_flag(phoneme, FLAG_DIPTHONG):
            # <DIPHTHONG ENDING WITH WX> -> <DIPHTHONG ENDING WITH WX> WX
            # <DIPHTHONG NOT ENDING WITH WX> -> <DIPHTHONG NOT ENDING WITH WX> YX
            # Example: OIL, COW
            dev_print(f"{pos} RULE: insert WX following diphthong NOT ending in IY sound"
                      if not phoneme_has_flag(phoneme, FLAG_DIP_YX)
                      else f"{pos} RULE: insert YX following diphthong ending in IY sound")
            # If ends with IY, use YX, else use WX
            # Insert at WX or YX following, copying the stress
            # 'WX' = 20 'YX' = 21
            insert_phoneme(pos + 1, 21 if phoneme_has_flag(phoneme, FLAG_DIP_YX) else 20, get_stress(pos))
            handle_uw_ch_j(phoneme, pos)
            continue

        if phoneme == 78:
            # 'UL' -> 'AX' 'L*'
            # Example: MEDDLE
            change_ax(pos, 24)
            continue

        if phoneme == 79:
            # 'UM' -> 'AX' 'M*'
            # Example: ASTRONOMY
            change_ax(pos, 27)
            continue

        if phoneme == 80:
            # 'UN' -> 'AX' 'N*'
            change_ax(pos, 28)
            continue

        if phoneme_has_flag(phoneme, FLAG_VOWEL) and get_stress(pos):
            # Example: FUNCTION
            # RULE:
            #       <STRESSED VOWEL> <SILENCE> <STRESSED VOWEL> -> <STRESSED VOWEL> <SILENCE> Q <VOWEL>
            # EXAMPLE: AWAY EIGHT
            if not get_phoneme(pos + 1):  # If following phoneme is a pause, get next
                phoneme = get_phoneme(pos + 2)
                if phoneme != END and phoneme_has_flag(phoneme, FLAG_VOWEL) and get_stress(pos + 2):
                    dev_print(f"{pos+2} RULE: Insert glottal stop between two stressed vowels with space between them")
                    insert_phoneme(pos + 2, 31, 0)  # 31 = 'Q'
            continue

        prior_phoneme = END if pos == 0 else get_phoneme(pos - 1)

        if phoneme == pR:
            # RULES FOR PHONEMES BEFORE R
            if prior_phoneme == pT:
                # Example: TRACK
                dev_print(f"{pos} RULE: T* R* -> CH R*")
                set_phoneme(pos - 1, 42)  # 'T*' 'R*' -> 'CH' 'R*'
            elif phoneme == pD:
                # Example: DRY
                dev_print(f"{pos} RULE: D* R* -> J* R*")
                set_phoneme(pos - 1, 44)  # 'J*'
            elif phoneme_has_flag(prior_phoneme, FLAG_VOWEL):
                # Example: ART
                dev_print(f"{pos} <VOWEL> R* -> <VOWEL> RX")
                set_phoneme(pos, 18)  # 'RX'
            continue

        # 'L*'
        if phoneme == 24 and phoneme_has_flag(prior_phoneme, FLAG_VOWEL):
            # Example: ALL
            dev_print(f"{pos} <VOWEL> L* -> <VOWEL> LX")
            set_phoneme(pos, 19)  # 'LX'
            continue

        # 'G*' 'S*'
        if prior_phoneme == 60 and phoneme == 32:
            # Can't get to fire -
            #    1. The G -> GX rule intervenes
            #    2. Reciter already replaces GS -> GZ
            dev_print(f"{pos} G S -> G Z")
            set_phoneme(pos, 38)
            continue

        # 'G*'
        if phoneme == 60:
            # G <VOWEL OR DIPHTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPHTHONG NOT ENDING WITH IY>
            # Example: GO
            Y = get_phoneme(pos + 1)
            # If dipthong ending with YX, move continue processing next phoneme
            if not phoneme_has_flag(Y, FLAG_DIP_YX) and (Y != END):
                # replace G with GX and continue processing next phoneme
                dev_print(f"{pos} RULE: G <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
                set_phoneme(pos, 63)  # 'GX'
                continue

        # 'K*'
        if phoneme == 72:
            # K <VOWEL OR DIPHTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPHTHONG NOT ENDING WITH IY>
            # Example: COW
            Y = get_phoneme(pos + 1)
            # If at end, replace current phoneme with KX
            if not phoneme_has_flag(Y, FLAG_DIP_YX) or Y == END:
                # VOWELS AND DIPHTHONGS ENDING WITH IY SOUND flag set?
                dev_print(f"{pos} K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
                set_phoneme(pos, 75)
                phoneme = 75

        # Replace with softer version?
        if phoneme_has_flag(phoneme, FLAG_UNVOICED_STOPCONS) and (prior_phoneme == 32):  # 'S*'
            # RULE:
            #   'S*' 'P*' -> 'S*' 'B*'
            #   'S*' 'T*' -> 'S*' 'D*'
            #   'S*' 'K*' -> 'S*' 'G*'
            #   'S*' 'KX' -> 'S*' 'GX'
            #   'S*' 'UM' -> 'S*' '**'
            #   'S*' 'UN' -> 'S*' '**'
            # Examples: SPY, STY, SKY, SCOWL
            dev_print(f"{pos} RULE: S* {phoneme_name_table[phoneme]} -> S* {phoneme_name_table[phoneme-12]}")
            set_phoneme(pos, phoneme - 12)
        elif not phoneme_has_flag(phoneme, FLAG_UNVOICED_STOPCONS):
            handle_uw_ch_j(phoneme, pos)

        # 'T*', 'D*'
        if phoneme == 69 or phoneme == 57:
            # RULE: Soften T following vowel
            # NOTE: This rule fails for cases such as "ODD"
            #       <UNSTRESSED VOWEL> T <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>
            #       <UNSTRESSED VOWEL> D <PAUSE>  -> <UNSTRESSED VOWEL> DX <PAUSE>
            # Example: PARTY, TARDY
            if pos > 0 and phoneme_has_flag(get_phoneme(pos - 1), FLAG_VOWEL):
                phoneme = get_phoneme(pos + 1)
                if not phoneme:
                    phoneme = get_phoneme(pos + 2)
                if phoneme_has_flag(phoneme, FLAG_VOWEL) and not get_stress(pos + 1):
                    dev_print(f"{pos} Soften T or D following vowel or ER and preceding a pause -> DX")
                    set_phoneme(pos, 30)
            continue

        dev_print(f"{pos}: {phoneme_name_table[phoneme]}")
