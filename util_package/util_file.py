def matches_bitmask(bits, mask):
    """
    Test if a bit is set.

    :param bits: The bits
    :param mask: The mask to test
    :return: True if the bit is set, False otherwise
    """
    return (bits & mask) != 0


def text_to_uint8_array(text):
    """
    Convert a text string to a Uint8Array.

    :param text: The input text string
    :return: Uint8Array representing the text
    """
    buffer = bytearray(len(text))
    for index, char in enumerate(text):
        buffer[index] = ord(char)
    return buffer


def uint8_array_to_text(buffer):
    """
    Convert a Uint8Array to a text string.

    :param buffer: The input Uint8Array
    :return: Text string representation of the Uint8Array
    """
    text = ''.join(chr(byte) for byte in buffer)
    return text


def uint32_to_uint8_array(uint32):
    """
    Convert a 32-bit integer to a Uint8Array.

    :param uint32: The input 32-bit integer
    :return: Uint8Array representing the integer
    """
    result = bytearray(4)
    result[0] = uint32 & 0xFF
    result[1] = (uint32 >> 8) & 0xFF
    result[2] = (uint32 >> 16) & 0xFF
    result[3] = (uint32 >> 24) & 0xFF
    return result


def uint16_to_uint8_array(uint16):
    """
    Convert a 16-bit integer to a Uint8Array.

    :param uint16: The input 16-bit integer
    :return: Uint8Array representing the integer
    """
    result = bytearray(2)
    result[0] = uint16 & 0xFF
    result[1] = (uint16 >> 8) & 0xFF
    return result
