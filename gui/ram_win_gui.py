import wx
from wx import grid


class RamPopup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)

        elements = [self]
        # ram view
        self.SetBackgroundColour("CADET BLUE")
        title = wx.StaticText(self, -1, "RAM MEMORY (2KB)", pos=(14, 10), size=(40, 20), style=wx.ALIGN_RIGHT)
        title.SetFont(wx.Font(18, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        elements.append(title)

        # self.ram = wx.ListCtrl(self, pos=(2, 50), size=(840, 335), style=wx.LC_REPORT | wx.BORDER_DEFAULT)
        self.ram = wx.ListCtrl(self, pos=(2, 50), size=(1, 1), style=wx.LC_REPORT | wx.BORDER_DEFAULT)
        self.ram.InsertColumn(0, 'Address', width=80)
        elements.append(self.ram)

        for i in range(0, 16):
            self.ram.InsertColumn(i + 1, ('0x%1X' % i), width=47)

        elements.append(wx.StaticText(self, -1, "PAGE", pos=(690 - 105, 14), size=(40, 20), style=wx.ALIGN_RIGHT))
        self.page_spinner = wx.SpinCtrl(self, pos=(690 - 55, 12), size=(50, 20), style=wx.BORDER_RAISED)

        self.SetSize(710, 363)

        # ================
        self.ram_grid = grid.Grid(self, pos=(2, 50), size=(750, 340))
        self.ram_grid.CreateGrid(0x11, 0x11)

        self.ram_grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self.ram_grid.SetDefaultColSize(40, True)
        self.ram_grid.SetDefaultRowSize(18, True)

        self.ram_grid.SetMargins(0, 0)
        self.ram_grid.SetClientSize(self.Size)

        self.ram_grid.SetColSize(0, 60)

        self.ram_grid.HideRowLabels()
        self.ram_grid.HideColLabels()

        # mygrid.SetCellValue(1, 1, "Hello")
        # mygrid.SetCellFont(1, 1, wx.Font(15, wx.ROMAN, wx.ITALIC, wx.NORMAL))

        # self.ram_grid.SetCellValue(5, 5, "$AF")
        # self.ram_grid.SetCellBackgroundColour(5, 5, wx.RED)
        # self.ram_grid.SetCellTextColour(5, 5, wx.WHITE)

        # self.ram_grid.SetCellValue(8, 3, "$00")
        # self.ram_grid.SetReadOnly(8, 3, True)

        # self.ram_grid.SetCellEditor(6, 0, grid.GridCellNumberEditor(1, 20))
        # self.ram_grid.SetCellValue(6, 0, "$10")

        self.ram_grid.EnableScrolling(False, False)
        self.ram_grid.ShowScrollbars(False, False)

        self.normal_font = self.ram_grid.GetFont()
        self.bold_font = self.normal_font.Bold()

        self.__initialize_ram()

        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(mygrid, 1, wx.EXPAND)
        # self.SetSizer(sizer)
        # self.ram_grid.Update()

        for element in elements:
            element.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
            element.Bind(wx.EVT_MOTION, self.OnMouseMotion)
            element.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
            element.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def __initialize_ram(self):
        self.ram_grid.SetCellValue(0, 0, 'Address')
        self.ram_grid.SetCellBackgroundColour(0, 0, wx.LIGHT_GREY)

        for i in range(0, 0x10):
            self.ram_grid.SetCellValue(0, i + 1, '0x%1X' % i)
            self.ram_grid.SetCellBackgroundColour(0, i + 1, wx.LIGHT_GREY)
            self.ram_grid.SetCellBackgroundColour(i + 1, 0, wx.LIGHT_GREY)

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

    def GetBoldFont(self):
        return self.bold_font

    def GetNormalFont(self):
        return self.normal_font
