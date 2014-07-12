#!/usr/bin/python3.4

from OpenGL.GLUT import *
from OpenGL.GL import *
import sys
import csv

observers = {}
(view_rotx,view_roty,view_rotz) = (20.0, 30.0, 0.0)

class Viewer:
    def __init__(self, window_name, window_size_horizontal, window_size_vertical):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(window_size_horizontal, window_size_vertical)
        glutCreateWindow(bytes(window_name))
        glutDisplayFunc(self.display)
        glutSpecialFunc(self.special)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

    def start(self):
        glutMainLoop()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(0.5, 0.5, 0.5)
        glutWireSphere(0.5, 16, 16)
        glPopMatrix()
        glFlush()

        glPushMatrix()
        glRotatef(view_rotx, 1.0, 0.0, 0.0)
        glRotatef(view_roty, 0.0, 1.0, 0.0)
        glRotatef(view_rotz, 0.0, 0.0, 1.0)

        glPopMatrix()
        glutSwapBuffers()


    def special(k, x, y):
        global view_rotx, view_roty, view_rotz
      
        if k == GLUT_KEY_UP:
            view_rotx += 5.0
        elif k == GLUT_KEY_DOWN:
            view_rotx -= 5.0
        elif k == GLUT_KEY_LEFT:
            view_roty += 5.0
        elif k == GLUT_KEY_RIGHT:
            view_roty -= 5.0
        else:
            return
        glutPostRedisplay()


def load_data(path):
    global observers

    try:
        f = open(path, "r")
    except FileNotFoundError:
        print("ERR cannot open", path)
        sys.exit()

    data  = csv.reader(f,  quotechar = "\"")

    print("")
    for row in data:
        print("\rProcessing meteor number: ", row[0], end = "")
        
        if row[10] in observers: observers[row[10]] += 1
        else: observers[row[10]] = 1
    
    f.close()
    print("... Processing Done")
    for i in observers:
        print(i, ": ", observers[i])


window = Viewer(b"Meteor viewer", 640, 480)

try:
    load_data(sys.argv[1])
except IndexError:
    print("WARNING no file loaded")

window.start()