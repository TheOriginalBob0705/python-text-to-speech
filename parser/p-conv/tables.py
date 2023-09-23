from typing import List


def encodeTable(table):
    result = bytearray(len(table))
    for index, e in enumerate(table):
        result[index] = ord(e)
    return result


stress_input_table = encodeTable(['*', '1', '2', '3', '4', '5', '6', '7', '8'])
print(stress_input_table)
