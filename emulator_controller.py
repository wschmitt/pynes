import wx
import random

import cpu
from cpu_opcodes import opcodes
from emulator import Emulator
from gui.main_gui import EmuPanel
from rom import ROM


class EmuController:
    def __init__(self, emu: Emulator, emu_gui: EmuPanel):
        self.emu = emu
        self.view = emu_gui
        self.canvas = emu_gui.canvas

        self.__lookup_instr_table = {}
        self.ram_page = 0
        self.ram_page_size = int(self.emu.ram.size / 0x100)
        self.view.ram_gui.page_spinner.SetMax(self.ram_page_size - 1)

        self.current_instr = 0
        self.current_palette = 0

        self.current_clock_cycles_skip = 0

        self.__setup_events()
        self.refresh_view()

    def __setup_events(self):
        # self.view.Bind(wx.EVT_BUTTON, self.__next_page_ram, self.view.next_page_btn)
        # self.view.Bind(wx.EVT_BUTTON, self.__previous_page_ram, self.view.previous_page_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__tick_clock, self.view.tick_clock_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__execute_frame, self.view.execute_frame_btn)
        self.view.Bind(wx.EVT_BUTTON, self.__open_rom_dialog, self.view.load_rom)

        # POPUPS
        self.view.Bind(wx.EVT_BUTTON, self.__open_chr_popup, self.view.open_chr_table_gui)
        self.view.Bind(wx.EVT_BUTTON, self.__open_ram_gui, self.view.open_ram_gui)
        self.view.Bind(wx.EVT_BUTTON, self.__open_cpu_gui, self.view.open_cpu_gui)

        # SPINNERS
        self.view.chr_gui.Bind(wx.EVT_SPINCTRL, self.__change_chr_palette, self.view.chr_gui.palette_spinner)
        self.view.ram_gui.Bind(wx.EVT_SPINCTRL, self.__change_ram_page, self.view.ram_gui.page_spinner)

        self.view.Bind(wx.EVT_TEXT, self.__on_key_typed, self.view.tick_clock_qty_text)

    def __on_key_typed(self, evt):
        self.current_clock_cycles_skip = int(evt.GetString())

    def __change_chr_palette(self, evt):
        self.current_palette = self.view.chr_gui.palette_spinner.GetValue()
        self.__draw_chr_table()

    def __change_ram_page(self, evt):
        self.ram_page = self.view.ram_gui.page_spinner.GetValue()
        self.__refresh_ram()

    def __open_window_gui(self, evt, gui: wx.PopupWindow):
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()

        gui.Position(pos, (0, sz[1]))
        gui.Show(True)

    def __open_cpu_gui(self, evt):
        self.__open_window_gui(evt, self.view.cpu_gui)

    def __open_ram_gui(self, evt):
        self.__open_window_gui(evt, self.view.ram_gui)
        self.__refresh_ram()

    def __open_chr_popup(self, evt):
        self.__open_window_gui(evt, self.view.chr_gui)
        self.__draw_chr_table()

    def __draw_chr_table(self):
        if not self.view.chr_gui.IsShown():
            return

        pattern_tbl = self.emu.ppu.get_pattern_table(0, self.current_palette)

        for x in range(0, 0x80):
            for y in range(0, 0x80):
                self.view.chr_gui.canvas.SetPixel(x, y, pattern_tbl[x + 0x80 * y])

        self.view.chr_gui.canvas.OnDraw()

    def set_canvas_pixel(self, x: int, y: int, color: []):
        self.canvas.screen_tex[x][y] = color

    def repaint_canvas(self):
        self.canvas.OnDraw()

    def __execute_frame(self, evt):
        while not self.emu.ppu.frame_complete:
            self.emu.tick_clock()

        self.__update_ui()
        # self.canvas.SetPixel(0, 0, [255, 255, 255])
        # self.repaint_canvas()
        # for i in range(0, 100):
        #     self.emu.tick_clock()
        # self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]
        # self.update_instr_selection()
        # self.__refresh_cpu_registers()
        # self.__refresh_cpu_flags()
        # self.__refresh_ram()

    # executes the current selected instruction
    def __tick_clock(self, evt):
        # keep clocking until the current instr is done executing
        skip_instr = self.current_clock_cycles_skip
        while skip_instr > 0:
            while self.emu.cpu.cycles == 0:
                self.emu.tick_clock()
            while self.emu.cpu.cycles > 0:
                self.emu.tick_clock()
            skip_instr -= 1

        # point selection to the next instruction
        if self.emu.cpu.regPC() in self.__lookup_instr_table:
            self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]

        self.__update_ui()
        self.__draw_chr_table()

    def __update_ui(self):
        self.update_instr_selection()
        self.__refresh_cpu_registers()
        self.__refresh_cpu_flags()
        self.__refresh_ram()
        self.__refresh_canvas()

    def __refresh_canvas(self):
        self.canvas.SetTexture(self.emu.ppu.frameBuffer)
        self.repaint_canvas()

    def __refresh_ram(self):
        if not self.view.ram_gui.IsShown():
            return
        self.view.ram_gui.ram.DeleteAllItems()
        start_addr = self.ram_page * self.ram_page_size
        for ms_addr_in_page in range(0, 0x10):
            abs_addr = self.ram_page * 0x100 + ms_addr_in_page * 0x10
            self.view.ram_gui.ram_grid.SetCellValue(ms_addr_in_page + 1, 0, '$%04X' % abs_addr)
            for ls_addr_in_page in range(0, 0x10):
                rel_addr = ms_addr_in_page * 0x10 + ls_addr_in_page
                val = self.emu.ram.cpu_read(start_addr + rel_addr)

                # set font
                self.view.ram_gui.ram_grid.SetCellValue(ms_addr_in_page + 1, ls_addr_in_page + 1, '$%02X' % val)
                font = self.view.ram_gui.GetBoldFont() if val > 0 else self.view.ram_gui.GetNormalFont()
                self.view.ram_gui.ram_grid.SetCellFont(ms_addr_in_page + 1, ls_addr_in_page + 1, font)

    def __refresh_rom(self):
        cpu_view = self.view.cpu_gui
        cpu_view.clear_code_window()
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
            if cpu_view.code.ItemCount <= i:
                cpu_view.code.InsertItem(i, ('$%02x' % pc).upper())
            else:
                cpu_view.code.SetItem(i, ('$%02x' % pc).upper())
            cpu_view.code.SetItem(i, 1, instr.mnem)
            if instr.size == 1:
                cpu_view.code.SetItem(i, 4, "Imp")
                pc += 1
            elif instr.size == 2:
                mem = self.emu.rom.get(pc + 1)
                if instr.mode == cpu.imm:
                    cpu_view.code.SetItem(i, 2, ("#$%02x" % mem).upper())
                    cpu_view.code.SetItem(i, 4, "Imm")
                elif instr.mode == cpu.zp0:
                    cpu_view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    cpu_view.code.SetItem(i, 4, "Zp0")
                elif instr.mode == cpu.zpx:
                    cpu_view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    cpu_view.code.SetItem(i, 3, "X")
                    cpu_view.code.SetItem(i, 4, "ZpX")
                elif instr.mode == cpu.zpy:
                    cpu_view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    cpu_view.code.SetItem(i, 3, "Y")
                    cpu_view.code.SetItem(i, 4, "ZpY")
                elif instr.mode == cpu.idx:
                    cpu_view.code.SetItem(i, 2, ("($%02x," % mem).upper())
                    cpu_view.code.SetItem(i, 3, "X)")
                    cpu_view.code.SetItem(i, 4, "IdX")
                elif instr.mode == cpu.idy:
                    cpu_view.code.SetItem(i, 2, ("($%02x)" % mem).upper())
                    cpu_view.code.SetItem(i, 3, "Y")
                    cpu_view.code.SetItem(i, 4, "IdY")
                elif instr.mode == cpu.rel:
                    cpu_view.code.SetItem(i, 2, ("$%02x" % mem).upper())
                    cpu_view.code.SetItem(i, 4, "Rel")
                pc += 2
            elif instr.size == 3:
                mem = self.emu.rom.get_word(pc + 1)
                if instr.mode == cpu.abs:
                    # uses two bytes as addressing ex: JMP $4032
                    cpu_view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    cpu_view.code.SetItem(i, 4, "Abs")
                elif instr.mode == cpu.abx:
                    cpu_view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    cpu_view.code.SetItem(i, 3, "X")
                    cpu_view.code.SetItem(i, 4, "AbX")
                elif instr.mode == cpu.aby:
                    cpu_view.code.SetItem(i, 2, ('$%04x' % mem).upper())
                    cpu_view.code.SetItem(i, 3, "Y")
                    cpu_view.code.SetItem(i, 4, "AbY")
                elif instr.mode == cpu.ind:
                    cpu_view.code.SetItem(i, 2, ('($%04x)' % mem).upper())
                    cpu_view.code.SetItem(i, 4, "Ind")
                pc += 3

        self.current_instr = self.__lookup_instr_table[self.emu.cpu.regPC()]
        self.update_instr_selection()

    def update_instr_selection(self):
        self.view.cpu_gui.code.SetFocus()
        self.view.cpu_gui.code.Select(self.current_instr, 1)
        self.view.cpu_gui.code.EnsureVisible(self.view.cpu_gui.code.GetFirstSelected())

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
        self.view.cpu_gui.cpu_registers.SetLabelText(
            "[X: ${0}]    [Y: ${1}]    [A: ${2}]    [PC: ${3}]".format('%02x' % x, '%02x' % y, '%02x' % a,
                                                                       ('%04x' % pc).upper()))

    def __set_code_button(self, enabled: bool):
        self.view.tick_clock_btn.Enable(enabled)
        self.view.reset.Enable(enabled)
        self.view.open_chr_table_gui.Enable(enabled)

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
        self.view.cpu_gui.cpu_flags.SetLabelText(
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
