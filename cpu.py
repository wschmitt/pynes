from enum import IntFlag, IntEnum
import cpu_opcodes


# CPU registers
class Reg(IntEnum):
    A = 1  # Accumulator Reg
    X = 2  # X Reg
    Y = 3  # Y Reg
    P = 4  # Status Reg
    PC = 5  # program counter


# Status flags
class Flag(IntFlag):
    C = (1 << 0)  # Carry flag
    Z = (1 << 1)  # Zero flag
    I = (1 << 2)  # Disable Interrupt flag
    D = (1 << 3)  # Decimal flag (not used in nes)
    B = (1 << 4)  # Break
    U = (1 << 5)  # Unused
    V = (1 << 6)  # Overflow flag
    N = (1 << 7)  # Negative flag


# It can address 16-bit through a Bus to communicate with other hardware
# RAM - 0x0000 - 0x1FFF
# PPU - 0x2000 - 0x3FFF
# ROM - 0x4000 - 0xFFFF (handled by the cartridge)
class CPU:
    def __init__(self, cpu_read_func, cpu_write_func):
        self.regs = {Reg.A: 0x00, Reg.X: 0x00, Reg.Y: 0x00, Reg.P: 0x0, Reg.PC: 0xFFFC}

        self.processing = True

        # auxiliar variables
        self.cycles = 0  # the number of cycles needed to finish executing the current instruction
        self.stack_pt = 0xFD  # stack Pointer (points to location on bus)
        self.reset_addr = 0xFFFC

        # functions to read/write from/to devices connected to the bus
        self.cpu_read_func = cpu_read_func
        self.cpu_write_func = cpu_write_func

    def reset(self):
        addr = self.cpu_read_func(self.reset_addr, 2)
        self.regPC(addr)

    def clock(self):
        if self.cycles <= 0:
            instr = self.fetch_next_instr()
            self.process_instr(instr)

        self.cycles -= 1

    def fetch_next_instr(self):
        # read the next instruction pointed by the PC register
        addr = self.regPC()
        op = self.read(addr)

        # check if op code is from a valid instruction
        if op not in cpu_opcodes.opcodes:
            print("No valid instruction with opcode: {0} {1}".format(hex(addr), op))
            self.inc_pc()
            return None

        # check if op code is implemented yet
        instr = cpu_opcodes.opcodes[op]
        if instr.process is None:
            print("Not implemented: addr({0}) op({1}) mnem({2})".format(hex(addr), hex(op), instr.mnem))
            self.inc_pc(instr.size)
            return None

        print("Instr: addr({0}) op({1}) mnem({2})".format(hex(addr), hex(op), instr.mnem))
        # effectively executes the instruction and inc PC by the number of bytes required by the instruction
        # self.cpu.inc_reg_pc(instr.instr_size())
        return instr

    def process_instr(self, instr):
        self.cycles = instr.cycles
        self.set_flag(Flag.U, True)

        # execute addr mode
        self.inc_pc()
        extra_cycle_mode, addr = instr.addr_mode(self)
        self.inc_pc(instr.size - 1)

        # execute instruction
        extra_cycle_op = instr.process(self, addr, instr.addr_mode)

        if extra_cycle_mode and extra_cycle_op:
            self.cycles += 1

        self.set_flag(Flag.U, True)

    def inc_pc(self, val=1):
        self.regs[Reg.PC] += val

    def read(self, addr, byte=1):
        return self.cpu_read_func(addr, byte)

    def write(self, addr, val):
        return self.cpu_write_func(addr, val)

    def __str__(self):
        return 'A={} X={} Y={} P={} PC={}'.format(self.regA(), self.regX(), self.regY(), bin(self.regP())[2:].zfill(8),
                                                  hex(self.regPC())[2:].upper())

    def set_flag(self, flag: Flag, val: bool):
        if val:
            self.regs[Reg.P] |= flag.value
        else:
            self.regs[Reg.P] &= ~flag.value

    def get_flag(self, flag: Flag):
        return (self.regs[Reg.P] & flag.value) > 0

    # reg accessors - easy way to read/write from/to registers
    def regA(self, val=None):
        if val is not None:
            self.regs[Reg.A] = val
        return self.regs[Reg.A]

    def regX(self, val=None):
        if val is not None:
            self.regs[Reg.X] = val
        return self.regs[Reg.X]

    def regY(self, val=None):
        if val is not None:
            self.regs[Reg.Y] = val
        return self.regs[Reg.Y]

    def regP(self, val=None):
        if val is not None:
            self.regs[Reg.P] = val
        return self.regs[Reg.P]

    def regPC(self, val=None):
        if val is not None:
            self.regs[Reg.PC] = val
        return self.regs[Reg.PC]


# Addressing Modes ===================================>

# Implied Mode: Usually used for simple instructions that doesn't have any parameters.
def imp(cpu: CPU):
    return 0, cpu.regA()


# Immediate Mode: The next byte should be used as a value
def imm(cpu: CPU):
    return 0, cpu.regPC()


# Zero Page Mode:
def zp0(cpu: CPU):
    addr = cpu.read(cpu.regPC()) & 0x00FF
    return 0, addr


def zpx(cpu: CPU):
    addr = (cpu.read(cpu.regPC()) + cpu.regX()) & 0x00FF
    return 0, addr


def zpy(cpu: CPU):
    addr = (cpu.read(cpu.regPC()) + cpu.regY()) & 0x00FF
    return 0, addr


def rel(cpu: CPU):
    addr_rel = cpu.read(cpu.regPC())
    if addr_rel & 0x80:
        # calculate the 2's complement
        addr_rel = addr_rel - 0x100
    return 0, addr_rel


# Absolute: Full 16-bit address
def abs(cpu: CPU):
    addr = cpu.read(cpu.regPC(), 2)
    return 0, addr


def abx(cpu: CPU):
    addr = cpu.read(cpu.regPC(), 2)
    addr_x = addr + cpu.regX()
    if addr_x & 0xFF00 != addr & 0xFF00:
        return 1, addr_x
    return 0, addr_x


def aby(cpu: CPU):
    addr = cpu.read(cpu.regPC(), 2)
    addr_y = addr + cpu.regY()
    if addr_y & 0xFF0 != addr & 0xFF00:
        return 1, addr_y
    return 0, addr_y


def ind(cpu: CPU):
    addr = cpu.read(cpu.regPC(), 2)

    if (addr & 0x00FF) == 0x00FF:  # simulate page boundary hardware bug
        return 0, cpu.read(addr & 0xFF00) << 8 | cpu.read(addr)
    else:
        return 0, cpu.read(addr, 2)


def idx(cpu: CPU):
    addr = cpu.read(cpu.regPC())
    return 0, cpu.read(addr + cpu.regX(), 2)


def idy(cpu: CPU):
    addr = cpu.read(cpu.regPC())

    addr_y = cpu.read(addr, 2)
    addr_y += cpu.regY()

    if addr_y & 0xFF00 != addr & 0xFF00:
        return 1, addr_y
    else:
        return 0, addr_y


# INSTRUCTIONS =====================================>

def ADC(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = cpu.regA() + value + cpu.get_flag(Flag.C)
    cpu.set_flag(Flag.C, temp > 0x00FF)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    # check overflow cases: https://youtu.be/8XmxKPJDGU0?t=2971
    # Pos + Pos = Neg result
    # Neg + Neg = Pos result
    cpu.set_flag(Flag.V, bool((~(cpu.regA() ^ value) & (cpu.regA() ^ temp)) & 0x0080))
    cpu.set_flag(Flag.N, temp & 0x0080)
    cpu.regA(temp & 0x00FF)
    return 1


def SBC(cpu: CPU, addr_abs: int, mode):
    # invert the bottom 8 bits with bitwise xor
    value = cpu.read(addr_abs) ^ 0x00FF
    temp = cpu.regA() + value + cpu.get_flag(Flag.C)
    cpu.set_flag(Flag.C, temp > 0x00FF)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.V, bool((~(cpu.regA() ^ value) & (cpu.regA() ^ temp)) & 0x0080))
    cpu.set_flag(Flag.N, temp & 0x0080)
    cpu.regA(temp & 0x00FF)
    return 1


# Instruction: Clear Carry Flag
# C => 0
def CLC(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.C, False)
    return 0


# 0xd8 - clear decimal flag which controls how adds and subs are performed (not used on NES)
# D => 0
def CLD(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.D, False)
    return 0


# Instruction: set decimal flag (not used on NES)
# D => 1
def SED(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.D, True)
    return 0


# Instruction: Disable Interrupt / Clear Interrupt Flags
# I => 0
def CLI(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.I, False)
    return 0


# Instruction: Clear Overflow Flag
# V => 0
def CLV(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.V, False)
    return 0


# Instruction: Bitwise Logic AND
# Function A = A & M
# Set Flags: N, Z
def AND(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regs[Reg.A] = cpu.regA() & value
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 1


# Instruction: Arithmetic Shift Left
# Function: A = C <- (A << 1) <- 0
# Flags: N, Z, C
def ASL(cpu: CPU, addr_abs: int, mode):
    value = cpu.regA() if mode == imp else cpu.read(addr_abs)
    value <<= 1
    cpu.set_flag(Flag.C, value > 0xFF)
    cpu.set_flag(Flag.Z, (value & 0x00FF) == 0x00)
    cpu.set_flag(Flag.N, value & 0x80)
    if mode == imp:
        cpu.regA(value & 0x00FF)
    else:
        cpu.write(addr_abs, value & 0x00FF)
    return 0


# Instruction: Branch if Carry Clear
# Function: if(C == 0) pc = address
def BCC(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.C) == 0:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Carry Set
# Function: if(C == 1) pc = address
def BCS(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.C) == 1:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Equal
# Function: if (Z == 1) pc = address
def BEQ(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.Z) == 1:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction:
# Function:
def BIT(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    value_processed = cpu.regA() & value
    cpu.set_flag(Flag.Z, (value_processed & 0x00FF) == 0x00)
    cpu.set_flag(Flag.N, value & Flag.N.value)
    cpu.set_flag(Flag.V, value & Flag.V.value)
    return 0


# Instruction: Branch if Negative
# Function: if (N == 1) pc = address
def BMI(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.N) == 1:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Not Equal
# Function: if (Z == 0) pc = address
def BNE(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.Z) == 0:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Positive
# Function: if (N == 0) pc = address
def BPL(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.N) == 0:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Overflow Clear
# Function: if (V == 0) pc = address
def BVC(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.V) == 0:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Branch if Overflow Set
# Function: if (V == 1) pc = address
def BVS(cpu: CPU, addr_rel: int, mode):
    if cpu.get_flag(Flag.V) == 1:
        cpu.cycles += 1
        addr_abs = cpu.regPC() + addr_rel

        if addr_abs & 0xFF00 != cpu.regPC() & 0xFF00:
            cpu.cycles += 1

        cpu.regPC(addr_abs)
    return 0


# Instruction: Compare Accumulator
# Function: C <- A >= M     Z <- (A - M) == 0
# Flags: N, C, Z
def CMP(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = cpu.regA() - value
    cpu.set_flag(Flag.C, cpu.regA() >= value)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, temp & 0x0080)
    return 1


# Instruction: Compare X Register
# Function: C <- X >= M     Z <- (X - M) == 0
# Flags: N, C, Z
def CPX(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = cpu.regX() - value
    cpu.set_flag(Flag.C, cpu.regX() >= value)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, temp & 0x0080)
    return 0


# Instruction: Compare Y Register
# Function: C <- Y >= M     Z <- (Y - M) == 0
# Flags: N, C, Z
def CPY(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = cpu.regY() - value
    cpu.set_flag(Flag.C, cpu.regY() >= value)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, temp & 0x0080)
    return 0


# Instruction: Decrement Value at Memory Location
# Function: M = M - 1
# Flags: N, Z
def DEC(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = value - 1
    cpu.write(addr_abs, temp & 0x00FF)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, temp & 0x0080)
    return 0


# Instruction: Decrement X Register
# Function: X = X - 1
# Flags: N, Z
def DEX(cpu: CPU, addr_abs: int, mode):
    cpu.regs[Reg.X] -= 1
    cpu.set_flag(Flag.Z, cpu.regX() == 0x0)
    cpu.set_flag(Flag.N, bool(cpu.regX() & 0x80))
    return 0


# Instruction: Decrement Y Register
# Function: Y = Y - 1
# Flags: N, Z
def DEY(cpu: CPU, addr_abs: int, mode):
    cpu.regs[Reg.Y] -= 1
    cpu.set_flag(Flag.Z, cpu.regY() == 0x0)
    cpu.set_flag(Flag.N, bool(cpu.regY() & 0x80))
    return 0


# Instruction: Bitwise Logic XOR
# Function: A = A xor M
# Flags: N, Z
def EOR(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regs[Reg.A] ^= value
    cpu.set_flag(Flag.Z, cpu.regA() == 0x0)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 1


# Instruction: Increment Value at Memory Location
# Function: M = M + 1
# Flags: N, Z
def INC(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    temp = value + 1
    cpu.write(addr_abs, temp & 0x00FF)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, bool(temp & 0x0080))
    return 0


# Instruction: Increment X Register
# Function: X = X + 1
# Flags: N, Z
def INX(cpu: CPU, addr_abs: int, mode):
    cpu.regs[Reg.X] += 1
    cpu.set_flag(Flag.Z, cpu.regX() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regX() & 0x80))
    return 0


# Instruction: Increment Y Register
# Function: Y = Y + 1
# Flags: N, Z
def INY(cpu: CPU, addr_abs: int, mode):
    cpu.regs[Reg.Y] += 1
    cpu.set_flag(Flag.Z, cpu.regY() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regY() & 0x80))
    return 0


# Instruction: Jump to Location
# Function: pc = addr
def JMP(cpu: CPU, addr_abs: int, mode):
    cpu.regPC(addr_abs)
    return 0


# Instruction: Jump to Subroutine
# Function: Push current pc to stack, pc = addr
def JSR(cpu: CPU, addr_abs: int, mode):
    cpu.inc_pc(-1)
    cpu.write(0x0100 + cpu.stack_pt, (cpu.regPC() >> 8) & 0x00FF)
    cpu.stack_pt -= 1
    cpu.write(0x0100 + cpu.stack_pt, cpu.regPC() & 0x00FF)
    cpu.stack_pt -= 1

    cpu.regPC(addr_abs)
    return 0


# Instruction: Load the Accumulator
# Function: A = M
# Flags: N, Z
def LDA(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regA(value)
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 1


# Instruction: Load the X Register
# Function: X = M
# Flags: N, Z
def LDX(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regX(value)
    cpu.set_flag(Flag.Z, cpu.regX() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regX() & 0x80))
    return 1


# Instruction: Load the Y Register
# Function: Y = M
# Flags: N, Z
def LDY(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regY(value)
    cpu.set_flag(Flag.Z, cpu.regY() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regY() & 0x80))
    return 1


# Instruction: Logical Shift Right
# Function: A = C <- (A >> 1) <- 0
# Flags: N, Z, C
def LSR(cpu: CPU, addr_abs: int, mode):
    value = cpu.regA() if mode == imp else cpu.read(addr_abs)
    cpu.set_flag(Flag.C, value & 0x0001)
    temp = value >> 1
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, bool(temp & 0x0080))
    if mode == imp:
        cpu.regA(temp & 0x00FF)
    else:
        cpu.write(addr_abs, temp & 0x00FF)
    return 0


# Instruction: Bitwise Logic OR
# Function: A = A | M
# Flags: N, Z
def ORA(cpu: CPU, addr_abs: int, mode):
    value = cpu.read(addr_abs)
    cpu.regs[Reg.A] |= value
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 1


# Instruction: Push Accumulator to Stack
# Function: A -> stack
def PHA(cpu: CPU, addr_abs: int, mode):
    cpu.write(0x0100 + cpu.stack_pt, cpu.regA())
    cpu.stack_pt -= 1
    return 0


# Instruction: Pop Accumulator off Stack
# Function: A = <- stack
# Flags: N, Z
def PHP(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt += 1
    cpu.regA(cpu.read(0x0100 + cpu.stack_pt))
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 0


# Instruction: Pop Accumulator off Stack
# Function: A <- stack
# Flags: N, Z
def PLA(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt += 1
    cpu.regA(cpu.read(0x0100 + cpu.stack_pt))
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 0


# Instruction: Pop Status Register off Stack
# Function: Status <- stack
def PLP(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt += 1
    cpu.regP = cpu.read(0x0100 + cpu.stack_pt)
    cpu.set_flag(Flag.U, True)
    return 0


# Instruction: Logical Rotate Left
# Function:
# Flags: N, Z, C
def ROL(cpu: CPU, addr_abs: int, mode):
    value = cpu.regA() if mode == imp else cpu.read(addr_abs)
    value = (value << 1) | cpu.get_flag(Flag.C)
    cpu.set_flag(Flag.C, value & 0xFF00)
    cpu.set_flag(Flag.Z, (value & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, value & 0x0080)
    if mode == imp:
        cpu.regA(value & 0x00FF)
    else:
        cpu.write(addr_abs, value & 0x00FF)
    return 0


# Instruction: Logical Rotate Right
# Function:
# Flags: N, Z, C
def ROR(cpu: CPU, addr_abs: int, mode):
    value = cpu.regA() if mode == imp else cpu.read(addr_abs)
    temp = (cpu.get_flag(Flag.C) << 7) | (value >> 1)
    cpu.set_flag(Flag.C, value & 0x01)
    cpu.set_flag(Flag.Z, (temp & 0x00FF) == 0x0000)
    cpu.set_flag(Flag.N, temp & 0x0080)
    if mode == imp:
        cpu.regA(temp & 0x00FF)
    else:
        cpu.write(addr_abs, temp & 0x00FF)
    return 0


# Instruction: Return from Interrupt
def RTI(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt += 1
    cpu.regP = cpu.read(0x0100 + cpu.stack_pt)
    cpu.regs[Reg.P] &= ~cpu.get_flag(Flag.B)
    cpu.regs[Reg.P] &= ~cpu.get_flag(Flag.U)

    cpu.stack_pt += 1
    cpu.regPC(cpu.read(0x0100 + cpu.stack_pt, 2) + 1)
    cpu.stack_pt += 1
    return 0


# Instruction: Return from Subroutine
def RTS(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt += 1
    cpu.regPC(cpu.read(0x0100 + cpu.stack_pt, 2) + 1)
    cpu.stack_pt += 1
    return 0


# Instruction: Set Carry Flag
# Function: C <- 1
def SEC(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.C, True)
    return 0


# Instruction: Set Interrupt Flag / Enable Interrupts
# Function: D <- 1
def SEI(cpu: CPU, addr_abs: int, mode):
    cpu.set_flag(Flag.I, True)
    return 0


# Instruction: Store Accumulator Address
# Function: M <- A
def STA(cpu: CPU, addr_abs: int, mode):
    cpu.write(addr_abs, cpu.regA())
    return 0


# Instruction: Store Accumulator Address
# Function: M <- X
def STX(cpu: CPU, addr_abs: int, mode):
    cpu.write(addr_abs, cpu.regX())
    return 0


# Instruction: Store Accumulator Address
# Function: M <- Y
def STY(cpu: CPU, addr_abs: int, mode):
    cpu.write(addr_abs, cpu.regY())
    return 0


# Instruction: Transfer Accumulator to X Register
# Function: X <- A
# Flags: N, Z
def TAX(cpu: CPU, addr_abs: int, mode):
    cpu.regX(cpu.regA())
    cpu.set_flag(Flag.Z, cpu.regX() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regX() & 0x80))
    return 0


# Instruction: Transfer Accumulator to Y Register
# Function: Y <- A
# Flags: N, Z
def TAY(cpu: CPU, addr_abs: int, mode):
    cpu.regY(cpu.regA())
    cpu.set_flag(Flag.Z, cpu.regY() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regY() & 0x80))
    return 0


# Instruction: Transfer Stack Pointer to X Register
# Function: X <- stack
# Flags: N, Z
def TSX(cpu: CPU, addr_abs: int, mode):
    cpu.regX(cpu.stack_pt)
    cpu.set_flag(Flag.Z, cpu.regX() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regX() & 0x80))
    return 0


# Instruction: Transfer X Register to Accumulator
# Function: A <- X
# Flags: N, Z
def TXA(cpu: CPU, addr_abs: int, mode):
    cpu.regA(cpu.stack_pt)
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 0


# Instruction: Transfer X Register to Stack Pointer
# Function: stack <- X
def TXS(cpu: CPU, addr_abs: int, mode):
    cpu.stack_pt = cpu.regX()
    return 0


# Instruction: Transfer Y Register to Accumulator
# Function: A <- Y
# Flags: N, Z
def TYA(cpu: CPU, addr_abs: int, mode):
    cpu.regA(cpu.regY())
    cpu.set_flag(Flag.Z, cpu.regA() == 0x00)
    cpu.set_flag(Flag.N, bool(cpu.regA() & 0x80))
    return 0


# Instruction: Break
# Function: Program Sourced Interrupt
def BRK(cpu: CPU, addr_abs: int, mode):
    cpu.inc_pc(1)
    cpu.set_flag(Flag.I, True)

    pc = cpu.regPC()
    cpu.write(0x0100 + cpu.stack_pt, (pc >> 8) & 0x00FF)
    cpu.stack_pt -= 1
    cpu.write(0x0100 + cpu.stack_pt, pc & 0x00FF)
    cpu.stack_pt -= 1

    cpu.set_flag(Flag.B, True)
    cpu.write(0x0100 + cpu.stack_pt, cpu.regP())
    cpu.stack_pt -= 1
    cpu.set_flag(Flag.B, False)

    cpu.regPC(cpu.read(0xFFFE, 2))
    return 0


def NOP(cpu: CPU, addr_abs: int, mode):
    return 1
