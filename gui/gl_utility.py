from OpenGL.GL import *


def float_size(n=1):
    return sizeof(ctypes.c_float) * n


def pointer_offset(n=0):
    return ctypes.c_void_p(float_size(n))
