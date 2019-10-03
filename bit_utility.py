def get_bits(binary, start_pos, end_pos=None):
    mask = 1 if end_pos is None else (2 ** (end_pos - start_pos + 1)) - 1
    return [binary >> start_pos & mask]


def bytes_to_int(byte):
    if isinstance(byte, bytearray) or isinstance(byte, list):
        return int.from_bytes(byte, "little")
    else:
        return int(byte, 2)


def pad_hex(hex_num, pad):
    return "0x" + hex_num[2:].zfill(pad)
