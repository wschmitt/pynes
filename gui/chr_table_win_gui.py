import wx

from wx import glcanvas
from OpenGL.GL import *
import numpy as np
import gui.shaders as shader
import gui.gl_utility as gl_util


class OpenGLCanvasPatternTable(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(290, 275), pos=(5, 40))

        self.init = False
        self.screen_quad_vao = 0
        self.shader = None

        # opengl canvas for pattern table
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)

        self.__screen_tex = np.zeros((128, 128, 3))
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.InitGL()

    def SetContext(self):
        self.SetCurrent(self.context)
        glViewport(0, 0, 290, 275)
        self.InitGL()

        for i in range(0, 0x80):
            for j in range(0, 0x80):
                self.SetPixel(i, j, [0, 0, 0])

    def InitGL(self):
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

        glViewport(0, 0, 290, 275)
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
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 128, 128, 0, GL_RGB, GL_UNSIGNED_BYTE, self.__screen_tex)
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
        self.__screen_tex[127 - y][x] = color

    def SetTexture(self, tex):
        for y in range(0, len(self.__screen_tex)):
            for x in range(0, len(self.__screen_tex[y])):
                self.SetPixel(x, y, tex[y][x])

    def OnDraw(self):
        self.SetCurrent(self.context)
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw_quad()
        # glDrawArrays(GL_TRIANGLES, 0, 6)
        self.SwapBuffers()


class PatternPopup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)

        elements = [self]

        self.canvas = OpenGLCanvasPatternTable(self)
        self.SetBackgroundColour("CADET BLUE")
        elements.append(self.canvas)

        # change palettes
        title = wx.StaticText(self, -1, "CHR TABLE", pos=(10, 6), size=(40, 20), style=wx.ALIGN_RIGHT)
        title.SetFont(wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        elements.append(title)

        elements.append(wx.StaticText(self, -1, "PALETTE", pos=(190, 10), size=(50, 20), style=wx.ALIGN_RIGHT))
        self.palette_spinner = wx.SpinCtrl(self, pos=(250, 8), size=(50, 20), style=wx.BORDER_RAISED)
        self.palette_spinner.SetMax(7)

        self.SetSize(310, 330)

        for element in elements:
            element.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
            element.Bind(wx.EVT_MOTION, self.OnMouseMotion)
            element.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
            element.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        wx.CallAfter(self.Refresh)

    def SetContextAsCurrent(self):
        self.canvas.SetContext()

    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0, 0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                    self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
