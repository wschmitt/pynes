

# Picture Processing Unit
# it has only 8 registers that the cpu can access for write/read
# It can address 16-bit through a Bus to communicate with other hardware
# --- - 0x0000 - 0x1FFF
# --- - 0x2000 - 0x3FFF
# --- - 0x4000 - 0xFFFF (handled by the cartridge)
class PPU:
    def __init__(self, get_mem, set_mem):
        # functions to read/write from/to memory
        self.get_mem_func = get_mem
        self.set_mem_func = set_mem

    def read_mem(self, addr, byte=1):
        return self.get_mem_func(addr, byte)

    def write_mem(self, addr, val):
        return self.set_mem_func(addr, val)

    # CPU bus is accessing the PPU memory for writing
    def cpu_write(self, addr: int, val: int):
        addr &= 0x0007
        return 0

    # CPU bus is accessing the PPU memory for reading
    def cpu_read(self, addr: int):
        addr &= 0x0007
        return 0
