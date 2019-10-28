from enum import IntEnum, IntFlag
import pal_color_table


# PPU Registers
class Reg(IntEnum):
    STATUS = 1,
    MASK = 2,
    CONTROL = 3


# PPU Status Register Flags
class Status(IntFlag):
    SPR_OVERFLOW = (1 << 5),
    SPR_ZERO_HIT = (1 << 6),
    VERTICAL_BLANK = (1 << 7)


# PPU Mask Register Flags
class Mask(IntFlag):
    GREYSCALE = (1 << 0),
    RENDER_BG_LEFT = (1 << 1),
    RENDER_SPR_LEFT = (1 << 2),
    RENDER_BG = (1 << 3),
    RENDER_SPR = (1 << 4),
    ENHANCE_RED = (1 << 5),
    ENHANCE_GREEN = (1 << 6),
    ENHANCE_BLUE = (1 << 7),


# PPU Control Register Flags
class Control(IntFlag):
    NAME_TABLE_X = (1 << 0),
    NAME_TABLE_Y = (1 << 1),
    INCREMENT_MODE = (1 << 2),
    PATTERN_SPRITE = (1 << 3),
    PATTERN_BACKGROUND = (1 << 4),
    SPRITE_SIZE = (1 << 5),
    SLAVE_MODE = (1 << 6),
    ENABLE_NMI = (1 << 7),


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

        self.regs = {Reg.STATUS: 0x0, Reg.MASK: 0x0, Reg.CONTROL: 0x0}
        print(self.regs)

        # ppu memories
        self.tbl_pattern = [[] * 0x1000, [] * 0x1000]
        self.tbl_palette = []

        self.sprPatternTable = [[] * 0x4000, [] * 0x4000]
        self.pal_screen = pal_color_table.pal_screen

        # internal communication
        self.__addr_latch = 0x00
        self.__ppu_data_buffer = 0x00
        self.__ppu_addr = 0x0000

    # read the chr rom to for 8x8 sprites
    def get_pattern_table(self, pattern_id: int, palette: int):
        for tileX in range(0, 0xF):
            for tileY in range(0, 0xF):
                # each row has 16 tiles of 16 bits each (0x100)
                offset = tileY * 0x100 + tileX * 0xF

                # for each tile we got 8x8 sprite
                for row in range(0, 8):
                    tile_lsb = self.read_mem(0x1000 * pattern_id + offset + row + 0x0)
                    tile_msb = self.read_mem(0x1000 * pattern_id + offset + row + 0x8)
                    for col in range(0, 8):
                        pixel = (tile_lsb & 0x00000001) + ((tile_msb & 0x00000001) << 1)
                        tile_lsb >>= 1
                        tile_msb >>= 1

                        px = tileX * 8 + (7 - col)
                        py = tileY * 8 + row
                        self.sprPatternTable[pattern_id][px + 0x80 * py] = self.__get_color_from_palette(palette, pixel)
                break

    # This is a convenience function that takes a specified palette and pixel
    # index and returns the appropriate screen colour.
    # "0x3F00"       - Offset into PPU addressable range where palettes are stored
    # "palette << 2" - Each palette is 4 bytes in size
    # "pixel"        - Each pixel index is either 0, 1, 2 or 3
    # "& 0x3F"       - Stops us reading beyond the bounds of the palScreen array
    def __get_color_from_palette(self, palette, pixel):
        return self.pal_screen[self.read_mem(0x3F00 + (palette << 2) + pixel) & 0x3F]

    def set_flag(self, reg: Reg, flag: any, val: bool):
        if val:
            self.regs[reg] |= flag.value
        else:
            self.regs[reg] &= ~flag.value

    def read_mem(self, addr, byte=1):
        return self.get_mem_func(addr, byte)

    def write_mem(self, addr, val):
        return self.set_mem_func(addr, val)

    # CPU bus is accessing the PPU memory for writing
    def cpu_write(self, addr: int, val: int):
        addr &= 0x0007
        if addr == 0x0000:  # Control
            self.regs[Reg.CONTROL] = val & 0xFF
        elif addr == 0x0001:  # Mask
            self.regs[Reg.MASK] = val & 0xFF
        elif addr == 0x0002:  # Status
            self.regs[Reg.STATUS] = val & 0xFF
        elif addr == 0x0006:  # PPU Address
            if self.__addr_latch == 0:
                self.__ppu_addr = (self.__ppu_addr & 0x00FF) | (val << 8)
                self.__addr_latch = 1
            else:
                self.__ppu_addr = (self.__ppu_addr & 0xFF00) | val
                self.__addr_latch = 0
        elif addr == 0X0007:
            pass
        return 0

    # CPU bus is accessing the PPU memory for reading
    def cpu_read(self, addr: int):
        addr &= 0x0007
        if addr == 0x0000:  # Control
            pass
        elif addr == 0x0001:  # Mask
            pass
        elif addr == 0x0002:  # Status
            self.set_flag(Reg.STATUS, Status.VERTICAL_BLANK, False)
            self.__addr_latch = 0
            return (self.regs[Reg.STATUS] & 0xE0) | (self.__ppu_data_buffer & 0x1F)

        return 0
