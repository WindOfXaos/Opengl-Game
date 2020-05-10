import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from math import *

from objloader import *
import FPSM   
dm = 0

def moving():
    global dm
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    keys = pygame.key.get_pressed()

    if keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d]:
        fwd = 0.5*(keys[K_w]-keys[K_s])
        strafe = 0.5*(keys[K_a]-keys[K_d])
        if abs(fwd) or abs(strafe):
            glTranslate(fwd*m[2]*dm,0 ,fwd*m[10]*dm)
            glTranslate(strafe*m[0]*dm,0 ,strafe*m[8]*dm)
        if dm < 0.5: dm += 0.01
    else:
        dm = 0

def drawXYZ():
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3d(0, 0, 0)
    glVertex3d(100, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 100, 0)

    glColor3f(0, 0, 1)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 0, -100)

    glColor3f(1, 1, 1)
    glEnd()

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    viewport = (800,600)
    hx = viewport[0]/2
    hy = viewport[1]/2
    screen = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.set_pos(hx / 2, hy / 2)
   
    glMatrixMode(GL_PROJECTION)
    gluPerspective(90, viewport[0]/viewport[1], 0.01, 10000)
    glMatrixMode(GL_MODELVIEW)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)

    #Loading objects
    aksound = os.path.join(scriptDIR,"animated\\ak47shot.wav")
    effect1 = pygame.mixer.Sound(aksound)
    effect1.set_volume(0.2)

    obj2 = os.path.join(scriptDIR,"car\\Low_Poly_City_Cars.obj")
    world = OBJ(obj2,swapyz = True)

    obj3 = os.path.join(scriptDIR,"cats\\cat2.obj")
    cat1 = OBJ(obj3,swapyz = True)

    i = 0
    direct = os.path.join(scriptDIR, "animated")
    ak = [None for _ in range(13)]
    for filename in os.listdir(direct):
        if filename.endswith(".obj"):
            obj1 = os.path.join(direct, filename)
            ak[i] = OBJ(obj1,swapyz = True)
            i = i + 1
        else:
            continue

    
    
    clock = pygame.time.Clock()
    exit = True
    i = 0
    fire = False

    while exit:
        
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()  

        #EXIT GAME
        if keys[pygame.K_ESCAPE]:
            exit = False
 
        
            
        #UP_DOWN
        mup = -2 * (keys[K_UP]-keys[K_DOWN])
        if abs(mup):
            mup = mup * 4
            glTranslatef(0, mup, 0)


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        glPushMatrix()
        drawXYZ()
        glRotate(-90, 1, 0, 0)
        glCallList(world.gl_list)
        glPopMatrix()

        
        fire = False  
        mov = FPSM.Spectator()
        mov.get_keys()
        mov.controls_3d(1, 0,'w','s','a','d')
    
        glPushMatrix()
        glLoadIdentity()
        glTranslate(1.5+1.5, -1.5, -3-2.5)
        glRotate(-2, 1, 0, 0)
        glRotate(173, 0, 1, 0)

        pygame.mixer.stop()
        if pygame.mouse.get_pressed()[0]:
            fire = True
        if fire:
            effect1.play()
            moving()
            glCallList(ak[i].gl_list)
            i += 1
            if i == 13:
                fire, i = False, 0
        else:
            moving()
            glCallList(ak[0].gl_list)

        glPopMatrix()




        pygame.display.flip()

main()


