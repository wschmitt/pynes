class RAM:
    def __init__(self, size: int):
        self.size = size
        self.mod_mask = size - 1    # 2047
        self.ram = bytearray(size)

    def cpu_write(self, addr: int, val: int):
        self.ram[addr & self.mod_mask] = val
        return val

    def cpu_read(self, addr: int):
        return self.ram[addr & self.mod_mask]

    def get_word(self, addr):  # 2 bytes
        addr &= self.mod_mask
        return int.from_bytes(self.ram[addr:addr + 1], "little")
