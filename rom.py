from bit_utility import get_bits, bytes_to_int, pad_hex
from cpu_opcodes import opcodes


class ROM:
    def __init__(self, rom, is_nes: bool):
        rom.seek(0)
        self.rom = rom

        self.prg_code_addr = 0xC000
        if is_nes:
            self.header = self.__read_header()
            self.pgr_rom = bytearray(self.rom.read(0x4000 * bytes_to_int(self.header["pgr_banks_16k"])))
            print(self.header["mapper_lower"], self.header["mapper_higher"])
        else:
            self.pgr_rom = bytearray(self.rom.read())

    def __read_header(self):
        header = self.rom.read(16)
        return {
            "constant": bytearray(header[0:4]),
            "pgr_banks_16k": bytearray([header[4]]),
            "vrom_banks_8kb": bytearray([header[5]]),
            "h_or_v_mirror_flag": bytearray(get_bits(header[6], 0)),
            "battery_ram": bytearray(get_bits(header[6], 1)),
            "trainer_512": bytearray(get_bits(header[6], 2)),
            "vram_layout": bytearray(get_bits(header[6], 3)),
            "mapper_lower": bytearray(get_bits(header[6], 4, 7)),
            "vs_cartridges": bytearray(get_bits(header[7], 0)),
            "reserved1": bytearray(get_bits(header[7], 1, 3)),
            "mapper_higher": bytearray(get_bits(header[7], 4, 7)),
            "rom_banks_8kb": bytearray([header[8]]),
            "NTSC_PAL": bytearray(get_bits(header[9], 0)),
            "reserved2": bytearray(header[10:15])
        }

    def mem_rom_size(self):
        return len(self.pgr_rom)

    def get(self, addr: int):
        addr = addr - self.prg_code_addr
        return self.pgr_rom[addr] if 0 <= addr < len(self.pgr_rom) else None

    def get_word(self, addr):  # 2 bytes
        addr -= self.prg_code_addr
        return int.from_bytes(self.pgr_rom[addr:addr + 1], "little") if 0 <= addr < len(self.pgr_rom) - 1 else None

    def __build_rom_banks(self):
        # print("BANK 1 START ADDRESS: ", hex(16384*3))
        # print(hex(bytes_to_int(self.header["constant"])))
        for v in range(0, 4):
            self.set_rom(0x4000, v * 0x4000, -1 if v == 3 else 0)
        return None

    def __str__(self):
        header = "<<<==== HEADER ====>>> \n"
        for key, value in self.header.items():
            header += key + " --> 0x" + value.hex() + "\n"
        header += "<<<==== END ====>>> \n"

        print(hex(bytes_to_int(bytearray([0x2, 0x20]))))

        start_address = 0xC000
        extra_bytes = 0
        i = 0
        instr = ""
        while i < len(self.pgr_rom):
            cur_opcode = bytes_to_int([self.pgr_rom[i]])
            if extra_bytes > 0:
                instr += " " + hex(bytes_to_int(self.pgr_rom[i:i + extra_bytes]))
                i += extra_bytes
                extra_bytes = 0
            else:
                if cur_opcode in opcodes:
                    instr = pad_hex(hex(0x0010 + i), 4) + "    " + opcodes[cur_opcode].mnem
                    # print(0xC000 + i, opcodes[byte_str][0])
                    extra_bytes = opcodes[cur_opcode].instr_size() - 1
                else:
                    instr = ""
                i += 1
            if extra_bytes == 0 and instr:
                print(instr)

        # banks = "\n<<<==== HEADER ====>>> \n"
        # banks += self.rom_banks.hex()
        # banks += "\n<<<==== END ====>>> \n"

        return header  # + banks
