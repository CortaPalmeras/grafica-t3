import pyglet
from OpenGL.GL import *
import numpy as np
from math import cos, sin
import libs.transformations as tr
import libs.easy_shaders as sh
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

with open("assets\ship_cords.txt", "r") as file:
    ship_vert = np.array(file.read().replace("\n"," ").split(" "))

count = len(ship_vert)//6
dark_vert = np.array(ship_vert).reshape([count,6])
dark_vert[:,3:] = np.zeros(([count,3]))
dark_vert = dark_vert.reshape([count*6])

ship_ind = (0,1,4, 1,2,4, 2,3,4, 3,0,4, 3,2,5, 2,1,5, 1,0,5, 0,3,5,
            6,7,8, 9,8,7, 6,8,9, 9,7,6, 
            10,12,11, 11,12,13, 10,13,12, 10,11,13, 
            14,15,16, 17,19,18, 16,15,18, 14,18,15,
            22,21,20, 24,25,23, 24,21,22, 20,21,24)

ind_lines = (0,1, 1,2, 2,3, 3,0, 4,0, 4,1, 4,2, 4,3, 5,0,5,1, 5,2, 5,3,
            6,7, 7,8, 8,6, 6,9, 9,7, 9,8,
            10,11, 11,12, 12,10, 10,13, 13,11, 13,12,
            14,15, 15,16, 16,17, 17,18, 18,19, 15,18,
            24,21, 25,24, 24,23, 23,22, 22,21, 21,20)

win = pyglet.window.Window()
win.set_exclusive_mouse(True)
win.set_mouse_visible(False)
program = sh.SimpleModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
ship = gp.createGPUShape(program, Shape(ship_vert, ship_ind))
lines =  gp.createGPUShape(program, Shape(dark_vert, ind_lines))

glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glClearColor(0.15, 0.15, 0.17, 1.0)

view = tr.lookAt(np.array([0,0,2]), np.array([0,0,0]), np.array([0,1,2]))
glUniformMatrix4fv(glGetUniformLocation(program.shaderProgram, "view"), 1, GL_TRUE, view)
ratio = win.aspect_ratio
projection = tr.frustum(-0.5 * ratio, 0.5 * ratio, -0.5, 0.5, 0.5, 4)
glUniformMatrix4fv(glGetUniformLocation(program.shaderProgram, "projection"), 1, GL_TRUE, projection)
rot_loc = glGetUniformLocation(program.shaderProgram, "model")

theta = 0.0
phi = 0.0
rotate_left = False
rotate_right = False
forward = False
backward = False
position = np.zeros(3)

@win.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glUseProgram(program.shaderProgram)
    program.drawCall(ship, GL_TRIANGLES)
    program.drawCall(lines, GL_LINES)

    global theta, position
    if rotate_left:
        theta += 0.05
    if rotate_right:
        theta -= 0.05

    c = cos(theta)
    s = sin(theta)
    c2 = cos(phi)
    s2 = sin(phi)

    direction = np.array((-s*c2,s2,-c*c2))

    if forward:
        if position[1]<=0 and phi<0:
            direction[1] = 0
        position += direction * 0.05

    elif backward:
        if (position[1]<=0 and phi>0):
            direction[1] = 0
        position -= direction * 0.05

    transform = tr.translate(*position) @ tr.rotationY(theta) @ tr.rotationX(phi)
    glUniformMatrix4fv(rot_loc, 1, GL_TRUE, transform)

@win.event
def on_mouse_motion(x, y, dx, dy):
    global phi
    if dy > 0.0 and phi < 0.785:
        phi += dy/600
    elif dy < 0.0 and phi > -0.785:
        phi += dy/600

@win.event
def on_key_press(symbol, mods):
    global rotate_left, rotate_right, forward, backward
    if symbol == pyglet.window.key.A:
        rotate_left = True
    elif symbol == pyglet.window.key.D:
        rotate_right = True
    elif symbol == pyglet.window.key.W:
        forward = True
    elif symbol == pyglet.window.key.S:
        backward = True
    elif symbol == pyglet.window.key.ESCAPE:
        win.close()

@win.event
def on_key_release(symbol, mods):
    global rotate_left, rotate_right, forward, backward
    if symbol == pyglet.window.key.A:
        rotate_left = False
    elif symbol == pyglet.window.key.D:
        rotate_right = False
    elif symbol == pyglet.window.key.W:
        forward = False
    elif symbol == pyglet.window.key.S:
        backward = False

@win.event
def on_close():
    ship.clear()
    lines.clear()
    glDeleteProgram(program.shaderProgram)

pyglet.app.run()