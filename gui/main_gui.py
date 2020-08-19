import wx

from wx import glcanvas
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

import gui.shaders as shader
import gui.gl_utility as gl_util

from gui.chr_table_win_gui import PatternPopup
from gui.ram_win_gui import RamPopup
from gui.cpu_win_gui import CpuPopup


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
        glViewport(0, 0, size[0], size[1])

    def InitGL(self):
        glViewport(0, 0, 640, 600)
        # positions / tex coords
        quad = np.array([-1, 1, 0, 1,
                         -1, -1, 0, 0,
                         1, -1, 1, 0,
                         -1, 1, 0, 1,
                         1, -1, 1, 0,
                         1, 1, 1, 1], dtype=np.float32)

        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(shader.vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(shader.fragment_shader, GL_FRAGMENT_SHADER))

        self.screen_quad_vao = GLuint()
        glGenVertexArrays(1, self.screen_quad_vao)
        glBindVertexArray(self.screen_quad_vao)

        quad_vbo = GLuint()
        glGenBuffers(1, quad_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, gl_util.float_size(4), gl_util.pointer_offset(0))
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, gl_util.float_size(4), gl_util.pointer_offset(2))
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
        self.__screen_tex[239 - y][x] = color

    def SetTexture(self, tex):
        for y in range(0, len(self.__screen_tex)):
            for x in range(0, len(self.__screen_tex[y])):
                self.SetPixel(x, y, tex[y][x])

    def OnDraw(self):
        self.SetCurrent(self.context)
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw_quad()
        self.SwapBuffers()


class EmuPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.canvas = OpenGLCanvas(self)
        self.SetBackgroundColour("#626D58")

        # execute instruction button
        self.tick_clock_btn = wx.Button(self, -1, label="Tick Clock", pos=(960, 390), size=(100, 25))
        self.tick_clock_qty_text = wx.TextCtrl(self, -1, value="1", pos=(960, 417), size=(100, 25))
        self.execute_frame_btn = wx.Button(self, -1, label="Run Frame", pos=(960, 500), size=(100, 25))
        self.reset = wx.Button(self, -1, label="Reset Program", pos=(660, 390), size=(100, 25))

        # main menus
        self.load_rom = wx.Button(self, -1, label="Load ROM", pos=(660, 5), size=(100, 25))
        self.open_chr_table_gui = wx.Button(self, -1, label="Open CHR", pos=(660, 50), size=(100, 25))
        self.open_ram_gui = wx.Button(self, -1, label="Open RAM", pos=(660, 80), size=(100, 25))
        self.open_cpu_gui = wx.Button(self, -1, label="Open CPU", pos=(660, 110), size=(100, 25))
        # self.processor = wx.Button(self, -1, label="Pattern Table", pos=(760, 50), size=(100, 25))

        # other buttons
        # self.draw_pattern_table_checkbox = wx.CheckBox(self, -1, label="Draw CHR Table", pos=(660, 430), size=(100, 20))
        # self.draw_pattern_table_checkbox.SetBackgroundColour(wx.Colour(140, 150, 155))
        # self.draw_pattern_table_checkbox.SetValue(False)

        # floating windows
        self.chr_gui = PatternPopup(self.GetTopLevelParent(), style=wx.BORDER_RAISED)
        self.ram_gui = RamPopup(self.GetTopLevelParent(), style=wx.BORDER_RAISED)
        self.cpu_gui = CpuPopup(self.GetTopLevelParent(), style=wx.BORDER_RAISED)

        # self.on_show_popup(None)

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
