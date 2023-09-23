pR = 23
pD = 57
pT = 69

PHONEME_PERIOD = 1
PHONEME_QUESTION = 2

# Unknown: ' *', '.*', '?*', ',*', '-*'
FLAG_8000 = 0x8000

# Unknown: '.*', '?*', ',*', '-*', 'Q*'
FLAG_4000 = 0x4000

FLAG_FRICATIVE = 0x2000

# Liquic consonant
FLAG_LIQUIC = 0x1000

FLAG_NASAL = 0x0800

FLAG_ALVEOLAR = 0x0400

# Unused
FLAG_0200 = 0x0200

FLAG_PUNCT = 0x0100

FLAG_VOWEL = 0x0080

FLAG_CONSONANT = 0x0040

# Dipthong ending with YX
FLAG_DIP_YX = 0x0020

FLAG_DIPTHONG = 0x0010

'''
Unknown:
    'M*', 'N*', 'NX', 'DX', 'Q*', 'CH', 'J*', 'B*', '**', '**', 'D*',
    '**', '**', 'G*', '**', '**', 'GX', '**', '**', 'P*', '**', '**',
    'T*', '**', '**', 'K*', '**', '**', 'KX', '**', '**'
'''
FLAG_0008 = 0x0008

FLAG_VOICED = 0x0004

FLAG_STOPCONS = 0x0002

FLAG_UNVOICED_STOPCONS = 0x0001
