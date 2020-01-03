import wx

import cpu
from cpu_opcodes import opcodes
from emulator import Emulator
from emulator_gui import EmuPanel
from rom import ROM


class EmuController:
    def __init__(self, emu: Emulator, emu_gui: EmuPanel):
        self.emu = emu
        self.view = emu_gui
        self.canvas = emu_gui.canvas

        self.__lookup_instr_table = {}
        self.ram_page = 0
        self.ram_page_size = int(self.emu.ram.size / 0x100)

        self.current_instr = 0

        self.__setup_events()
        self.refresh_view()

    def __setup_events(self):
        self.view.Bind(wx.EVT_BUTTON, self.__next_page_ram, self.view.next_page_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__previous_page_ram, self.view.previous_page_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__tick_clock, self.view.tick_clock_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__execute_frame, self.view.execute_frame_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__open_rom_dialog, self.view.load_rom)
        self.view.Bind(wx.EVT_CHECKBOX, self.__draw_chr_table, self.view.draw_pattern_table_checkbox)

    def __draw_chr_table(self, evt):
        if self.view.draw_pattern_table_checkbox.GetValue():
            pattern_tbl = self.emu.ppu.get_pattern_table(0, 0)
            for x in range(256):
                for y in range(240):
                    self.canvas.SetPixel(x, y, [0, 0, 0])

            for x in range(0, 128):
                for y in range(0, 128):
                    # print(x, y, pattern_tbl[x + 128 * y])
                    # try:
                    self.canvas.SetPixel(x, y, pattern_tbl[x + 128 * y])  # pattern_tbl[x + 128 * y]
                # except:
                #     continue

            # for x in range(len(self.canvas.screen_tex)):
            #    for y in range(len(self.canvas.screen_tex[x])):
            #        color = pattern_tbl[x][y] if x < len(pattern_tbl) and y < len(pattern_tbl[0]) else [255, 255, 255]
            # color = pattern_tbl[x][y]  # get color from chr pattern in PPU
            #        self.canvas.screen_tex[x][y] = color
        # else:
        # self.canvas.SetTexture(np.random.randint(256, size=(240, 256, 3)))

        self.repaint_canvas()

    def set_canvas_pixel(self, x: int, y: int, color: []):
        self.canvas.screen_tex[x][y] = color

    def repaint_canvas(self):
        self.canvas.OnDraw()

    def __execute_frame(self, evt):
        self.canvas.SetPixel(0, 0, [255, 255, 255])
        self.repaint_canvas()
        # for i in range(0, 100):
        #     self.emu.tick_clock()
        # self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]
        # self.update_instr_selection()
        # self.__refresh_cpu_registers()
        # self.__refresh_cpu_flags()
        # self.__refresh_ram()

    # executes the current selected instruction
    def __tick_clock(self, evt):
        self.emu.tick_clock()
        # point selection to the next instruction
        self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]

        # update UI
        self.update_instr_selection()
        self.__refresh_cpu_registers()
        self.__refresh_cpu_flags()
        self.__refresh_ram()
        self.__refresh_canvas()

    def __refresh_canvas(self):
        self.canvas.SetTexture(self.emu.ppu.frameBuffer)
        self.repaint_canvas()

    def __next_page_ram(self, evt):
        self.ram_page = min(self.ram_page + 1, self.ram_page_size - 1)
        self.view.page.SetLabelText("page {0}".format(self.ram_page))
        self.__refresh_ram()

    def __previous_page_ram(self, evt):
        self.ram_page = max(self.ram_page - 1, 0)
        self.view.page.SetLabelText("page {0}".format(self.ram_page))
        self.__refresh_ram()

    def __refresh_ram(self):
        self.view.ram.DeleteAllItems()
        start_addr = self.ram_page * self.ram_page_size
        for addr in range(0, 0x100):
            val = self.emu.ram.cpu_read(start_addr + addr)
            self.view.ram.InsertItem(addr, ('$%02x' % addr).upper())
            self.view.ram.SetItem(addr, 1, '$%02x' % val)

    def __refresh_rom(self):
        self.view.clear_code_window()
        pc = 0xC000
        i = -1
        while True:
            i += 1
            self.__lookup_instr_table[pc] = i
            addr = self.emu.rom.get(pc)
            if not addr:
                break
            elif addr not in opcodes:
                print("opcode not found: ", hex(pc - 0xc000), hex(addr))
                pc += 1
                i -= 1
                continue
            instr = opcodes[addr]
            print(i, hex(addr), hex(pc), instr.mnem, instr.size)
            if self.view.code.ItemCount <= i:
                self.view.code.InsertItem(i, ('$%02x' % pc).upper())
            else:
                self.view.code.SetItem(i, ('$%02x' % pc).upper())
            self.view.code.SetItem(i, 1, instr.mnem)
            if instr.size == 1:
                self.view.code.SetItem(i, 4, "Imp")
                pc += 1
            elif instr.size == 2:
                mem = self.emu.rom.get(pc + 1)
                if instr.mode == cpu.imm:
                    self.view.code.SetItem(i, 2, ("#$%02x" % mem).upper())
                    self.view.code.SetItem(i, 4, "Imm")
                elif instr.mode == cpu.zp0:
                    self.view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    self.view.code.SetItem(i, 4, "Zp0")
                elif instr.mode == cpu.zpx:
                    self.view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    self.view.code.SetItem(i, 3, "X")
                    self.view.code.SetItem(i, 4, "ZpX")
                elif instr.mode == cpu.zpy:
                    self.view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    self.view.code.SetItem(i, 3, "Y")
                    self.view.code.SetItem(i, 4, "ZpY")
                elif instr.mode == cpu.idx:
                    self.view.code.SetItem(i, 2, ("($%02x," % mem).upper())
                    self.view.code.SetItem(i, 3, "X)")
                    self.view.code.SetItem(i, 4, "IdX")
                elif instr.mode == cpu.idy:
                    self.view.code.SetItem(i, 2, ("($%02x)" % mem).upper())
                    self.view.code.SetItem(i, 3, "Y")
                    self.view.code.SetItem(i, 4, "IdY")
                elif instr.mode == cpu.rel:
                    self.view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    self.view.code.SetItem(i, 4, "Rel")
                pc += 2
            elif instr.size == 3:
                mem = self.emu.rom.get_word(pc + 1)
                if instr.mode == cpu.abs:
                    # uses two bytes as addressing ex: JMP $4032
                    self.view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    self.view.code.SetItem(i, 4, "Abs")
                elif instr.mode == cpu.abx:
                    self.view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    self.view.code.SetItem(i, 3, "X")
                    self.view.code.SetItem(i, 4, "AbX")
                elif instr.mode == cpu.aby:
                    self.view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    self.view.code.SetItem(i, 3, "Y")
                    self.view.code.SetItem(i, 4, "AbY")
                elif instr.mode == cpu.ind:
                    self.view.code.SetItem(i, 2, ('($%04x)' % mem).upper())
                    self.view.code.SetItem(i, 4, "Ind")
                pc += 3

        self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]
        self.update_instr_selection()

    def update_instr_selection(self):
        self.view.code.SetFocus()
        self.view.code.Select(self.current_instr, 1)
        self.view.code.EnsureVisible(self.view.code.GetFirstSelected())

    def refresh_view(self):
        self.__refresh_ram()
        self.__refresh_cpu_registers()
        self.__refresh_cpu_flags()
        if self.emu.has_rom():
            self.__refresh_rom()
            self.__set_code_button(True)
        else:
            self.__set_code_button(False)

    def __refresh_cpu_registers(self):
        a = self.emu.cpu.regA()
        x = self.emu.cpu.regX()
        y = self.emu.cpu.regY()
        pc = self.emu.cpu.regPC()
        self.view.cpu_registers.SetLabelText(
            "[X: ${0}]    [Y: ${1}]    [A: ${2}]    [PC: ${3}]".format('%02x' % x, '%02x' % y, '%02x' % a,
                                                                       ('%04x' % pc).upper()))

    def __set_code_button(self, enabled: bool):
        self.view.tick_clock_btn.Enable(enabled)
        self.view.reset.Enable(enabled)

    def __refresh_cpu_flags(self):
        from cpu import Flag
        c = int(self.emu.cpu.get_flag(Flag.C))
        z = int(self.emu.cpu.get_flag(Flag.Z))
        i = int(self.emu.cpu.get_flag(Flag.I))
        d = int(self.emu.cpu.get_flag(Flag.D))
        b = int(self.emu.cpu.get_flag(Flag.B))
        u = int(self.emu.cpu.get_flag(Flag.U))
        v = int(self.emu.cpu.get_flag(Flag.V))
        n = int(self.emu.cpu.get_flag(Flag.N))
        self.view.cpu_flags.SetLabelText(
            "[C: {0}]   [Z: {1}]   [I: {2}]   [D: {3}]   [B: {4}]   [U: {5}]   [V: {6}]   [N: {7}]".
                format(c, z, i, d, b, u, v, n))

    def __open_rom_dialog(self, evt):
        path = self.view.show_file_dialog()
        if path:
            try:
                with open(path, 'rb') as file:
                    if path.endswith(".nes") or path.endswith(".NES"):
                        self.emu.set_rom(ROM(file, True))
                    elif path.endswith(".dat") or path.endswith(".DAT"):
                        self.emu.set_rom(ROM(file, False))
                    self.__refresh_rom()
            except IOError:
                wx.LogError("Cannot open file: '%s'." % path)

        self.__set_code_button(self.emu.has_rom())
