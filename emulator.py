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
        self.ppu = PPU(self.ppu_write, self.ppu_read)

    def set_rom(self, rom: ROM):
        self.rom = rom

    def has_rom(self):
        return self.rom is not None

    def execute_instr(self):
        # read the next instruction pointed by the PC register
        addr = self.cpu.regPC()
        op = self.cpu_read(addr)

        # check if op code is from a valid instruction
        if op not in cpu_opcodes.opcodes:
            print("No valid instruction with opcode: {0} {1}".format(hex(addr), op))
            self.cpu.inc_pc()
            return

        # check if op code is implemented yet
        instr = cpu_opcodes.opcodes[op]
        if instr.process is None:
            print("Not implemented: addr({0}) op({1}) mnem({2})".format(hex(addr), hex(op), instr.mnem))
            self.cpu.inc_pc(instr.size)
            return

        print("Instr: addr({0}) op({1}) mnem({2})".format(hex(addr), hex(op), instr.mnem))
        # effectively executes the instruction and inc PC by the number of bytes required by the instruction
        # self.cpu.inc_reg_pc(instr.instr_size())
        self.cpu.process_instr(instr)

    def run(self):
        for i in range(0, 10):
            # check if cpu is still processing the previous instruction, if so, we just skip the loop
            if self.cpu.cycles == 0:
                self.execute_instr()
            self.cpu.cycles -= 1

    # ----------------------------------- PPU BUS ADDRESSING
    def ppu_write(self, addr, value):
        pass

    def ppu_read(self, addr, byte=1):
        pass

    def __ppu_memory_access(self, write, addr, value, word=0):
        pass

    # ----------------------------------- CPU BUS ADDRESSING
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
                return self.ram.set(addr, value)
            else:
                if word:
                    return self.ram.get_word(addr)  # pop 2 bytes from memory
                else:
                    return self.ram.get(addr)  # pop 1 byte from memory

        # PPU Ranges from 0x2000 to 0x3FFF
        elif addr <= 0x3FFF:
            if write:
                return self.ppu.cpu_write(addr, value)
            else:
                return self.ppu.cpu_read(addr)

        # access rom otherwise
        if word:
            return self.rom.get_word(addr)

        return self.rom.cpu_read(addr)
