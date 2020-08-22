import wx
from wx import grid


class CpuPopup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)
        self.SetBackgroundColour("CADET BLUE")

        elements = [self]

        self.red = (220, 30, 30)
        self.green = (30, 255, 30)

        # title
        title = wx.StaticText(self, -1, "CODE AND CPU FLAGS", pos=(14, 10), size=(40, 20), style=wx.ALIGN_RIGHT)
        title.SetFont(wx.Font(18, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        elements.append(title)

        # cpu view box
        wx.StaticBox(self, wx.ID_ANY, "CPU", pos=(290, 45), size=(215, 200))

        # registers X, Y, A, PC
        cpu_registers_label = wx.StaticText(self, -1, label="Registers", pos=(300, 70), size=(50, 15),
                                            style=wx.ALIGN_LEFT)
        self.registerX = wx.StaticText(self, -1, label="X: $00", pos=(300, 95), size=(70, 20), style=wx.ALIGN_LEFT)
        self.registerY = wx.StaticText(self, -1, label="Y: $00", pos=(300, 115), size=(70, 20), style=wx.ALIGN_LEFT)
        self.registerA = wx.StaticText(self, -1, label="A: $00", pos=(300, 135), size=(70, 20), style=wx.ALIGN_LEFT)
        self.registerPC = wx.StaticText(self, -1, label="PC: $0000", pos=(300, 165), size=(70, 20), style=wx.ALIGN_LEFT)

        self.__registers = {"x": self.registerX, "y": self.registerY, "a": self.registerA}
        self.__registers_values = {"x": 0, "y": 0, "a": 0}

        # flags = "C: {0} Z: {1} I: {2} D: {3} B: {4} U: {5} V: {6} N: {7}".format(0, 0, 0, 0, 0, 0, 0, 0)
        cpu_flags_label = wx.StaticText(self, -1, label="Flags", pos=(433, 70), size=(70, 15), style=wx.ALIGN_LEFT)
        self.flagC = wx.StaticText(self, -1, label="C: 0", pos=(435, 95), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagZ = wx.StaticText(self, -1, label="Z: 0", pos=(435, 113), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagI = wx.StaticText(self, -1, label="I: 0", pos=(435, 131), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagD = wx.StaticText(self, -1, label="D: 0", pos=(435, 149), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagB = wx.StaticText(self, -1, label="B: 0", pos=(435, 167), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagU = wx.StaticText(self, -1, label="U: 0", pos=(435, 185), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagV = wx.StaticText(self, -1, label="V: 0", pos=(435, 203), size=(50, 20), style=wx.ALIGN_LEFT)
        self.flagN = wx.StaticText(self, -1, label="N: 0", pos=(435, 221), size=(50, 20), style=wx.ALIGN_LEFT)

        self.__flags = {"c": self.flagC,
                        "z": self.flagZ,
                        "i": self.flagI,
                        "d": self.flagD,
                        "b": self.flagB,
                        "u": self.flagU,
                        "v": self.flagV,
                        "n": self.flagN}

        font = cpu_registers_label.GetFont()
        font.Family = wx.FONTFAMILY_MODERN
        font.PointSize += 3
        font = font.Bold()

        self.registerX.SetFont(font)
        self.registerY.SetFont(font)
        self.registerA.SetFont(font)
        self.registerPC.SetFont(font)

        self.flagC.SetFont(font)
        self.flagZ.SetFont(font)
        self.flagI.SetFont(font)
        self.flagD.SetFont(font)
        self.flagB.SetFont(font)
        self.flagU.SetFont(font)
        self.flagV.SetFont(font)
        self.flagN.SetFont(font)

        cpu_registers_label.SetFont(font)
        cpu_flags_label.SetFont(font)

        # Buttons
        self.tick_clock_btn = wx.Button(self, -1, label="Execute 1", pos=(290, 250), size=(100, 25))
        self.tick_clock_n_btn = wx.Button(self, -1, label="Execute N", pos=(290, 280), size=(100, 25))
        self.tick_clock_address_btn = wx.Button(self, -1, label="Execute Addr", pos=(290, 310), size=(100, 25))
        self.execute_frame_btn = wx.Button(self, -1, label="Complete Frame", pos=(290, 345), size=(100, 25))

        self.tick_clock_qty_text = wx.SpinCtrl(self, -1, value="2", pos=(400, 280), size=(100, 25),
                                               style=wx.TE_PROCESS_ENTER)
        self.tick_clock_address_text = wx.TextCtrl(self, -1, value="C400", pos=(400, 310), size=(100, 25))

        self.tick_clock_qty_text.SetMin(1)
        self.tick_clock_qty_text.SetMax(100000)

        self.SetSize(520, 450)

        # ================
        self.code_grid = grid.Grid(self, pos=(2, 50), size=(450, 300))
        self.code_grid.CreateGrid(1, 4)

        self.code_grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self.code_grid.SetDefaultColSize(40, True)
        self.code_grid.SetDefaultRowSize(18, True)

        self.code_grid.SetMargins(0, 0)
        self.code_grid.SetClientSize((280, 390))

        self.code_grid.HideRowLabels()
        self.code_grid.HideColLabels()

        self.code_grid.DisableDragColSize()
        self.code_grid.DisableDragRowSize()
        self.code_grid.DisableDragGridSize()

        self.set_code_window_header(True)

        self.code_grid.EnableEditing(False)

        # self.code_grid.SelectRow(0)

        self.code_grid.SetSelectionMode(wx.grid.Grid.GridSelectionModes.GridSelectRows)

        self.code_grid.GetGridWindow().Bind(wx.EVT_MOTION, self.__ignore_event)
        self.code_grid.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.__ignore_event)

        for element in elements:
            element.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
            element.Bind(wx.EVT_MOTION, self.OnMouseMotion)
            element.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
            element.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def __ignore_event(self, event):
        # just trap this event and prevent it from percolating up the window hierarchy
        pass

    def set_registers(self, x, y, a, pc):
        registers = {"x": x, "y": y, "a": a}
        for name, value in registers.items():
            if value != self.__registers_values[name]:
                self.__registers_values[name] = value
                self.__registers[name].SetForegroundColour(self.green)
                self.__registers[name].SetLabelText("{0}: ${1}".format(name.upper(), '%02X' % value))
            else:
                self.__registers[name].SetForegroundColour(wx.BLACK)
                self.__registers[name].Update()

        self.registerPC.SetLabelText("PC: ${0}".format('%04X' % pc))
        self.Refresh()

    def set_flags(self, c, z, i, d, b, u, v, n):
        flags = {"c": c, "z": z, "i": i, "d": d, "b": b, "u": u, "v": v, "n": n}
        for name, value in flags.items():
            color = self.green if value > 0 else self.red
            self.__flags[name].SetForegroundColour(color)
            self.__flags[name].SetLabelText("{0}: {1}".format(name.upper(), value))

    def clear_code_window(self):
        self.code_grid.ClearGrid()
        self.set_code_window_header(False)

    def set_code_window_header(self, extended):
        cols = ['Address', 'Instr.', 'Parameters', 'Addr. Mode']
        sizes = [60, 50, 90, 80] if extended else [60, 40, 80, 80]

        for i in range(0, len(cols)):
            self.code_grid.SetCellValue(0, i, cols[i])
            self.code_grid.SetColMinimalWidth(i, sizes[i])
            self.code_grid.AutoSizeColLabelSize(i)
            self.code_grid.SetCellBackgroundColour(0, i, wx.LIGHT_GREY)

    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0, 0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            try:
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                        self.wPos.y + (dPos.y - self.ldPos.y))
                self.Move(nPos)
            except:
                pass

    def OnMouseLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
