import pyglet
from OpenGL.GL import *
import numpy as np
import ctypes
from PIL import Image
from OpenGL.GL.shaders import compileProgram, compileShader

vertex_shader = """
#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 vertexColor;
layout (location=2) in vec2 vertexTexCoord;

out vec3 fragmentColor;
out vec2 fragmentTexCoord;

void main()
{
    gl_Position = vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
    fragmentTexCoord = vertexTexCoord;
}"""

fragment_shader = """
#version 330 core

in vec3 fragmentColor;
in vec2 fragmentTexCoord;

out vec4 color;

uniform sampler2D imageTexture;

void main()
{
    color = vec4(fragmentColor, 1.0) * texture(imageTexture, fragmentTexCoord);
}
"""

# CREAR VENTANA Y PROGRAMA

win = pyglet.window.Window(800, 600)
glClearColor(0.15, 0.15, 0.17, 1.0)
program = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                        compileShader(fragment_shader, GL_FRAGMENT_SHADER))
glUseProgram(program)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# DEFINIR VERTICES

vertices = np.array((
    -0.5, -0.5, 0.0, 0.9, 0.0, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
     0.5,  0.5, 0.0, 0.9, 0.0, 0.0, 1.0, 0.0,
), dtype=np.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))


# IMPORTAR TEXTURAS

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

image = np.array(Image.open("Tarea3\cat.png"))
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
glUniform1i(glGetUniformLocation(program, "imageTexture"), 0)
glGenerateMipmap(GL_TEXTURE_2D) 
glActiveTexture(GL_TEXTURE0)

# DEFINIR EVENTOS

@win.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 6)

@win.event
def on_close():
    glDeleteVertexArrays(1,(vao,))
    glDeleteBuffers(1,(vbo,))
    glDeleteTextures(1, (texture,))
    glDeleteProgram(program)
    print("mememoria liberada")

pyglet.app.run()