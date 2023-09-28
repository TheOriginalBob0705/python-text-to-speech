pR = 23
pD = 57
pT = 69

PHONEME_PERIOD = 1
PHONEME_QUESTION = 2

# Unknown: ' *', '.*', '?*', ',*', '-*'
FLAG_8000               = int(0x8000)  # 32768

# Unknown: '.*', '?*', ',*', '-*', 'Q*'
FLAG_4000               = int(0x4000)  # 16384

FLAG_FRICATIVE          = int(0x2000)  # 8192

# Liquic consonant
FLAG_LIQUIC             = int(0x1000)  # 4096

FLAG_NASAL              = int(0x0800)  # 2048

FLAG_ALVEOLAR           = int(0x0400)  # 1024

# Unused
FLAG_0200               = int(0x0200)  # 512

FLAG_PUNCT              = int(0x0100)  # 256

FLAG_VOWEL              = int(0x0080)  # 128

FLAG_CONSONANT          = int(0x0040)  # 64

# Dipthong ending with YX
FLAG_DIP_YX             = int(0x0020)  # 32

FLAG_DIPTHONG           = int(0x0010)  # 16

'''
Unknown:
    'M*', 'N*', 'NX', 'DX', 'Q*', 'CH', 'J*', 'B*', '**', '**', 'D*',
    '**', '**', 'G*', '**', '**', 'GX', '**', '**', 'P*', '**', '**',
    'T*', '**', '**', 'K*', '**', '**', 'KX', '**', '**'
'''
FLAG_0008               = int(0x0008)  # 8

FLAG_VOICED             = int(0x0004)  # 4

# Stop consonant
FLAG_STOPCONS           = int(0x0002)  # 2

FLAG_UNVOICED_STOPCONS  = int(0x0001)  # 1
