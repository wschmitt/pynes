import cpu_opcodes
from cpu import CPU
from ppu import PPU
from ram import RAM
from rom import ROM


class Emulator:
    def __init__(self):
        self.MEMORY_SIZE = 0x800  # 2kB

        self.rom = None
        self.ram = RAM(self.MEMORY_SIZE)
        self.cpu = CPU(self.cpu_read, self.cpu_write)
        self.ppu = PPU(self.ppu_read, self.ppu_write)

        self.system_clock = 0

    def set_rom(self, rom: ROM):
        self.rom = rom
        self.cpu.reset()

    def has_rom(self):
        return self.rom is not None

    def tick_clock(self):
        self.ppu.clock()

        if self.system_clock % 3 == 0:
            self.cpu.clock()

        self.system_clock += 1

    # ----------------------------------- PPU BUS ADDRESSING - 16 bits range - 0x0000 to 0xFFFF
    def ppu_write(self, addr, value):
        addr &= 0x3FFF

        # pattern memory
        # if addr <= 0x1FFF:
        # return self.rom.get_chr_data(addr)  # self.ppu.tbl_pattern[int(addr >= 0x1000)][addr & 0x0FFF]
        # elif addr <= 0x3EFF:
        #    pass
        # palette memory
        if 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            # mirroring
            if addr == 0x0010 or addr == 0x0014 or addr == 0x0018 or addr == 0x001C:
                addr -= 0x10
            self.ppu.tbl_palette[addr] = value
        return value

    def ppu_read(self, addr, byte=1):
        addr &= 0x3FFF

        # pattern memory
        if addr <= 0x1FFF:
            return self.rom.get_chr_data(addr)  # self.ppu.tbl_pattern[int(addr >= 0x1000)][addr & 0x0FFF]
        elif addr <= 0x3EFF:
            pass
        # palette memory
        elif 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            # mirroring
            if addr == 0x0010 or addr == 0x0014 or addr == 0x0018 or addr == 0x001C:
                addr -= 0x10
            return self.ppu.tbl_palette[addr]

    def __ppu_memory_access(self, write, addr, value, word=0):
        pass

    # ----------------------------------- CPU BUS ADDRESSING - 16 bits range - 0x0000 to 0xFFFF
    # CPU write to memory
    def cpu_write(self, addr, value):
        return self.__cpu_memory_access(True, addr, value)

    # CPU read from memory
    def cpu_read(self, addr, byte=1):
        if byte == 2:
            return self.__cpu_memory_access(False, addr, None, 1)
        return self.__cpu_memory_access(False, addr, None)

    def __cpu_memory_access(self, write, addr, value, word=0):
        # RAM ranges from 0x0000 to 0x2000 and uses mirroring each 0x800
        if addr <= 0x1FFF:
            if write:
                return self.ram.cpu_write(addr, value)
            else:
                if word:
                    return self.ram.get_word(addr)  # pop 2 bytes from memory
                else:
                    return self.ram.cpu_read(addr)  # pop 1 byte from memory

        # PPU Ranges from 0x2000 to 0x3FFF
        elif addr <= 0x3FFF:
            if write:
                return self.ppu.cpu_write(addr, value)
            else:
                return self.ppu.cpu_read(addr)

        # access rom otherwise
        if word:
            return self.rom.get_word(addr)

        return self.rom.get(addr)
