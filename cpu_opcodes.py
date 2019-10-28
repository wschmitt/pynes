import cpu

instr_len = {
    "Imm": 2,  # immediate - ex MOV A, 0x10 --> set regA with the value 0x10
    "ZP": 2,  # zero page
    "ZPX": 2,  # zero page x
    "ZPY": 2,  # zero page y
    "ABS": 3,  # absolute
    "ABSX": 3,  # absolute x
    "ABSY": 3,  # absolute y
    "IND": 3,  # indirect
    "INDX": 2,  # indirect x
    "INDY": 2,  # indirect y
    "SNGL": 1,  # no params
    "BRA": 2  # -
}


class Instr(object):
    def __init__(self, mnem: str, mode, instr, cycles, size, extra_cycle=False):
        self.mnem = mnem
        self.size = size
        self.mode = mode
        self.cycles = cycles
        self.extra_cycle = extra_cycle

        self.addr_mode = mode  # map to the addressing mode function
        self.process = instr  # map to the instruction function


opcodes = {
    # Imm
    0x69: Instr("ADC", cpu.imm, cpu.ADC, 2, 2),
    0x29: Instr("AND", cpu.imm, cpu.AND, 2, 2),
    0xc9: Instr("CMP", cpu.imm, cpu.CMP, 2, 2),
    0xe0: Instr("CPX", cpu.imm, cpu.CPX, 2, 2),
    0xc0: Instr("CPY", cpu.imm, cpu.CPY, 2, 2),
    0x49: Instr("EOR", cpu.imm, cpu.EOR, 2, 2),
    0xa9: Instr("LDA", cpu.imm, cpu.LDA, 2, 2),
    0xa2: Instr("LDX", cpu.imm, cpu.LDX, 2, 2),
    0xa0: Instr("LDY", cpu.imm, cpu.LDY, 2, 2),
    0x09: Instr("ORA", cpu.imm, cpu.ORA, 2, 2),
    0xe9: Instr("SBC", cpu.imm, cpu.SBC, 2, 2),
    # ZP
    0x65: Instr("ADC", cpu.zp0, cpu.ADC, 3, 2),
    0x25: Instr("AND", cpu.zp0, cpu.AND, 3, 2),
    0x06: Instr("ASL", cpu.zp0, cpu.ASL, 5, 2),
    0x24: Instr("BIT", cpu.zp0, cpu.BIT, 3, 2),
    0xc5: Instr("CMP", cpu.zp0, cpu.CMP, 3, 2),
    0xe4: Instr("CPX", cpu.zp0, cpu.CPX, 3, 2),
    0xc4: Instr("CPY", cpu.zp0, cpu.CPY, 3, 2),
    0xc6: Instr("DEC", cpu.zp0, cpu.DEC, 5, 2),
    0x45: Instr("EOR", cpu.zp0, cpu.EOR, 3, 2),
    0xe6: Instr("INC", cpu.zp0, cpu.INC, 5, 2),
    0xa5: Instr("LDA", cpu.zp0, cpu.LDA, 3, 2),
    0xa6: Instr("LDX", cpu.zp0, cpu.LDX, 3, 2),
    0xa4: Instr("LDY", cpu.zp0, cpu.LDY, 3, 2),
    0x46: Instr("LSR", cpu.zp0, cpu.LSR, 5, 2),
    0x05: Instr("ORA", cpu.zp0, cpu.ORA, 3, 2),
    0x66: Instr("ROR", cpu.zp0, cpu.ROR, 5, 2),
    0x26: Instr("ROL", cpu.zp0, cpu.ROL, 5, 2),
    0xe5: Instr("SBC", cpu.zp0, cpu.SBC, 3, 2),
    0x85: Instr("STA", cpu.zp0, cpu.STA, 3, 2),
    0x86: Instr("STX", cpu.zp0, cpu.STX, 3, 2),
    0x84: Instr("STY", cpu.zp0, cpu.STY, 3, 2),
    # ZPX, 2
    0x75: Instr("ADC", cpu.zpx, cpu.ADC, 4, 2),
    0x35: Instr("AND", cpu.zpx, cpu.AND, 4, 2),
    0x16: Instr("ASL", cpu.zpx, cpu.ASL, 6, 2),
    0xd5: Instr("CMP", cpu.zpx, cpu.CMP, 4, 2),
    0xd6: Instr("DEC", cpu.zpx, cpu.DEC, 6, 2),
    0x55: Instr("EOR", cpu.zpx, cpu.EOR, 4, 2),
    0xf6: Instr("INC", cpu.zpx, cpu.INC, 6, 2),
    0xb5: Instr("LDA", cpu.zpx, cpu.LDA, 4, 2),
    0xb4: Instr("LDY", cpu.zpx, cpu.LDY, 4, 2),
    0x56: Instr("LSR", cpu.zpx, cpu.LSR, 6, 2),
    0x15: Instr("ORA", cpu.zpx, cpu.ORA, 4, 2),
    0x76: Instr("ROR", cpu.zpx, cpu.ROR, 6, 2),
    0x36: Instr("ROL", cpu.zpx, cpu.ROL, 6, 2),
    0xf5: Instr("SBC", cpu.zpx, cpu.SBC, 4, 2),
    0x95: Instr("STA", cpu.zpx, cpu.STA, 4, 2),
    0x94: Instr("STY", cpu.zpx, cpu.STY, 4, 2),
    # ZPY, 2
    0xb6: Instr("LDX", cpu.zpy, cpu.LDX, 4, 2),
    0x96: Instr("STX", cpu.zpy, cpu.STX, 4, 2),
    # ABS
    0x6d: Instr("ADC", cpu.abs, cpu.ADC, 4, 3),
    0x2d: Instr("AND", cpu.abs, cpu.AND, 4, 3),
    0x0e: Instr("ASL", cpu.abs, cpu.ASL, 6, 3),
    0x2c: Instr("BIT", cpu.abs, cpu.BIT, 4, 3),
    0xcd: Instr("CMP", cpu.abs, cpu.CMP, 4, 3),
    0xec: Instr("CPX", cpu.abs, cpu.CPX, 4, 3),
    0xcc: Instr("CPY", cpu.abs, cpu.CPY, 4, 3),
    0xce: Instr("DEC", cpu.abs, cpu.DEC, 6, 3),
    0x4d: Instr("EOR", cpu.abs, cpu.EOR, 4, 3),
    0xee: Instr("INC", cpu.abs, cpu.INC, 6, 3),
    0x4c: Instr("JMP", cpu.abs, cpu.JMP, 3, 3),
    0x20: Instr("JSR", cpu.abs, cpu.JSR, 6, 3),
    0xad: Instr("LDA", cpu.abs, cpu.LDA, 4, 3),
    0xae: Instr("LDX", cpu.abs, cpu.LDX, 4, 3),
    0xac: Instr("LDY", cpu.abs, cpu.LDY, 4, 3),
    0x4e: Instr("LSR", cpu.abs, cpu.LSR, 6, 3),
    0x0d: Instr("ORA", cpu.abs, cpu.ORA, 4, 3),
    0x6e: Instr("ROR", cpu.abs, cpu.ROR, 6, 3),
    0x2e: Instr("ROL", cpu.abs, cpu.ROL, 6, 3),
    0xed: Instr("SBC", cpu.abs, cpu.SBC, 4, 3),
    0x8d: Instr("STA", cpu.abs, cpu.STA, 4, 3),
    0x8e: Instr("STX", cpu.abs, cpu.STX, 4, 3),
    0x8c: Instr("STY", cpu.abs, cpu.STY, 4, 3),
    # ABSX
    0x7d: Instr("ADC", cpu.abx, cpu.ADC, 4, 3, True),
    0x3d: Instr("AND", cpu.abx, cpu.AND, 4, 3, True),
    0x1e: Instr("ASL", cpu.abx, cpu.ASL, 7, 3),
    0xdd: Instr("CMP", cpu.abx, cpu.CMP, 4, 3, True),
    0xde: Instr("DEC", cpu.abx, cpu.DEC, 7, 3),
    0x5d: Instr("EOR", cpu.abx, cpu.EOR, 4, 3, True),
    0xfe: Instr("INC", cpu.abx, cpu.INC, 7, 3),
    0xbd: Instr("LDA", cpu.abx, cpu.LDA, 4, 3, True),
    0xbc: Instr("LDY", cpu.abx, cpu.LDY, 4, 3, True),
    0x5e: Instr("LSR", cpu.abx, cpu.LSR, 7, 3),
    0x1d: Instr("ORA", cpu.abx, cpu.ORA, 4, 3, True),
    0x7e: Instr("ROR", cpu.abx, cpu.ROR, 7, 3),
    0x3e: Instr("ROL", cpu.abx, cpu.ROL, 7, 3),
    0xfd: Instr("SBC", cpu.abx, cpu.SBC, 4, 3, True),
    0x9d: Instr("STA", cpu.abx, cpu.STA, 5, 3),
    # ABSY
    0x79: Instr("ADC", cpu.aby, cpu.ADC, 4, 3, True),
    0x39: Instr("AND", cpu.aby, cpu.AND, 4, 3, True),
    0xd9: Instr("CMP", cpu.aby, cpu.CMP, 4, 3, True),
    0x59: Instr("EOR", cpu.aby, cpu.EOR, 4, 3, True),
    0xb9: Instr("LDA", cpu.aby, cpu.LDA, 4, 3, True),
    0xbe: Instr("LDX", cpu.aby, cpu.LDX, 4, 3, True),
    0x19: Instr("ORA", cpu.aby, cpu.ORA, 4, 3, True),
    0xf9: Instr("SBC", cpu.aby, cpu.SBC, 4, 3, True),
    0x99: Instr("STA", cpu.aby, cpu.STA, 5, 3),
    # IND
    0x6c: Instr("JMP", cpu.ind, cpu.JMP, 5, 3),
    # INDX
    0x61: Instr("ADC", cpu.idx, cpu.ADC, 6, 2),
    0x21: Instr("AND", cpu.idx, cpu.AND, 6, 2),
    0xc1: Instr("CMP", cpu.idx, cpu.CMP, 6, 2),
    0x41: Instr("EOR", cpu.idx, cpu.EOR, 6, 2),
    0xa1: Instr("LDA", cpu.idx, cpu.LDA, 6, 2),
    0x01: Instr("ORA", cpu.idx, cpu.ORA, 6, 2),
    0xe1: Instr("SBC", cpu.idx, cpu.SBC, 6, 2),
    0x81: Instr("STA", cpu.idx, cpu.STA, 6, 2),
    # INDY
    0x71: Instr("ADC", cpu.idy, cpu.ADC, 5, 2, True),
    0x31: Instr("AND", cpu.idy, cpu.AND, 5, 2, True),
    0xd1: Instr("CMP", cpu.idy, cpu.CMP, 5, 2, True),
    0x51: Instr("EOR", cpu.idy, cpu.EOR, 5, 2, True),
    0xb1: Instr("LDA", cpu.idy, cpu.LDA, 5, 2, True),
    0x11: Instr("ORA", cpu.idy, cpu.ORA, 5, 2, True),
    0xf1: Instr("SBC", cpu.idy, cpu.SBC, 5, 2, True),
    0x91: Instr("STA", cpu.idy, cpu.STA, 6, 2),
    # IMPLIED
    0x0a: Instr("ASL", cpu.imp, cpu.ASL, 2, 1),
    0x00: Instr("BRK", cpu.imp, cpu.BRK, 7, 1),
    0x18: Instr("CLC", cpu.imp, cpu.CLC, 2, 1),
    0x38: Instr("SEC", cpu.imp, cpu.SEC, 2, 1),
    0x58: Instr("CLI", cpu.imp, cpu.CLI, 2, 1),
    0x78: Instr("SEI", cpu.imp, cpu.SEI, 2, 1),
    0xb8: Instr("CLV", cpu.imp, cpu.CLV, 2, 1),
    0xd8: Instr("CLD", cpu.imp, cpu.CLD, 2, 1),
    0xf8: Instr("SED", cpu.imp, cpu.SED, 2, 1),
    0x4a: Instr("LSR", cpu.imp, cpu.LSR, 2, 1),
    0xea: Instr("NOP", cpu.imp, cpu.NOP, 2, 1),
    0xaa: Instr("TAX", cpu.imp, cpu.TAX, 2, 1),
    0x8a: Instr("TXA", cpu.imp, cpu.TXA, 2, 1),
    0xca: Instr("DEX", cpu.imp, cpu.DEX, 2, 1),
    0xe8: Instr("INX", cpu.imp, cpu.INX, 2, 1),
    0xa8: Instr("TAY", cpu.imp, cpu.TAY, 2, 1),
    0x98: Instr("TYA", cpu.imp, cpu.TYA, 2, 1),
    0x88: Instr("DEY", cpu.imp, cpu.DEY, 2, 1),
    0xc8: Instr("INY", cpu.imp, cpu.INY, 2, 1),
    0x6a: Instr("ROR", cpu.imp, cpu.ROR, 2, 1),
    0x2a: Instr("ROL", cpu.imp, cpu.ROL, 2, 1),
    0x40: Instr("RTI", cpu.imp, cpu.RTI, 6, 1),
    0x60: Instr("RTS", cpu.imp, cpu.RTS, 6, 1),
    0x9a: Instr("TXS", cpu.imp, cpu.TXS, 2, 1),
    0xba: Instr("TSX", cpu.imp, cpu.TSX, 2, 1),
    0x48: Instr("PHA", cpu.imp, cpu.PHA, 3, 1),
    0x68: Instr("PLA", cpu.imp, cpu.PLA, 4, 1),
    0x08: Instr("PHP", cpu.imp, cpu.PHP, 3, 1),
    0x28: Instr("PLP", cpu.imp, cpu.PLP, 4, 1),
    # REL
    0x10: Instr("BPL", cpu.rel, cpu.BPL, 2, 2, True),
    0x30: Instr("BMI", cpu.rel, cpu.BMI, 2, 2, True),
    0x50: Instr("BVC", cpu.rel, cpu.BVC, 2, 2, True),
    0x70: Instr("BVS", cpu.rel, cpu.BVS, 2, 2, True),
    0x90: Instr("BCC", cpu.rel, cpu.BCC, 2, 2, True),
    0xb0: Instr("BCS", cpu.rel, cpu.BCS, 2, 2, True),
    0xd0: Instr("BNE", cpu.rel, cpu.BNE, 2, 2, True),
    0xf0: Instr("BEQ", cpu.rel, cpu.BEQ, 2, 2, True),
}

# opcodes_table = [
#     # Name, Imm,  ZP,   ZPX,  ZPY,  ABS, ABSX, ABSY,  IND, INDX, INDY, SNGL, BRA
#     ["ADC", 0x69, 0x65, 0x75, None, 0x6d, 0x7d, 0x79, None, 0x61, 0x71, None, None],
#     ["AND", 0x29, 0x25, 0x35, None, 0x2d, 0x3d, 0x39, None, 0x21, 0x31, None, None],
#     ["ASL", None, 0x06, 0x16, None, 0x0e, 0x1e, None, None, None, None, 0x0a, None],
#     ["BIT", None, 0x24, None, None, 0x2c, None, None, None, None, None, None, None],
#     ["BPL", None, None, None, None, None, None, None, None, None, None, None, 0x10],
#     ["BMI", None, None, None, None, None, None, None, None, None, None, None, 0x30],
#     ["BVC", None, None, None, None, None, None, None, None, None, None, None, 0x50],
#     ["BVS", None, None, None, None, None, None, None, None, None, None, None, 0x70],
#     ["BCC", None, None, None, None, None, None, None, None, None, None, None, 0x90],
#     ["BCS", None, None, None, None, None, None, None, None, None, None, None, 0xb0],
#     ["BNE", None, None, None, None, None, None, None, None, None, None, None, 0xd0],
#     ["BEQ", None, None, None, None, None, None, None, None, None, None, None, 0xf0],
#     ["BRK", None, None, None, None, None, None, None, None, None, None, 0x00, None],
#     ["CMP", 0xc9, 0xc5, 0xd5, None, 0xcd, 0xdd, 0xd9, None, 0xc1, 0xd1, None, None],
#     ["CPX", 0xe0, 0xe4, None, None, 0xec, None, None, None, None, None, None, None],
#     ["CPY", 0xc0, 0xc4, None, None, 0xcc, None, None, None, None, None, None, None],
#     ["DEC", None, 0xc6, 0xd6, None, 0xce, 0xde, None, None, None, None, None, None],
#     ["EOR", 0x49, 0x45, 0x55, None, 0x4d, 0x5d, 0x59, None, 0x41, 0x51, None, None],
#     ["CLC", None, None, None, None, None, None, None, None, None, None, 0x18, None],
#     ["SEC", None, None, None, None, None, None, None, None, None, None, 0x38, None],
#     ["CLI", None, None, None, None, None, None, None, None, None, None, 0x58, None],
#     ["SEI", None, None, None, None, None, None, None, None, None, None, 0x78, None],
#     ["CLV", None, None, None, None, None, None, None, None, None, None, 0xb8, None],
#     ["CLD", None, None, None, None, None, None, None, None, None, None, 0xd8, None],
#     ["SED", None, None, None, None, None, None, None, None, None, None, 0xf8, None],
#     ["INC", None, 0xe6, 0xf6, None, 0xee, 0xfe, None, None, None, None, None, None],
#     ["JMP", None, None, None, None, 0x4c, None, None, 0x6c, None, None, None, None],
#     ["JSR", None, None, None, None, 0x20, None, None, None, None, None, None, None],
#     ["LDA", 0xa9, 0xa5, 0xb5, None, 0xad, 0xbd, 0xb9, None, 0xa1, 0xb1, None, None],
#     ["LDX", 0xa2, 0xa6, None, 0xb6, 0xae, None, 0xbe, None, None, None, None, None],
#     ["LDY", 0xa0, 0xa4, 0xb4, None, 0xac, 0xbc, None, None, None, None, None, None],
#     ["LSR", None, 0x46, 0x56, None, 0x4e, 0x5e, None, None, None, None, 0x4a, None],
#     ["NOP", None, None, None, None, None, None, None, None, None, None, 0xea, None],
#     ["ORA", 0x09, 0x05, 0x15, None, 0x0d, 0x1d, 0x19, None, 0x01, 0x11, None, None],
#     ["TAX", None, None, None, None, None, None, None, None, None, None, 0xaa, None],
#     ["TXA", None, None, None, None, None, None, None, None, None, None, 0x8a, None],
#     ["DEX", None, None, None, None, None, None, None, None, None, None, 0xca, None],
#     ["INX", None, None, None, None, None, None, None, None, None, None, 0xe8, None],
#     ["TAY", None, None, None, None, None, None, None, None, None, None, 0xa8, None],
#     ["TYA", None, None, None, None, None, None, None, None, None, None, 0x98, None],
#     ["DEY", None, None, None, None, None, None, None, None, None, None, 0x88, None],
#     ["INY", None, None, None, None, None, None, None, None, None, None, 0xc8, None],
#     ["ROR", None, 0x66, 0x76, None, 0x6e, 0x7e, None, None, None, None, 0x6a, None],
#     ["ROL", None, 0x26, 0x36, None, 0x2e, 0x3e, None, None, None, None, 0x2a, None],
#     ["RTI", None, None, None, None, None, None, None, None, None, None, 0x40, None],
#     ["RTS", None, None, None, None, None, None, None, None, None, None, 0x60, None],
#     ["SBC", 0xe9, 0xe5, 0xf5, None, 0xed, 0xfd, 0xf9, None, 0xe1, 0xf1, None, None],
#     ["STA", None, 0x85, 0x95, None, 0x8d, 0x9d, 0x99, None, 0x81, 0x91, None, None],
#     ["TXS", None, None, None, None, None, None, None, None, None, None, 0x9a, None],
#     ["TSX", None, None, None, None, None, None, None, None, None, None, 0xba, None],
#     ["PHA", None, None, None, None, None, None, None, None, None, None, 0x48, None],
#     ["PLA", None, None, None, None, None, None, None, None, None, None, 0x68, None],
#     ["PHP", None, None, None, None, None, None, None, None, None, None, 0x08, None],
#     ["PLP", None, None, None, None, None, None, None, None, None, None, 0x28, None],
#     ["STX", None, 0x86, None, 0x96, 0x8e, None, None, None, None, None, None, None],
#     ["STY", None, 0x84, 0x94, None, 0x8c, None, None, None, None, None, None, None],
#     ["---", None, None, None, None, None, None, None, None, None, None, None, None]
# ]
