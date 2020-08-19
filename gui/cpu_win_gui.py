import wx
from wx import grid


class CpuPopup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)

        elements = [self]

        # registers
        self.cpu_registers = wx.StaticText(self, -1, label="", pos=(10, 10), size=(400, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cpu_registers.BackgroundColour = [200, 200, 200]

        # flags = "C: {0} Z: {1} I: {2} D: {3} B: {4} U: {5} V: {6} N: {7}".format(0, 0, 0, 0, 0, 0, 0, 0)
        self.cpu_flags = wx.StaticText(self, -1, label="", pos=(10, 30), size=(400, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cpu_flags.BackgroundColour = [200, 200, 200]

        font = self.cpu_registers.GetFont()
        font.PointSize += 2
        font = font.Bold()
        self.cpu_registers.SetFont(font)
        self.cpu_flags.SetFont(font)

        # code view
        self.code = wx.ListCtrl(self, pos=(10, 80), size=(400, 300),
                                style=wx.LC_REPORT | wx.BORDER_DEFAULT | wx.LC_SINGLE_SEL)
        self.set_code_window_header()
        self.code.Bind(wx.EVT_LEFT_DOWN, lambda evt: self.code.SetFocus())
        self.code.Bind(wx.EVT_RIGHT_DOWN, lambda evt: self.code.SetFocus())

        self.SetSize(600, 800)

        for element in elements:
            element.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
            element.Bind(wx.EVT_MOTION, self.OnMouseMotion)
            element.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
            element.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def clear_code_window(self):
        self.code.ClearAll()
        self.set_code_window_header()

    def set_code_window_header(self):
        self.code.InsertColumn(0, 'Address', width=60)
        self.code.InsertColumn(1, 'Instr.', width=70)
        self.code.InsertColumn(2, 'Param 1', width=70)
        self.code.InsertColumn(3, 'Param 2', width=70)
        self.code.InsertColumn(4, 'Addr. Mode', width=100)

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
