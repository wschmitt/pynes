import wx

from wx import glcanvas
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy

vertex_shader = """
# version 330
in layout(location = 0) vec3 positions;
in layout(location = 1) vec3 colors;

out vec3 newColor;

void main() {
    gl_Position = vec4(positions, 1.0);
    newColor = colors;
}
"""

fragment_shader = """
# version 330

in vec3 newColor;
out vec4 outColor;

void main() {
    outColor = vec4(newColor, 1.0);
}
"""


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(640, 480), pos=(4, 4))
        self.init = False
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        glClearColor(0.1, 0.15, 0.1, 1.0)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.InitGL()

    def OnResize(self, event):
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def InitGL(self):
        # vertices/colors
        triangle = [-0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
                    0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
                    0.0, 0.5, 0.0, 0.0, 0.0, 1.0]
        triangle = numpy.array(triangle, dtype=numpy.float32)
        shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, len(triangle) * 4, triangle, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glClearColor(0.1, 0.15, 0.1, 1.0)

        glUseProgram(shader)

    def OnPaint(self, event):
        if not self.init:
            self.init = True
        self.OnDraw()

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        self.SwapBuffers()


class EmuPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.canvas = OpenGLCanvas(self)
        self.SetBackgroundColour("#626D58")

        # ram view
        self.ram = wx.ListCtrl(self, pos=(1080, 10), size=(170, 500), style=wx.LC_REPORT | wx.BORDER_DEFAULT)
        self.ram.InsertColumn(0, 'Address', width=60)
        self.ram.InsertColumn(1, 'Value', width=80)

        # ram page changer
        self.previous_page_btn = wx.Button(self, -1, label="<<", pos=(1080, 520), size=(50, 25))
        self.next_page_btn = wx.Button(self, -1, label=">>", pos=(1200, 520), size=(50, 25))
        self.page = wx.StaticText(self, -1, label="Page 0", pos=(1135, 520), size=(60, 25),
                                  style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.page.BackgroundColour = [200, 200, 200]

        # code view
        self.code = wx.ListCtrl(self, pos=(660, 80), size=(400, 300),
                                style=wx.LC_REPORT | wx.BORDER_DEFAULT | wx.LC_SINGLE_SEL)
        self.set_code_window_header()
        self.code.Bind(wx.EVT_LEFT_DOWN, lambda evt: self.code.SetFocus())
        self.code.Bind(wx.EVT_RIGHT_DOWN, lambda evt: self.code.SetFocus())

        # execute instruction button
        self.execute_instr_btn = wx.Button(self, -1, label="Run Instruction", pos=(960, 390), size=(100, 25))
        self.load_rom = wx.Button(self, -1, label="Load ROM", pos=(845, 390), size=(100, 25))
        self.reset = wx.Button(self, -1, label="Reset Program", pos=(660, 390), size=(100, 25))

        # registers
        self.cpu_registers = wx.StaticText(self, -1, label="", pos=(660, 10), size=(400, 15),
                                           style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cpu_registers.BackgroundColour = [200, 200, 200]

        # flags = "C: {0} Z: {1} I: {2} D: {3} B: {4} U: {5} V: {6} N: {7}".format(0, 0, 0, 0, 0, 0, 0, 0)
        self.cpu_flags = wx.StaticText(self, -1, label="", pos=(660, 30), size=(400, 15),
                                       style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cpu_flags.BackgroundColour = [200, 200, 200]

        font = self.cpu_registers.GetFont()
        font.PointSize += 2
        font = font.Bold()
        self.cpu_registers.SetFont(font)
        self.cpu_flags.SetFont(font)

    def clear_code_window(self):
        self.code.ClearAll()
        self.set_code_window_header()

    def set_code_window_header(self):
        self.code.InsertColumn(0, 'Address', width=60)
        self.code.InsertColumn(1, 'Instr.', width=70)
        self.code.InsertColumn(2, 'Param 1', width=70)
        self.code.InsertColumn(3, 'Param 2', width=70)
        self.code.InsertColumn(4, 'Addr. Mode', width=100)

    def show_file_dialog(self):
        with wx.FileDialog(self, "Open ROM File", wildcard="ROM Files (*.nes)|*.nes|6502 Bytecode (*.dat)|*.dat",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return ""
            # Proceed loading the file chosen
            return fileDialog.GetPath()


class EmuFrame(wx.Frame):
    def __init__(self):
        self.size = (1280, 720)
        wx.Frame.__init__(self, None, title="Emulator PyNes", size=self.size,
                          style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        self.SetMinSize(self.size)
        self.SetMaxSize(self.size)
        self.panel = EmuPanel(self)


class EmuApp(wx.App):
    def OnInit(self):
        self.frame = EmuFrame()
        self.frame.Show()
        return True
