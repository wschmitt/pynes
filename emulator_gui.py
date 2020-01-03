import wx

from wx import glcanvas
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

vertex_shader2 = """
# version 330
in layout(location = 0) vec3 positions;
in layout(location = 1) vec3 colors;

out vec3 newColor;

void main() {
    gl_Position = vec4(positions, 1.0);
    newColor = colors;
}
"""

fragment_shader2 = """
# version 330

in vec3 newColor;
out vec4 outColor;

void main() {
    outColor = vec4(newColor, 1.0);
}
"""

vertex_shader = """# version 400
layout(location=0) in vec2 position;
layout(location=1) in vec2 texCoords;
out vec2 TexCoords;
void main()
{
    gl_Position = vec4(position.x, position.y, 0.0f, 1.0f);
    TexCoords = texCoords;
}
"""

fragment_shader = """# version 400
in vec2 TexCoords;
out vec4 color;
uniform sampler2D screenTexture;
void main()
{
    vec3 sampled = vec4(texture(screenTexture, TexCoords)).xyz; // original rendered pixel color value
    //color = vec4(TexCoords.x, TexCoords.y, 0., 1.); // to see whether I placed quad correctly
    //color = vec4(sampled, 1.0); // original
    color = vec4(sampled, 1.0); // processed (inverted)
}
"""


# Utility functions
def float_size(n=1):
    return sizeof(ctypes.c_float) * n


def pointer_offset(n=0):
    return ctypes.c_void_p(float_size(n))


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        # the nes resolution is 256 x 240 - we are making it 2.5x bigger
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(640, 600), pos=(4, 4))
        self.init = False
        self.screen_quad_vao = 0
        self.shader = None
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        glClearColor(0.1, 0.15, 0.1, 1.0)

        self.__screen_tex = np.zeros((240, 256, 3))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.InitGL()

    def OnResize(self, event):
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def InitGL(self):
        # positions / tex coords
        quad = np.array([-1, 1, 0, 1,
                         -1, -1, 0, 0,
                         1, -1, 1, 0,
                         -1, 1, 0, 1,
                         1, -1, 1, 0,
                         1, 1, 1, 1], dtype=np.float32)

        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

        self.screen_quad_vao = GLuint()
        glGenVertexArrays(1, self.screen_quad_vao)
        glBindVertexArray(self.screen_quad_vao)

        quad_vbo = GLuint()
        glGenBuffers(1, quad_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, float_size(4), pointer_offset(0))
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, float_size(4), pointer_offset(2))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        glClearColor(0.1, 0.15, 0.1, 1.0)

    def draw_quad(self):
        # Framebuffer to render offscreen
        fbo = GLuint()
        glGenFramebuffers(1, fbo)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 256, 240, 0, GL_RGB, GL_UNSIGNED_BYTE, self.__screen_tex)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(1, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glBindVertexArray(self.screen_quad_vao)
        glUseProgram(self.shader)
        glBindTexture(GL_TEXTURE_2D, texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

    def OnPaint(self, event):
        if not self.init:
            self.init = True
        self.OnDraw()

    def SetPixel(self, x: int, y: int, color):
        #self.__screen_tex[239 - y][x] = color
        pass

    def SetTexture(self, tex):
        pass
        # for y in range(0, len(self.__screen_tex)):
        #     for x in range(0, len(self.__screen_tex[y])):
        #         self.SetPixel(x, y, tex[y][x])

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw_quad()
        # glDrawArrays(GL_TRIANGLES, 0, 6)
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
        self.tick_clock_btn = wx.Button(self, -1, label="Tick Clock", pos=(960, 390), size=(100, 25))
        self.execute_frame_btn = wx.Button(self, -1, label="Run Frame", pos=(960, 500), size=(100, 25))
        self.load_rom = wx.Button(self, -1, label="Load ROM", pos=(845, 390), size=(100, 25))
        self.reset = wx.Button(self, -1, label="Reset Program", pos=(660, 390), size=(100, 25))

        # other buttons
        self.draw_pattern_table_checkbox = wx.CheckBox(self, -1, label="Draw CHR Table", pos=(660, 430), size=(400, 20))
        self.draw_pattern_table_checkbox.SetBackgroundColour(wx.Colour(140, 150, 155))
        self.draw_pattern_table_checkbox.SetValue(False)

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
